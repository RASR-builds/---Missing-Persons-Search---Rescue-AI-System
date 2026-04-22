from core.exceptions import ValidationError
from core.models import CaseReport
from core.utils import sanitize_text, contains_blocked_content
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

        subject_name = sanitize_text(raw_input["subject_name"], max_len=80)
        last_seen_location = sanitize_text(raw_input["last_seen_location"], max_len=120)
        notes = sanitize_text(raw_input["notes"], max_len=400)

        status_type = str(raw_input["status_type"]).strip()
        weather = str(raw_input["weather"]).strip()
        terrain = str(raw_input["terrain"]).strip()
        mobility_level = str(raw_input["mobility_level"]).strip()
        medical_risk = str(raw_input["medical_risk"]).strip()
        stress_level = str(raw_input["stress_level"]).strip()

        allowed_status_types = {"Hiker", "Child", "Disaster Victim"}
        allowed_weather = {"Clear", "Rain", "Fog", "Cold Night"}
        allowed_terrain = {"Forest", "Mountain", "Urban Edge", "Lake / Trail"}
        allowed_mobility = {"Low", "Medium", "High"}
        allowed_risk = {"Low", "Medium", "High"}
        allowed_stress = {"Low", "Medium", "High"}

        if not subject_name:
            raise ValidationError("Subject name cannot be empty.")
        if not last_seen_location:
            raise ValidationError("Last seen location cannot be empty.")

        if status_type not in allowed_status_types:
            raise ValidationError("Invalid status type.")
        if weather not in allowed_weather:
            raise ValidationError("Invalid weather value.")
        if terrain not in allowed_terrain:
            raise ValidationError("Invalid terrain value.")
        if mobility_level not in allowed_mobility:
            raise ValidationError("Invalid mobility level.")
        if medical_risk not in allowed_risk:
            raise ValidationError("Invalid medical risk value.")
        if stress_level not in allowed_stress:
            raise ValidationError("Invalid stress level value.")

        for field_name, value in {
            "subject_name": subject_name,
            "last_seen_location": last_seen_location,
            "notes": notes,
        }.items():
            if contains_blocked_content(value):
                raise ValidationError(
                    f"Invalid content detected in {field_name}. Please enter only search-and-rescue case information."
                )

        return CaseReport(
            subject_name=subject_name,
            age=age,
            status_type=status_type,
            hours_missing=hours_missing,
            last_seen_location=last_seen_location,
            weather=weather,
            temperature_f=temperature_f,
            terrain=terrain,
            mobility_level=mobility_level,
            medical_risk=medical_risk,
            has_phone=bool(raw_input["has_phone"]),
            phone_battery=phone_battery,
            wearable_detected=bool(raw_input["wearable_detected"]),
            stress_level=stress_level,
            notes=notes,
        )