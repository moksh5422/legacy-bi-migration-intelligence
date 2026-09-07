from __future__ import annotations


def build_lineage(report: dict) -> list[dict]:
    lineage: list[dict] = []
    for calc in report.get("calculations", []):
        lineage.append({
            "source_expression": calc.get("expression"),
            "metric": calc.get("name"),
            "target_layer": calc.get("target_layer", "semantic_model"),
        })
    for item in report.get("transformations", []):
        lineage.append({
            "source_expression": item.get("logic"),
            "metric": item.get("name"),
            "target_layer": "fabric_transformation",
        })
    return lineage
