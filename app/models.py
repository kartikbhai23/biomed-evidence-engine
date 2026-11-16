from __future__ import annotations

from pydantic import BaseModel, Field


class DocumentIn(BaseModel):
    document_id: str = Field(min_length=1, max_length=120)
    title: str = Field(min_length=1, max_length=240)
    text: str = Field(min_length=1)


class DocumentSummary(BaseModel):
    document_id: str
    title: str
    passages: int


class QueryIn(BaseModel):
    question: str = Field(min_length=3, max_length=2000)
    top_k: int = Field(default=3, ge=1, le=10)


class Citation(BaseModel):
    document_id: str
    passage_id: str
    title: str
    score: float
    excerpt: str


class QueryOut(BaseModel):
    answer: str
    citations: list[Citation]
    abstained: bool
    request_id: str
    latency_ms: float
