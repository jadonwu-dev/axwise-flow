"""
Extractor modules for Persona Formation V2.

Each extractor can operate over pre-computed attributes to avoid duplicate
LLM calls. They return AttributedField-like dicts with value/evidence.
"""
from typing import Dict, Any


class BaseExtractor:
    target_field: str

    def from_attributes(self, attributes: Dict[str, Any]) -> Dict[str, Any]:
        data = attributes.get(self.target_field, {}) or {}
        if isinstance(data, str):
            return {"value": data, "confidence": 0.7, "evidence": []}
        if isinstance(data, dict):
            # Ensure required keys exist
            return {
                "value": data.get("value", ""),
                "confidence": float(data.get("confidence", 0.7) or 0.7),
                "evidence": list(data.get("evidence", []) or []),
            }
        return {"value": "", "confidence": 0.5, "evidence": []}


class DemographicsExtractor(BaseExtractor):
    target_field = "demographics"


class GoalsExtractor(BaseExtractor):
    target_field = "goals_and_motivations"


class ChallengesExtractor(BaseExtractor):
    target_field = "challenges_and_frustrations"


class KeyQuotesExtractor(BaseExtractor):
    target_field = "key_quotes"

