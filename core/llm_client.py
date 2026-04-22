import os
from dotenv import load_dotenv
from openai import OpenAI

from core.parsers import extract_json


load_dotenv()


class LLMClient:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-5.4")
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None

    def is_available(self) -> bool:
        return bool(self.api_key and self.client)

    def generate_json(self, instructions: str, payload: dict) -> dict:
        if not self.is_available():
            raise RuntimeError("OPENAI_API_KEY is not configured.")

        response = self.client.responses.create(
            model=self.model,
            instructions=instructions,
            input=str(payload),
        )
        return extract_json(response.output_text)
