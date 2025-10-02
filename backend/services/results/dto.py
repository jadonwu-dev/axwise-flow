from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


@dataclass(frozen=True)
class AnalysisResultRow:
    """Minimal DTO for an analysis result row needed for read paths.

    This does not shape API responses; it is an internal transport object.
    """

    result_id: int
    data_id: Optional[int]
    analysis_date: Optional[str]
    status: Optional[str]
    llm_provider: Optional[str]
    llm_model: Optional[str]
    results: Optional[Any]
    stakeholder_intelligence: Optional[Any]
