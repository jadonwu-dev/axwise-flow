"""
V1 Core Service
Orchestrates all V1 core functionality - proven and reliable.
"""

import logging
import time
from typing import Dict, Any, List, Optional
from backend.api.research.research_types import (
    ChatRequest,
    AnalysisResult,
    ResearchQuestions,
)
from backend.services.llm import LLMServiceFactory

from .conversation_analyzer import (
    extract_context_with_llm,
    analyze_user_intent_with_llm,
    validate_business_readiness_with_llm,
    classify_industry_with_llm,
)
from .response_generator import (
    generate_research_response_with_retry,
    generate_confirmation_response,
    generate_contextual_suggestions,
)
from .question_generator import (
    generate_comprehensive_research_questions,
    detect_stakeholders_with_llm,
)

logger = logging.getLogger(__name__)


class V1CoreService:
    """
    V1 Core Service - Proven and Reliable

    Handles all core customer research functionality that has been
    tested and proven to work reliably in production.
    """

    def __init__(self):
        self.llm_service = None
        logger.info("🏗️ V1 Core Service initialized")

    async def _get_llm_service(self):
        """Get or create LLM service"""
        if not self.llm_service:
            self.llm_service = LLMServiceFactory.create(
                "gemini"
            )  # Use basic gemini instead of enhanced
        return self.llm_service

    async def analyze_conversation(self, request: ChatRequest) -> AnalysisResult:
        """
        Analyze conversation using V1 proven methods.

        Returns comprehensive analysis including:
        - Context extraction (business idea, target customer, problem)
        - Intent analysis (what user wants to do)
        - Business readiness (ready for questions?)
        - Industry classification
        """
        start_time = time.time()

        try:
            llm_service = await self._get_llm_service()

            # Build conversation context
            conversation_context = ""
            for msg in request.messages:
                conversation_context += f"{msg.role}: {msg.content}\n"
            if request.input:
                conversation_context += f"user: {request.input}\n"

            logger.info("🧠 Starting V1 conversation analysis")

            # Run all analysis functions in parallel for efficiency
            import asyncio

            context_task = extract_context_with_llm(
                llm_service, conversation_context, request.input
            )
            intent_task = analyze_user_intent_with_llm(
                llm_service, conversation_context, request.input, request.messages
            )
            business_task = validate_business_readiness_with_llm(
                llm_service, conversation_context, request.input
            )

            # Wait for all analysis to complete
            context_analysis, intent_analysis, business_validation = (
                await asyncio.gather(context_task, intent_task, business_task)
            )

            # Simple user confirmation detection
            user_confirmation = {
                "is_confirmation": intent_analysis.get("intent")
                in ["confirmation", "question_request"],
                "confidence": intent_analysis.get("confidence", 0.5),
                "reasoning": "V1 confirmation detection based on intent",
            }

            processing_time = int((time.time() - start_time) * 1000)

            result = AnalysisResult(
                context_analysis=context_analysis,
                intent_analysis=intent_analysis,
                business_validation=business_validation,
                user_confirmation=user_confirmation,
                processing_time_ms=processing_time,
            )

            logger.info(f"✅ V1 analysis completed in {processing_time}ms")
            return result

        except Exception as e:
            logger.error(f"V1 conversation analysis failed: {e}")
            # Return minimal fallback analysis
            return AnalysisResult(
                context_analysis={
                    "businessIdea": None,
                    "targetCustomer": None,
                    "problem": None,
                },
                intent_analysis={"intent": "clarify_business", "confidence": 0.3},
                business_validation={
                    "ready_for_questions": False,
                    "readiness_score": 0.2,
                },
                user_confirmation={"is_confirmation": False, "confidence": 0.3},
                processing_time_ms=int((time.time() - start_time) * 1000),
            )

    async def generate_response(
        self,
        request: ChatRequest,
        analysis: AnalysisResult,
        response_type: str = "conversational",
    ) -> Dict[str, Any]:
        """
        Generate response using V1 proven methods.

        Args:
            request: Chat request
            analysis: Analysis result from analyze_conversation
            response_type: "conversational", "confirmation", or "questions"
        """
        try:
            llm_service = await self._get_llm_service()

            # Build conversation context
            conversation_context = ""
            for msg in request.messages:
                conversation_context += f"{msg.role}: {msg.content}\n"
            if request.input:
                conversation_context += f"user: {request.input}\n"

            if response_type == "confirmation":
                # Generate confirmation response
                content = await generate_confirmation_response(
                    llm_service,
                    request.messages,
                    request.input,
                    request.context,
                    conversation_context,
                )
                suggestions = [
                    "Yes, that's correct",
                    "Let me add something",
                    "I need to clarify something",
                ]

            elif response_type == "questions":
                # Generate research questions
                questions = await self.generate_questions(request, analysis)
                content = "Perfect! I've generated your custom research questions based on our conversation."
                suggestions = ["Export questions", "Modify questions", "Start research"]

                return {
                    "content": content,
                    "questions": questions,
                    "suggestions": suggestions,
                    "metadata": {
                        "response_type": "questions",
                        "v1_core": True,
                        "analysis": analysis.model_dump(),
                        "extracted_context": {
                            "business_idea": analysis.context_analysis.get(
                                "businessIdea"
                            ),
                            "target_customer": analysis.context_analysis.get(
                                "targetCustomer"
                            ),
                            "problem": analysis.context_analysis.get("problem"),
                            "questions_generated": True,
                        },
                    },
                }

            else:
                # Generate conversational response
                content = await generate_research_response_with_retry(
                    llm_service,
                    request.messages,
                    request.input,
                    request.context,
                    conversation_context,
                )
                suggestions = await generate_contextual_suggestions(
                    llm_service,
                    request.messages,
                    request.input,
                    content,
                    conversation_context,
                )

            return {
                "content": content,
                "questions": None,
                "suggestions": suggestions,
                "metadata": {
                    "response_type": response_type,
                    "v1_core": True,
                    "analysis": analysis.model_dump(),
                    "extracted_context": {
                        "business_idea": analysis.context_analysis.get("businessIdea"),
                        "target_customer": analysis.context_analysis.get(
                            "targetCustomer"
                        ),
                        "problem": analysis.context_analysis.get("problem"),
                        "questions_generated": False,
                    },
                },
            }

        except Exception as e:
            logger.error(f"V1 response generation failed: {e}")
            return {
                "content": "I'd love to learn more about your business idea. Can you tell me what problem you're trying to solve?",
                "questions": None,
                "suggestions": [
                    "Tell me more",
                    "Can you be more specific?",
                    "What industry is this for?",
                ],
                "metadata": {
                    "response_type": "fallback",
                    "v1_core": True,
                    "error": str(e),
                    "extracted_context": {
                        "business_idea": None,
                        "target_customer": None,
                        "problem": None,
                        "questions_generated": False,
                    },
                },
            }

    async def generate_questions(
        self, request: ChatRequest, analysis: AnalysisResult
    ) -> ResearchQuestions:
        """Generate research questions using V1 proven methods."""
        try:
            llm_service = await self._get_llm_service()

            # Create context object from analysis
            context_data = analysis.context_analysis
            from backend.api.research.research_types import ResearchContext

            context = ResearchContext(
                businessIdea=context_data.get("businessIdea"),
                targetCustomer=context_data.get("targetCustomer"),
                problem=context_data.get("problem"),
                stage=context_data.get("stage"),
            )

            # Detect stakeholders
            stakeholder_data = await detect_stakeholders_with_llm(
                llm_service, context, request.messages
            )

            # Generate comprehensive questions
            questions = await generate_comprehensive_research_questions(
                llm_service, context, request.messages, stakeholder_data
            )

            logger.info("✅ V1 questions generated successfully")
            return questions

        except Exception as e:
            logger.error(f"V1 question generation failed: {e}")
            # Return minimal fallback questions
            from backend.api.research.v1_core.question_generator import (
                generate_fallback_questions,
            )

            return await generate_fallback_questions(
                context if "context" in locals() else None
            )

    def should_generate_questions(self, analysis: AnalysisResult) -> bool:
        """
        Determine if we should generate questions based on proper validation.

        Requires sufficient context to generate meaningful, targeted research questions.
        """
        try:
            # Check user confirmation
            user_confirmed = analysis.user_confirmation.get("is_confirmation", False)

            # Check intent for explicit question request
            intent = analysis.intent_analysis.get("intent", "")
            explicit_request = intent in ["question_request", "confirmation"]

            # Only proceed if user confirmed or explicitly requested
            if not (user_confirmed or explicit_request):
                return False

            # Check business readiness - must have sufficient context
            business_ready = analysis.business_validation.get(
                "ready_for_questions", False
            )

            if business_ready:
                logger.info("✅ Generating questions with sufficient context")
                return True

            # Additional check: if user explicitly requests questions, check minimal requirements
            if explicit_request:
                context_analysis = analysis.context_analysis

                has_business_idea = bool(
                    context_analysis.get("businessIdea")
                    or context_analysis.get("business_idea")
                )
                has_target_customer = bool(
                    context_analysis.get("targetCustomer")
                    or context_analysis.get("target_customer")
                )
                has_problem = bool(context_analysis.get("problem"))

                # Require at least business idea + (customer OR problem)
                if has_business_idea and (has_target_customer or has_problem):
                    logger.info(
                        "✅ Generating questions with minimal but sufficient context"
                    )
                    return True
                else:
                    logger.info("❌ Insufficient context for meaningful questions")
                    return False

            logger.info("❌ Not ready for questions - need more context")
            return False

        except Exception as e:
            logger.error(f"Question readiness check failed: {e}")
            return False

    def should_show_confirmation(self, analysis: AnalysisResult) -> bool:
        """
        Determine if we should show confirmation before questions.

        Only show confirmation when we have sufficient context for meaningful questions.
        """
        try:
            user_confirmed = analysis.user_confirmation.get("is_confirmation", False)

            # Don't show confirmation if already confirmed
            if user_confirmed:
                return False

            # Check business readiness - DON'T show confirmation if ready for questions
            business_ready = analysis.business_validation.get(
                "ready_for_questions", False
            )

            # FIXED: If business is ready, we should generate questions, not show confirmation
            if business_ready:
                logger.info(
                    "❌ Not showing confirmation - business ready, should generate questions"
                )
                return False

            # Alternative: check if we have minimal sufficient context
            context_analysis = analysis.context_analysis

            has_business_idea = bool(
                context_analysis.get("businessIdea")
                or context_analysis.get("business_idea")
            )
            has_target_customer = bool(
                context_analysis.get("targetCustomer")
                or context_analysis.get("target_customer")
            )
            has_problem = bool(context_analysis.get("problem"))

            # Show confirmation if we have business idea + (customer OR problem)
            if has_business_idea and (has_target_customer or has_problem):
                logger.info("✅ Showing confirmation - minimal sufficient context")
                return True

            logger.info("❌ Not showing confirmation - need more context")
            return False

        except Exception as e:
            logger.error(f"Confirmation check failed: {e}")
            return False
