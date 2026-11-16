from __future__ import annotations

from dataclasses import dataclass
import re

from app.models import DocumentIn, DocumentSummary


@dataclass(frozen=True)
class Passage:
    document_id: str
    passage_id: str
    title: str
    text: str


class DocumentStore:
    def __init__(self, chunk_chars: int = 700) -> None:
        self.chunk_chars = chunk_chars
        self._documents: dict[str, DocumentIn] = {}
        self._passages: list[Passage] = []

    def add(self, document: DocumentIn) -> None:
        self._documents[document.document_id] = document
        self._rebuild()

    def passages(self) -> list[Passage]:
        return list(self._passages)

    def list_documents(self) -> list[DocumentSummary]:
        counts: dict[str, int] = {}
        for p in self._passages:
            counts[p.document_id] = counts.get(p.document_id, 0) + 1
        return [
            DocumentSummary(document_id=d.document_id, title=d.title, passages=counts.get(d.document_id, 0))
            for d in self._documents.values()
        ]

    def _rebuild(self) -> None:
        passages: list[Passage] = []
        for document in self._documents.values():
            chunks = self._chunk(document.text)
            for idx, chunk in enumerate(chunks, start=1):
                passages.append(Passage(
                    document_id=document.document_id,
                    passage_id=f"{document.document_id}:p{idx}",
                    title=document.title,
                    text=chunk,
                ))
        self._passages = passages

    def _chunk(self, text: str) -> list[str]:
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
        chunks: list[str] = []
        current = ""
        for paragraph in paragraphs:
            candidate = f"{current}\n\n{paragraph}".strip()
            if current and len(candidate) > self.chunk_chars:
                chunks.append(current)
                current = paragraph
            else:
                current = candidate
        if current:
            chunks.append(current)
        return chunks or [text.strip()]
