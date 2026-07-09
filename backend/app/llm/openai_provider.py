from __future__ import annotations

import json
from collections.abc import AsyncIterator

import httpx

from ..config import settings
from .base import LLMProvider

BASE = "https://api.openai.com/v1"


class OpenAIProvider(LLMProvider):
    name = "openai"

    def __init__(self) -> None:
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is not set.")
        self.api_key = settings.openai_api_key
        self.model = settings.openai_model

    async def stream(self, system: str, user: str) -> AsyncIterator[str]:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "stream": True,
        }
        headers = {"Authorization": f"Bearer {self.api_key}"}
        async with httpx.AsyncClient(timeout=httpx.Timeout(120.0)) as client:
            async with client.stream(
                "POST", f"{BASE}/chat/completions", json=payload, headers=headers
            ) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not line.startswith("data:"):
                        continue
                    chunk = line[len("data:"):].strip()
                    if not chunk or chunk == "[DONE]":
                        continue
                    data = json.loads(chunk)
                    for choice in data.get("choices", []):
                        token = choice.get("delta", {}).get("content")
                        if token:
                            yield token
