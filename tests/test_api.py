from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_query_has_citations():
    response = client.post(
        "/v1/query",
        json={"question": "What should be logged for an evidence assistant?", "top_k": 3},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["request_id"]
    assert isinstance(body["citations"], list)
    assert body["citations"]


def test_add_document():
    response = client.post(
        "/v1/documents",
        json={
            "document_id": "demo",
            "title": "Demo",
            "text": "A sufficiently long piece of evidence for indexing.",
        },
    )
    assert response.status_code == 200
    assert response.json()["document_id"] == "demo"


def test_query_abstains_without_evidence():
    response = client.post(
        "/v1/query",
        json={"question": "How should I tune a racing motorcycle suspension?", "top_k": 3},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["abstained"] is True
    assert body["citations"] == []
