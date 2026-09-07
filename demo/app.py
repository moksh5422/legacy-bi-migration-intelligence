from __future__ import annotations

import json
from pathlib import Path

from pipeline.etl import build_curated, extract_csv, transform_sales
from pipeline.evaluation import evaluate_migration, ragas_fixture
from pipeline.lineage import build_lineage
from pipeline.planner import plan_reports
from pipeline.review import build_review_queue
from pipeline.security import authorize, detect_pii_fields
from .agents import DiscoveryAgent, MigrationAgent, PIIAgent, PlanningAgent, SecurityPolicy

ROOT = Path(__file__).resolve().parents[1]


def reconcile(source: dict, target: dict) -> list[dict]:
    results = []
    for name in ("row_count", "revenue"):
        left = source[name]
        right = target[name]
        results.append({
            "name": name,
            "source": left,
            "target": right,
            "status": "PASS" if left == right else "REVIEW",
        })
    return results


def main() -> None:
    report = json.loads((ROOT / "examples" / "legacy_report.json").read_text(encoding="utf-8"))
    raw_rows = extract_csv(ROOT / "examples" / "sales.csv")
    curated = build_curated(transform_sales(raw_rows))

    discovery = DiscoveryAgent()
    planner = PlanningAgent()
    migration = MigrationAgent()
    security = SecurityPolicy()
    pii = PIIAgent()

    print("=== 1. DISCOVERY ===")
    inventory = discovery.inventory(report)
    print(json.dumps(inventory, indent=2))

    print("\n=== 2. PLANNING ===")
    plan = planner.plan([report])
    print(json.dumps(plan, indent=2))

    print("\n=== 3. AI-ASSISTED MIGRATION ANALYSIS ===")
    spec = migration.analyze(report)
    print(json.dumps(spec, indent=2))

    print("\n=== 4. SECURITY + PII ===")
    auth = security.authorize("migration-engineer", "sample-data")
    pii_result = pii.scan(report)
    print(json.dumps({"authorization": auth, "pii": pii_result}, indent=2))

    print("\n=== 5. ETL / CURATED DATA ===")
    print(json.dumps({k: v for k, v in curated.items() if k != "rows"}, indent=2))

    print("\n=== 6. LINEAGE ===")
    print(json.dumps(build_lineage(report), indent=2))

    print("\n=== 7. RECONCILIATION ===")
    source = {"row_count": len(raw_rows), "revenue": 1000.0}
    checks = reconcile(source, curated)
    print(json.dumps(checks, indent=2))

    migration_dict = getattr(spec, "__dict__", spec)
    evaluation = evaluate_migration(migration_dict, checks)
    review = build_review_queue(report, migration_dict, {"pii_detected": pii_result.get("pii_detected", False)}, checks)

    print("\n=== 8. EVALUATION ===")
    print(json.dumps({"migration": evaluation, "ragas_fixture": ragas_fixture()}, indent=2))

    print("\n=== 9. FINAL DECISION ===")
    decision = "HUMAN_REVIEW" if review or evaluation["requires_human_review"] else "READY"
    print(json.dumps({"decision": decision, "review_queue": review}, indent=2))


if __name__ == "__main__":
    main()
