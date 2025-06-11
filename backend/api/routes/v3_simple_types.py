"""
Type definitions for Customer Research API v3 Simplified.

This module contains all Pydantic models, dataclasses, and type definitions
used by the V3 Simple customer research system.

Extracted from customer_research_v3_simple.py for better modularity.
"""

import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from pydantic import BaseModel, Field


@dataclass
class SimplifiedConfig:
    """Simplified configuration for V3 research service."""

    # Feature flags
    enable_industry_analysis: bool = True
    enable_stakeholder_detection: bool = True
    enable_enhanced_context: bool = True
    enable_conversation_flow: bool = True
    enable_thinking_process: bool = True

    # Performance settings
    enable_caching: bool = True
    cache_ttl_seconds: int = 300  # 5 minutes
    request_timeout_seconds: int = 30

    # Quality settings
    min_confidence_threshold: float = 0.6
    enable_quality_checks: bool = True

    # Fallback settings
    enable_v1_fallback: bool = False  # Disable V1 fallback to force V3 to work
    max_retries: int = 2

    # Memory management
    max_thinking_steps: int = 20
    max_metrics_history: int = 100


@dataclass
class RequestMetrics:
    """Metrics for a single request."""

    request_id: str
    start_time: float = field(default_factory=time.time)
    end_time: float = 0.0

    # Component timings (ms)
    context_analysis_ms: int = 0
    intent_analysis_ms: int = 0
    business_validation_ms: int = 0
    industry_analysis_ms: int = 0
    stakeholder_detection_ms: int = 0
    conversation_flow_ms: int = 0
    response_generation_ms: int = 0

    # Quality metrics
    confidence_scores: Dict[str, float] = field(default_factory=dict)
    cache_hits: int = 0
    cache_misses: int = 0

    # Error tracking
    errors_encountered: List[str] = field(default_factory=list)
    fallback_used: bool = False

    @property
    def total_duration_ms(self) -> int:
        """Calculate total duration in milliseconds."""
        if self.end_time > 0:
            return int((self.end_time - self.start_time) * 1000)
        return int((time.time() - self.start_time) * 1000)

    @property
    def success_rate(self) -> float:
        """Calculate success rate based on errors."""
        total_operations = 7  # Number of main operations
        failed_operations = len(self.errors_encountered)
        return max(0.0, (total_operations - failed_operations) / total_operations)


class Message(BaseModel):
    id: str
    content: str
    role: str  # 'user' or 'assistant'
    timestamp: str
    metadata: Optional[Dict[str, Any]] = None


class ResearchContext(BaseModel):
    businessIdea: Optional[str] = None
    targetCustomer: Optional[str] = None
    problem: Optional[str] = None
    stage: Optional[str] = None
    questionsGenerated: Optional[bool] = None
    multiStakeholderConsidered: Optional[bool] = None
    multiStakeholderDetected: Optional[bool] = None
    detectedStakeholders: Optional[Dict[str, Any]] = None


class ChatRequest(BaseModel):
    messages: List[Message]
    input: str
    context: Optional[ResearchContext] = None
    session_id: Optional[str] = None
    user_id: Optional[str] = None

    # V3 Simple options
    enable_enhanced_analysis: bool = Field(default=True, description="Enable enhanced analysis features")
    enable_thinking_process: bool = Field(default=True, description="Enable thinking process tracking")


class ChatResponse(BaseModel):
    content: str
    metadata: Optional[Dict[str, Any]] = None
    questions: Optional[Any] = None  # Support any format - simple, comprehensive, or custom
    session_id: Optional[str] = None
    thinking_process: Optional[List[Dict[str, Any]]] = None
    performance_metrics: Optional[Dict[str, Any]] = None
    api_version: str = Field(default="v3-simple")


class HealthResponse(BaseModel):
    status: str
    version: str
    features: List[str]
    performance: Dict[str, Any]
    timestamp: str


class GenerateQuestionsRequest(BaseModel):
    context: ResearchContext
    conversationHistory: List[Message]


class ResearchQuestions(BaseModel):
    problemDiscovery: List[str]
    solutionValidation: List[str]
    followUp: List[str]
