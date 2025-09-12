import pytest

from backend.services.stakeholder_analysis_service import StakeholderAnalysisService


class DummyAgent:
    def __init__(self, result):
        self._result = result
        self.called = False

    async def run(self, context):
        self.called = True
        return self._result


class DummyFactory:
    def __init__(self, agents):
        # agents is a dict: {"consensus":DummyAgent, "conflict":..., "influence":..., "summary":..., "theme":...}
        self._agents = agents

    def get_consensus_agent(self):
        return self._agents["consensus"]

    def get_conflict_agent(self):
        return self._agents["conflict"]

    def get_influence_agent(self):
        return self._agents["influence"]

    def get_summary_agent(self):
        return self._agents["summary"]

    def get_theme_agent(self):
        return self._agents["theme"]


class DummyContainer:
    def __init__(self, factory):
        self._factory = factory

    def get_stakeholder_agent_factory(self):
        return self._factory


@pytest.mark.asyncio
async def test_all_service_flags_route_through_services(monkeypatch):
    # Enable DI-backed factory and all service flags
    monkeypatch.setenv("USE_STAKEHOLDER_AGENT_FACTORY", "true")
    monkeypatch.setenv("USE_CONSENSUS_SERVICE", "true")
    monkeypatch.setenv("USE_CONFLICT_SERVICE", "true")
    monkeypatch.setenv("USE_INFLUENCE_SERVICE", "true")
    monkeypatch.setenv("USE_SUMMARY_SERVICE", "true")
    monkeypatch.setenv("USE_THEME_SERVICE", "true")

    # Prepare dummy agents returning minimal valid results
    consensus_agent = DummyAgent([])
    conflict_agent = DummyAgent([])
    influence_agent = DummyAgent([])
    summary_agent = DummyAgent({"key_insights": []})
    theme_agent = DummyAgent({"stakeholder_contributions": []})

    # Create dummy factory and container, and patch DI accessor
    factory = DummyFactory(
        {
            "consensus": consensus_agent,
            "conflict": conflict_agent,
            "influence": influence_agent,
            "summary": summary_agent,
            "theme": theme_agent,
        }
    )

    import backend.api.dependencies as deps

    monkeypatch.setattr(
        deps, "get_container", lambda: DummyContainer(factory), raising=True
    )

    # Patch service classes to test doubles that mark engagement
    engaged = {
        "consensus": False,
        "conflict": False,
        "influence": False,
        "summary": False,
        "theme": False,
    }

    class ConsensusSvc:
        def __init__(self, agent_factory):
            pass

        async def analyze(self, ctx):
            engaged["consensus"] = True
            return await consensus_agent.run(ctx)

    class ConflictSvc:
        def __init__(self, agent_factory):
            pass

        async def analyze(self, ctx):
            engaged["conflict"] = True
            return await conflict_agent.run(ctx)

    class InfluenceSvc:
        def __init__(self, agent_factory):
            pass

        async def analyze(self, ctx):
            engaged["influence"] = True
            return await influence_agent.run(ctx)

    class SummarySvc:
        def __init__(self, agent_factory):
            pass

        async def analyze(self, ctx):
            engaged["summary"] = True
            return await summary_agent.run(ctx)

    class ThemeSvc:
        def __init__(self, agent_factory):
            pass

        async def analyze(self, ctx):
            engaged["theme"] = True
            return await theme_agent.run(ctx)

        async def analyze_with_retry(self, ctx, retry_cfg, label):
            engaged["theme"] = True
            return await theme_agent.run(ctx)

    import backend.services.stakeholder.analysis.consensus_analysis_service as c_mod
    import backend.services.stakeholder.analysis.conflict_analysis_service as f_mod
    import backend.services.stakeholder.analysis.influence_analysis_service as i_mod
    import backend.services.stakeholder.analysis.summary_analysis_service as s_mod
    import backend.services.stakeholder.analysis.theme_analysis_service as t_mod

    monkeypatch.setattr(c_mod, "ConsensusAnalysisService", ConsensusSvc, raising=True)
    monkeypatch.setattr(f_mod, "ConflictAnalysisService", ConflictSvc, raising=True)
    monkeypatch.setattr(i_mod, "InfluenceAnalysisService", InfluenceSvc, raising=True)
    monkeypatch.setattr(s_mod, "SummaryAnalysisService", SummarySvc, raising=True)
    monkeypatch.setattr(t_mod, "ThemeAnalysisService", ThemeSvc, raising=True)

    # Instantiate service; this will pull our DummyFactory via DI
    svc = StakeholderAnalysisService(llm_service=None)

    # Assert factory wired via DI
    assert isinstance(svc.agent_factory, DummyFactory)

    # 1) Trigger consensus/conflict/influence through real method
    _ = await svc._analyze_real_cross_stakeholder_patterns([], [])

    # 2) Trigger summary through real method with minimal CrossStakeholderPatterns
    from backend.schemas import CrossStakeholderPatterns

    empty_patterns = CrossStakeholderPatterns(
        consensus_areas=[],
        conflict_zones=[],
        influence_networks=[],
        stakeholder_priority_matrix={},
    )
    _ = await svc._generate_real_multi_stakeholder_summary([], empty_patterns, [])

    # 3) Trigger theme via parallel path
    _ = await svc._analyze_theme_stakeholder_attribution_parallel(
        {"name": "Theme X"},
        {"S1": {"stakeholder_type": "decision_maker"}},
        {"truncated_content": "", "content_length": 0},
        1,
    )

    # Services should have been instantiated on-demand on the StakeholderAnalysisService
    assert hasattr(svc, "consensus_service")
    assert hasattr(svc, "conflict_service")
    assert hasattr(svc, "influence_service")
    assert hasattr(svc, "summary_service")
    assert hasattr(svc, "theme_service")

    # And their analyze methods should have been engaged (no fallback)
    assert all(engaged.values())

    # Agents should have been called via the service paths
    assert consensus_agent.called is True
    assert conflict_agent.called is True
    assert influence_agent.called is True
    assert summary_agent.called is True
    assert theme_agent.called is True
