"""Local, CPU-based embeddings and reranking via fastembed (no API key required)."""
from __future__ import annotations

import logging
from functools import lru_cache

import numpy as np
from fastembed import TextEmbedding
from fastembed.rerank.cross_encoder import TextCrossEncoder

from .config import settings

logger = logging.getLogger(__name__)


@lru_cache
def _embedder() -> TextEmbedding:
    logger.info("Loading embedding model: %s", settings.embedding_model)
    return TextEmbedding(model_name=settings.embedding_model)


@lru_cache
def _reranker() -> TextCrossEncoder:
    logger.info("Loading reranker model: %s", settings.reranker_model)
    return TextCrossEncoder(model_name=settings.reranker_model)


def embed_texts(texts: list[str]) -> list[np.ndarray]:
    """Embed a batch of texts. Returns one float32 vector per input text.

    Returns numpy arrays because pgvector's psycopg adapter maps ndarray -> vector;
    plain Python lists would be sent as Postgres float arrays instead.
    """
    if not texts:
        return []
    return [np.asarray(vec, dtype=np.float32) for vec in _embedder().embed(texts)]


def embed_query(text: str) -> np.ndarray:
    """Embed a single query string."""
    return embed_texts([text])[0]


def rerank(query: str, documents: list[str]) -> list[float]:
    """Return a relevance score for each document against the query."""
    if not documents:
        return []
    return list(_reranker().rerank(query, documents))


def warmup() -> None:
    """Eagerly load models so the first request is not slow."""
    _embedder()
    if settings.use_reranker:
        _reranker()
