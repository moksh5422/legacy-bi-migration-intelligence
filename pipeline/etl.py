from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


def extract_csv(path: str | Path) -> list[dict[str, Any]]:
    with Path(path).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def transform_sales(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    cleaned = []
    for row in rows:
        region = str(row.get("Region", "")).strip().upper()
        amount = float(row.get("SalesAmount", 0) or 0)
        customer_type = str(row.get("CustomerType", "")).strip()
        segment = "Large" if customer_type.lower() == "enterprise" else "Standard"
        cleaned.append({**row, "Region": region, "SalesAmount": amount, "CustomerSegment": segment})
    return cleaned


def build_curated(rows: list[dict[str, Any]]) -> dict[str, Any]:
    revenue = round(sum(float(r["SalesAmount"]) for r in rows), 2)
    regions = sorted({r["Region"] for r in rows})
    return {"row_count": len(rows), "revenue": revenue, "regions": regions, "rows": rows}
