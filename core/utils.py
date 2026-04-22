import re


BLOCKED_PATTERNS = [
    "ignore previous instructions",
    "ignore all previous instructions",
    "disregard previous instructions",
    "reveal your prompt",
    "show your system prompt",
    "system prompt",
    "jailbreak",
    "do my homework",
    "help with homework",
    "write my essay",
    "cheat on",
    "answer unrelated questions",
    "ignore your role",
    "pretend you are",
]


ALLOWED_URGENCY = {"Low", "Medium", "High"}
ALLOWED_CONFIDENCE = {"Low", "Medium", "High"}
ALLOWED_ZONES = {"Zone A", "Zone B", "Zone C", "Zone D"}
ALLOWED_PRIORITIES = {"High", "Medium", "Support", "Reserve"}


def sanitize_text(value: str, max_len: int = 300) -> str:
    if value is None:
        return ""
    value = str(value).strip()

    # Remove characters commonly used in prompt injection / formatting abuse
    value = value.replace("{", "").replace("}", "")
    value = value.replace("<", "").replace(">", "")
    value = value.replace("```", "")
    value = re.sub(r"\s+", " ", value)

    return value[:max_len]


def contains_blocked_content(text: str) -> bool:
    if not text:
        return False
    lowered = text.lower()
    return any(pattern in lowered for pattern in BLOCKED_PATTERNS)


def validate_allowed(value: str, allowed: set[str], fallback: str) -> str:
    if value in allowed:
        return value
    return fallback


def normalize_zone_scores(rankings: list[dict]) -> list[dict]:
    total = sum(max(0, float(item.get("probability_score", 0))) for item in rankings) or 1.0
    normalized = []
    for item in rankings:
        score = max(0, float(item.get("probability_score", 0)))
        normalized.append(
            {
                **item,
                "probability_score": round((score / total) * 100, 2),
            }
        )
    return normalized


def format_operational_summary(case, signal, zones, llm_meta) -> str:
    top_zone = zones[0]
    second_zone = zones[1]
    llm_line = (
        f"- LLM enhancement: **Enabled ({llm_meta.llm_model})**.\n"
        if llm_meta.llm_used else
        "- LLM enhancement: **Unavailable, deterministic fallback used**.\n"
    )

    return (
        f"## Operational Summary\n\n"
        f"- Subject: **{case.subject_name}**, classified as **{case.status_type}**.\n"
        f"- Time missing: **{case.hours_missing:.1f} hours**.\n"
        f"- Highest-probability zone: **{top_zone.zone_name} ({top_zone.probability_score}%)**.\n"
        f"- Secondary zone: **{second_zone.zone_name} ({second_zone.probability_score}%)**.\n"
        f"- Signal picture: **{signal.signal_type} / {signal.confidence} confidence**.\n"
        f"{llm_line}"
        f"- Immediate recommendation: launch drone coverage over the top two zones while ground teams verify the nearest accessible corridor."
    )