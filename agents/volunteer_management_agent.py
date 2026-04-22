from core.models import CaseReport, SearchZone, VolunteerTeam
from config.prompts import AGENT_PROMPTS


class VolunteerManagementAgent:
    name = "Volunteer Management Agent"
    prompt = AGENT_PROMPTS["volunteer_management"]

    def process(self, case: CaseReport, zones: list[SearchZone]) -> list[VolunteerTeam]:
        volunteer_pool = [
            ("Team Ridge", 6, "Trail Search", "radios, med kit, flashlights"),
            ("Team Echo", 5, "Medical Support", "stretcher, med kit, thermal blankets"),
            ("Team Pine", 4, "Dense Brush Search", "GPS, rope, radios"),
        ]

        teams = []
        for idx, (team_name, members, specialty, equipment) in enumerate(volunteer_pool):
            zone = zones[idx if idx < len(zones) else -1]
            priority = "High" if idx == 0 else ("Medium" if idx == 1 else "Reserve")
            objective = f"Conduct structured line search in {zone.zone_name}; report tracks, calls, or discarded items every 20 minutes."

            if case.medical_risk == "High" and idx == 1:
                objective = f"Stage near {zone.zone_name} for rapid extraction and warming support if the subject is located."

            teams.append(
                VolunteerTeam(
                    team_name=team_name,
                    assigned_zone=zone.zone_name,
                    specialty=specialty,
                    members=members,
                    equipment=equipment,
                    priority=priority,
                    objective=objective,
                )
            )
        return teams
