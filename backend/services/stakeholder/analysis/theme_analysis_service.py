import logging
from typing import Any

from backend.utils.pydantic_ai_retry import safe_pydantic_ai_call

logger = logging.getLogger(__name__)


class ThemeAnalysisService:
    """
    Thin wrapper around the PydanticAI theme agent. Extracted from the monolithic
    StakeholderAnalysisService to improve separation of concerns.

    This service is optional and enabled via USE_THEME_SERVICE feature flag.
    When disabled or unavailable, the legacy inline agent flow remains the fallback.
    """

    def __init__(self, agent_factory):
        self.agent_factory = agent_factory
        try:
            self.theme_agent = self.agent_factory.get_theme_agent()
        except Exception as e:
            logger.warning(
                f"ThemeAnalysisService: failed to acquire theme agent from factory: {e}"
            )
            raise

    async def analyze(self, theme_context: Any) -> Any:
        """
        Run theme attribution analysis directly via agent.run on prepared context.
        """
        return await self.theme_agent.run(theme_context)

    async def analyze_with_retry(
        self, theme_context: Any, retry_config: Any, context_label: str
    ) -> Any:
        """
        Run theme attribution analysis with retry using the shared helper.
        Mirrors the inline safe_pydantic_ai_call(...) usage in the legacy path.
        """
        return await safe_pydantic_ai_call(
            agent=self.theme_agent,
            prompt=theme_context,
            context=context_label,
            retry_config=retry_config,
        )

