from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from backend.services.results.dto import AnalysisResultRow
from backend.services.results.mappers import to_analysis_result_row
from backend.services.results.repositories import AnalysisResultRepository


class AnalysisResultQuery:
    """Read-only query layer for Results domain.

    Uses repositories for authorization-aware DB access and returns DTOs.
    """

    def __init__(self, db: Session):
        self.db = db
        self.repo = AnalysisResultRepository(db)

    def get_owned_result_dto(self, *, result_id: int, user_id: str) -> Optional[AnalysisResultRow]:
        row = self.repo.get_by_id(result_id, user_id)
        if row is None:
            return None
        return to_analysis_result_row(row)

