from __future__ import annotations

import hashlib
import json
from pathlib import Path

STATE_FILE = Path(".migration_state.json")


def report_hash(report: dict) -> str:
    return hashlib.sha256(json.dumps(report, sort_keys=True).encode("utf-8")).hexdigest()


def load() -> dict:
    if not STATE_FILE.exists():
        return {}
    return json.loads(STATE_FILE.read_text(encoding="utf-8"))


def should_process(report: dict) -> bool:
    state = load()
    return state.get(report["report_id"]) != report_hash(report)


def mark_processed(report: dict) -> None:
    state = load()
    state[report["report_id"]] = report_hash(report)
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")
