"""
Conversation Routines API Router
Implements the 2025 Conversation Routines framework endpoint
"""

import logging
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from .service import ConversationRoutineService
from .models import ConversationRoutineRequest, ConversationRoutineResponse
from backend.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/research/conversation-routines", tags=["Conversation Routines"]
)

# Initialize service
conversation_service = ConversationRoutineService()


@router.post("/chat", response_model=ConversationRoutineResponse)
async def conversation_routine_chat(
    request: ConversationRoutineRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Conversation Routines Chat Endpoint

    Implements the 2025 Conversation Routines framework for customer research.
    Uses single LLM call with embedded workflow logic instead of complex orchestration.

    Features:
    - Embedded business logic in natural language prompts
    - Context-driven flow decisions (no state machines)
    - Proactive transition to question generation
    - Maximum 6 exchanges before generating questions
    - Automatic user fatigue detection
    - Efficient stakeholder-based question generation
    """
    try:
        logger.info(f"🎯 Conversation Routines chat request: {request.input[:50]}...")

        # Process through conversation routine service
        response = await conversation_service.process_conversation(request)

        # TODO: Add session management in background task if needed
        # background_tasks.add_task(save_conversation_session, request, response, db)

        logger.info("✅ Conversation Routines chat completed successfully")
        return response

    except Exception as e:
        logger.error(f"🔴 Conversation Routines chat failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Conversation service temporarily unavailable: {str(e)}",
        )


@router.get("/health")
async def health_check():
    """Health check endpoint for conversation routines service"""
    try:
        # Basic service health check
        return {
            "status": "healthy",
            "service": "conversation-routines",
            "framework": "2025-conversation-routines",
            "features": [
                "embedded-workflow-logic",
                "context-driven-decisions",
                "proactive-transitions",
                "efficiency-optimization",
            ],
        }
    except Exception as e:
        logger.error(f"🔴 Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")


@router.post("/test")
async def test_conversation_routine():
    """Test endpoint for conversation routines functionality"""
    try:
        # Create test request
        test_request = ConversationRoutineRequest(
            input="I want to create a meal planning app for busy parents",
            messages=[],
            session_id="test-session",
        )

        # Process test conversation
        response = await conversation_service.process_conversation(test_request)

        return {
            "test_status": "success",
            "response_preview": (
                response.content[:100] + "..."
                if len(response.content) > 100
                else response.content
            ),
            "context_completeness": response.context.get_completeness_score(),
            "should_generate_questions": response.should_generate_questions,
            "suggestions_count": len(response.suggestions),
        }

    except Exception as e:
        logger.error(f"🔴 Test failed: {e}")
        raise HTTPException(status_code=500, detail=f"Test failed: {str(e)}")
