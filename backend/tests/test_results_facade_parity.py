import os

import pytest

from backend.infrastructure.container import Container


class DummyUser:
    def __init__(self, user_id: str = "u1"):
        self.user_id = user_id


@pytest.fixture
def container():
    return Container()


@pytest.fixture
def dummy_db():
    return object()


@pytest.fixture
def sample_payload():
    return {"status": "completed", "result_id": 123, "results": {"personas": []}}


def _patch_legacy_and_repo(monkeypatch, sample_payload):
    # Patch legacy ResultsService.get_analysis_result to return a fixed payload
    import backend.services.results_service as legacy_mod

    def _fake_get(self, result_id: int):
        return sample_payload

    monkeypatch.setattr(
        legacy_mod.ResultsService, "get_analysis_result", _fake_get, raising=True
    )

    # Patch repository get_by_id to return a non-None row so facade auth passes
    import backend.services.results.repositories as repos_mod

    def _fake_get_by_id(self, result_id: int, user_id: str):
        return object()

    monkeypatch.setattr(
        repos_mod.AnalysisResultRepository, "get_by_id", _fake_get_by_id, raising=True
    )


def test_parity_off_vs_on(monkeypatch, container, dummy_db, sample_payload):
    _patch_legacy_and_repo(monkeypatch, sample_payload)

    # OFF → legacy
    monkeypatch.setenv("RESULTS_SERVICE_V2", "false")
    c1 = Container()  # new container per flag state
    f1 = c1.get_results_service()
    svc_off = f1(dummy_db, DummyUser())
    out_off = svc_off.get_analysis_result(123)

    # ON → facade (delegates to legacy, but authorizes via repo)
    monkeypatch.setenv("RESULTS_SERVICE_V2", "true")
    c2 = Container()
    f2 = c2.get_results_service()
    svc_on = f2(dummy_db, DummyUser())
    out_on = svc_on.get_analysis_result(123)

    assert out_off == out_on == sample_payload

