from __future__ import annotations

TOOLS = {
    "list_report_dependencies",
    "get_transformation",
    "get_sample_data",
    "validate_report",
    "submit_for_review",
}

ROLE_TOOLS = {
    "migration-engineer": TOOLS,
    "reviewer": {"list_report_dependencies", "validate_report", "submit_for_review"},
    "viewer": {"list_report_dependencies"},
}


def invoke(tool: str, role: str, payload: dict | None = None) -> dict:
    allowed = tool in ROLE_TOOLS.get(role, set())
    return {"tool": tool, "role": role, "allowed": allowed, "payload": payload or {}}
