from __future__ import annotations

import json
from pathlib import Path
import time
import uuid

from fastapi import FastAPI, Response

from app.models import DocumentIn, DocumentSummary, QueryIn, QueryOut
from app.observability import log_event, metrics
from app.retrieval import HybridRetriever
from app.store import DocumentStore
from app.synthesis import GroundedSynthesizer


app = FastAPI(
    title="Biomed Evidence Engine",
    version="0.1.0",
    description="Citation-first retrieval and evaluation for scientific documents.",
)
store = DocumentStore()
synthesizer = GroundedSynthesizer()


def _load_sample_data() -> None:
    path = Path(__file__).resolve().parents[1] / "data" / "sample_documents.json"
    if not path.exists():
        return
    for item in json.loads(path.read_text()):
        store.add(DocumentIn(**item))


_load_sample_data()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/v1/documents", response_model=list[DocumentSummary])
def list_documents() -> list[DocumentSummary]:
    return store.list_documents()


@app.post("/v1/documents", response_model=DocumentSummary)
def add_document(document: DocumentIn) -> DocumentSummary:
    store.add(document)
    metrics.inc("document_ingest")
    return next(d for d in store.list_documents() if d.document_id == document.document_id)


@app.post("/v1/query", response_model=QueryOut)
def query(request: QueryIn) -> QueryOut:
    started = time.perf_counter()
    request_id = str(uuid.uuid4())
    retriever = HybridRetriever(store)
    hits = retriever.search(request.question, top_k=request.top_k)
    answer, citations, abstained = synthesizer.answer(request.question, hits)
    latency_ms = round((time.perf_counter() - started) * 1000, 2)

    metrics.inc("query")
    metrics.inc("abstain" if abstained else "answered")
    log_event(
        "query_completed",
        request_id=request_id,
        latency_ms=latency_ms,
        retrieved=len(hits),
        abstained=abstained,
    )
    return QueryOut(
        answer=answer,
        citations=citations,
        abstained=abstained,
        request_id=request_id,
        latency_ms=latency_ms,
    )


@app.get("/metrics")
def get_metrics() -> Response:
    return Response(metrics.render(), media_type="text/plain; version=0.0.4")
