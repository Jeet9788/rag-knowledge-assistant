"""RAG quality evaluation using ragas.

Measures faithfulness, answer relevancy, context precision, and context recall
against a small labeled dataset. This is the metric harness that lets you show a
before/after retrieval-quality improvement on your resume.

Usage:
    # 1. Start the stack (docker compose up) and ingest your documents.
    # 2. Install eval deps:  pip install -r eval/requirements.txt
    # 3. Provide a judge LLM key (ragas needs one), e.g. OpenAI:
    #       export OPENAI_API_KEY=sk-...
    # 4. Run:  python eval/ragas_eval.py --api http://localhost:8000 --collection default
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import httpx


def query_backend(api: str, question: str, collection: str) -> tuple[str, list[str]]:
    """Call the backend /chat SSE endpoint; return (answer, retrieved_contexts)."""
    answer_parts: list[str] = []
    contexts: list[str] = []
    with httpx.Client(timeout=180.0) as client:
        with client.stream(
            "POST",
            f"{api}/chat",
            json={"question": question, "collection": collection},
        ) as resp:
            resp.raise_for_status()
            event_type = None
            for line in resp.iter_lines():
                if line.startswith("event:"):
                    event_type = line.split(":", 1)[1].strip()
                elif line.startswith("data:"):
                    data = json.loads(line.split(":", 1)[1].strip())
                    if event_type == "sources":
                        contexts = [s["snippet"] for s in data.get("sources", [])]
                    elif event_type == "token":
                        answer_parts.append(data.get("text", ""))
    return "".join(answer_parts), contexts


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--api", default="http://localhost:8000")
    parser.add_argument("--collection", default="default")
    parser.add_argument(
        "--dataset", default=str(Path(__file__).parent / "eval_dataset.json")
    )
    args = parser.parse_args()

    # Imported here so the module can be read without eval deps installed.
    from ragas import EvaluationDataset, evaluate
    from ragas.metrics import (
        answer_relevancy,
        context_precision,
        context_recall,
        faithfulness,
    )

    samples = json.loads(Path(args.dataset).read_text(encoding="utf-8"))

    rows = []
    for item in samples:
        answer, contexts = query_backend(args.api, item["question"], args.collection)
        rows.append(
            {
                "user_input": item["question"],
                "response": answer,
                "retrieved_contexts": contexts,
                "reference": item.get("ground_truth", ""),
            }
        )

    dataset = EvaluationDataset.from_list(rows)
    result = evaluate(
        dataset=dataset,
        metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
    )
    print("\n=== RAG evaluation results ===")
    print(result)


if __name__ == "__main__":
    main()
