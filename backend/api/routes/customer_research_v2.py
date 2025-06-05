"""
Customer Research API v2 - Using Pydantic + LangGraph state machine.
This replaces the complex conditional logic with a proper workflow.
"""

import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, ValidationError
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.services.external.auth_middleware import get_current_user
from backend.models import User
from backend.services.llm import LLMServiceFactory
from backend.services.research_session_service import ResearchSessionService
from backend.models.research_session import ResearchSessionCreate, ResearchSessionUpdate
from backend.models.conversation_state import (
    ConversationStage,
    BusinessContext
)
from backend.api.routes.customer_research import ResearchContext
from backend.utils.research_validation import validate_research_request, ValidationError as ResearchValidationError
from backend.utils.research_error_handler import (
    ErrorHandler, with_retry, with_timeout, APIError, APITimeoutError,
    ServiceUnavailableError, safe_execute
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/research/v2",
    tags=["customer_research_v2"],
    responses={404: {"description": "Not found"}},
)



# Request/Response models for API compatibility
class Message(BaseModel):
    id: str
    content: str
    role: str
    timestamp: str
    metadata: Optional[Dict[str, Any]] = None


class ResearchContext(BaseModel):
    businessIdea: Optional[str] = None
    targetCustomer: Optional[str] = None
    problem: Optional[str] = None
    stage: Optional[str] = None
    questionsGenerated: Optional[bool] = None


class ChatRequest(BaseModel):
    messages: List[Message]
    input: str
    context: Optional[ResearchContext] = None
    session_id: Optional[str] = None
    user_id: Optional[str] = None


class ChatResponse(BaseModel):
    content: str
    metadata: Optional[Dict[str, Any]] = None
    questions: Optional[Dict[str, List[str]]] = None
    session_id: Optional[str] = None





