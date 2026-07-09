from __future__ import annotations

import json
from collections.abc import AsyncIterator

import httpx

from ..config import settings
from .base import LLMProvider


class OllamaProvider(LLMProvider):
    name = "ollama"

    def __init__(self) -> None:
        self.base_url = settings.ollama_base_url.rstrip("/")
        self.model = settings.ollama_model

    async def stream(self, system: str, user: str) -> AsyncIterator[str]:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "stream": True,
        }
        async with httpx.AsyncClient(timeout=httpx.Timeout(120.0)) as client:
            async with client.stream(
                "POST", f"{self.base_url}/api/chat", json=payload
            ) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not line.strip():
                        continue
                    data = json.loads(line)
                    token = data.get("message", {}).get("content")
                    if token:
                        yield token
                    if data.get("done"):
                        break
