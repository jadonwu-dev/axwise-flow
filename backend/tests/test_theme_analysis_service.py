import asyncio
import pytest

from backend.services.stakeholder.analysis.theme_analysis_service import (
    ThemeAnalysisService,
)
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

    def get_theme_agent(self):
        return self._agent


@pytest.mark.asyncio
async def test_theme_analysis_service_invokes_agent():
    agent = DummyAgent({"stakeholder_contributions": []})
    factory = DummyFactory(agent)
    service = ThemeAnalysisService(factory)

    res = await service.analyze("context")

    assert res == {"stakeholder_contributions": []}
    assert agent.called is True


@pytest.mark.asyncio
async def test_stakeholder_analysis_theme_flag_fallback_non_parallel(monkeypatch):
    # Enable theme service usage, but force the service constructor to raise
    monkeypatch.setenv("USE_THEME_SERVICE", "true")

    svc = StakeholderAnalysisService(llm_service=None)

    # Ensure the service branch is taken and fallback goes to inline agent.run
    svc.pydantic_ai_available = True
    dummy_theme_agent = DummyAgent({"stakeholder_contributions": []})
    svc.theme_agent = dummy_theme_agent
    svc.agent_factory = object()

    class RaisingThemeService:
        def __init__(self, *args, **kwargs):
            raise RuntimeError("boom")

        async def analyze(self, *args, **kwargs):  # pragma: no cover
            return {"stakeholder_contributions": []}

    import backend.services.stakeholder.analysis.theme_analysis_service as theme_mod

    monkeypatch.setattr(
        theme_mod, "ThemeAnalysisService", RaisingThemeService, raising=True
    )

    # Minimal inputs for non-parallel attribution path
    res = await svc._analyze_theme_stakeholder_attribution({"name": "Theme A"}, {}, [])

    # Fallback should have called the inline theme agent
    assert dummy_theme_agent.called is True
    assert isinstance(res, dict)


@pytest.mark.asyncio
async def test_stakeholder_analysis_theme_service_used_in_parallel(monkeypatch):
    # Enable theme service usage and provide a dummy service with analyze_with_retry
    monkeypatch.setenv("USE_THEME_SERVICE", "true")

    svc = StakeholderAnalysisService(llm_service=None)
    svc.pydantic_ai_available = True
    # Provide a no-op agent since we will route via the service
    svc.theme_agent = DummyAgent({})
    svc.agent_factory = object()

    class DummyThemeService:
        def __init__(self, *args, **kwargs):
            pass

        async def analyze_with_retry(self, theme_context, retry_config, context_label):
            return {
                "stakeholder_contributions": [
                    {"stakeholder_id": "S1", "contribution_strength": 0.7}
                ]
            }

    import backend.services.stakeholder.analysis.theme_analysis_service as theme_mod

    monkeypatch.setattr(
        theme_mod, "ThemeAnalysisService", DummyThemeService, raising=True
    )

    res = await svc._analyze_theme_stakeholder_attribution_parallel(
        {"name": "Theme B"},
        {"S1": {"stakeholder_type": "decision_maker"}},
        {"truncated_content": "", "content_length": 0},
        1,
    )

    assert isinstance(res, dict)
    assert "stakeholder_contributions" in res
    assert len(res["stakeholder_contributions"]) == 1
