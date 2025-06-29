"""
Conversation Routines Package
Implements the 2025 Conversation Routines framework for customer research

Based on "Conversation Routines: A Prompt Engineering Framework for Task-Oriented Dialog Systems"
by Giorgio Robino (January 2025)
"""

from .service import ConversationRoutineService
from .models import (
    ConversationRoutineRequest,
    ConversationRoutineResponse,
    ConversationContext,
    ConversationMessage
)
from .router import router as conversation_routines_router

__all__ = [
    "ConversationRoutineService",
    "ConversationRoutineRequest", 
    "ConversationRoutineResponse",
    "ConversationContext",
    "ConversationMessage",
    "conversation_routines_router"
]
