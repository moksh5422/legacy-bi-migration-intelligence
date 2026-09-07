from pipeline.etl import build_curated, transform_sales
from pipeline.security import authorize, detect_pii_fields
from pipeline.evaluation import evaluate_migration


def test_transform_and_curate():
    rows = transform_sales([{"Region": " emea ", "CustomerType": "Enterprise", "SalesAmount": "200"}])
    result = build_curated(rows)
    assert result["row_count"] == 1
    assert result["revenue"] == 200.0
    assert rows[0]["Region"] == "EMEA"
    assert rows[0]["CustomerSegment"] == "Large"


def test_rbac():
    assert authorize("migration-engineer", "sample-data") is True
    assert authorize("viewer", "sample-data") is False


def test_pii_detection():
    assert "customer_id" in detect_pii_fields(["customer_id", "Region"])


def test_evaluation_requires_review_on_failed_validation():
    result = evaluate_migration({"confidence": 0.95}, [{"status": "REVIEW"}])
    assert result["requires_human_review"] is True
