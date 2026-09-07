import json
from pathlib import Path

from .agents import DiscoveryAgent, MigrationAgent, PlanningAgent, SecurityPolicy, EvaluationAgent

ROOT = Path(__file__).resolve().parent


def reconcile(source: dict, target: dict) -> list[dict]:
    checks = []
    for key in ("row_count", "revenue"):
        source_value = source.get(key)
        target_value = target.get(key)
        checks.append(
            {
                "name": key,
                "source": source_value,
                "target": target_value,
                "status": "PASS" if source_value == target_value else "REVIEW",
            }
        )
    return checks


def main() -> None:
    report = json.loads((ROOT / "sample_report.json").read_text(encoding="utf-8"))

    discovery = DiscoveryAgent()
    planner = PlanningAgent()
    migration = MigrationAgent()
    security = SecurityPolicy()
    evaluation = EvaluationAgent()

    print("=== 1. DISCOVERY AGENT ===")
    inventory = discovery.inventory(report)
    print(json.dumps(inventory, indent=2))

    print("\n=== 2. PLANNING AGENT ===")
    plan = planner.plan([report])
    print(json.dumps(plan, indent=2))

    print("\n=== 3. MIGRATION ANALYSIS AGENT ===")
    spec = migration.analyze(report)
    print(json.dumps(spec, indent=2))

    print("\n=== 4. SECURITY / RBAC ===")
    print(json.dumps(security.authorize("migration-engineer", "sample-data"), indent=2))
    print(json.dumps(security.authorize("viewer", "sample-data"), indent=2))

    print("\n=== 5. EVALUATION ===")
    evaluation_result = evaluation.review(spec)
    print(json.dumps(evaluation_result, indent=2))

    print("\n=== 6. DETERMINISTIC RECONCILIATION ===")
    checks = reconcile(
        {"row_count": 100000, "revenue": 1250000},
        {"row_count": 100000, "revenue": 1249997},
    )
    print(json.dumps(checks, indent=2))

    needs_review = evaluation_result["requires_human_review"] or any(
        c["status"] == "REVIEW" for c in checks
    )
    print("\n=== DECISION ===")
    print("HUMAN REVIEW REQUIRED" if needs_review else "READY FOR MIGRATION")


if __name__ == "__main__":
    main()
