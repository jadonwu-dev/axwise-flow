"""Domain services for Results (scaffolding).

These services will compose repositories and presentation adapters to provide
use-case oriented APIs. During scaffolding, legacy behavior is preserved via
ResultsServiceFacade delegating to backend.services.results_service.ResultsService.
"""
from __future__ import annotations

from typing import Any, Dict, Optional


class ResultsQueryService:
    """Query services for results domain (to be implemented in Phase 2)."""

    def __init__(self, *, repos: Any):  # noqa: ANN401
        self.repos = repos

    # Example method signatures to be fleshed out during migration
    async def get_analysis_result(self, result_id: int, *, user_id: str) -> Dict[str, Any]:
        raise NotImplementedError

    async def list_analyses(
        self,
        *,
        user_id: str,
        sort_by: str = "createdAt",
        sort_direction: str = "desc",
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        raise NotImplementedError

