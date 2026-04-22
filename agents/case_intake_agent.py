from core.exceptions import ValidationError
from core.models import CaseReport
from config.prompts import AGENT_PROMPTS


class CaseIntakeAgent:
    name = "Case Intake Agent"
    prompt = AGENT_PROMPTS["case_intake"]

    def process(self, raw_input: dict) -> CaseReport:
        required_fields = [
            "subject_name",
            "age",
            "status_type",
            "hours_missing",
            "last_seen_location",
            "weather",
            "temperature_f",
            "terrain",
            "mobility_level",
            "medical_risk",
            "has_phone",
            "phone_battery",
            "wearable_detected",
            "stress_level",
            "notes",
        ]

        missing = [field for field in required_fields if field not in raw_input]
        if missing:
            raise ValidationError(f"Missing required fields: {', '.join(missing)}")

        age = int(raw_input["age"])
        hours_missing = float(raw_input["hours_missing"])
        phone_battery = int(raw_input["phone_battery"])
        temperature_f = int(raw_input["temperature_f"])

        if age < 0 or age > 120:
            raise ValidationError("Age must be between 0 and 120.")
        if hours_missing < 0:
            raise ValidationError("Hours missing cannot be negative.")
        if phone_battery < 0 or phone_battery > 100:
            raise ValidationError("Phone battery must be between 0 and 100.")

        return CaseReport(
            subject_name=str(raw_input["subject_name"]).strip() or "Unknown Subject",
            age=age,
            status_type=str(raw_input["status_type"]),
            hours_missing=hours_missing,
            last_seen_location=str(raw_input["last_seen_location"]),
            weather=str(raw_input["weather"]),
            temperature_f=temperature_f,
            terrain=str(raw_input["terrain"]),
            mobility_level=str(raw_input["mobility_level"]),
            medical_risk=str(raw_input["medical_risk"]),
            has_phone=bool(raw_input["has_phone"]),
            phone_battery=phone_battery,
            wearable_detected=bool(raw_input["wearable_detected"]),
            stress_level=str(raw_input["stress_level"]),
            notes=str(raw_input["notes"]).strip(),
        )
