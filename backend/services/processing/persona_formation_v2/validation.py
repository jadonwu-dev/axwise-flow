"""
Validation utilities for Persona Formation V2.

Ensures adherence to the Golden Schema:
- AttributedField with value/evidence arrays
- StructuredDemographics without top-level value/evidence
- Presence of the 5 required UI fields
"""
from typing import Dict, Any


class PersonaValidation:
    REQUIRED_FIELDS = [
        "name",
        "demographics",
        "goals_and_motivations",
        "challenges_and_frustrations",
        "key_quotes",
    ]

    def ensure_golden_schema(self, persona: Dict[str, Any]) -> Dict[str, Any]:
        p = dict(persona or {})

        # Ensure required fields exist
        for f in self.REQUIRED_FIELDS:
            if f not in p:
                if f == "name":
                    p[f] = "Participant"
                else:
                    p[f] = {"value": "", "confidence": 0.7, "evidence": []}

        # Enforce AttributedField shape on traits (value/evidence keys)
        for trait in [
            "goals_and_motivations",
            "challenges_and_frustrations",
            "key_quotes",
        ]:
            v = p.get(trait)
            if isinstance(v, str):
                p[trait] = {"value": v, "confidence": 0.7, "evidence": []}
            elif isinstance(v, dict):
                v.setdefault("value", "")
                v.setdefault("confidence", 0.7)
                v.setdefault("evidence", [])

        # Enforce StructuredDemographics (no top-level value/evidence)
        demo = p.get("demographics")
        if isinstance(demo, dict) and "value" in demo:
            # Convert simple PersonaTrait demographics into structured container
            # Keep original evidence as best effort under professional_context
            p["demographics"] = {
                "experience_level": {"value": "", "evidence": []},
                "industry": {"value": "", "evidence": []},
                "location": {"value": "", "evidence": []},
                "professional_context": {
                    "value": demo.get("value", ""),
                    "evidence": demo.get("evidence", []),
                },
                "roles": {"value": "", "evidence": []},
                "age_range": {"value": "", "evidence": []},
                "confidence": float(demo.get("confidence", 0.7) or 0.7),
            }
        elif isinstance(demo, dict) and "confidence" not in demo:
            # Add a confidence for structured demographics
            demo["confidence"] = 0.7

        return p

