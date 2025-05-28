"""
Research Session Models for Customer Research Feature
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

Base = declarative_base()

class ResearchSession(Base):
    """Database model for research sessions."""
    
    __tablename__ = "research_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)  # From Clerk auth when implemented
    session_id = Column(String, unique=True, index=True)
    
    # Business context
    business_idea = Column(Text)
    target_customer = Column(Text)
    problem = Column(Text)
    industry = Column(String, default="general")
    
    # Session metadata
    stage = Column(String, default="initial")  # initial, business_idea, target_customer, validation, completed
    status = Column(String, default="active")  # active, completed, abandoned
    
    # Conversation data
    messages = Column(JSON)  # List of message objects
    conversation_context = Column(Text)
    
    # Generated questions
    questions_generated = Column(Boolean, default=False)
    research_questions = Column(JSON)  # ResearchQuestions object
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    exports = relationship("ResearchExport", back_populates="session")

class ResearchExport(Base):
    """Database model for research exports."""
    
    __tablename__ = "research_exports"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("research_sessions.session_id"))
    
    export_type = Column(String)  # pdf, csv, email
    export_format = Column(String)  # detailed, summary, questions_only
    file_path = Column(String, nullable=True)  # For file exports
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session = relationship("ResearchSession", back_populates="exports")

# Pydantic models for API
class ResearchSessionCreate(BaseModel):
    user_id: Optional[str] = None
    business_idea: Optional[str] = None
    target_customer: Optional[str] = None
    problem: Optional[str] = None

class ResearchSessionUpdate(BaseModel):
    business_idea: Optional[str] = None
    target_customer: Optional[str] = None
    problem: Optional[str] = None
    industry: Optional[str] = None
    stage: Optional[str] = None
    status: Optional[str] = None
    messages: Optional[List[Dict[str, Any]]] = None
    conversation_context: Optional[str] = None
    questions_generated: Optional[bool] = None
    research_questions: Optional[Dict[str, Any]] = None

class ResearchSessionResponse(BaseModel):
    id: int
    session_id: str
    user_id: Optional[str]
    business_idea: Optional[str]
    target_customer: Optional[str]
    problem: Optional[str]
    industry: str
    stage: str
    status: str
    questions_generated: bool
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class ResearchSessionSummary(BaseModel):
    """Summary model for dashboard display."""
    id: int
    session_id: str
    business_idea: Optional[str]
    industry: str
    stage: str
    status: str
    questions_generated: bool
    created_at: datetime
    message_count: int
    
    class Config:
        from_attributes = True
