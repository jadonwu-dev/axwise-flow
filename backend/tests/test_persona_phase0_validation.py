"""
Unit tests for Phase 0 persona evidence validation system.
- AttributedField coercion to EvidenceItem
- Validator matching on simple transcript and text
- Snapshot shape for SSoT persona conversion
"""
from __future__ import annotations

from typing import Dict, Any, List

from backend.domain.models.persona_schema import AttributedField, EvidenceItem
from backend.services.adapters.persona_adapters import to_ssot_persona, from_ssot_to_frontend
from backend.services.validation.persona_evidence_validator import PersonaEvidenceValidator


def test_attributed_field_evidence_coercion_strings():
    af = AttributedField(value="Test", evidence=["Quote A", "Quote B"])
    assert isinstance(af.evidence, list)
    assert len(af.evidence) == 2
    assert isinstance(af.evidence[0], EvidenceItem)
    assert af.evidence[0].quote == "Quote A"


def test_attributed_field_evidence_coercion_dicts():
    af = AttributedField(value="Test", evidence=[{"text": "Hello"}, {"quote": "World"}])
    assert isinstance(af.evidence[0], EvidenceItem)
    assert af.evidence[0].quote == "Hello"
    assert af.evidence[1].quote == "World"


def test_validator_match_transcript():
    persona = {
        "name": "Tester",
        "description": "",
        "archetype": "",
        "demographics": {"confidence": 0.7},
        "goals_and_motivations": {
            "value": "Goal",
            "evidence": [{"quote": "I really like coffee"}],
        },
        "challenges_and_frustrations": {"value": "Challenge", "evidence": []},
        "key_quotes": {"value": "Quote", "evidence": []},
    }
    transcript = [
        {"speaker": "A", "dialogue": "Hello there"},
        {"speaker": "User", "dialogue": "I really like coffee and tea"},
    ]

    validator = PersonaEvidenceValidator()
    matches = validator.match_evidence(persona, transcript=transcript)
    assert matches and matches[0].match_type in ("verbatim", "normalized")


def test_to_ssot_persona_snapshot_minimal():
    legacy = {
        "name": "Analyst",
        "description": "Data person",
        "demographics": {
            "professional_context": {"value": "Works in finance", "evidence": ["Finance department"]},
            "confidence": 0.8,
        },
        "goals_and_motivations": {"value": "Improve reporting", "evidence": ["faster reports"]},
        "challenges": {"value": "Manual work", "evidence": ["too many spreadsheets"]},
        "quotes": {"value": "We need automation", "evidence": ["we need automation"]},
    }
    ssot = to_ssot_persona(legacy)
    assert ssot["name"] == "Analyst"
    assert ssot["demographics"]["confidence"] == 0.8
    # Evidence should be list of dicts with quote
    assert ssot["goals_and_motivations"]["evidence"][0]["quote"]

    # Backward to frontend shape
    fe = from_ssot_to_frontend(ssot)
    assert isinstance(fe.get("demographics"), dict)
    assert isinstance(fe.get("goals_and_motivations"), dict)

