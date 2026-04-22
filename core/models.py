from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class CaseReport:
    subject_name: str
    age: int
    status_type: str
    hours_missing: float
    last_seen_location: str
    weather: str
    temperature_f: int
    terrain: str
    mobility_level: str
    medical_risk: str
    has_phone: bool
    phone_battery: int
    wearable_detected: bool
    stress_level: str
    notes: str


@dataclass
class SearchZone:
    zone_name: str
    terrain_modifier: float
    behavior_modifier: float
    signal_modifier: float
    weather_modifier: float
    probability_score: float
    lat: float
    lon: float
    rationale: str


@dataclass
class DroneTask:
    drone_id: str
    zone_name: str
    pattern: str
    eta_minutes: int
    priority: str
    objective: str


@dataclass
class VolunteerTeam:
    team_name: str
    assigned_zone: str
    specialty: str
    members: int
    equipment: str
    priority: str
    objective: str


@dataclass
class SignalFinding:
    signal_type: str
    confidence: str
    last_ping_minutes_ago: Optional[int]
    recommended_zone: str
    rationale: str


@dataclass
class LLMMetadata:
    llm_used: bool = False
    llm_model: str = ""
    llm_error: str = ""
    agent_notes: List[str] = field(default_factory=list)
