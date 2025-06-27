"""
Clean Research Router
Unified FastAPI router that replaces the monolithic endpoints.
"""

import logging
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.api.research.research_types import (
    ChatRequest,
    ChatResponse,
    ResearchQuestions,
)
from backend.api.research.research_orchestrator import ResearchOrchestrator

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/research",
    tags=["Customer Research - Modular V1+V3"],
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"},
    },
)

# Initialize orchestrator
orchestrator = ResearchOrchestrator()


@router.post("/chat", response_model=ChatResponse)
async def research_chat(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Customer Research Chat Endpoint

    Uses V1 core (proven & reliable) + V3 enhancements (intelligent & fail-safe).
    Always provides working functionality even if advanced features fail.

    Features:
    - V1 Core: Proven conversation analysis, response generation, question creation
    - V3 Enhancements: UX methodology, advanced stakeholder detection, enhanced suggestions
    - Fail-Safe Design: Automatic fallback to V1 if enhancements fail
    - Performance Optimized: Efficient LLM usage and response caching
    """
    try:
        logger.info(f"📞 Research chat request: {request.input[:50]}...")

        # Process request through orchestrator
        response = await orchestrator.process_chat_request(request)

        # TODO: Add session management in background task if needed
        # background_tasks.add_task(save_to_session, request, response, db)

        logger.info("✅ Research chat completed successfully")
        return response

    except Exception as e:
        logger.error(f"🔴 Research chat failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Research chat service temporarily unavailable: {str(e)}",
        )


@router.post("/questions", response_model=ResearchQuestions)
async def generate_questions(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Generate Research Questions Endpoint

    Creates comprehensive research questions based on conversation context.
    Uses V1 core question generation + V3 advanced stakeholder detection.
    """
    try:
        logger.info("🎯 Research questions generation request")

        # Generate questions through orchestrator
        questions = await orchestrator.generate_questions(request)

        logger.info("✅ Research questions generated successfully")
        return questions

    except Exception as e:
        logger.error(f"🔴 Question generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Question generation service temporarily unavailable: {str(e)}",
        )


@router.get("/health")
async def health_check():
    """
    Health Check Endpoint

    Returns status of orchestrator and all components.
    """
    try:
        health_data = await orchestrator.health_check()
        return health_data

    except Exception as e:
        logger.error(f"🔴 Health check failed: {e}")
        return {"status": "error", "service": "research_router", "error": str(e)}


@router.get("/stats")
async def get_stats():
    """
    Get Orchestrator Statistics

    Returns information about the modular architecture and components.
    """
    try:
        stats = orchestrator.get_orchestrator_stats()
        return stats

    except Exception as e:
        logger.error(f"🔴 Stats retrieval failed: {e}")
        return {"error": str(e), "service": "research_router"}


# TODO: Add these endpoints when session management is needed
# @router.get("/sessions")
# async def get_research_sessions(
#     user_id: Optional[str] = None,
#     limit: int = 20,
#     db: Session = Depends(get_db)
# ):
#     """Get research sessions for dashboard."""
#     pass

# @router.get("/sessions/{session_id}")
# async def get_research_session(
#     session_id: str,
#     db: Session = Depends(get_db)
# ):
#     """Get a specific research session."""
#     pass

# @router.delete("/sessions/{session_id}")
# async def delete_research_session(
#     session_id: str,
#     db: Session = Depends(get_db)
# ):
#     """Delete a specific research session."""
#     pass


# Module Information
__version__ = "1.0.0-modular"
__description__ = "Clean modular customer research API - V1 core + V3 enhancements"
__architecture__ = "v1_core_plus_v3_enhancements"


@router.post("/test-stakeholders")
async def test_stakeholders():
    """Simple test endpoint to verify stakeholder generation works"""
    try:
        from backend.api.research.v3_enhancements.stakeholder_detector import (
            StakeholderDetector,
        )
        from backend.services.llm import LLMServiceFactory

        logger.info("🧪 Testing stakeholder generation directly...")

        detector = StakeholderDetector()
        llm_service = LLMServiceFactory.create("gemini")

        # Test with explicit context
        context_analysis = {
            "business_idea": "Legacy API for database access",
            "target_customer": "developers and database administrators",
            "problem": "difficulty accessing data from outdated databases",
        }

        # Create mock messages
        messages = [
            type(
                "Message",
                (),
                {"role": "user", "content": "I want to develop Legacy API"},
            )(),
            type("Message", (), {"role": "assistant", "content": "Tell me more"})(),
            type(
                "Message",
                (),
                {
                    "role": "user",
                    "content": "It provides unified access to outdated databases",
                },
            )(),
        ]

        result = await detector.generate_dynamic_stakeholders_with_unique_questions(
            llm_service=llm_service,
            context_analysis=context_analysis,
            messages=messages,
            business_idea="Legacy API for database access",
            target_customer="developers and database administrators",
            problem="difficulty accessing data from outdated databases",
        )

        logger.info(f"🧪 Test result: {result}")

        return {
            "success": True,
            "stakeholders": result,
            "primary_count": len(result.get("primary", [])),
            "secondary_count": len(result.get("secondary", [])),
        }

    except Exception as e:
        logger.error(f"🧪 Test failed: {e}")
        import traceback

        logger.error(f"🧪 Test traceback: {traceback.format_exc()}")
        return {"success": False, "error": str(e), "traceback": traceback.format_exc()}


logger.info(f"🎯 Research Router loaded - {__description__} v{__version__}")
logger.info(f"🏗️ Architecture: {__architecture__}")
logger.info("✅ Modular research system ready!")
