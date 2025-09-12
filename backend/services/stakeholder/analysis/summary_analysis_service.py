import logging
from typing import Any

logger = logging.getLogger(__name__)


class SummaryAnalysisService:
    """
    Thin wrapper around the PydanticAI summary agent. Extracted from the monolithic
    StakeholderAnalysisService to improve separation of concerns.

    This service is optional and enabled via USE_SUMMARY_SERVICE feature flag.
    When disabled or unavailable, the legacy inline agent flow remains the fallback.
    """

    def __init__(self, agent_factory):
        self.agent_factory = agent_factory
        try:
            self.summary_agent = self.agent_factory.get_summary_agent()
        except Exception as e:
            logger.warning(
                f"SummaryAnalysisService: failed to acquire summary agent from factory: {e}"
            )
            raise

    async def analyze(self, summary_context: Any) -> Any:
        """
        Run summary analysis on a prepared summary_context.

        Args:
            summary_context: The context string prepared by StakeholderAnalysisService
                             via _prepare_multi_stakeholder_context
        Returns:
            Agent run result (same structure as inline summary_agent.run(...))
        """
        return await self.summary_agent.run(summary_context)

