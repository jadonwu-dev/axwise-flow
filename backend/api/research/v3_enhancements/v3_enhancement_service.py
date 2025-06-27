"""
V3 Enhancement Service
Orchestrates all V3 enhancements that layer on top of V1 core.
"""

import logging
import time
from typing import Dict, Any, List, Optional
from backend.api.research.research_types import (
    ChatRequest,
    AnalysisResult,
    EnhancementResult,
)

from .ux_methodology import UXResearchMethodology
from .stakeholder_detector import StakeholderDetector

logger = logging.getLogger(__name__)


class V3EnhancementService:
    """
    V3 Enhancement Service

    Applies UX methodology and advanced features on top of V1 core.
    Designed to fail gracefully - if enhancements fail, V1 core continues working.
    """

    def __init__(self):
        self.ux_methodology = UXResearchMethodology()
        self.stakeholder_detector = StakeholderDetector()
        self.applied_enhancements = []
        self.enhancement_failures = []

        logger.info("🏗️ V3 Enhancement Service initialized")

    async def enhance_response(
        self,
        v1_response: Dict[str, Any],
        request: ChatRequest,
        analysis: AnalysisResult,
    ) -> EnhancementResult:
        """
        Apply V3 enhancements to V1 response.

        Args:
            v1_response: Response from V1 core service
            request: Original chat request
            analysis: Analysis result from V1 core

        Returns:
            EnhancementResult with enhanced response and metadata
        """
        start_time = time.time()
        enhanced_response = v1_response.copy()
        applied_enhancements = []
        enhancement_failures = []

        try:
            # Enhancement 1: UX Methodology Suggestions
            if "suggestions" in enhanced_response and enhanced_response["suggestions"]:
                try:
                    conversation_stage = self._determine_conversation_stage(analysis)
                    enhanced_suggestions = self.ux_methodology.enhance_suggestions(
                        enhanced_response["suggestions"], conversation_stage
                    )
                    enhanced_response["suggestions"] = enhanced_suggestions
                    applied_enhancements.append("ux_suggestions")
                    logger.info("✅ Applied UX suggestion enhancement")
                except Exception as e:
                    enhancement_failures.append(f"ux_suggestions: {e}")
                    logger.warning(f"UX suggestion enhancement failed: {e}")

            # Enhancement 2: UX Methodology Response Tone
            if "content" in enhanced_response:
                try:
                    conversation_stage = self._determine_conversation_stage(analysis)
                    enhanced_content = self.ux_methodology.enhance_response_tone(
                        enhanced_response["content"], conversation_stage
                    )
                    enhanced_response["content"] = enhanced_content
                    applied_enhancements.append("ux_response_tone")
                    logger.info("✅ Applied UX response tone enhancement")
                except Exception as e:
                    enhancement_failures.append(f"ux_response_tone: {e}")
                    logger.warning(f"UX response tone enhancement failed: {e}")

            # Enhancement 3: Advanced Stakeholder Detection (for questions)
            if "questions" in enhanced_response and enhanced_response["questions"]:
                try:
                    enhanced_questions = (
                        await self._enhance_questions_with_stakeholders(
                            enhanced_response["questions"], request, analysis
                        )
                    )
                    enhanced_response["questions"] = enhanced_questions
                    applied_enhancements.append("advanced_stakeholders")
                    logger.info("✅ Applied advanced stakeholder enhancement")
                except Exception as e:
                    enhancement_failures.append(f"advanced_stakeholders: {e}")
                    logger.warning(f"Advanced stakeholder enhancement failed: {e}")

            # Enhancement 4: Add V3 Metadata
            try:
                if "metadata" not in enhanced_response:
                    enhanced_response["metadata"] = {}

                enhanced_response["metadata"].update(
                    {
                        "v3_enhancements_applied": applied_enhancements,
                        "v3_enhancement_failures": enhancement_failures,
                        "ux_methodology_active": True,
                        "conversation_stage": self._determine_conversation_stage(
                            analysis
                        ),
                        "enhancement_processing_time_ms": int(
                            (time.time() - start_time) * 1000
                        ),
                    }
                )
                applied_enhancements.append("v3_metadata")
            except Exception as e:
                enhancement_failures.append(f"v3_metadata: {e}")
                logger.warning(f"V3 metadata enhancement failed: {e}")

            processing_time = int((time.time() - start_time) * 1000)
            logger.info(
                f"✅ V3 enhancements completed in {processing_time}ms - applied: {applied_enhancements}"
            )

            return EnhancementResult(
                enhanced_response=enhanced_response,
                enhancements_applied=applied_enhancements,
                enhancement_failures=enhancement_failures,
                fallback_used=False,
            )

        except Exception as e:
            logger.error(f"V3 enhancement service failed: {e}")
            # Return original V1 response with failure metadata
            v1_response["metadata"] = v1_response.get("metadata", {})
            v1_response["metadata"]["v3_enhancement_failed"] = str(e)

            return EnhancementResult(
                enhanced_response=v1_response,
                enhancements_applied=[],
                enhancement_failures=[f"service_failure: {e}"],
                fallback_used=True,
            )

    async def _enhance_questions_with_stakeholders(
        self, questions: Dict[str, Any], request: ChatRequest, analysis: AnalysisResult
    ) -> Dict[str, Any]:
        """Enhance questions with advanced stakeholder detection"""
        try:
            logger.info("🔍 Starting stakeholder enhancement process...")

            from backend.services.llm import LLMServiceFactory

            llm_service = LLMServiceFactory.create(
                "gemini"
            )  # Use basic gemini instead of enhanced

            context_analysis = analysis.context_analysis
            business_idea = context_analysis.get("business_idea", "")
            target_customer = context_analysis.get("target_customer", "")
            problem = context_analysis.get("problem", "")

            logger.info(
                f"🔍 Context for stakeholder generation: business='{business_idea}', customer='{target_customer}', problem='{problem}'"
            )

            # Generate dynamic stakeholders with unique questions
            logger.info("🔍 About to call stakeholder detector...")
            stakeholder_data = await self.stakeholder_detector.generate_dynamic_stakeholders_with_unique_questions(
                llm_service=llm_service,
                context_analysis=context_analysis,
                messages=request.messages,
                business_idea=business_idea,
                target_customer=target_customer,
                problem=problem,
            )
            logger.info(f"🔍 Stakeholder detector returned: {stakeholder_data}")

            # DEBUG: Log stakeholder data before merging
            logger.info(f"🔍 Stakeholder data before merging: {stakeholder_data}")
            if isinstance(stakeholder_data, dict):
                primary_count = len(stakeholder_data.get("primary", []))
                secondary_count = len(stakeholder_data.get("secondary", []))
                logger.info(
                    f"🔍 Stakeholder counts: {primary_count} primary, {secondary_count} secondary"
                )

            # Create V3-only questions structure with rich stakeholder data
            # V1 bypassed - create questions structure from V3 Enhancement Service
            if questions and isinstance(questions, dict):
                enhanced_questions = questions.copy()
            else:
                logger.info(
                    "🔧 Base questions are empty, creating new questions structure"
                )
                enhanced_questions = {
                    "problemDiscovery": [],
                    "solutionValidation": [],
                    "followUp": [],
                }

            # Add stakeholder data and time estimates
            enhanced_questions["stakeholders"] = stakeholder_data
            enhanced_questions["estimatedTime"] = (
                self.stakeholder_detector.calculate_stakeholder_time_estimates(
                    stakeholder_data
                )
            )

            # DEBUG: Log final questions structure
            final_stakeholders = enhanced_questions.get("stakeholders", {})
            if isinstance(final_stakeholders, dict):
                final_primary = len(final_stakeholders.get("primary", []))
                final_secondary = len(final_stakeholders.get("secondary", []))
                logger.info(
                    f"🔍 Final V3-only questions: {final_primary} primary, {final_secondary} secondary stakeholders"
                )

            return enhanced_questions

        except Exception as e:
            logger.error(f"🔴 Stakeholder enhancement failed: {e}")
            import traceback

            logger.error(
                f"🔴 Stakeholder enhancement traceback: {traceback.format_exc()}"
            )
            return questions  # Return original questions

    def _determine_conversation_stage(self, analysis: AnalysisResult) -> str:
        """Determine conversation stage from analysis"""
        try:
            intent = analysis.intent_analysis.get("intent", "")
            business_ready = analysis.business_validation.get(
                "ready_for_questions", False
            )
            user_confirmed = analysis.user_confirmation.get("is_confirmation", False)

            if intent in ["question_request", "confirmation"] or (
                business_ready and user_confirmed
            ):
                return "ready_for_questions"
            elif business_ready and not user_confirmed:
                return "confirmation"
            elif intent == "clarify_business":
                return "business_discovery"
            elif "customer" in str(
                analysis.context_analysis.get("missing_elements", [])
            ):
                return "customer_discovery"
            elif "problem" in str(
                analysis.context_analysis.get("missing_elements", [])
            ):
                return "problem_discovery"
            else:
                return "validation_and_refinement"

        except Exception as e:
            logger.error(f"Stage determination failed: {e}")
            return "discovery"

    def get_enhancement_stats(self) -> Dict[str, Any]:
        """Get statistics about applied enhancements"""
        return {
            "service": "v3_enhancement_service",
            "version": "v3_rebuilt_modular",
            "available_enhancements": [
                "ux_suggestions",
                "ux_response_tone",
                "advanced_stakeholders",
                "v3_metadata",
            ],
            "enhancement_components": {
                "ux_methodology": self.ux_methodology.get_enhancement_metadata(),
                "stakeholder_detector": "advanced_stakeholder_detection",
            },
        }

    def should_apply_enhancements(
        self, v1_response: Dict[str, Any], analysis: AnalysisResult
    ) -> bool:
        """Determine if V3 enhancements should be applied"""
        try:
            # Always try to apply enhancements - they're designed to fail gracefully
            return True

        except Exception:
            return False  # Conservative fallback
