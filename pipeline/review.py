from __future__ import annotations


def build_review_queue(report: dict, migration_spec: dict, security: dict, validation: list[dict]) -> list[dict]:
    items: list[dict] = []
    if migration_spec.get("confidence", 0) < 0.80:
        items.append({"type": "mapping", "report_id": report["report_id"], "reason": "confidence below threshold"})
    if security.get("pii_detected"):
        items.append({"type": "security", "report_id": report["report_id"], "reason": "PII detected"})
    for check in validation:
        if check["status"] != "PASS":
            items.append({"type": "validation", "report_id": report["report_id"], "reason": check["name"] + " mismatch"})
    return items
