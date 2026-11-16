from __future__ import annotations

import re

from app.models import Citation
from app.retrieval import SearchHit


class GroundedSynthesizer:
    """Deterministic synthesis used so the demo and CI require no model API."""

    def __init__(self, min_confidence: float = 0.08) -> None:
        self.min_confidence = min_confidence

    def answer(self, question: str, hits: list[SearchHit]) -> tuple[str, list[Citation], bool]:
        if not hits or hits[0].confidence < self.min_confidence:
            return (
                "I do not have enough evidence in the indexed documents to answer that confidently.",
                [],
                True,
            )

        query_terms = set(re.findall(r"[A-Za-z0-9_-]+", question.lower()))
        ranked_sentences: list[tuple[int, str, SearchHit]] = []
        for hit in hits:
            sentences = re.split(r"(?<=[.!?])\s+", hit.passage.text)
            for sentence in sentences:
                terms = set(re.findall(r"[A-Za-z0-9_-]+", sentence.lower()))
                overlap = len(query_terms & terms)
                ranked_sentences.append((overlap, sentence.strip(), hit))

        ranked_sentences.sort(key=lambda x: (x[0], x[2].score), reverse=True)
        selected = [x for x in ranked_sentences if x[1]][:2]
        answer = " ".join(sentence for _, sentence, _ in selected)
        if not answer:
            answer = hits[0].passage.text[:360].strip()

        citations = [
            Citation(
                document_id=hit.passage.document_id,
                passage_id=hit.passage.passage_id,
                title=hit.passage.title,
                score=round(hit.score, 5),
                excerpt=hit.passage.text[:240].strip(),
            )
            for hit in hits
        ]
        return answer, citations, False
