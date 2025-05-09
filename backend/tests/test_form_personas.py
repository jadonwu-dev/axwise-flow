"""
Test script for the form_personas method.

This script tests the form_personas method in the PersonaFormationService class.
"""

import sys
import os
import logging
import json
import asyncio

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the parent directory to the Python path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Import the necessary modules
from services.processing.persona_formation_service import PersonaFormationService

# Create a mock LLM service
class MockLLMService:
    """Mock LLM service for testing."""

    async def analyze(self, request):
        """Mock analyze method."""
        logger.info(f"Mock LLM service called with task: {request.get('task')}")

        # Return a mock response based on the task
        if request.get("task") == "persona_formation":
            return {
                "name": "Pattern-Based Persona",
                "description": "A persona generated from patterns",
                "role_context": {
                    "value": "Works in a structured environment",
                    "confidence": 0.8,
                    "evidence": ["Evidence from patterns"]
                },
                "key_responsibilities": {
                    "value": "Validates information from multiple sources",
                    "confidence": 0.7,
                    "evidence": ["Evidence from patterns"]
                },
                "tools_used": {
                    "value": "Research tools and validation frameworks",
                    "confidence": 0.6,
                    "evidence": ["Evidence from patterns"]
                },
                "collaboration_style": {
                    "value": "Collaborative with verification steps",
                    "confidence": 0.7,
                    "evidence": ["Evidence from patterns"]
                },
                "analysis_approach": {
                    "value": "Thorough and methodical",
                    "confidence": 0.8,
                    "evidence": ["Evidence from patterns"]
                },
                "pain_points": {
                    "value": "Time-consuming validation processes",
                    "confidence": 0.7,
                    "evidence": ["Evidence from patterns"]
                }
            }

        # Default response
        return {"error": "Unknown task"}

async def test_form_personas():
    """Test the form_personas method."""
    try:
        # Create a mock LLM service
        llm_service = MockLLMService()

        # Create a mock config
        class MockConfig:
            def __init__(self):
                self.validation = type("obj", (object,), {"min_confidence": 0.4})
                self.llm = type("obj", (object,), {"provider": "test", "model": "test-model"})

        # Create PersonaFormationService
        persona_service = PersonaFormationService(MockConfig(), llm_service)

        # Create mock patterns
        patterns = [
            {
                "name": "Multi-source Validation",
                "category": "Workflow",
                "description": "Users repeatedly check multiple sources before making decisions",
                "frequency": 0.65,
                "sentiment": -0.3,
                "evidence": [
                    "I always check multiple sources first, then validate with our own research, before presenting options",
                    "We go through a three-step validation process: first check best practices, then look at competitors, then test with users"
                ],
                "impact": "Slows down decision-making but improves quality",
                "suggested_actions": [
                    "Streamline validation process",
                    "Create a centralized knowledge base"
                ]
            }
        ]

        # Call form_personas
        logger.info("Calling form_personas...")
        personas = await persona_service.form_personas(patterns)

        # Check results
        if personas and len(personas) > 0:
            logger.info(f"Successfully formed {len(personas)} personas")
            logger.info(f"First persona: {json.dumps(personas[0], indent=2)}")
            return True
        else:
            logger.error("No personas formed")
            return False

    except Exception as e:
        logger.error(f"Error in test_form_personas: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_form_personas())
