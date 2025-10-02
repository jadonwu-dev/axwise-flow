from __future__ import annotations

from typing import Any

from backend.services.results.dto import AnalysisResultRow


def to_analysis_result_row(row: Any) -> AnalysisResultRow:
    """Map an ORM-like row to AnalysisResultRow DTO.

    Accepts any object that exposes attributes used below. This keeps mapper
    independent of the ORM and easy to unit-test with fakes.
    """
    return AnalysisResultRow(
        result_id=getattr(row, "result_id", None),
        data_id=getattr(row, "data_id", None),
        analysis_date=getattr(row, "analysis_date", None),
        status=getattr(row, "status", None),
        llm_provider=getattr(row, "llm_provider", None),
        llm_model=getattr(row, "llm_model", None),
        results=getattr(row, "results", None),
        stakeholder_intelligence=getattr(row, "stakeholder_intelligence", None),
    )
