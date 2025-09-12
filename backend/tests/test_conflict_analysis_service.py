import asyncio
import os
import types
import pytest

from backend.services.stakeholder.analysis.conflict_analysis_service import ConflictAnalysisService
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

    def get_conflict_agent(self):
        return self._agent


@pytest.mark.asyncio
async def test_conflict_analysis_service_invokes_agent():
    agent = DummyAgent([{"topic": "X"}])
    factory = DummyFactory(agent)
    service = ConflictAnalysisService(factory)

    res = await service.analyze({"any": "context"})

    assert res == [{"topic": "X"}]
    assert agent.called is True


@pytest.mark.asyncio
async def test_stakeholder_analysis_conflict_flag_fallback(monkeypatch):
    # Ensure conflict service path is enabled, but we'll make it raise to trigger fallback
    monkeypatch.setenv("USE_CONFLICT_SERVICE", "true")
    # Disable consensus service usage for this test to reduce dependencies
    monkeypatch.setenv("USE_CONSENSUS_SERVICE", "false")

    svc = StakeholderAnalysisService(llm_service=None)

    # Force PydanticAI availability and inject dummy agents
    svc.pydantic_ai_available = True

    dummy_conflict_agent = DummyAgent([])
    svc.conflict_agent = dummy_conflict_agent

    svc.consensus_agent = DummyAgent([])
    svc.influence_agent = DummyAgent([])

    # Ensure agent_factory exists (required for service branch), but make the
    # conflict service constructor raise to force inline fallback
    class RaisingConflictService:
        def __init__(self, *args, **kwargs):
            raise RuntimeError("boom")

        async def analyze(self, *args, **kwargs):  # pragma: no cover
            return []

    # Patch the import target used in StakeholderAnalysisService
    import backend.services.stakeholder.analysis.conflict_analysis_service as conflict_mod

    monkeypatch.setattr(conflict_mod, "ConflictAnalysisService", RaisingConflictService, raising=True)

    # Call the real analysis method directly with minimal inputs
    # Empty detected_stakeholders and files are acceptable for this unit test path
    patterns = await svc._analyze_real_cross_stakeholder_patterns([], [])

    # Fallback should have called the inline conflict agent
    assert dummy_conflict_agent.called is True
    # And patterns should be created successfully with empty conflict_zones
    assert hasattr(patterns, "conflict_zones")
    assert isinstance(patterns.conflict_zones, list)

