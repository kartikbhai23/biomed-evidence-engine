from app.models import DocumentIn
from app.retrieval import HybridRetriever
from app.store import DocumentStore


def test_retrieval_prefers_matching_document():
    store = DocumentStore()
    store.add(DocumentIn(
        document_id="seq",
        title="Sequencing",
        text="RNA sequencing quality includes read quality and adapter contamination.",
    ))
    store.add(DocumentIn(
        document_id="infra",
        title="Infrastructure",
        text="Containers package software for deployment.",
    ))

    hits = HybridRetriever(store).search("sequencing read quality", top_k=1)
    assert hits[0].passage.document_id == "seq"


def test_irrelevant_query_has_low_confidence():
    store = DocumentStore()
    store.add(DocumentIn(
        document_id="seq",
        title="Sequencing",
        text="RNA sequencing quality includes read quality and adapter contamination.",
    ))
    hits = HybridRetriever(store).search("medieval architecture castles", top_k=1)
    assert hits[0].confidence < 0.08
