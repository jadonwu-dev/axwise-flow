from backend.services.results.formatters import should_compute_influence_metrics


def test_should_compute_influence_metrics_when_missing():
    assert should_compute_influence_metrics({}) is True


def test_should_compute_influence_metrics_when_all_default():
    si = {"influence_metrics": {"decision_power": 0.5, "technical_influence": 0.5, "budget_influence": 0.5}}
    assert should_compute_influence_metrics(si) is True


def test_should_compute_influence_metrics_when_present_and_non_default():
    si = {"influence_metrics": {"decision_power": 0.7, "technical_influence": 0.9, "budget_influence": 0.6}}
    assert should_compute_influence_metrics(si) is False

