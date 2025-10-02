import os

from backend.infrastructure.container import Container
from backend.services.results_service import ResultsService as LegacyResultsService
from backend.services.results.facade import ResultsServiceFacade


class DummyUser:
    def __init__(self, user_id: str = "test_user"):
        self.user_id = user_id


def test_results_service_flag_resolution(monkeypatch):
    # Ensure default: flag OFF → legacy
    monkeypatch.delenv("RESULTS_SERVICE_V2", raising=False)
    c = Container()
    factory = c.get_results_service()
    svc = factory(object(), DummyUser())
    assert isinstance(svc, LegacyResultsService)

    # Flag ON → facade (note: new container to avoid cached factory)
    monkeypatch.setenv("RESULTS_SERVICE_V2", "true")
    c2 = Container()
    factory2 = c2.get_results_service()
    svc2 = factory2(object(), DummyUser())
    assert isinstance(svc2, ResultsServiceFacade)

