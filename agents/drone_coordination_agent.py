from core.models import DroneTask, SearchZone
from config.prompts import AGENT_PROMPTS


class DroneCoordinationAgent:
    name = "Drone Coordination Agent"
    prompt = AGENT_PROMPTS["drone_coordination"]

    def process(self, zones: list[SearchZone], weather: str) -> list[DroneTask]:
        patterns = {
            "Clear": ["Grid Sweep", "Spiral Pass", "Thermal Sweep"],
            "Rain": ["Low-Altitude Corridor Sweep", "Thermal Sweep", "Contour Pass"],
            "Fog": ["Slow Thermal Sweep", "Low-Visibility Corridor Sweep", "Hold / Confirm Windows"],
            "Cold Night": ["Thermal Sweep", "Heat Signature Confirmation", "Grid Sweep"],
        }

        weather_patterns = patterns.get(weather, ["Grid Sweep", "Thermal Sweep", "Contour Pass"])
        tasks = []
        for idx, zone in enumerate(zones[:3], start=1):
            tasks.append(
                DroneTask(
                    drone_id=f"DR-{idx}",
                    zone_name=zone.zone_name,
                    pattern=weather_patterns[(idx - 1) % len(weather_patterns)],
                    eta_minutes=8 + (idx * 4),
                    priority="High" if idx == 1 else ("Medium" if idx == 2 else "Support"),
                    objective=f"Scan {zone.zone_name} for thermal anomalies, movement trails, and visible gear or clothing.",
                )
            )
        return tasks
