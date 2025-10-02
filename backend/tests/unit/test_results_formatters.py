import pytest

from backend.services.results.formatters import compute_influence_metrics_for_persona


def test_influence_metrics_defaults_for_unknown_persona():
    out = compute_influence_metrics_for_persona({})
    assert set(out.keys()) == {"decision_power", "technical_influence", "budget_influence"}
    for v in out.values():
        assert 0.0 <= v <= 1.0


def test_influence_metrics_detects_keywords():
    persona = {
        "name": "CTO",
        "description": "technical leader and decision maker",
        "archetype": "architect",
        "demographics": {"value": "senior executive"},
    }
    out = compute_influence_metrics_for_persona(persona)
    assert out["technical_influence"] >= 0.85
    assert out["decision_power"] >= 0.6
    # budget may be boosted if finance markers present; here it's default-ish but clamped
    assert 0.0 <= out["budget_influence"] <= 1.0

