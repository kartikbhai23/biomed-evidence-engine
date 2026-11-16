from __future__ import annotations

from collections import Counter
import json
import logging
import time
from typing import Any


logger = logging.getLogger("biomed_evidence_engine")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
logger.setLevel(logging.INFO)


class Metrics:
    def __init__(self) -> None:
        self.counters: Counter[str] = Counter()

    def inc(self, key: str) -> None:
        self.counters[key] += 1

    def render(self) -> str:
        lines = ["# TYPE evidence_engine_requests_total counter"]
        for key, value in sorted(self.counters.items()):
            lines.append(f'evidence_engine_requests_total{{kind="{key}"}} {value}')
        return "\n".join(lines) + "\n"


metrics = Metrics()


def log_event(event: str, **fields: Any) -> None:
    payload = {"event": event, "ts": round(time.time(), 3), **fields}
    logger.info(json.dumps(payload, sort_keys=True))
