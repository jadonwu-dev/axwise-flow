from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel


class ConversationState(str, Enum):
    """Lightweight conversation states for customer research flow"""
    GATHERING_INFO = "gathering_info"
    READY_FOR_CONFIRMATION = "ready_for_confirmation" 
    AWAITING_CONFIRMATION = "awaiting_confirmation"
    GENERATING_QUESTIONS = "generating_questions"
    COMPLETED = "completed"
    ERROR = "error"


class StateTransition(BaseModel):
    """Simple state transition model"""
    from_state: ConversationState
    to_state: ConversationState
    condition_met: bool = False
    metadata: Optional[Dict[str, Any]] = None


class ConversationStateManager:
    """Lightweight state machine for conversation flow"""
    
    # Valid transitions - prevents invalid state changes
    VALID_TRANSITIONS = {
        ConversationState.GATHERING_INFO: [
            ConversationState.READY_FOR_CONFIRMATION,
            ConversationState.ERROR
        ],
        ConversationState.READY_FOR_CONFIRMATION: [
            ConversationState.AWAITING_CONFIRMATION,
            ConversationState.GATHERING_INFO,  # fallback
            ConversationState.ERROR
        ],
        ConversationState.AWAITING_CONFIRMATION: [
            ConversationState.GENERATING_QUESTIONS,  # user confirmed
            ConversationState.GATHERING_INFO,        # user rejected/wants to add
            ConversationState.ERROR
        ],
        ConversationState.GENERATING_QUESTIONS: [
            ConversationState.COMPLETED,
            ConversationState.ERROR
        ],
        ConversationState.COMPLETED: [
            ConversationState.GATHERING_INFO  # restart conversation
        ],
        ConversationState.ERROR: [
            ConversationState.GATHERING_INFO  # recovery
        ]
    }
    
    def __init__(self, initial_state: ConversationState = ConversationState.GATHERING_INFO):
        self.current_state = initial_state
        self.context = {}
    
    def can_transition_to(self, target_state: ConversationState) -> bool:
        """Check if transition is valid"""
        return target_state in self.VALID_TRANSITIONS.get(self.current_state, [])
    
    def transition_to(self, target_state: ConversationState, metadata: Optional[Dict] = None) -> bool:
        """Attempt to transition to target state"""
        if not self.can_transition_to(target_state):
            return False
            
        self.current_state = target_state
        if metadata:
            self.context.update(metadata)
        return True
    
    def get_current_state(self) -> ConversationState:
        """Get current state"""
        return self.current_state
    
    def is_in_state(self, state: ConversationState) -> bool:
        """Check if currently in specific state"""
        return self.current_state == state
    
    def get_valid_next_states(self) -> list[ConversationState]:
        """Get list of valid next states"""
        return self.VALID_TRANSITIONS.get(self.current_state, [])


# Helper functions for easy integration
def create_state_manager(initial_state: ConversationState = ConversationState.GATHERING_INFO) -> ConversationStateManager:
    """Factory function to create state manager"""
    return ConversationStateManager(initial_state)


def should_generate_questions(state: ConversationState) -> bool:
    """Helper to determine if questions should be generated"""
    return state == ConversationState.GENERATING_QUESTIONS


def should_show_confirmation(state: ConversationState) -> bool:
    """Helper to determine if confirmation should be shown"""
    return state == ConversationState.AWAITING_CONFIRMATION


def is_conversation_complete(state: ConversationState) -> bool:
    """Helper to check if conversation is complete"""
    return state == ConversationState.COMPLETED
