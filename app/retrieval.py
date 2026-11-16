from __future__ import annotations

from dataclasses import dataclass
import re

import numpy as np
from rank_bm25 import BM25Okapi
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.store import DocumentStore, Passage


_TOKEN_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]+")
_CONFIDENCE_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "before", "by", "for", "from",
    "how", "i", "in", "is", "it", "of", "on", "or", "should", "that", "the",
    "to", "what", "when", "where", "which", "with",
}


def tokenize(text: str) -> list[str]:
    return [m.group(0).lower() for m in _TOKEN_RE.finditer(text)]


@dataclass(frozen=True)
class SearchHit:
    passage: Passage
    score: float
    confidence: float
    lexical_rank: int
    tfidf_rank: int


class HybridRetriever:
    """Deterministic BM25 + TF-IDF retriever with reciprocal-rank fusion."""

    def __init__(self, store: DocumentStore, rrf_k: int = 60) -> None:
        self.store = store
        self.rrf_k = rrf_k

    def search(self, query: str, top_k: int = 3) -> list[SearchHit]:
        passages = self.store.passages()
        if not passages:
            return []

        texts = [p.text for p in passages]
        tokenized = [tokenize(t) for t in texts]
        query_tokens = tokenize(query)
        bm25 = BM25Okapi(tokenized)
        bm25_scores = np.asarray(bm25.get_scores(query_tokens), dtype=float)

        vectorizer = TfidfVectorizer(lowercase=True, ngram_range=(1, 2), stop_words="english")
        matrix = vectorizer.fit_transform(texts + [query])
        tfidf_scores = cosine_similarity(matrix[-1], matrix[:-1]).ravel()

        lexical_order = list(np.argsort(-bm25_scores))
        tfidf_order = list(np.argsort(-tfidf_scores))
        lexical_rank = {idx: rank + 1 for rank, idx in enumerate(lexical_order)}
        tfidf_rank = {idx: rank + 1 for rank, idx in enumerate(tfidf_order)}

        query_token_set = {t for t in query_tokens if t not in _CONFIDENCE_STOPWORDS}
        fused: list[SearchHit] = []
        for idx, passage in enumerate(passages):
            rrf_score = (
                1.0 / (self.rrf_k + lexical_rank[idx])
                + 1.0 / (self.rrf_k + tfidf_rank[idx])
            )
            passage_tokens = set(tokenized[idx])
            token_overlap = (
                len(query_token_set & passage_tokens) / len(query_token_set)
                if query_token_set else 0.0
            )
            confidence = max(float(tfidf_scores[idx]), token_overlap)
            fused.append(SearchHit(
                passage=passage,
                score=float(rrf_score),
                confidence=confidence,
                lexical_rank=lexical_rank[idx],
                tfidf_rank=tfidf_rank[idx],
            ))

        fused.sort(key=lambda h: h.score, reverse=True)
        return fused[:top_k]
