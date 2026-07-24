"""Retrieval-quality evaluation — does the passage that actually answers the
question land near the top of the results, and does the cross-encoder reranker
improve that ordering?

These are pure information-retrieval metrics (Hit@k and MRR) computed against a
small labelled set. A question's "relevant" passage is identified by a substring
that only appears in the sentence that answers it. Crucially this needs **no
judge LLM and makes no generation calls**, so it costs nothing and never touches
the app's LLM quota — unlike a ragas-style faithfulness eval.

Run inside the backend container (it has the DB, the models, and the app):

    docker compose exec -T backend python -m eval.retrieval_eval

Reports the pipeline with the reranker OFF (hybrid + RRF only) vs ON
(hybrid + RRF + cross-encoder rerank), so the reranker's contribution is visible
as a before/after.
"""
from __future__ import annotations

import json
from pathlib import Path

from app.config import settings
from app.retrieval import retrieve

DATASET = Path(__file__).parent / "retrieval_dataset.json"
KS = (1, 3, 5)
COLLECTION = "default"


def first_relevant_rank(question: str, needle: str) -> int | None:
    """Rank (1-based) of the first retrieved chunk containing the answer text,
    or None if no returned chunk contains it."""
    needle = needle.lower()
    chunks = retrieve(question, collection=COLLECTION)
    for rank, chunk in enumerate(chunks, start=1):
        if needle in chunk.content.lower():
            return rank
    return None


def run(use_reranker: bool, samples: list[dict]) -> tuple[dict, float, list[int | None]]:
    settings.use_reranker = use_reranker
    ranks = [first_relevant_rank(s["question"], s["relevant_substring"]) for s in samples]
    n = len(ranks)
    hits = {k: sum(1 for r in ranks if r is not None and r <= k) / n for k in KS}
    mrr = sum((1.0 / r) if r else 0.0 for r in ranks) / n
    return hits, mrr, ranks


def main() -> None:
    samples = json.loads(DATASET.read_text(encoding="utf-8"))
    print(f"Retrieval eval — {len(samples)} labelled questions, collection '{COLLECTION}'\n")

    results = {}
    header = f"{'reranker':<9}{'Hit@1':>8}{'Hit@3':>8}{'Hit@5':>8}{'MRR':>8}"
    print(header)
    print("-" * len(header))
    for flag, label in [(False, "off"), (True, "on")]:
        hits, mrr, ranks = run(flag, samples)
        results[label] = (hits, mrr, ranks)
        print(f"{label:<9}{hits[1]:>8.2f}{hits[3]:>8.2f}{hits[5]:>8.2f}{mrr:>8.3f}")

    (off_hits, off_mrr, off_ranks) = results["off"]
    (on_hits, on_mrr, on_ranks) = results["on"]
    print(
        f"\nReranker lift:  Hit@1 {off_hits[1]:.2f} -> {on_hits[1]:.2f}"
        f"   MRR {off_mrr:.3f} -> {on_mrr:.3f}  ({on_mrr - off_mrr:+.3f})"
    )

    print("\nfirst-relevant rank per question (off -> on; '-' = not in top 5):")
    for s, ro, rn in zip(samples, off_ranks, on_ranks):
        f = lambda r: "-" if r is None else str(r)
        print(f"  {f(ro):>2} -> {f(rn):>2}   {s['question']}")


if __name__ == "__main__":
    main()
