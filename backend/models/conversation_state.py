"""
Pydantic models for customer research conversation state.
Used with LangGraph for type-safe state management.
"""

from enum import Enum
from typing import Annotated, Optional, Dict, Any, List, Literal
from pydantic import BaseModel, Field, validator
from datetime import datetime
import operator


class ConversationStage(str, Enum):
    """Conversation stages for customer research flow"""

    GATHERING_INFO = "gathering_info"
    READY_FOR_CONFIRMATION = "ready_for_confirmation"
    AWAITING_CONFIRMATION = "awaiting_confirmation"
    GENERATING_QUESTIONS = "generating_questions"
    COMPLETED = "completed"
    ERROR = "error"


class UserIntent(str, Enum):
    """User intent types"""

    CONFIRMATION = "confirmation"
    REJECTION = "rejection"
    CLARIFICATION = "clarification"
    CONTINUATION = "continuation"
    UNKNOWN = "unknown"


class ConversationQuality(str, Enum):
    """Conversation quality levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Message(BaseModel):
    """Structured message with validation"""

    id: str
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = None

    @validator("content")
    def validate_content(cls, v):
        if not v or not v.strip():
            raise ValueError("Message content cannot be empty")
        return v.strip()


class BusinessContext(BaseModel):
    """Validated business context"""

    business_idea: Optional[str] = None
    target_customer: Optional[str] = None
    problem_statement: Optional[str] = None
    industry: Optional[str] = None
    additional_details: Dict[str, Any] = Field(default_factory=dict)

    @validator("business_idea")
    def validate_business_idea(cls, v):
        if v and len(v.strip()) < 5:
            raise ValueError("Business idea must be at least 5 characters")
        return v.strip() if v else None

    @validator("target_customer")
    def validate_target_customer(cls, v):
        if v and len(v.strip()) < 3:
            raise ValueError("Target customer must be at least 3 characters")
        return v.strip() if v else None

    def is_complete(self) -> bool:
        """Check if business context has sufficient information"""
        return bool(self.business_idea and self.target_customer)

    def get_completion_score(self) -> float:
        """Get completion score (0.0 to 1.0)"""
        fields = [self.business_idea, self.target_customer, self.problem_statement]
        completed = sum(1 for field in fields if field)
        return completed / len(fields)


class LLMValidation(BaseModel):
    """LLM validation result with strong typing"""

    ready_for_questions: bool = False
    conversation_quality: ConversationQuality = ConversationQuality.LOW
    confidence_score: float = Field(ge=0.0, le=1.0, default=0.0)
    missing_elements: List[str] = Field(default_factory=list)
    reasoning: Optional[str] = None

    @validator("confidence_score")
    def validate_confidence(cls, v):
        return max(0.0, min(1.0, v))  # Clamp between 0 and 1


class IntentAnalysis(BaseModel):
    """User intent analysis with validation"""

    intent: UserIntent = UserIntent.UNKNOWN
    confidence: float = Field(ge=0.0, le=1.0, default=0.0)
    reasoning: Optional[str] = None
    extracted_info: Dict[str, Any] = Field(default_factory=dict)


class ResearchQuestion(BaseModel):
    """Individual research question with metadata"""

    question: str
    priority: Literal["high", "medium", "low"] = "medium"
    category: Literal["problem_discovery", "solution_validation", "follow_up"] = (
        "problem_discovery"
    )

    @validator("question")
    def validate_question(cls, v):
        if not v or not v.strip():
            raise ValueError("Question cannot be empty")
        return v.strip()


class ResearchQuestions(BaseModel):
    """Generated research questions with validation"""

    problem_discovery: List[ResearchQuestion] = Field(default_factory=list)
    solution_validation: List[ResearchQuestion] = Field(default_factory=list)
    follow_up: List[ResearchQuestion] = Field(default_factory=list)

    def to_legacy_format(self) -> Dict[str, List[str]]:
        """Convert to legacy format for API compatibility"""
        return {
            "problemDiscovery": [q.question for q in self.problem_discovery],
            "solutionValidation": [q.question for q in self.solution_validation],
            "followUp": [q.question for q in self.follow_up],
        }


class Stakeholder(BaseModel):
    """Stakeholder information with validation"""

    name: str
    role: str
    priority: Literal["high", "medium", "low"] = "medium"
    description: Optional[str] = None

    @validator("name", "role")
    def validate_required_fields(cls, v):
        if not v or not v.strip():
            raise ValueError("Name and role are required")
        return v.strip()


class StakeholderAnalysis(BaseModel):
    """Stakeholder analysis result"""

    primary: List[Stakeholder] = Field(default_factory=list)
    secondary: List[Stakeholder] = Field(default_factory=list)
    industry: str = "general"
    reasoning: Optional[str] = None


# LangGraph State Schema using Pydantic
class CustomerResearchState(BaseModel):
    """
    LangGraph state schema with Pydantic validation
    This is the core state that flows through the entire workflow
    """

    # Core conversation data
    messages: Annotated[List[Message], operator.add] = Field(default_factory=list)
    business_context: BusinessContext = Field(default_factory=BusinessContext)
    conversation_stage: ConversationStage = ConversationStage.GATHERING_INFO

    # User interaction flags
    user_confirmed: bool = False
    user_rejected: bool = False
    user_wants_clarification: bool = False

    # LLM analysis results
    last_validation: Optional[LLMValidation] = None
    last_intent_analysis: Optional[IntentAnalysis] = None

    # Generated content
    research_questions: Optional[ResearchQuestions] = None
    stakeholder_analysis: Optional[StakeholderAnalysis] = None

    # Error handling
    error_count: int = 0
    last_error: Optional[str] = None

    # Loop prevention
    gather_info_count: int = 0
    validation_count: int = 0

    # Metadata
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        # Allow LangGraph to work with this model
        arbitrary_types_allowed = True
        # Enable field updates
        validate_assignment = True

    def add_message(
        self, role: str, content: str, metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Add a message and return state update"""
        message = Message(
            id=f"{role}_{len(self.messages)}",
            role=role,
            content=content,
            metadata=metadata,
        )
        return {"messages": [message], "updated_at": datetime.now()}

    def update_business_context(self, **kwargs) -> Dict[str, Any]:
        """Update business context and return state update"""
        current_data = self.business_context.model_dump()
        current_data.update(kwargs)
        new_context = BusinessContext(**current_data)

        return {"business_context": new_context, "updated_at": datetime.now()}

    def transition_to_stage(
        self, new_stage: ConversationStage, reason: str = None
    ) -> Dict[str, Any]:
        """Transition to new stage and return state update"""
        return {"conversation_stage": new_stage, "updated_at": datetime.now()}

    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get conversation history in simple format for LLM"""
        return [{"role": msg.role, "content": msg.content} for msg in self.messages]

    def should_generate_questions(self) -> bool:
        """Check if ready to generate questions"""
        return (
            self.conversation_stage == ConversationStage.GENERATING_QUESTIONS
            and self.user_confirmed
            and self.business_context.is_complete()
        )

    def should_show_confirmation(self) -> bool:
        """Check if should show confirmation"""
        return self.conversation_stage == ConversationStage.AWAITING_CONFIRMATION

    def is_completed(self) -> bool:
        """Check if conversation is completed"""
        return self.conversation_stage == ConversationStage.COMPLETED

    def get_api_response_format(self) -> Dict[str, Any]:
        """Convert to API response format"""
        return {
            "content": self.messages[-1].content if self.messages else "",
            "questions": (
                self.research_questions.to_legacy_format()
                if self.research_questions
                else None
            ),
            "stakeholders": (
                self.stakeholder_analysis.model_dump()
                if self.stakeholder_analysis
                else None
            ),
            "session_id": self.session_id,
            "metadata": {
                "conversation_stage": self.conversation_stage.value,
                "business_context": self.business_context.model_dump(),
                "completion_score": self.business_context.get_completion_score(),
                "error_count": self.error_count,
                "show_confirmation": self.should_show_confirmation(),
            },
        }
