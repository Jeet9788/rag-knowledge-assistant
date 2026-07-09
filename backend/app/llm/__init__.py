"""LLM provider abstraction. Select provider via LLM_PROVIDER env var."""
from __future__ import annotations

from functools import lru_cache

from ..config import settings
from .base import LLMProvider
from .gemini_provider import GeminiProvider
from .ollama_provider import OllamaProvider
from .openai_provider import OpenAIProvider


@lru_cache
def get_llm() -> LLMProvider:
    provider = settings.llm_provider.lower()
    if provider == "ollama":
        return OllamaProvider()
    if provider == "gemini":
        return GeminiProvider()
    if provider == "openai":
        return OpenAIProvider()
    raise ValueError(f"Unknown LLM_PROVIDER: {settings.llm_provider}")


__all__ = ["get_llm", "LLMProvider"]
