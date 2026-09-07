from __future__ import annotations

import re

PII_PATTERNS = re.compile(r"email|phone|mobile|address|ssn|account|customer_id", re.I)
ROLE_SCOPES = {
    "migration-engineer": {"metadata", "sample-data", "validation"},
    "reviewer": {"metadata", "validation"},
    "viewer": {"metadata"},
}


def authorize(role: str, scope: str) -> bool:
    return scope in ROLE_SCOPES.get(role, set())


def detect_pii_fields(fields: list[str]) -> list[str]:
    return [field for field in fields if PII_PATTERNS.search(field)]
