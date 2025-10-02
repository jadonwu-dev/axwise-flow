from backend.services.results.formatters import build_source_payload


def test_build_source_payload_transcript():
    rd = {"transcript": [{"speaker": "A"}, {"speaker": "B"}]}
    out = build_source_payload(rd, data_id=7)
    assert "transcript" in out and "original_text" not in out and "dataId" not in out


def test_build_source_payload_original_text():
    rd = {"original_text": " hello "}
    out = build_source_payload(rd, data_id=7)
    assert out == {"original_text": " hello "}


def test_build_source_payload_fallback_data_id():
    rd = {}
    out = build_source_payload(rd, data_id=99)
    assert out == {"dataId": 99}

