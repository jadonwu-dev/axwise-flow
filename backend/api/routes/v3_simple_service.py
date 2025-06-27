"""
Core service class for Customer Research API v3 Simplified.

This module contains the main SimplifiedResearchService class that orchestrates
all V3 Simple customer research operations.

Extracted from customer_research_v3_simple.py for better modularity.
"""

import asyncio
import time
import logging
from typing import Dict, Any, List, Optional

from .v3_simple_types import SimplifiedConfig, RequestMetrics, Message
from .v3_simple_utils import get_operation_description

logger = logging.getLogger(__name__)


class SimplifiedResearchService:
    """
    Simplified research service that provides all V3 features with V1/V2 stability.

    This service is designed to be:
    - Request-scoped (no global state)
    - Memory efficient (bounded collections)
    - Error resilient (clear fallback paths)
    - Performance optimized (smart caching)
    - Production ready (proper monitoring)
    """

    # Class-level registry for active instances (for progressive updates)
    _active_instances: Dict[str, "SimplifiedResearchService"] = {}

    def __init__(self, config: Optional[SimplifiedConfig] = None):
        """Initialize the simplified research service."""

        self.config = config or SimplifiedConfig()
        self.request_id = f"req_{int(time.time() * 1000)}_{id(self)}"

        # Initialize metrics for this request
        self.metrics = RequestMetrics(request_id=self.request_id)

        # Initialize thinking process tracking
        self.thinking_steps: List[Dict[str, Any]] = []

        # Initialize cache for this request
        self.request_cache: Dict[str, Any] = {}

        # Initialize LLM interaction tracking for raw content capture
        self.llm_interactions: List[Dict[str, Any]] = []

        # Initialize LLM client (reuse from V1/V2 proven patterns)
        self._llm_client = None

        # Initialize Instructor client for structured output (V1 sustainability pattern)
        self._instructor_client = None

        # Store instance in global registry for progressive updates
        SimplifiedResearchService._active_instances[self.request_id] = self
        logger.debug(
            f"Added instance {self.request_id} to registry. Total active instances: {len(SimplifiedResearchService._active_instances)}"
        )

        logger.info(f"Initialized SimplifiedResearchService {self.request_id}")

    def _get_llm_client(self):
        """Get or create LLM client using proven V1/V2 patterns."""
        if self._llm_client is None:
            # Import the proven LLM service factory from V1/V2
            from backend.services.llm import LLMServiceFactory

            self._llm_client = LLMServiceFactory.create("enhanced_gemini")
        return self._llm_client

    def _get_instructor_client(self):
        """Get or create Instructor client for structured output (V1 sustainability pattern)."""
        if self._instructor_client is None:
            from backend.services.llm.instructor_gemini_client import (
                InstructorGeminiClient,
            )

            self._instructor_client = InstructorGeminiClient()
        return self._instructor_client

    def _add_thinking_step(
        self,
        step: str,
        status: str = "in_progress",
        details: str = "",
        duration_ms: int = 0,
    ):
        """Add or update a thinking step with memory management."""
        try:
            # Check if this step already exists (to update instead of duplicate)
            existing_step_index = None
            for i, existing_step in enumerate(self.thinking_steps):
                if existing_step["step"] == step:
                    existing_step_index = i
                    break

            thinking_step = {
                "step": step,
                "status": status,
                "details": details,
                "duration_ms": duration_ms,
                "timestamp": int(time.time() * 1000),
            }

            if existing_step_index is not None:
                # Update existing step
                self.thinking_steps[existing_step_index] = thinking_step
            else:
                # Add new step
                self.thinking_steps.append(thinking_step)

            # Memory management: keep only recent steps
            if len(self.thinking_steps) > self.config.max_thinking_steps:
                self.thinking_steps = self.thinking_steps[
                    -self.config.max_thinking_steps :
                ]

            logger.debug(
                f"{'Updated' if existing_step_index is not None else 'Added'} thinking step: {step}"
            )
        except Exception as e:
            logger.warning(f"Failed to add thinking step: {e}")

    def _capture_llm_interaction(
        self,
        operation_name: str,
        prompt: str,
        response: str,
        metadata: Dict[str, Any] = None,
    ):
        """Capture raw LLM interactions for transparent thinking process."""
        try:
            interaction = {
                "operation": operation_name,
                "timestamp": int(time.time() * 1000),
                "prompt": prompt,
                "response": response,
                "metadata": metadata or {},
            }
            self.llm_interactions.append(interaction)

            # Memory management: keep only recent interactions
            if len(self.llm_interactions) > 20:  # Keep last 20 interactions
                self.llm_interactions = self.llm_interactions[-20:]

            logger.debug(f"Captured LLM interaction for {operation_name}")
        except Exception as e:
            logger.warning(f"Failed to capture LLM interaction: {e}")

    def get_current_thinking_steps(self) -> List[Dict[str, Any]]:
        """Get current thinking steps for progressive updates."""
        return self.thinking_steps.copy()

    def cleanup(self):
        """Clean up instance from registry."""
        if self.request_id in SimplifiedResearchService._active_instances:
            del SimplifiedResearchService._active_instances[self.request_id]
            logger.debug(
                f"Removed instance {self.request_id} from registry. Remaining active instances: {len(SimplifiedResearchService._active_instances)}"
            )
        else:
            logger.warning(
                f"Instance {self.request_id} not found in registry during cleanup"
            )

    def _get_cache_key(self, operation: str, context_hash: str) -> str:
        """Generate cache key for operation."""
        return f"v3_simple:{operation}:{context_hash[:16]}"

    def _get_from_cache(self, cache_key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.config.enable_caching:
            return None

        # Check request-level cache first
        if cache_key in self.request_cache:
            self.metrics.cache_hits += 1
            return self.request_cache[cache_key]

        # TODO: Add Redis cache integration here
        # For now, only use request-level cache
        self.metrics.cache_misses += 1
        return None

    def _store_in_cache(self, cache_key: str, value: Any):
        """Store value in cache."""
        if not self.config.enable_caching:
            return

        # Store in request-level cache
        self.request_cache[cache_key] = value

        # TODO: Add Redis cache integration here

    async def _execute_with_monitoring(
        self, operation_name: str, operation_func, *args, **kwargs
    ) -> Any:
        """Execute operation with monitoring and error handling."""

        start_time = time.time()

        try:
            # Add initial thinking step with more descriptive content
            if self.config.enable_thinking_process:
                initial_description = get_operation_description(
                    operation_name, "starting"
                )
                self._add_thinking_step(
                    operation_name, "in_progress", initial_description
                )

            # Execute with timeout
            result = await asyncio.wait_for(
                operation_func(*args, **kwargs),
                timeout=self.config.request_timeout_seconds,
            )

            # Calculate duration
            duration_ms = int((time.time() - start_time) * 1000)

            # Update metrics
            setattr(
                self.metrics,
                f"{operation_name.lower().replace(' ', '_')}_ms",
                duration_ms,
            )

            # Update thinking step to completed with detailed results
            if self.config.enable_thinking_process:
                completion_description = get_operation_description(
                    operation_name,
                    "completed",
                    result,
                    duration_ms,
                    self.llm_interactions,
                )
                self._add_thinking_step(
                    operation_name, "completed", completion_description, duration_ms
                )

            logger.debug(f"{operation_name} completed in {duration_ms}ms")
            return result

        except asyncio.TimeoutError:
            duration_ms = int((time.time() - start_time) * 1000)
            error_msg = f"{operation_name} timed out after {self.config.request_timeout_seconds}s"

            self.metrics.errors_encountered.append(error_msg)

            if self.config.enable_thinking_process:
                self._add_thinking_step(
                    operation_name, "failed", error_msg, duration_ms
                )

            logger.warning(error_msg)
            raise

        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            error_msg = f"{operation_name} failed: {str(e)}"

            self.metrics.errors_encountered.append(error_msg)

            if self.config.enable_thinking_process:
                self._add_thinking_step(
                    operation_name, "failed", error_msg, duration_ms
                )

            logger.error(error_msg)
            raise

    async def analyze_comprehensive(
        self,
        conversation_context: str,
        latest_input: str,
        messages: List[Dict[str, Any]],
        existing_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Perform comprehensive research analysis using all V3 features with V1/V2 stability.

        This method provides:
        - Sequential processing (no parallel complexity)
        - Smart caching for performance
        - Clear error handling with fallbacks
        - Complete thinking process tracking
        - All V3 enhanced features
        """

        logger.info(f"Starting comprehensive analysis for request {self.request_id}")

        try:
            # Import analysis functions (will be in separate modules)
            from .v3_simple_analysis import (
                analyze_context_enhanced,
                analyze_intent_enhanced,
                validate_business_readiness,
                analyze_industry_enhanced,
                detect_stakeholders_enhanced,
                analyze_conversation_flow,
            )
            from .v3_simple_questions import generate_response_enhanced

            # Phase 1: Core Analysis (using proven V1/V2 functions)
            context_analysis = await self._execute_with_monitoring(
                "Context Analysis",
                analyze_context_enhanced,
                self,
                conversation_context,
                latest_input,
                existing_context,
            )

            intent_analysis = await self._execute_with_monitoring(
                "Intent Analysis",
                analyze_intent_enhanced,
                self,
                conversation_context,
                latest_input,
                messages,
            )

            business_validation = await self._execute_with_monitoring(
                "Business Validation",
                validate_business_readiness,
                self,
                conversation_context,
                latest_input,
            )

            # Phase 2: Enhanced Analysis (V3 features with caching)
            industry_analysis = await self._execute_with_monitoring(
                "Industry Analysis",
                analyze_industry_enhanced,
                self,
                conversation_context,
                context_analysis,
            )

            stakeholder_detection = await self._execute_with_monitoring(
                "Stakeholder Detection",
                detect_stakeholders_enhanced,
                self,
                conversation_context,
                context_analysis,
                industry_analysis,
            )

            conversation_flow = await self._execute_with_monitoring(
                "Conversation Flow",
                analyze_conversation_flow,
                self,
                messages,
                context_analysis,
                intent_analysis,
                latest_input,
            )

            # Phase 3: Response Generation
            response_generation = await self._execute_with_monitoring(
                "Response Generation",
                generate_response_enhanced,
                self,
                conversation_context,
                latest_input,
                context_analysis,
                intent_analysis,
                business_validation,
                industry_analysis,
                stakeholder_detection,
                conversation_flow,
            )

            # Compile final results
            final_result = {
                "context": context_analysis,
                "intent": intent_analysis,
                "business_validation": business_validation,
                "industry": industry_analysis,
                "stakeholders": stakeholder_detection,
                "conversation_flow": conversation_flow,
                "response": response_generation,
                "thinking_process": self.get_current_thinking_steps(),
                "performance_metrics": {
                    "request_id": self.request_id,
                    "total_duration_ms": self.metrics.total_duration_ms,
                    "success_rate": self.metrics.success_rate,
                    "cache_hits": self.metrics.cache_hits,
                    "cache_misses": self.metrics.cache_misses,
                    "component_timings": {
                        "context_analysis_ms": self.metrics.context_analysis_ms,
                        "intent_analysis_ms": self.metrics.intent_analysis_ms,
                        "business_validation_ms": self.metrics.business_validation_ms,
                        "industry_analysis_ms": self.metrics.industry_analysis_ms,
                        "stakeholder_detection_ms": self.metrics.stakeholder_detection_ms,
                        "conversation_flow_ms": self.metrics.conversation_flow_ms,
                        "response_generation_ms": self.metrics.response_generation_ms,
                    },
                },
            }

            # Mark metrics as completed
            self.metrics.end_time = time.time()

            logger.info(
                f"Comprehensive analysis completed for request {self.request_id} in {self.metrics.total_duration_ms}ms"
            )
            return final_result

        except Exception as e:
            logger.error(
                f"Comprehensive analysis failed for request {self.request_id}: {str(e)}"
            )
            self.metrics.errors_encountered.append(
                f"Comprehensive analysis failed: {str(e)}"
            )
            raise
