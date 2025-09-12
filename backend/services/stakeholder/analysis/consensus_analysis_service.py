import logging
from typing import Any, List

logger = logging.getLogger(__name__)


class ConsensusAnalysisService:
    """
    Thin wrapper around the PydanticAI consensus agent. Extracted from the monolithic
    StakeholderAnalysisService to improve separation of concerns.

    This service is optional and enabled via USE_CONSENSUS_SERVICE feature flag.
    When disabled or unavailable, the legacy inline agent flow remains the fallback.
    """

    def __init__(self, agent_factory):
        self.agent_factory = agent_factory
        try:
            self.consensus_agent = self.agent_factory.get_consensus_agent()
        except Exception as e:
            logger.warning(
                f"ConsensusAnalysisService: failed to acquire consensus agent from factory: {e}"
            )
            raise

    async def analyze(self, stakeholder_context: Any) -> Any:
        """
        Run consensus analysis on an already-prepared stakeholder_context.

        Args:
            stakeholder_context: The context object constructed by StakeholderAnalysisService
                                 (e.g., via _prepare_stakeholder_context)
        Returns:
            Agent run result (the same structure as inline consensus_agent.run(...))
        """
        return await self.consensus_agent.run(stakeholder_context)

