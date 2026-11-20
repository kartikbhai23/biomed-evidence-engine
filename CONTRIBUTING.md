# Contributing

Thanks for your interest in Biomed Evidence Engine.

This project is meant to be a compact reference implementation of trustworthy scientific AI systems. Contributions should improve the engineering quality, evaluation rigor, or usability of the system rather than add features for their own sake.

## Good contribution areas

- retrieval evaluation and reranking
- citation integrity checks
- observability and tracing
- API robustness
- frontend usability
- test coverage
- synthetic scientific evaluation cases

## Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
python -m evals.run
```

Frontend:

```bash
cd web
npm install
npm run build
```

## Pull requests

Please keep PRs focused and include:

- what changed
- why it matters
- how it was tested
- any tradeoffs or follow-up work

For behavior changes, add or update tests. For retrieval changes, report the effect on the evaluation suite.

Small, well-scoped PRs are welcome. If you want to pair on an issue, comment on it first and we can coordinate the implementation.
