from core.models import CaseReport, SignalFinding
from config.prompts import AGENT_PROMPTS


class SignalDetectionAgent:
    name = "Signal Detection Agent"
    prompt = AGENT_PROMPTS["signal_detection"]

    def process(self, case: CaseReport) -> SignalFinding:
        if case.has_phone and case.phone_battery >= 50:
            return SignalFinding(
                signal_type="Phone",
                confidence="High",
                last_ping_minutes_ago=18,
                recommended_zone="Zone B",
                rationale="Phone battery is healthy, so recent pings are likely actionable and should strongly influence nearby search placement.",
            )
        if case.has_phone and case.phone_battery >= 15:
            return SignalFinding(
                signal_type="Phone",
                confidence="Medium",
                last_ping_minutes_ago=47,
                recommended_zone="Zone C",
                rationale="Phone exists but battery is low, so signal confidence drops and search should broaden around the last known corridor.",
            )
        if case.wearable_detected:
            return SignalFinding(
                signal_type="Wearable",
                confidence="Medium",
                last_ping_minutes_ago=35,
                recommended_zone="Zone A",
                rationale="Wearable telemetry is intermittent but still useful enough to prioritize the nearest high-access zone first.",
            )

        return SignalFinding(
            signal_type="None",
            confidence="Low",
            last_ping_minutes_ago=None,
            recommended_zone="Zone D",
            rationale="No useful device data is available, so the search should rely more heavily on behavior, terrain, and elapsed time assumptions.",
        )
