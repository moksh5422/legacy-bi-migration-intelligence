from __future__ import annotations


def score_report(report: dict) -> dict:
    score = (
        len(report.get("calculations", []))
        + 2 * len(report.get("transformations", []))
        + len(report.get("filters", []))
        + len(report.get("data_sources", []))
    )
    risk = "LOW" if score <= 3 else "MEDIUM" if score <= 7 else "HIGH"
    priority = 1 if risk == "LOW" else 2 if risk == "MEDIUM" else 3
    return {"report_id": report.get("report_id"), "complexity_score": score, "risk": risk, "priority": priority}


def plan_reports(reports: list[dict]) -> list[dict]:
    return sorted((score_report(r) for r in reports), key=lambda x: (x["priority"], x["complexity_score"]))
