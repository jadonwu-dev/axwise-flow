"""Repositories for Results domain (scaffolding).

These repositories provide DB access abstractions for analysis results,
personas, and sessions. During the scaffolding phase, the facade delegates
behavior to the legacy ResultsService; these classes exist to seed the
modular structure and will be wired in Phase 2.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session


class AnalysisResultRepository:
    def __init__(self, db: Session):
        self.db = db

    # Placeholder APIs to be implemented in Phase 2
    def get_by_id(self, result_id: int, user_id: str) -> Optional[Any]:  # noqa: ANN401
        """Return AnalysisResult row for the given id if owned by the user."""
        raise NotImplementedError

    def list_for_user(
        self,
        user_id: str,
        *,
        sort_by: str = "createdAt",
        sort_direction: str = "desc",
        status: Optional[str] = None,
    ) -> List[Any]:  # noqa: ANN401
        """List analysis results for a user with optional sorting/filtering."""
        raise NotImplementedError


class PersonaRepository:
    def __init__(self, db: Session):
        self.db = db

    # Add persona-specific queries as migration progresses


class SessionRepository:
    def __init__(self, db: Session):
        self.db = db

    # Add research session queries as migration progresses

