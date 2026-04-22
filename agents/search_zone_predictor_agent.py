from core.models import CaseReport, SearchZone, SignalFinding
from config.prompts import AGENT_PROMPTS


class SearchZonePredictorAgent:
    name = "Search Zone Predictor Agent"
    prompt = AGENT_PROMPTS["search_zone_predictor"]

    def _terrain_weights(self, terrain: str) -> dict:
        terrain_profiles = {
            "Forest": {"A": 1.00, "B": 1.18, "C": 0.92, "D": 0.83},
            "Mountain": {"A": 0.88, "B": 1.20, "C": 1.06, "D": 0.79},
            "Urban Edge": {"A": 1.15, "B": 0.96, "C": 1.05, "D": 0.78},
            "Lake / Trail": {"A": 1.10, "B": 1.08, "C": 0.95, "D": 0.84},
        }
        return terrain_profiles.get(terrain, {"A": 1.0, "B": 1.0, "C": 1.0, "D": 1.0})

    def _weather_weights(self, weather: str) -> dict:
        weather_profiles = {
            "Clear": {"A": 1.0, "B": 1.0, "C": 1.0, "D": 1.0},
            "Rain": {"A": 1.03, "B": 0.95, "C": 1.00, "D": 0.96},
            "Fog": {"A": 1.00, "B": 1.05, "C": 1.04, "D": 0.90},
            "Cold Night": {"A": 0.98, "B": 1.08, "C": 1.02, "D": 0.93},
        }
        return weather_profiles.get(weather, {"A": 1.0, "B": 1.0, "C": 1.0, "D": 1.0})

    def _behavior_weights(self, case: CaseReport) -> dict:
        base = {"A": 1.0, "B": 1.0, "C": 1.0, "D": 1.0}

        if case.status_type == "Hiker":
            base["B"] += 0.18
            base["C"] += 0.10
        elif case.status_type == "Child":
            base["A"] += 0.16
            base["C"] += 0.08
        elif case.status_type == "Disaster Victim":
            base["A"] += 0.10
            base["D"] += 0.14

        if case.mobility_level == "Low":
            base["A"] += 0.12
            base["B"] -= 0.06
        elif case.mobility_level == "High":
            base["C"] += 0.12
            base["D"] += 0.08

        if case.stress_level == "High":
            base["A"] += 0.08
            base["B"] += 0.05

        if case.hours_missing > 12:
            base["C"] += 0.10
            base["D"] += 0.07

        return base

    def process(self, case: CaseReport, signal: SignalFinding) -> list[SearchZone]:
        terrain = self._terrain_weights(case.terrain)
        weather = self._weather_weights(case.weather)
        behavior = self._behavior_weights(case)

        signal_map = {
            "Zone A": {"A": 1.12, "B": 0.96, "C": 0.90, "D": 0.88},
            "Zone B": {"A": 0.96, "B": 1.20, "C": 1.05, "D": 0.90},
            "Zone C": {"A": 0.95, "B": 1.02, "C": 1.16, "D": 0.92},
            "Zone D": {"A": 0.92, "B": 0.95, "C": 1.00, "D": 1.15},
        }.get(signal.recommended_zone, {"A": 1.0, "B": 1.0, "C": 1.0, "D": 1.0})

        zone_meta = {
            "A": ("Zone A", 34.530, -83.986, "Closest to point last seen; easiest for rapid ground verification."),
            "B": ("Zone B", 34.544, -83.972, "Dense terrain corridor consistent with likely foot travel and partial signal support."),
            "C": ("Zone C", 34.520, -83.958, "Extended movement corridor for longer elapsed cases or mobile subjects."),
            "D": ("Zone D", 34.506, -83.993, "Lower-probability fallback zone for containment and widening the search ring."),
        }

        raw_scores = {}
        for key in ["A", "B", "C", "D"]:
            raw_scores[key] = terrain[key] * weather[key] * behavior[key] * signal_map[key]

        total = sum(raw_scores.values()) or 1.0

        zones = []
        for key, score in raw_scores.items():
            zone_name, lat, lon, rationale = zone_meta[key]
            zones.append(
                SearchZone(
                    zone_name=zone_name,
                    terrain_modifier=terrain[key],
                    behavior_modifier=behavior[key],
                    signal_modifier=signal_map[key],
                    weather_modifier=weather[key],
                    probability_score=round((score / total) * 100, 2),
                    lat=lat,
                    lon=lon,
                    rationale=rationale,
                )
            )

        zones.sort(key=lambda z: z.probability_score, reverse=True)
        return zones