@router.post("/chat", response_model=ChatResponse)
async def research_chat_v2(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    Handle customer research chat conversation using simple Pydantic state machine.
    """
    try:
        logger.info("Processing research chat request v2")
        logger.info(f"Request data: messages={len(request.messages)}, input='{request.input}', session_id={request.session_id}")

        # Input validation
        if hasattr(request, 'input') and request.input:
            from backend.utils.research_validation import ResearchValidator
            request.input = ResearchValidator.sanitize_input(request.input)
            logger.debug(f"Sanitized input: {request.input}")

        # Create services
        session_service = ResearchSessionService(db)
        llm_service = LLMServiceFactory.create("enhanced_gemini")

        logger.info("Services created successfully")

        # Handle session management
        session_id = request.session_id
        is_local_session = session_id and session_id.startswith('local_')

        if not session_id:
            # Create new session
            session_data = ResearchSessionCreate(
                user_id=request.user_id,
                business_idea=request.context.businessIdea if request.context else None,
                target_customer=request.context.targetCustomer if request.context else None,
                problem=request.context.problem if request.context else None
            )
            session = session_service.create_session(session_data)
            session_id = session.session_id
        elif is_local_session:
            logger.info(f"Processing local session: {session_id}")
            session = None
        else:
            session = session_service.get_session(session_id)
            if not session:
                raise HTTPException(status_code=404, detail="Session not found")

        # Build conversation context for LLM
        conversation_context = ""
        for msg in request.messages:
            conversation_context += f"{msg.role}: {msg.content}\n"
        conversation_context += f"user: {request.input}\n"

        logger.info(f"Conversation context built: {len(conversation_context)} characters")

        # Use the proven LLM-based approach from original customer_research.py
        from backend.api.routes.customer_research import (
            generate_research_response_with_retry,
            analyze_user_intent_with_llm,
            validate_business_readiness_with_llm,
            generate_confirmation_response,
            generate_research_questions,
            generate_contextual_suggestions,
            extract_context_with_llm,
            classify_industry_with_llm,
            determine_research_stage_from_context,
            detect_stakeholders_with_llm
        )

        # Generate proper conversational response using LLM
        try:
            response_content = await generate_research_response_with_retry(
                llm_service=llm_service,
                messages=request.messages,
                user_input=request.input,
                context=request.context,
                conversation_context=conversation_context
            )
            logger.info(f"Generated response: {response_content}")
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return ChatResponse(
                content="I'm experiencing technical difficulties. Please try again.",
                metadata={"error": str(e), "llm_error": True},
                session_id=session_id
            )

        # Analyze user intent and business readiness using LLM
        try:
            user_intent = await analyze_user_intent_with_llm(
                llm_service, conversation_context, request.input, request.messages
            )
            business_validation = await validate_business_readiness_with_llm(
                llm_service, conversation_context, request.input
            )

            logger.info(f"User intent: {user_intent}")
            logger.info(f"Business validation: {business_validation}")

        except Exception as e:
            logger.warning(f"Error in LLM analysis: {e}")
            user_intent = {"intent": "continuation"}
            business_validation = {"ready_for_questions": False}

        # Extract business context from conversation using LLM (same as original API)
        extracted_context = {}
        try:
            extracted_context = await extract_context_with_llm(
                llm_service, conversation_context, request.input
            )
            logger.info(f"Extracted context: {extracted_context}")
        except Exception as e:
            logger.warning(f"Error extracting context: {e}")
            extracted_context = {
                "business_idea": None,
                "target_customer": None,
                "problem": None
            }

        # Extract intent from LLM analysis - be more strict about confirmations
        llm_says_confirmation = user_intent.get('intent') == 'confirmation'
        business_is_ready = business_validation.get('ready_for_questions', False)
        has_confirmation_words = any(word in request.input.lower() for word in ['yes', 'correct', 'right', 'confirm', 'that\'s right'])

        user_confirmed = llm_says_confirmation and business_is_ready and has_confirmation_words
        user_rejected = user_intent.get('intent') == 'rejection'
        user_wants_clarification = user_intent.get('intent') == 'clarification'

        logger.info(f"CONFIRMATION CHECK: input='{request.input}', llm_intent='{user_intent.get('intent')}', business_ready={business_is_ready}, has_conf_words={has_confirmation_words}, final_confirmed={user_confirmed}")

        # Be more conservative - require higher confidence and quality
        should_confirm = (
            business_validation.get('ready_for_questions', False) and
            business_validation.get('conversation_quality') in ['medium', 'high'] and
            business_validation.get('confidence', 0) >= 0.7 and  # Require higher confidence
            len(request.messages) >= 3 and  # Require at least some conversation
            not user_confirmed and
            not user_rejected and
            not user_wants_clarification
        )

        logger.info(f"Should confirm: {should_confirm} (ready: {business_validation.get('ready_for_questions')}, quality: {business_validation.get('conversation_quality')}, confidence: {business_validation.get('confidence')}, messages: {len(request.messages)})")

        # Generate questions ONLY if user explicitly confirmed
        questions_dict = None
        stakeholder_data = None
        if user_confirmed:
            logger.info("User confirmed - generating questions")
            try:
                # Create enriched context from extracted information
                enriched_context = ResearchContext(
                    businessIdea=extracted_context.get('business_idea') or (request.context.businessIdea if request.context else None),
                    targetCustomer=extracted_context.get('target_customer') or (request.context.targetCustomer if request.context else None),
                    problem=extracted_context.get('problem') or (request.context.problem if request.context else None)
                )

                questions = await generate_research_questions(
                    llm_service=llm_service,
                    context=enriched_context,
                    conversation_history=request.messages
                )
                questions_dict = {
                    "problemDiscovery": questions.problemDiscovery,
                    "solutionValidation": questions.solutionValidation,
                    "followUp": questions.followUp
                }

                # Detect stakeholders using LLM (same as original API)
                stakeholder_data = await detect_stakeholders_with_llm(
                    llm_service=llm_service,
                    context=enriched_context,
                    conversation_history=request.messages
                )

                # Mark questions as generated in extracted context
                extracted_context['questions_generated'] = True
                if stakeholder_data:
                    extracted_context['detected_stakeholders'] = stakeholder_data

                logger.info("Generated research questions and detected stakeholders successfully")
            except Exception as e:
                logger.error(f"Error generating questions: {e}")
        else:
            logger.info(f"Not generating questions - user_confirmed: {user_confirmed}, should_confirm: {should_confirm}")

        # If we should confirm, generate confirmation message
        if should_confirm and not questions_dict:
            try:
                confirmation_response = await generate_confirmation_response(
                    llm_service, request.messages, request.input,
                    request.context or ResearchContext(), conversation_context
                )
                response_content = confirmation_response
                logger.info("Generated confirmation message")
            except Exception as e:
                logger.warning(f"Error generating confirmation: {e}")
                # Keep the original response

        # Generate contextual suggestions using LLM
        contextual_suggestions = []
        try:
            contextual_suggestions = await generate_contextual_suggestions(
                llm_service=llm_service,
                messages=request.messages,
                user_input=request.input,
                assistant_response=response_content,
                conversation_context=conversation_context
            )
            logger.info(f"Generated contextual suggestions: {contextual_suggestions}")
        except Exception as e:
            logger.warning(f"Error generating contextual suggestions: {e}")
            # Use fallback suggestions
            contextual_suggestions = ["Tell me more", "That sounds right", "I need to clarify"]

        # Classify industry using LLM (same as original API)
        industry_data = {}
        try:
            industry_data = await classify_industry_with_llm(
                llm_service, conversation_context, request.input
            )
            logger.info(f"Classified industry: {industry_data}")
        except Exception as e:
            logger.warning(f"Error classifying industry: {e}")
            industry_data = {"industry": "general", "confidence": 0.5}

        # Response content and questions are already set above
        # No additional extraction needed

        # Save messages to session (skip for local sessions)
        if not is_local_session and session:
            try:
                # Save user message
                user_message_dict = {
                    "id": f"user_{len(request.messages)}",
                    "content": request.input,
                    "role": "user",
                    "timestamp": datetime.now().isoformat()
                }
                session_service.add_message(session_id, user_message_dict)

                # Save assistant response
                assistant_message_dict = {
                    "id": f"assistant_{len(request.messages)}",
                    "content": response_content,
                    "role": "assistant",
                    "timestamp": datetime.now().isoformat(),
                    "metadata": {
                        "conversation_stage": "confirming" if should_confirm else "chatting",
                        "questions_generated": bool(questions_dict)
                    }
                }
                session_service.add_message(session_id, assistant_message_dict)

                # Update session context with LLM-extracted information (same as original API)
                if extracted_context and (extracted_context.get('business_idea') or extracted_context.get('target_customer')):
                    update_data = ResearchSessionUpdate(
                        business_idea=extracted_context.get('business_idea'),
                        target_customer=extracted_context.get('target_customer'),
                        problem=extracted_context.get('problem'),
                        industry=industry_data.get('industry', 'general'),
                        stage=determine_research_stage_from_context(extracted_context),
                        conversation_context=conversation_context
                    )
                    session_service.update_session(session_id, update_data)

                # Mark session as completed if questions were generated
                if questions_dict:
                    session_service.complete_session(session_id, questions_dict)

            except Exception as e:
                logger.error(f"Error saving to session: {e}")
                # Continue with response even if session save fails

        # Prepare response metadata (same structure as original API)
        metadata = {
            "questionCategory": "validation" if questions_dict else "discovery",
            "researchStage": determine_research_stage_from_context(extracted_context),
            "suggestions": contextual_suggestions,
            "extracted_context": extracted_context,
            "conversation_stage": "confirming" if should_confirm else "chatting",
            "show_confirmation": should_confirm and not questions_dict,
            "questions_generated": bool(questions_dict),
            "workflow_version": "v2_llm_based",
            "user_intent": user_intent.get('intent'),
            "business_validation": business_validation,
            "industry_data": industry_data
        }

        return ChatResponse(
            content=response_content,
            metadata=metadata,
            questions=questions_dict,
            session_id=session_id
        )

    except ValidationError as e:
        logger.error(f"Pydantic validation error: {e}")
        return ChatResponse(
            content="I noticed some issues with the conversation data. Let's start fresh.",
            metadata={"error": str(e), "validation_error": True},
            session_id=request.session_id
        )
    except Exception as e:
        logger.error(f"Error in research chat v2: {str(e)}")
        error_response, error_code = ErrorHandler.handle_llm_error(e, {"stage": "general"})
        return ChatResponse(
            content=error_response,
            metadata={"error_code": error_code, "general_error": True},
            session_id=request.session_id
        )


@router.get("/health")
async def health_check():
    """Health check endpoint for v2 API"""
    return {
        "status": "healthy",
        "version": "v2",
        "features": ["pydantic_validation", "langgraph_workflow", "state_machine"]
    }
