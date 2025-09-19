"""Presenters/serializers for Results domain (scaffolding).

Translate domain objects into API response shapes. During scaffolding, we keep
legacy shapes and delegate through the facade to avoid breaking changes.
"""
from __future__ import annotations

from typing import Any, Dict, List


class ResultsPresenter:
    @staticmethod
    def to_api_result(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Pass-through in scaffolding; reserved for future shaping logic."""
        return payload

    @staticmethod
    def to_api_list(payload: Dict[str, Any]) -> Dict[str, Any]:
        return payload

