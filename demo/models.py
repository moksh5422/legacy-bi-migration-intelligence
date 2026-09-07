from dataclasses import dataclass, field
from typing import Any


@dataclass
class MigrationSpec:
    report_id: str
    source_system: str
    sources: list[str]
    calculations: list[dict[str, Any]]
    transformations: list[dict[str, Any]]
    filters: list[dict[str, Any]]
    review_items: list[str] = field(default_factory=list)
    confidence: float = 0.0
