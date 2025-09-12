import asyncio
import pytest

from backend.services.stakeholder.analysis.summary_analysis_service import SummaryAnalysisService
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

    def get_summary_agent(self):
        return self._agent


@pytest.mark.asyncio
async def test_summary_analysis_service_invokes_agent():
    agent = DummyAgent({"key_insights": ["A"]})
    factory = DummyFactory(agent)
    service = SummaryAnalysisService(factory)

    res = await service.analyze("context")

    assert res == {"key_insights": ["A"]}
    assert agent.called is True


@pytest.mark.asyncio
async def test_stakeholder_analysis_summary_flag_fallback(monkeypatch):
    # Enable summary service usage, but force the service constructor to raise
    monkeypatch.setenv("USE_SUMMARY_SERVICE", "true")

    svc = StakeholderAnalysisService(llm_service=None)

    # Ensure the service branch is taken: pydantic ai available + summary agent + factory present
    svc.pydantic_ai_available = True
    dummy_summary_agent = DummyAgent({"key_insights": []})
    svc.summary_agent = dummy_summary_agent
    svc.agent_factory = object()

    class RaisingSummaryService:
        def __init__(self, *args, **kwargs):
            raise RuntimeError("boom")

        async def analyze(self, *args, **kwargs):  # pragma: no cover
            return {"key_insights": []}

    import backend.services.stakeholder.analysis.summary_analysis_service as summary_mod

    monkeypatch.setattr(
        summary_mod, "SummaryAnalysisService", RaisingSummaryService, raising=True
    )

    # Call the summary generation method directly with minimal inputs
    # Minimal detected_stakeholders and empty cross patterns are okay because
    # DummyAgent ignores the context and just returns
    from backend.schemas import CrossStakeholderPatterns

    empty_patterns = CrossStakeholderPatterns(
        consensus_areas=[], conflict_zones=[], influence_networks=[], stakeholder_priority_matrix={}
    )

    res = await svc._generate_real_multi_stakeholder_summary([], empty_patterns, [])

    # Fallback should have called the inline summary agent
    assert dummy_summary_agent.called is True

