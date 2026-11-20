# Biomed Evidence Engine

A production-style scientific evidence assistant that retrieves source passages, produces citation-first answers, and measures retrieval quality before deployment.

This repository is intentionally built as an **AI product system**, not a notebook. It demonstrates the engineering layer between scientific documents and a trustworthy user-facing AI feature: ingestion, hybrid retrieval, grounded synthesis, evaluation, observability, APIs, testing, and deployment.

## Why this project

Many AI demos stop at "send context to an LLM." In scientific and regulated environments, that is not enough. A useful system needs to answer harder engineering questions:

- Which source passages were actually used?
- Can retrieval quality be measured independently from generation?
- What happens when the system has insufficient evidence?
- Can behavior be tested deterministically in CI?
- Can the model/provider be swapped without rewriting the product?
- Can an operator trace a request and understand latency or failure modes?

## System architecture

```mermaid
flowchart LR
    U[Scientist / User] --> API[FastAPI]
    API --> R[Hybrid Retriever]
    R --> S[(Document Store)]
    R --> B[BM25]
    R --> V[TF-IDF Similarity]
    API --> G[Grounded Synthesizer]
    G --> C[Citation Validator]
    API --> O[Structured Logs + Metrics]
    E[Evaluation Runner] --> R
    E --> M[Recall@K / Citation Coverage]
```

## What it demonstrates

- **Hybrid retrieval** using lexical BM25 and TF-IDF similarity
- **Citation-first answers** with document and passage identifiers
- **Abstention behavior** when evidence is too weak
- **Provider abstraction** so deterministic local synthesis can be swapped for an LLM
- **FastAPI** service with typed request/response contracts
- **Evaluation harness** with retrieval Recall@K and citation coverage
- **Structured JSON logging** with request IDs and latency
- **Prometheus-style metrics endpoint**
- **Unit and API tests**
- **Docker** support
- **GitHub Actions CI**
- Small **React + TypeScript** client scaffold

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for the API explorer.

### Ask a question

```bash
curl -s http://127.0.0.1:8000/v1/query \
  -H 'Content-Type: application/json' \
  -d '{"question":"What should be checked before a sequencing run is accepted?","top_k":3}'
```

## Evaluation

The repository includes a synthetic gold set so retrieval can be evaluated in CI without private data or external APIs.

```bash
python -m evals.run
```

Metrics include **Recall@K**, **citation coverage**, and **abstention rate**.

## API

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/health` | liveness check |
| `POST` | `/v1/query` | retrieve evidence and synthesize an answer |
| `POST` | `/v1/documents` | add a document at runtime |
| `GET` | `/v1/documents` | list indexed documents |
| `GET` | `/metrics` | lightweight operational metrics |

## Design choices

### Hybrid retrieval instead of embeddings-only

For small scientific corpora, exact terminology matters. BM25 preserves lexical matching while TF-IDF adds a second similarity signal. Reciprocal-rank fusion combines the two without pretending their raw scores are calibrated.

### Deterministic synthesis by default

The default synthesizer is deterministic and extractive, keeping tests reproducible and the project runnable without API keys. The interface can later support OpenAI, Anthropic, Bedrock, or local models.

### Explicit abstention

RRF ranking scores are not treated as confidence. The retriever calculates a separate evidence-confidence signal using TF-IDF similarity and lexical overlap. Weak evidence causes the system to abstain rather than fabricate an answer.

### Auditability

Every response contains a request ID and passage-level citations. Structured logs record latency, retrieval count, and abstention state without logging document text by default.

## Repository layout

```text
app/                  FastAPI, retrieval, synthesis, observability
evals/                gold cases and regression evaluation
data/                 synthetic scientific documents
tests/                API and retrieval tests
web/                  React + TypeScript client
.github/workflows/    CI
Dockerfile
```

## Production extensions

- pgvector / OpenSearch / managed vector search
- embedding and reranking models
- object storage and asynchronous ingestion
- OCR and document layout extraction
- auth, tenant isolation, and row-level permissions
- provider-backed generation with structured outputs
- prompt/version tracking and offline regression evals
- OpenTelemetry traces and production dashboards
- PII/PHI policy enforcement where applicable
- human review queues for low-confidence answers
- AWS deployment with ECS/Fargate or Kubernetes

## Recruiter TL;DR

This project shows end-to-end ownership of a production-style AI feature: **retrieval + evaluation + API + observability + testing + deployment**, with scientific data as the product context. It is a system-design project, not a model-training notebook.

## Data note

All sample documents are synthetic and exist only to demonstrate the system. They are not clinical, regulatory, or medical guidance.

## License

MIT


## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidance and scoped areas where another contributor can make a meaningful improvement.
