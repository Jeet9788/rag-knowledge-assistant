"""Text chunking strategies.

Two strategies are provided so the project can demonstrate a retrieval-quality
experiment (naive fixed-size vs. sentence-aware chunking). The active strategy
is controlled by CHUNK_SIZE / CHUNK_OVERLAP in settings.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


@dataclass
class Chunk:
    content: str
    page: int | None


def _clean(text: str) -> str:
    return re.sub(r"[ \t]+", " ", text).strip()


def fixed_size_chunks(
    text: str, chunk_size: int, overlap: int, page: int | None = None
) -> list[Chunk]:
    """Split text into overlapping fixed-size character windows."""
    text = _clean(text)
    if not text:
        return []
    chunks: list[Chunk] = []
    start = 0
    step = max(1, chunk_size - overlap)
    while start < len(text):
        window = text[start : start + chunk_size]
        chunks.append(Chunk(content=window.strip(), page=page))
        start += step
    return [c for c in chunks if c.content]


def sentence_aware_chunks(
    text: str, chunk_size: int, overlap: int, page: int | None = None
) -> list[Chunk]:
    """Group whole sentences into chunks near the target size (avoids mid-sentence cuts)."""
    text = _clean(text)
    if not text:
        return []
    sentences = [s.strip() for s in _SENTENCE_SPLIT.split(text) if s.strip()]
    chunks: list[Chunk] = []
    current: list[str] = []
    current_len = 0
    for sentence in sentences:
        if current_len + len(sentence) > chunk_size and current:
            chunks.append(Chunk(content=" ".join(current), page=page))
            # start next chunk with a tail overlap of the previous chunk
            tail: list[str] = []
            tail_len = 0
            for prev in reversed(current):
                if tail_len + len(prev) > overlap:
                    break
                tail.insert(0, prev)
                tail_len += len(prev)
            current = tail
            current_len = tail_len
        current.append(sentence)
        current_len += len(sentence)
    if current:
        chunks.append(Chunk(content=" ".join(current), page=page))
    return [c for c in chunks if c.content]


def chunk_pages(
    pages: list[tuple[int | None, str]],
    chunk_size: int,
    overlap: int,
    strategy: str = "sentence",
) -> list[Chunk]:
    """Chunk a list of (page_number, text) tuples using the chosen strategy."""
    fn = sentence_aware_chunks if strategy == "sentence" else fixed_size_chunks
    out: list[Chunk] = []
    for page, text in pages:
        out.extend(fn(text, chunk_size, overlap, page))
    return out
