from backend.services.results.formatters import derive_detected_stakeholders_from_personas


def test_derive_detected_stakeholders_basic():
    personas = [
        {
            "name": "Alice",
            "stakeholder_intelligence": {"stakeholder_type": "Decision Maker"},
            "demographics": {"value": "Senior leader in finance"},
            "overall_confidence": 0.9,
        },
        {
            "name": "Bob",
            "archetype": "Influencer",
            "demographics": {"value": "Product strategist"},
            "overall_confidence": 0.8,
        },
    ]

    out = derive_detected_stakeholders_from_personas(personas)
    assert isinstance(out, list) and len(out) == 2

    # First derived entry should reflect decision_maker
    d0 = out[0]
    assert d0["stakeholder_type"] == "decision_maker"
    assert d0["stakeholder_id"] == "decision_maker"
    assert d0["demographic_profile"]["summary"].startswith("Senior leader")

    # Second derived entry should reflect influencer
    d1 = out[1]
    assert d1["stakeholder_type"] == "influencer"
    assert d1["stakeholder_id"] == "influencer"  # from archetype fallback

