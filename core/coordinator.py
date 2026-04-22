from datetime import datetime
from dataclasses import asdict

from agents import (
    CaseIntakeAgent,
    DroneCoordinationAgent,
    SearchZonePredictorAgent,
    SignalDetectionAgent,
    VolunteerManagementAgent,
)
from core.llm_client import LLMClient
from core.models import DroneTask, LLMMetadata, SearchZone, SignalFinding, VolunteerTeam
from core.utils import (
    ALLOWED_CONFIDENCE,
    ALLOWED_PRIORITIES,
    ALLOWED_URGENCY,
    ALLOWED_ZONES,
    format_operational_summary,
    normalize_zone_scores,
    validate_allowed,
)


class MissionCoordinator:
    def __init__(self, use_llm: bool = True):
        self.case_intake = CaseIntakeAgent()
        self.signal_detection = SignalDetectionAgent()
        self.zone_predictor = SearchZonePredictorAgent()
        self.drone_agent = DroneCoordinationAgent()
        self.volunteer_agent = VolunteerManagementAgent()
        self.use_llm = use_llm
        self.llm_client = LLMClient()

    def run(self, raw_input: dict, progress_callback=None) -> dict:
        llm_meta = LLMMetadata(llm_used=False, llm_model=self.llm_client.model)
        intake_analysis = {
            "intake_summary": "Deterministic intake validation completed.",
            "risk_flags": [],
            "urgency_level": "Medium",
        }

        def update_progress(label: str, state: str = "running"):
            if progress_callback:
                progress_callback(label, state)

        update_progress("Validating case intake")
        case = self.case_intake.process(raw_input)

        update_progress("Running signal detection")
        signal = self.signal_detection.process(case)

        update_progress("Ranking search zones")
        zones = self.zone_predictor.process(case, signal)

        update_progress("Assigning drone tasks")
        drones = self.drone_agent.process(zones, case.weather)

        update_progress("Assigning volunteer teams")
        volunteers = self.volunteer_agent.process(case, zones)

        if self.use_llm:
            try:
                if not self.llm_client.is_available():
                    raise RuntimeError("No OPENAI_API_KEY found.")

                update_progress("LLM: refining case intake")
                intake_payload = self.llm_client.generate_json(
                    self.case_intake.prompt,
                    {"case": asdict(case)},
                )

                urgency_level = validate_allowed(
                    intake_payload.get("urgency_level", "Medium"),
                    ALLOWED_URGENCY,
                    "Medium",
                )

                risk_flags = intake_payload.get("risk_flags", [])
                if not isinstance(risk_flags, list):
                    risk_flags = []

                intake_analysis = {
                    "intake_summary": str(
                        intake_payload.get("intake_summary", "No intake summary returned.")
                    )[:400],
                    "risk_flags": [str(flag)[:120] for flag in risk_flags[:5]],
                    "urgency_level": urgency_level,
                }
                llm_meta.agent_notes.append(
                    f"Case Intake Agent: {intake_analysis['intake_summary']}"
                )

                update_progress("LLM: refining signal analysis")
                signal_payload = self.llm_client.generate_json(
                    self.signal_detection.prompt,
                    {"case": asdict(case), "intake_analysis": intake_analysis},
                )

                signal_type = signal_payload.get("signal_type", signal.signal_type)
                if signal_type not in {"Phone", "Wearable", "None"}:
                    signal_type = signal.signal_type

                confidence = validate_allowed(
                    signal_payload.get("confidence", signal.confidence),
                    ALLOWED_CONFIDENCE,
                    signal.confidence,
                )
                recommended_zone = validate_allowed(
                    signal_payload.get("recommended_zone", signal.recommended_zone),
                    ALLOWED_ZONES,
                    signal.recommended_zone,
                )

                signal = SignalFinding(
                    signal_type=signal_type,
                    confidence=confidence,
                    last_ping_minutes_ago=signal.last_ping_minutes_ago,
                    recommended_zone=recommended_zone,
                    rationale=str(signal_payload.get("rationale", signal.rationale))[:400],
                )
                llm_meta.agent_notes.append(f"Signal Detection Agent: {signal.rationale}")

                update_progress("LLM: refining zone predictions")
                zones_payload = self.llm_client.generate_json(
                    self.zone_predictor.prompt,
                    {
                        "case": asdict(case),
                        "intake_analysis": intake_analysis,
                        "signal": asdict(signal),
                    },
                )

                zone_rankings = zones_payload.get("zone_rankings", [])
                if not isinstance(zone_rankings, list):
                    zone_rankings = []

                cleaned_zone_rankings = []
                for item in zone_rankings:
                    if not isinstance(item, dict):
                        continue
                    zone_name = validate_allowed(
                        item.get("zone_name", ""),
                        ALLOWED_ZONES,
                        "",
                    )
                    if not zone_name:
                        continue
                    cleaned_zone_rankings.append(
                        {
                            "zone_name": zone_name,
                            "probability_score": item.get("probability_score", 0),
                            "rationale": str(item.get("rationale", ""))[:300],
                        }
                    )

                zone_rankings = normalize_zone_scores(cleaned_zone_rankings)
                zone_lookup = {z.zone_name: z for z in zones}
                llm_zones = []

                for item in zone_rankings:
                    zone_name = item.get("zone_name")
                    if zone_name in zone_lookup:
                        original = zone_lookup[zone_name]
                        llm_zones.append(
                            SearchZone(
                                zone_name=zone_name,
                                terrain_modifier=original.terrain_modifier,
                                behavior_modifier=original.behavior_modifier,
                                signal_modifier=original.signal_modifier,
                                weather_modifier=original.weather_modifier,
                                probability_score=float(item.get("probability_score", original.probability_score)),
                                lat=original.lat,
                                lon=original.lon,
                                rationale=item.get("rationale", original.rationale),
                            )
                        )

                if len(llm_zones) >= 2:
                    llm_zones.sort(key=lambda z: z.probability_score, reverse=True)
                    zones = llm_zones
                    llm_meta.agent_notes.append("Search Zone Predictor Agent: LLM zone ranking applied.")

                update_progress("LLM: refining drone coordination")
                drone_payload = self.llm_client.generate_json(
                    self.drone_agent.prompt,
                    {
                        "case": asdict(case),
                        "intake_analysis": intake_analysis,
                        "signal": asdict(signal),
                        "zones": [asdict(z) for z in zones[:3]],
                    },
                )

                llm_drone_tasks = []
                drone_items = drone_payload.get("drone_tasks", [])
                if not isinstance(drone_items, list):
                    drone_items = []

                for idx, item in enumerate(drone_items[:3], start=1):
                    if not isinstance(item, dict):
                        continue
                    fallback = drones[min(idx - 1, len(drones) - 1)]
                    llm_drone_tasks.append(
                        DroneTask(
                            drone_id=str(item.get("drone_id", fallback.drone_id))[:20],
                            zone_name=validate_allowed(
                                item.get("zone_name", fallback.zone_name),
                                ALLOWED_ZONES,
                                fallback.zone_name,
                            ),
                            pattern=str(item.get("pattern", fallback.pattern))[:80],
                            eta_minutes=fallback.eta_minutes,
                            priority=validate_allowed(
                                item.get("priority", fallback.priority),
                                ALLOWED_PRIORITIES,
                                fallback.priority,
                            ),
                            objective=str(item.get("objective", fallback.objective))[:300],
                        )
                    )

                if llm_drone_tasks:
                    drones = llm_drone_tasks
                    llm_meta.agent_notes.append("Drone Coordination Agent: LLM drone tasking applied.")

                update_progress("LLM: refining volunteer assignments")
                volunteer_payload = self.llm_client.generate_json(
                    self.volunteer_agent.prompt,
                    {
                        "case": asdict(case),
                        "intake_analysis": intake_analysis,
                        "signal": asdict(signal),
                        "zones": [asdict(z) for z in zones[:3]],
                    },
                )

                llm_teams = []
                volunteer_items = volunteer_payload.get("volunteer_teams", [])
                if not isinstance(volunteer_items, list):
                    volunteer_items = []

                for idx, item in enumerate(volunteer_items[:3], start=1):
                    if not isinstance(item, dict):
                        continue
                    fallback = volunteers[min(idx - 1, len(volunteers) - 1)]
                    llm_teams.append(
                        VolunteerTeam(
                            team_name=str(item.get("team_name", fallback.team_name))[:40],
                            assigned_zone=validate_allowed(
                                item.get("assigned_zone", fallback.assigned_zone),
                                ALLOWED_ZONES,
                                fallback.assigned_zone,
                            ),
                            specialty=str(item.get("specialty", fallback.specialty))[:60],
                            members=fallback.members,
                            equipment=fallback.equipment,
                            priority=validate_allowed(
                                item.get("priority", fallback.priority),
                                ALLOWED_PRIORITIES,
                                fallback.priority,
                            ),
                            objective=str(item.get("objective", fallback.objective))[:300],
                        )
                    )

                if llm_teams:
                    volunteers = llm_teams
                    llm_meta.agent_notes.append("Volunteer Management Agent: LLM volunteer assignments applied.")

                llm_meta.llm_used = True
                update_progress("Mission plan ready", "complete")

            except Exception as ex:
                llm_meta.llm_error = str(ex)
                llm_meta.agent_notes.append("LLM enhancement failed. Deterministic fallback remained active.")
                update_progress("LLM unavailable, fallback plan ready", "complete")
        else:
            update_progress("Mission plan ready", "complete")

        return {
            "case": case,
            "signal": signal,
            "zones": zones,
            "drones": drones,
            "volunteers": volunteers,
            "intake_analysis": intake_analysis,
            "summary": format_operational_summary(case, signal, zones, llm_meta),
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "llm_meta": llm_meta,
        }