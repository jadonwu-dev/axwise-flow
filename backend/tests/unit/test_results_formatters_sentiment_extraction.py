import pytest

from backend.services.results.formatters import extract_sentiment_statements_from_data


def test_extract_sentiment_statements_splits_by_scores_and_limits():
    themes = [
        {"sentiment": 0.3, "statements": ["A" * 25]},
        {"sentiment": -0.4, "statements": ["B" * 30]},
        {"sentiment": 0.0, "statements": ["short"],},  # ignored (too short)
    ]
    patterns = [
        {"evidence": ["C" * 40], "impact": "This improves workflows"},  # positive
        {"evidence": ["D" * 40], "impact": "Major frustration with tool"},  # negative
    ]

    out = extract_sentiment_statements_from_data(themes, patterns)

    assert set(out.keys()) == {"positive", "neutral", "negative"}
    # positives should contain theme[0] + pattern[0]
    assert any(len(s) >= 20 for s in out["positive"]) and "A" * 25 in out["positive"]
    assert "C" * 40 in out["positive"]
    # negatives should contain theme[1] + pattern[1]
    assert "B" * 30 in out["negative"]
    assert "D" * 40 in out["negative"]
    # neutral exists but likely empty here
    assert isinstance(out["neutral"], list)


def test_extract_sentiment_statements_deduplicates_and_caps():
    long_stmt = "E" * 50
    themes = [{"sentiment": 0.5, "statements": [long_stmt, long_stmt]}]
    out = extract_sentiment_statements_from_data(themes, [])
    assert out["positive"].count(long_stmt) == 1
    # Cap to 20
    bulk = [{"sentiment": 0.6, "statements": [str(i) * 25]} for i in range(30)]
    out2 = extract_sentiment_statements_from_data(bulk, [])
    assert len(out2["positive"]) <= 20

