"""Results Service Facade (scaffolding).

Preserves existing endpoint behavior by delegating to the legacy
backend.services.results_service.ResultsService while we gradually migrate
logic into repositories/services/presenters in this package.
"""

from __future__ import annotations

from typing import Any, Dict, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
import os

from backend.models import User
from backend.services.results_service import ResultsService as LegacyResultsService
from backend.services.results.query import AnalysisResultQuery
from backend.services.results.presenter import present_formatted_results


class ResultsServiceFacade:
    """Thin wrapper maintaining API compatibility with the legacy ResultsService."""

    def __init__(self, db: Session, user: User):
        self.db = db
        self.user = user

    # Public API kept identical to legacy
    def get_analysis_result(self, result_id: int) -> Dict[str, Any]:
        """Authorize via query layer, then delegate formatting to legacy service."""
        q = AnalysisResultQuery(self.db)
        dto = q.get_owned_result_dto(result_id=result_id, user_id=self.user.user_id)
        if dto is None:
            raise HTTPException(
                status_code=404, detail=f"Results not found for result_id: {result_id}"
            )
        # Optionally use presenter path behind internal flag; fallback to legacy
        use_presenter = os.getenv("RESULTS_SERVICE_V2_PRESENTER", "false").lower() in (
            "1",
            "true",
            "yes",
            "on",
        )
        if use_presenter:
            return present_formatted_results(self.db, dto)
        # Delegate shaping/formatting to legacy to preserve behavior
        return LegacyResultsService(self.db, self.user).get_analysis_result(result_id)

    def get_all_analyses(
        self,
        *,
        sort_by: Optional[str] = None,
        sort_direction: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        return LegacyResultsService(self.db, self.user).get_all_analyses(
            sort_by=sort_by, sort_direction=sort_direction, status=status
        )

    def get_design_thinking_personas(self, result_id: int):
        return LegacyResultsService(self.db, self.user).get_design_thinking_personas(
            result_id
        )
