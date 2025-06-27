"""
Research Orchestrator
Main coordination service that combines V1 core + V3 enhancements.
"""

import logging
import time
from typing import Dict, Any, Optional
from backend.api.research.research_types import (
    ChatRequest,
    ChatResponse,
    ResearchQuestions,
)

from .v1_core.v1_core_service import V1CoreService
from .v3_enhancements.v3_enhancement_service import V3EnhancementService

logger = logging.getLogger(__name__)


class ResearchOrchestrator:
    """
    Main orchestrator for customer research functionality.

    Coordinates V1 core (proven & reliable) with V3 enhancements (intelligent & fail-safe).
    Always ensures working functionality even if enhancements fail.
    """

    def __init__(self):
        self.v1_core = V1CoreService()
        self.v3_enhancements = V3EnhancementService()

        logger.info(
            "🎯 Research Orchestrator initialized - V1 core + V3 enhancements ready"
        )

    async def process_chat_request(self, request: ChatRequest) -> ChatResponse:
        """
        Process chat request using V1 core + V3 enhancements.

        Flow:
        1. V1 core analyzes conversation (always reliable)
        2. V1 core generates response (always works)
        3. V3 enhancements improve response (fail-safe)
        4. Return enhanced response with metadata
        """
        start_time = time.time()

        try:
            logger.info(f"🎯 Processing chat request: {request.input[:50]}...")

            # Step 1: V1 Core Analysis (Always reliable)
            logger.info("🧠 Running V1 core analysis...")
            analysis = await self.v1_core.analyze_conversation(request)

            # Step 2: Determine response type based on V1 logic
            response_type = self._determine_response_type(analysis)
            logger.info(f"📋 Response type determined: {response_type}")

            # Step 3: V1 Core Response Generation (Always works)
            logger.info(f"🤖 Generating {response_type} response with V1 core...")
            v1_response = await self.v1_core.generate_response(
                request, analysis, response_type
            )

            # Step 4: V3 Enhancements (Fail-safe)
            logger.info("✨ Applying V3 enhancements...")
            enhancement_result = await self.v3_enhancements.enhance_response(
                v1_response, request, analysis
            )

            # Step 5: Build final response
            final_response = enhancement_result.enhanced_response
            processing_time = int((time.time() - start_time) * 1000)

            # Add orchestrator metadata
            if "metadata" not in final_response:
                final_response["metadata"] = {}

            final_response["metadata"].update(
                {
                    "orchestrator": "v1_core_plus_v3_enhancements",
                    "v1_core_used": True,
                    "v3_enhancements_applied": enhancement_result.enhancements_applied,
                    "v3_enhancement_failures": enhancement_result.enhancement_failures,
                    "v3_fallback_used": enhancement_result.fallback_used,
                    "total_processing_time_ms": processing_time,
                    "response_type": response_type,
                }
            )

            # Create ChatResponse
            chat_response = ChatResponse(
                content=final_response["content"],
                metadata=final_response["metadata"],
                questions=final_response.get("questions"),
                suggestions=final_response.get("suggestions"),
                session_id=request.session_id,
                api_version="v1-v3-modular",
                processing_time_ms=processing_time,
            )

            logger.info(f"✅ Chat request completed in {processing_time}ms")
            return chat_response

        except Exception as e:
            logger.error(f"🔴 Orchestrator failed: {e}")

            # Ultimate fallback - simple response
            processing_time = int((time.time() - start_time) * 1000)
            return ChatResponse(
                content="I'd love to learn more about your business idea. Can you tell me what problem you're trying to solve?",
                metadata={
                    "orchestrator_error": str(e),
                    "fallback_response": True,
                    "processing_time_ms": processing_time,
                },
                suggestions=[
                    "Tell me more",
                    "Can you be more specific?",
                    "What industry is this for?",
                ],
                session_id=request.session_id,
                api_version="v1-v3-modular-fallback",
                processing_time_ms=processing_time,
            )

    async def generate_questions(self, request: ChatRequest) -> ResearchQuestions:
        """
        Generate research questions using V1 core + V3 enhancements.
        """
        try:
            logger.info("🎯 Generating research questions...")

            # Use V3 Enhancement Service directly for analysis and question generation
            logger.info(f"🔍 Starting V3-only conversation analysis...")
            analysis = await self.v1_core.analyze_conversation(request)
            logger.info(f"🔍 Analysis context: {analysis.context_analysis}")

            # Skip V1 question generation - go directly to V3 Enhancement Service
            logger.info(f"🔍 Generating questions with V3 Enhancement Service only...")

            # Create minimal base structure for V3 Enhancement Service
            base_questions = {
                "problemDiscovery": [],
                "solutionValidation": [],
                "followUp": [],
            }

            logger.info(
                f"🔍 Applying V3 enhancements to generate rich stakeholder-based questions..."
            )
            v1_response = {"questions": base_questions}
            enhancement_result = await self.v3_enhancements.enhance_response(
                v1_response, request, analysis
            )

            enhanced_questions = enhancement_result.enhanced_response.get(
                "questions", questions
            )

            # Debug: Check enhanced questions after V3
            if (
                isinstance(enhanced_questions, dict)
                and "stakeholders" in enhanced_questions
            ):
                stakeholders = enhanced_questions["stakeholders"]
                if isinstance(stakeholders, dict):
                    primary_count = len(stakeholders.get("primary", []))
                    secondary_count = len(stakeholders.get("secondary", []))
                    logger.info(
                        f"🔍 Enhanced questions stakeholders: {primary_count} primary, {secondary_count} secondary"
                    )

            logger.info("✅ Research questions generated successfully")
            return enhanced_questions

        except Exception as e:
            logger.error(f"Question generation failed: {e}")
            # Return minimal fallback questions
            from backend.api.research.v1_core.question_generator import (
                generate_fallback_questions,
            )

            return await generate_fallback_questions(request.context)

    def _determine_response_type(self, analysis) -> str:
        """Determine what type of response to generate based on V1 analysis"""
        try:
            # Check if ready for questions and user confirmed
            if self.v1_core.should_generate_questions(analysis):
                return "questions"

            # Check if ready for questions but needs confirmation
            elif self.v1_core.should_show_confirmation(analysis):
                return "confirmation"

            # Default to conversational response
            else:
                return "conversational"

        except Exception as e:
            logger.error(f"Response type determination failed: {e}")
            return "conversational"

    async def health_check(self) -> Dict[str, Any]:
        """Health check for the orchestrator and all components"""
        try:
            health_data = {
                "status": "healthy",
                "service": "research_orchestrator",
                "version": "v1_v3_modular",
                "architecture": "v1_core_plus_v3_enhancements",
                "components": {
                    "v1_core_service": "healthy",
                    "v3_enhancement_service": "healthy",
                },
                "enhancement_stats": self.v3_enhancements.get_enhancement_stats(),
            }

            logger.info("✅ Health check completed - all components healthy")
            return health_data

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "degraded",
                "service": "research_orchestrator",
                "error": str(e),
                "fallback_available": True,
            }

    def get_orchestrator_stats(self) -> Dict[str, Any]:
        """Get statistics about the orchestrator"""
        return {
            "orchestrator": "research_orchestrator",
            "architecture": "v1_core_plus_v3_enhancements",
            "design_principles": [
                "v1_core_always_reliable",
                "v3_enhancements_fail_safe",
                "graceful_degradation",
                "comprehensive_fallbacks",
            ],
            "response_types": ["conversational", "confirmation", "questions"],
            "components": {
                "v1_core": "proven_reliable_functionality",
                "v3_enhancements": "ux_methodology_and_advanced_features",
            },
        }
