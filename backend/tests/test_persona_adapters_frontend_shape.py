"""
Snapshot-ish tests for from_ssot_to_frontend to ensure legacy-safe shape.
"""
from __future__ import annotations

from backend.services.adapters.persona_adapters import from_ssot_to_frontend


def test_from_ssot_to_frontend_shape():
    ssot = {
        "name": "Ops Manager",
        "description": "",
        "archetype": "",
        "demographics": {
            "experience_level": {"value": "10+ years", "evidence": [{"quote": "I've been here 12 years"}]},
            "industry": {"value": "Manufacturing", "evidence": []},
            "confidence": 0.75,
        },
        "goals_and_motivations": {"value": "Reduce downtime", "evidence": [{"quote": "downtime kills us"}]},
        "challenges_and_frustrations": {"value": "Legacy systems", "evidence": [{"quote": "old systems"}]},
        "key_quotes": {"value": "We need visibility", "evidence": [{"quote": "need visibility"}]},
    }
    fe = from_ssot_to_frontend(ssot)
    assert fe["name"] == "Ops Manager"
    assert isinstance(fe["demographics"], dict)
    assert isinstance(fe["goals_and_motivations"], dict)
    assert isinstance(fe["challenges_and_frustrations"], dict)
    assert isinstance(fe["key_quotes"], dict)

