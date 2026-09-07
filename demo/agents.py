import json
import os
from typing import Any

from .models import MigrationSpec


class DiscoveryAgent:
    """Build a compact inventory from a report definition."""

    def inventory(self, report: dict[str, Any]) -> dict[str, Any]:
        return {
            "report_id": report["report_id"],
            "source_system": report.get("source_system", "legacy-bi"),
            "data_sources": report.get("data_sources", []),
            "calculation_count": len(report.get("calculations", [])),
            "transformation_count": len(report.get("transformations", [])),
            "filter_count": len(report.get("filters", [])),
        }


class PlanningAgent:
    """Create a simple migration plan from report inventory."""

    def plan(self, reports: list[dict[str, Any]]) -> dict[str, Any]:
        planned = []
        for report in reports:
            complexity = (
                len(report.get("data_sources", []))
                + len(report.get("calculations", []))
                + len(report.get("transformations", []))
            )
            planned.append(
                {
                    "report_id": report["report_id"],
                    "complexity_score": complexity,
                    "priority": "high" if complexity >= 4 else "normal",
                }
            )
        return {"reports": planned}


class MigrationAgent:
    """Interpret a legacy BI report and propose a target implementation."""

    def __init__(self) -> None:
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")

    @property
    def llm_enabled(self) -> bool:
        return bool(self.endpoint and self.api_key and self.deployment)

    def analyze(self, report: dict[str, Any]) -> dict[str, Any]:
        if self.llm_enabled:
            return self._analyze_with_azure_openai(report)
        return self._analyze_with_rules(report)

    def _analyze_with_rules(self, report: dict[str, Any]) -> dict[str, Any]:
        calculations = []
        review_items = []

        for item in report.get("calculations", []):
            expr = item.get("expression", "")
            if "SUM(" in expr.upper():
                target_layer = "semantic_model"
                confidence = 0.95
            else:
                target_layer = "fabric_transformation"
                confidence = 0.72

            calculations.append(
                {
                    **item,
                    "target_layer": target_layer,
                    "confidence": confidence,
                }
            )

            if confidence < 0.80:
                review_items.append(item.get("name", "unnamed"))

        confidence = min([x["confidence"] for x in calculations] or [0.0])
        return {
            "report_id": report["report_id"],
            "source_system": report.get("source_system", "legacy-bi"),
            "sources": report.get("data_sources", []),
            "calculations": calculations,
            "transformations": report.get("transformations", []),
            "filters": report.get("filters", []),
            "review_items": review_items,
            "confidence": confidence,
        }

    def _analyze_with_azure_openai(self, report: dict[str, Any]) -> dict[str, Any]:
        try:
            from openai import AzureOpenAI
        except ImportError as exc:
            raise RuntimeError("Install requirements.txt to enable Azure OpenAI mode") from exc

        client = AzureOpenAI(
            azure_endpoint=self.endpoint,
            api_key=self.api_key,
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21"),
        )

        system = (
            "You are a legacy BI migration analysis agent. Return JSON only. "
            "For each calculation, recommend either semantic_model or "
            "fabric_transformation. Include confidence from 0 to 1 and flag "
            "ambiguous mappings for human review. Never claim an uncertain "
            "mapping is correct. Preserve the input report_id, sources, "
            "transformations and filters."
        )

        response = client.chat.completions.create(
            model=self.deployment,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": json.dumps(report)},
            ],
        )
        return json.loads(response.choices[0].message.content)


class SecurityPolicy:
    """Check access before data or tools are exposed to an AI workflow."""

    def authorize(self, role: str, requested_scope: str) -> dict[str, Any]:
        allowed = {
            "migration-engineer": {"report-metadata", "sample-data"},
            "reviewer": {"report-metadata", "validation"},
            "viewer": {"report-metadata"},
        }
        permitted = requested_scope in allowed.get(role, set())
        return {
            "role": role,
            "requested_scope": requested_scope,
            "allowed": permitted,
            "decision": "ALLOW" if permitted else "DENY",
        }


class EvaluationAgent:
    """Route uncertain AI outputs to a human instead of silently accepting them."""

    def review(self, spec: dict[str, Any]) -> dict[str, Any]:
        confidence = float(spec.get("confidence", 0.0))
        review_items = spec.get("review_items", [])
        requires_review = bool(review_items) or confidence < 0.80
        return {
            "checks": [
                {"name": "confidence_floor", "passed": confidence >= 0.80},
                {"name": "review_items_visible", "passed": True},
            ],
            "requires_human_review": requires_review,
        }


class SimilarityAgent:
    """Find simple reuse opportunities among report calculations."""

    def find_reuse_candidates(self, reports: list[dict[str, Any]]) -> list[dict[str, Any]]:
        groups: dict[str, list[str]] = {}
        for report in reports:
            for calculation in report.get("calculations", []):
                expression = calculation.get("expression", "").strip().lower()
                if expression:
                    groups.setdefault(expression, []).append(report["report_id"])

        return [
            {"expression": expression, "reports": report_ids}
            for expression, report_ids in groups.items()
            if len(report_ids) > 1
        ]
