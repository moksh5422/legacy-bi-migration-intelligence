from __future__ import annotations

import json
from pathlib import Path

from pipeline.etl import build_curated, extract_csv, transform_sales
from pipeline.evaluation import evaluate_migration, ragas_fixture
from pipeline.lineage import build_lineage
from pipeline.planner import plan_reports
from pipeline.review import build_review_queue
from pipeline.security import authorize, detect_pii_fields

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    report = json.loads((ROOT / "examples" / "legacy_report.json").read_text(encoding="utf-8"))
    rows = extract_csv(ROOT / "examples" / "sales.csv")
    curated = build_curated(transform_sales(rows))

    inventory = report.copy()
    inventory["row_count"] = curated["row_count"]
    inventory["revenue"] = curated["revenue"]

    plan = plan_reports([report])
    pii_fields = detect_pii_fields(["customer_id", "Region", "SalesAmount"])
    security = {"authorized": authorize("migration-engineer", "sample-data"), "pii_detected": bool(pii_fields), "pii_fields": pii_fields}

    migration_spec = {
        "report_id": report["report_id"],
        "calculations": report.get("calculations", []),
        "transformations": report.get("transformations", []),
        "confidence": 0.91,
    }

    validation = [
        {"name": "row_count", "source": 5, "target": curated["row_count"], "status": "PASS" if curated["row_count"] == 5 else "REVIEW"},
        {"name": "revenue", "source": 1000.0, "target": curated["revenue"], "status": "PASS" if curated["revenue"] == 1000.0 else "REVIEW"},
    ]

    review_queue = build_review_queue(report, migration_spec, security, validation)
    evaluation = evaluate_migration(migration_spec, validation)

    output = {
        "inventory": inventory,
        "plan": plan,
        "security": security,
        "lineage": build_lineage(report),
        "curated": {k: v for k, v in curated.items() if k != "rows"},
        "evaluation": evaluation,
        "ragas_fixture": ragas_fixture(),
        "review_queue": review_queue,
        "decision": "HUMAN_REVIEW" if review_queue or evaluation["requires_human_review"] else "READY",
    }
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
