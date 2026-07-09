from __future__ import annotations

import abc
from collections.abc import AsyncIterator


class LLMProvider(abc.ABC):
    """Common interface for chat LLM providers with streaming support."""

    name: str = "base"

    @abc.abstractmethod
    async def stream(self, system: str, user: str) -> AsyncIterator[str]:
        """Yield answer text incrementally for the given system + user prompt."""
        raise NotImplementedError
        yield ""  # pragma: no cover - makes this an async generator
