from __future__ import annotations

import json
from collections.abc import AsyncIterator

import httpx

from ..config import settings
from .base import LLMProvider

BASE = "https://generativelanguage.googleapis.com/v1beta"


class GeminiProvider(LLMProvider):
    name = "gemini"

    def __init__(self) -> None:
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is not set.")
        self.api_key = settings.gemini_api_key
        self.model = settings.gemini_model

    async def stream(self, system: str, user: str) -> AsyncIterator[str]:
        url = f"{BASE}/models/{self.model}:streamGenerateContent"
        payload = {
            "system_instruction": {"parts": [{"text": system}]},
            "contents": [{"role": "user", "parts": [{"text": user}]}],
        }
        params = {"alt": "sse", "key": self.api_key}
        async with httpx.AsyncClient(timeout=httpx.Timeout(120.0)) as client:
            async with client.stream(
                "POST", url, params=params, json=payload
            ) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not line.startswith("data:"):
                        continue
                    chunk = line[len("data:"):].strip()
                    if not chunk or chunk == "[DONE]":
                        continue
                    data = json.loads(chunk)
                    for candidate in data.get("candidates", []):
                        for part in candidate.get("content", {}).get("parts", []):
                            text = part.get("text")
                            if text:
                                yield text
