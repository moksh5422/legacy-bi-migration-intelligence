from __future__ import annotations

from statistics import mean


def evaluate_migration(spec: dict, validation: list[dict]) -> dict:
    passed = [x["status"] == "PASS" for x in validation]
    return {
        "confidence": spec.get("confidence", 0.0),
        "validation_pass_rate": mean(passed) if passed else 0.0,
        "requires_human_review": spec.get("confidence", 0.0) < 0.80 or not all(passed),
    }


def ragas_fixture() -> dict:
    return {
        "context_recall": 0.91,
        "answer_relevance": 0.94,
        "faithfulness": 0.92,
        "note": "Synthetic fixture demonstrating the evaluation contract; replace with a real RAGAS run in a secured environment."
    }
