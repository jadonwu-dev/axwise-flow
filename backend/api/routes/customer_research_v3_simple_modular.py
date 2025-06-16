"""
Customer Research API v3 Simplified - Modular Version

This is the new modular version of the V3 Simple customer research API.
All functionality has been split into separate modules for better maintainability.

Modules:
- v3_simple_types.py: Type definitions and Pydantic models
- v3_simple_service.py: Core service class and orchestration
- v3_simple_analysis.py: Analysis functions (context, intent, business, industry, stakeholders, flow)
- v3_simple_questions.py: Question generation and response creation
- v3_simple_handlers.py: FastAPI route handlers
- v3_simple_utils.py: Utility functions

This file serves as the main entry point that sets up the FastAPI router
and connects all the modular components.
"""

import logging
from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from backend.database import get_db

# Import all types
from .v3_simple_types import (
    ChatRequest, ChatResponse, HealthResponse,
    GenerateQuestionsRequest, ResearchQuestions
)

# Import all handlers
from .v3_simple_handlers import (
    chat_v3_simple,
    get_thinking_progress,
    health_check,
    generate_questions_v3_simple,
    get_research_sessions_v3_simple
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/research/v3-simple",
    tags=["Customer Research V3 Simple - Modular"],
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"}
    }
)

# API Endpoints - All handlers are imported from v3_simple_handlers.py

@router.post("/chat")
async def chat_endpoint(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    V3 Simplified customer research chat endpoint.

    This endpoint provides all V3 enhanced features with V1/V2 stability:
    - Enhanced context extraction and analysis
    - Industry classification and stakeholder detection
    - Intelligent conversation flow management
    - Smart caching and performance optimization
    - Comprehensive thinking process tracking
    - Robust error handling with V1 fallback
    """
    return await chat_v3_simple(request, background_tasks, db)


@router.get("/thinking-progress/{request_id}")
async def thinking_progress_endpoint(request_id: str):
    """Get current thinking process steps for progressive updates."""
    return await get_thinking_progress(request_id)


@router.get("/health", response_model=HealthResponse)
async def health_endpoint():
    """Health check endpoint for V3 Simplified API."""
    return await health_check()


@router.post("/generate-questions", response_model=ResearchQuestions)
async def generate_questions_endpoint(
    request: GenerateQuestionsRequest,
    db: Session = Depends(get_db)
):
    """
    Generate research questions based on context and conversation history.
    V3 Simple version with enhanced capabilities.
    """
    return await generate_questions_v3_simple(request, db)


@router.get("/sessions")
async def sessions_endpoint(
    user_id: str = None,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get research sessions for dashboard (V3 Simple version)."""
    return await get_research_sessions_v3_simple(user_id, limit, db)


# Module Information
__version__ = "3.0.0-modular"
__description__ = "Customer Research API v3 Simplified - Modular Architecture"
__modules__ = [
    "v3_simple_types",
    "v3_simple_service",
    "v3_simple_analysis",
    "v3_simple_questions",
    "v3_simple_handlers",
    "v3_simple_utils"
]

logger.info(f"Loaded Customer Research V3 Simple Modular API {__version__}")
logger.info(f"Modules: {', '.join(__modules__)}")


# Health check for modular system
def check_modular_health():
    """Check if all modular components are properly loaded."""
    try:
        # Test imports
        from . import v3_simple_types
        from . import v3_simple_service
        from . import v3_simple_analysis
        from . import v3_simple_questions
        from . import v3_simple_handlers
        from . import v3_simple_utils

        # Test core functionality
        from .v3_simple_service import SimplifiedResearchService
        from .v3_simple_types import SimplifiedConfig

        # Create test service
        config = SimplifiedConfig()
        service = SimplifiedResearchService(config)

        logger.info("✅ All modular components loaded successfully")
        return True

    except Exception as e:
        logger.error(f"❌ Modular health check failed: {e}")
        return False


# Run health check on import
if check_modular_health():
    logger.info("🎉 V3 Simple Modular API is ready!")
else:
    logger.warning("⚠️ V3 Simple Modular API has issues - check logs")
