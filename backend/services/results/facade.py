"""Results Service Facade (scaffolding).

Preserves existing endpoint behavior by delegating to the legacy
backend.services.results_service.ResultsService while we gradually migrate
logic into repositories/services/presenters in this package.
"""
from __future__ import annotations

from typing import Any, Dict, Optional
from sqlalchemy.orm import Session

from backend.models import User
from backend.services.results_service import ResultsService as LegacyResultsService


class ResultsServiceFacade:
    """Thin wrapper maintaining API compatibility with the legacy ResultsService."""

    def __init__(self, db: Session, user: User):
        self.db = db
        self.user = user

    # Public API kept identical to legacy
    def get_analysis_result(self, result_id: int) -> Dict[str, Any]:
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
        return LegacyResultsService(self.db, self.user).get_design_thinking_personas(result_id)

