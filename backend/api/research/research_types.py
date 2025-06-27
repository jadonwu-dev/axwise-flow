"""
Research Types and Models
Clean Pydantic models for the modular research system.
"""

from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime


class Message(BaseModel):
    """Chat message model"""

    id: Optional[str] = None
    content: str
    role: Literal["user", "assistant", "system"]
    timestamp: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ResearchContext(BaseModel):
    """Business context for research"""

    businessIdea: Optional[str] = None
    targetCustomer: Optional[str] = None
    problem: Optional[str] = None
    stage: Optional[str] = None
    questionsGenerated: Optional[bool] = None
    multiStakeholderConsidered: Optional[bool] = None
    multiStakeholderDetected: Optional[bool] = None
    detectedStakeholders: Optional[List[Dict[str, Any]]] = None


class ChatRequest(BaseModel):
    """Chat request model"""

    messages: List[Message]
    input: str
    context: Optional[ResearchContext] = None
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    enable_enhanced_analysis: bool = True
    enable_thinking_process: bool = False


class Stakeholder(BaseModel):
    """Stakeholder model"""

    name: str
    description: str
    questions: Dict[str, List[str]] = Field(
        default_factory=lambda: {
            "problemDiscovery": [],
            "solutionValidation": [],
            "followUp": [],
        },
        description="Categorized questions for this stakeholder",
    )


class StakeholderQuestions(BaseModel):
    """Pydantic model for stakeholder-specific questions - categorized format"""

    problemDiscovery: List[str] = Field(
        default_factory=list,
        max_items=5,
        description="Questions to understand current state and pain points",
    )
    solutionValidation: List[str] = Field(
        default_factory=list,
        max_items=5,
        description="Questions to validate the proposed solution approach",
    )
    followUp: List[str] = Field(
        default_factory=list,
        max_items=3,
        description="Questions for deeper insights and next steps",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "problemDiscovery": [
                    "How difficult is it for you to carry laundry to and from a laundromat?",
                    "What time of day do you typically do your laundry?",
                ],
                "solutionValidation": [
                    "How interested would you be in a pick-up and delivery service?",
                    "What concerns would you have about this service?",
                ],
                "followUp": ["Can you tell me more about your laundry routine?"],
            }
        }


class ResearchQuestions(BaseModel):
    """Generated research questions"""

    problemDiscovery: List[str] = []
    solutionValidation: List[str] = []
    followUp: List[str] = []
    stakeholders: Dict[str, List[Stakeholder]] = Field(
        default_factory=lambda: {"primary": [], "secondary": []}
    )
    estimatedTime: str = "25-43 minutes"


class ChatResponse(BaseModel):
    """Chat response model"""

    content: str
    metadata: Optional[Dict[str, Any]] = None
    questions: Optional[ResearchQuestions] = None
    suggestions: Optional[List[str]] = None
    session_id: Optional[str] = None
    api_version: str = "v1-v3-modular"
    processing_time_ms: Optional[int] = None


class AnalysisResult(BaseModel):
    """Analysis result from V1 core or V3 enhancements"""

    context_analysis: Dict[str, Any]
    intent_analysis: Dict[str, Any]
    business_validation: Dict[str, Any]
    user_confirmation: Optional[Dict[str, Any]] = None
    processing_time_ms: int = 0


class EnhancementResult(BaseModel):
    """Result from V3 enhancement application"""

    enhanced_response: Dict[str, Any]
    enhancements_applied: List[str]
    enhancement_failures: List[str] = []
    fallback_used: bool = False
