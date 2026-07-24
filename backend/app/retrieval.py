"""Hybrid retrieval: dense vector search + keyword (full-text) search fused via RRF,
then an optional cross-encoder reranker for the final ordering."""
from __future__ import annotations

import logging
import math
from dataclasses import dataclass

from .config import settings
from .db import get_pool
from .embeddings import embed_query, rerank

logger = logging.getLogger(__name__)

RRF_K = 60  # standard reciprocal-rank-fusion constant


def _sigmoid(x: float) -> float:
    """Map a cross-encoder logit onto 0-1. Guarded against overflow, which
    math.exp raises on for logits beyond about -745."""
    if x >= 0:
        return 1.0 / (1.0 + math.exp(-x))
    e = math.exp(x)
    return e / (1.0 + e)


@dataclass
class RetrievedChunk:
    chunk_id: str
    document_id: str
    filename: str
    page: int | None
    chunk_index: int
    content: str
    score: float


def _vector_search(collection: str, query_vec, limit: int) -> list[str]:
    pool = get_pool()
    with pool.connection() as conn:
        rows = conn.execute(
            "SELECT id FROM chunks WHERE collection = %s "
            "ORDER BY embedding <=> %s LIMIT %s",
            (collection, query_vec, limit),
        ).fetchall()
    return [str(r[0]) for r in rows]


def _keyword_search(collection: str, query: str, limit: int) -> list[str]:
    pool = get_pool()
    with pool.connection() as conn:
        rows = conn.execute(
            "SELECT id FROM chunks "
            "WHERE collection = %s AND tsv @@ plainto_tsquery('english', %s) "
            "ORDER BY ts_rank(tsv, plainto_tsquery('english', %s)) DESC LIMIT %s",
            (collection, query, query, limit),
        ).fetchall()
    return [str(r[0]) for r in rows]


def _reciprocal_rank_fusion(rankings: list[list[str]]) -> dict[str, float]:
    scores: dict[str, float] = {}
    for ranking in rankings:
        for rank, chunk_id in enumerate(ranking):
            scores[chunk_id] = scores.get(chunk_id, 0.0) + 1.0 / (RRF_K + rank + 1)
    return scores


def _fetch_chunks(chunk_ids: list[str]) -> dict[str, RetrievedChunk]:
    if not chunk_ids:
        return {}
    pool = get_pool()
    with pool.connection() as conn:
        rows = conn.execute(
            "SELECT c.id, c.document_id, d.filename, c.page, c.chunk_index, c.content "
            "FROM chunks c JOIN documents d ON d.id = c.document_id "
            "WHERE c.id::text = ANY(%s)",
            (chunk_ids,),
        ).fetchall()
    return {
        str(r[0]): RetrievedChunk(
            chunk_id=str(r[0]),
            document_id=str(r[1]),
            filename=r[2],
            page=r[3],
            chunk_index=r[4],
            content=r[5],
            score=0.0,
        )
        for r in rows
    }


def retrieve(query: str, collection: str = "default", top_k: int | None = None) -> list[RetrievedChunk]:
    """Return the most relevant chunks for a query using hybrid search + reranking."""
    final_k = top_k or settings.final_top_k
    candidate_k = settings.retrieve_top_k

    query_vec = embed_query(query)
    vector_ids = _vector_search(collection, query_vec, candidate_k)
    keyword_ids = _keyword_search(collection, query, candidate_k)

    fused = _reciprocal_rank_fusion([vector_ids, keyword_ids])
    if not fused:
        return []

    ranked_ids = sorted(fused, key=lambda cid: fused[cid], reverse=True)[:candidate_k]
    chunk_map = _fetch_chunks(ranked_ids)
    candidates = [chunk_map[cid] for cid in ranked_ids if cid in chunk_map]

    if settings.use_reranker and candidates:
        scores = rerank(query, [c.content for c in candidates])
        for chunk, score in zip(candidates, scores):
            # The cross-encoder emits an unbounded logit (commonly negative),
            # which is fine for ordering but meaningless to show a reader. These
            # ms-marco models are trained with binary cross-entropy, so the
            # sigmoid of that logit is a calibrated relevance probability.
            # Squashing here keeps `score` on a single 0-1 scale for every
            # caller, whichever branch produced it.
            chunk.score = _sigmoid(float(score))
        candidates.sort(key=lambda c: c.score, reverse=True)
    else:
        # RRF sums 1/(k+rank), so the raw fused value is tiny (~0.03 at best)
        # and depends on how many rankings were fused. Normalising against the
        # best candidate keeps the reported scale comparable to the reranked
        # branch instead of always reading as "almost zero relevance".
        best = max(fused.values())
        for chunk in candidates:
            raw = fused.get(chunk.chunk_id, 0.0)
            chunk.score = raw / best if best else 0.0

    return candidates[:final_k]
