from backend.services.results.formatters import assemble_flattened_results


def test_assemble_flattened_results_defaults():
    results_dict = {}
    personas = []
    default = {"positive": 0.33, "neutral": 0.34, "negative": 0.33}

    out = assemble_flattened_results(results_dict, personas, sentiment_overview_default=default)
    assert out["themes"] == []
    assert out["enhanced_themes"] == []
    assert out["patterns"] == []
    assert out["sentiment"] == []
    assert out["sentimentOverview"] == default
    assert out["sentimentStatements"] == {"positive": [], "neutral": [], "negative": []}
    assert out["insights"] == []
    assert out["personas"] == []


def test_assemble_flattened_results_with_values():
    results_dict = {
        "themes": [1],
        "enhanced_themes": [2],
        "patterns": [3],
        "sentiment": [4],
        "sentimentOverview": {"p": 1},
        "sentimentStatements": {"positive": ["x"], "neutral": [], "negative": []},
        "insights": [5],
    }
    out = assemble_flattened_results(results_dict, ["p1"], sentiment_overview_default={})
    assert out["themes"] == [1]
    assert out["enhanced_themes"] == [2]
    assert out["patterns"] == [3]
    assert out["sentiment"] == [4]
    assert out["sentimentOverview"] == {"p": 1}
    assert out["sentimentStatements"]["positive"] == ["x"]
    assert out["insights"] == [5]
    assert out["personas"] == ["p1"]

