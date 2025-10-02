from backend.services.results.formatters import create_ui_safe_stakeholder_intelligence


def test_ui_safe_from_detected_list():
    src = {"detected_stakeholders": [{"stakeholder_id": "a"}, {"stakeholder_id": "b"}]}
    ui = create_ui_safe_stakeholder_intelligence(src)
    assert ui["total_stakeholders"] == 2
    assert isinstance(ui["processing_metadata"], dict) and ui["processing_metadata"]["ui_safe"] is True


def test_ui_safe_from_stakeholders_dict():
    src = {"stakeholders": {"x": {"stakeholder_type": "influencer"}}}
    ui = create_ui_safe_stakeholder_intelligence(src)
    assert ui["total_stakeholders"] == 1
    assert ui["detected_stakeholders"][0]["stakeholder_id"] == "x"


def test_ui_safe_fallback_non_dict():
    ui = create_ui_safe_stakeholder_intelligence("oops")
    assert ui["total_stakeholders"] == 0
    assert ui["processing_metadata"]["ui_safe"] is True

