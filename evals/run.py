from __future__ import annotations

import json
from pathlib import Path

from app.main import store
from app.retrieval import HybridRetriever
from app.synthesis import GroundedSynthesizer


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    cases = [
        json.loads(line)
        for line in (root / "evals" / "gold.jsonl").read_text().splitlines()
        if line.strip()
    ]
    retriever = HybridRetriever(store)
    synthesizer = GroundedSynthesizer()

    hits_at_3 = 0
    cited = 0
    answered = 0
    for case in cases:
        hits = retriever.search(case["question"], top_k=3)
        if any(h.passage.document_id == case["expected_document_id"] for h in hits):
            hits_at_3 += 1
        _, citations, abstained = synthesizer.answer(case["question"], hits)
        if not abstained:
            answered += 1
            cited += int(bool(citations))

    n = len(cases)
    print(json.dumps({
        "cases": n,
        "recall_at_3": round(hits_at_3 / n, 3),
        "citation_coverage": round(cited / answered, 3) if answered else 0.0,
        "abstention_rate": round((n - answered) / n, 3),
    }, indent=2))


if __name__ == "__main__":
    main()
