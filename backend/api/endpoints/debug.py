"""
Debug API Endpoint

This module provides endpoints for debugging the application.
"""

from fastapi import APIRouter, HTTPException, Request, Depends
from sqlalchemy.orm import Session
import logging
import json
from typing import Dict, Any, List, Optional

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Import after router creation to avoid circular imports
from backend.database import get_db
from backend.models import User, AnalysisResult
from backend.services.external.auth_middleware import get_current_user
from backend.services.processing.persona_formation_service import PersonaFormationService
from backend.services.llm import LLMServiceFactory
from backend.services.processing.attribute_extractor import AttributeExtractor
from backend.services.processing.evidence_linking_service import EvidenceLinkingService
from backend.services.processing.trait_formatting_service import TraitFormattingService
from backend.services.processing.persona_builder import PersonaBuilder, persona_to_dict

@router.post(
    "/debug/persona",
    tags=["Debug"],
    summary="Debug persona generation",
    description="Generate a persona from text and return detailed debug information",
)
async def debug_persona_generation(
    request: Request,
    text: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Debug endpoint for persona generation.
    
    This endpoint generates a persona from text and returns detailed debug information
    about the persona generation process, including the intermediate data structures.
    """
    try:
        # Initialize services
        llm_service = LLMServiceFactory.create("gemini")
        attribute_extractor = AttributeExtractor(llm_service)
        persona_builder = PersonaBuilder()
        
        # Extract attributes
        logger.info("Extracting attributes from text")
        attributes = await attribute_extractor.extract_attributes_from_text(text, "Interviewee")
        
        # Log attribute keys
        logger.info(f"Extracted attribute keys: {list(attributes.keys())}")
        
        # Check for evidence in attributes
        evidence_counts = {}
        for key, value in attributes.items():
            if isinstance(value, dict) and "evidence" in value:
                evidence_counts[key] = len(value["evidence"])
        
        logger.info(f"Evidence counts in attributes: {evidence_counts}")
        
        # Build persona
        logger.info("Building persona from attributes")
        persona = persona_builder.build_persona_from_attributes(attributes, role="Interviewee")
        
        # Convert persona to dict
        persona_dict = persona_to_dict(persona)
        
        # Check for evidence in persona dict
        persona_evidence_counts = {}
        for key, value in persona_dict.items():
            if isinstance(value, dict) and "evidence" in value:
                persona_evidence_counts[key] = len(value["evidence"])
        
        logger.info(f"Evidence counts in persona dict: {persona_evidence_counts}")
        
        # Return debug information
        return {
            "success": True,
            "message": "Debug persona generation completed",
            "attributes": attributes,
            "persona": persona_dict,
            "evidence_counts": {
                "attributes": evidence_counts,
                "persona": persona_evidence_counts
            }
        }
    
    except Exception as e:
        logger.error(f"Error in debug persona generation: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error in debug persona generation: {str(e)}")
