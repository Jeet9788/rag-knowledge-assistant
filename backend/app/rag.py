"""RAG orchestration: retrieve context, build a grounded prompt, stream the answer."""
from __future__ import annotations

import logging
from collections.abc import AsyncIterator

from .llm import get_llm
from .retrieval import RetrievedChunk, retrieve

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a precise assistant that answers strictly from the provided context. "
    "Cite the sources you use with inline markers like [1], [2] that correspond to "
    "the numbered context passages. If the answer is not contained in the context, "
    "say you don't have enough information. Do not invent facts or citations."
)


def _build_context(chunks: list[RetrievedChunk]) -> str:
    blocks = []
    for i, chunk in enumerate(chunks, start=1):
        location = f"{chunk.filename}"
        if chunk.page is not None:
            location += f", p.{chunk.page}"
        blocks.append(f"[{i}] (source: {location})\n{chunk.content}")
    return "\n\n".join(blocks)


def _citations(chunks: list[RetrievedChunk]) -> list[dict]:
    out = []
    for i, chunk in enumerate(chunks, start=1):
        snippet = chunk.content.strip().replace("\n", " ")
        if len(snippet) > 280:
            snippet = snippet[:277] + "..."
        out.append(
            {
                "marker": i,
                "chunk_id": chunk.chunk_id,
                "document_id": chunk.document_id,
                "filename": chunk.filename,
                "page": chunk.page,
                "chunk_index": chunk.chunk_index,
                "score": round(chunk.score, 4),
                "snippet": snippet,
            }
        )
    return out


async def answer_stream(
    question: str, collection: str = "default", top_k: int | None = None
) -> AsyncIterator[dict]:
    """Yield event dicts: {'type': 'sources'|'token'|'done'|'error', ...}."""
    try:
        chunks = retrieve(question, collection=collection, top_k=top_k)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Retrieval failed")
        yield {"type": "error", "message": f"Retrieval error: {exc}"}
        return

    yield {"type": "sources", "sources": _citations(chunks)}

    if not chunks:
        yield {
            "type": "token",
            "text": "I don't have any indexed documents that answer this question.",
        }
        yield {"type": "done"}
        return

    context = _build_context(chunks)
    user_prompt = (
        f"Context passages:\n\n{context}\n\n"
        f"Question: {question}\n\n"
        "Answer using only the context above and cite passages with [n] markers."
    )

    try:
        llm = get_llm()
        async for token in llm.stream(SYSTEM_PROMPT, user_prompt):
            yield {"type": "token", "text": token}
    except Exception as exc:  # noqa: BLE001
        logger.exception("LLM streaming failed")
        yield {"type": "error", "message": f"LLM error: {exc}"}
        return

    yield {"type": "done"}
