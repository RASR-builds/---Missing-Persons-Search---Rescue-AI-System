import json
import re


def extract_json(text: str) -> dict:
    if not text:
        raise ValueError("Empty LLM response.")

    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise ValueError("Could not parse JSON from LLM response.")
