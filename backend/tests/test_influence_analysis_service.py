import asyncio
import pytest

from backend.services.stakeholder.analysis.influence_analysis_service import InfluenceAnalysisService
from backend.services.stakeholder_analysis_service import StakeholderAnalysisService


class DummyAgent:
    def __init__(self, result):
        self._result = result
        self.called = False

    async def run(self, context):
        self.called = True
        return self._result


class DummyFactory:
    def __init__(self, agent: DummyAgent):
        self._agent = agent

    def get_influence_agent(self):
        return self._agent


@pytest.mark.asyncio
async def test_influence_analysis_service_invokes_agent():
    agent = DummyAgent([{"source": "A", "target": "B"}])
    factory = DummyFactory(agent)
    service = InfluenceAnalysisService(factory)

    res = await service.analyze({"any": "context"})

    assert res == [{"source": "A", "target": "B"}]
    assert agent.called is True


@pytest.mark.asyncio
async def test_stakeholder_analysis_influence_flag_fallback(monkeypatch):
    # Ensure influence service path is enabled; we will force it to raise to trigger fallback
    monkeypatch.setenv("USE_INFLUENCE_SERVICE", "true")
    # Keep consensus/ conflict off to reduce unrelated behavior for this unit path
    monkeypatch.setenv("USE_CONSENSUS_SERVICE", "false")
    monkeypatch.setenv("USE_CONFLICT_SERVICE", "false")

    svc = StakeholderAnalysisService(llm_service=None)

    # Prepare inline agents and ensure the service branch is entered
    svc.pydantic_ai_available = True
    dummy_influence_agent = DummyAgent([])
    svc.influence_agent = dummy_influence_agent
    svc.consensus_agent = DummyAgent([])
    svc.conflict_agent = DummyAgent([])
    # Make agent_factory attribute exist so the service branch condition is satisfied
    svc.agent_factory = object()

    class RaisingInfluenceService:
        def __init__(self, *args, **kwargs):
            raise RuntimeError("boom")

        async def analyze(self, *args, **kwargs):  # pragma: no cover
            return []

    # Patch the import target used in StakeholderAnalysisService
    import backend.services.stakeholder.analysis.influence_analysis_service as influence_mod

    monkeypatch.setattr(
        influence_mod, "InfluenceAnalysisService", RaisingInfluenceService, raising=True
    )

    patterns = await svc._analyze_real_cross_stakeholder_patterns([], [])

    # Fallback should have called the inline influence agent
    assert dummy_influence_agent.called is True
    # And the patterns object should exist with influence_networks present as list
    assert hasattr(patterns, "influence_networks")
    assert isinstance(patterns.influence_networks, list)

