import logging
from typing import Any

logger = logging.getLogger(__name__)


class InfluenceAnalysisService:
    """
    Thin wrapper around the PydanticAI influence agent. Extracted from the monolithic
    StakeholderAnalysisService to improve separation of concerns.

    This service is optional and enabled via USE_INFLUENCE_SERVICE feature flag.
    When disabled or unavailable, the legacy inline agent flow remains the fallback.
    """

    def __init__(self, agent_factory):
        self.agent_factory = agent_factory
        try:
            self.influence_agent = self.agent_factory.get_influence_agent()
        except Exception as e:
            logger.warning(
                f"InfluenceAnalysisService: failed to acquire influence agent from factory: {e}"
            )
            raise

    async def analyze(self, stakeholder_context: Any) -> Any:
        """
        Run influence analysis on an already-prepared stakeholder_context.

        Args:
            stakeholder_context: The context object constructed by StakeholderAnalysisService
                                 (e.g., via _prepare_stakeholder_context)
        Returns:
            Agent run result (the same structure as inline influence_agent.run(...))
        """
        return await self.influence_agent.run(stakeholder_context)

