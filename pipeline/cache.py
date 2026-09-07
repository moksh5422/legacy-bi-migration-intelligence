from __future__ import annotations

import hashlib
import json
from pathlib import Path

CACHE_DIR = Path(".migration_cache")


def key(payload: dict) -> str:
    value = json.dumps(payload, sort_keys=True).encode("utf-8")
    return hashlib.sha256(value).hexdigest()


def get(payload: dict) -> dict | None:
    path = CACHE_DIR / f"{key(payload)}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def put(payload: dict, result: dict) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    (CACHE_DIR / f"{key(payload)}.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
