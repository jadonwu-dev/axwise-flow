"""
Test the refactored persona formation service.
"""

import sys
import os
import logging
import json
import asyncio
from typing import Dict, Any, List

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the parent directory to the Python path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Import the refactored modules
from services.processing.persona_formation_service import PersonaFormationService
from services.processing.transcript_processor import TranscriptProcessor
from services.processing.attribute_extractor import AttributeExtractor
from services.processing.persona_builder import PersonaBuilder
from services.processing.prompts import PromptGenerator


class MockLLMService:
    """Mock LLM service for testing."""

    async def analyze(self, data: Dict[str, Any]) -> str:
        """Mock analyze method that returns a predefined response."""
        logger.info(f"MockLLMService.analyze called with task: {data.get('task')}")

        # Return a mock persona JSON
        return json.dumps({
            "name": "Test Persona",
            "description": "A test persona for unit testing",
            "archetype": "Test Subject",
            "demographics": {
                "value": "Test demographics",
                "confidence": 0.8,
                "evidence": ["Evidence 1", "Evidence 2"]
            },
            "goals_and_motivations": {
                "value": "Test goals",
                "confidence": 0.7,
                "evidence": ["Evidence 1", "Evidence 2"]
            },
            "skills_and_expertise": {
                "value": "Test skills",
                "confidence": 0.9,
                "evidence": ["Evidence 1", "Evidence 2"]
            },
            "role_context": {
                "value": "Test role context",
                "confidence": 0.8,
                "evidence": ["Evidence 1", "Evidence 2"]
            },
            "key_responsibilities": {
                "value": "Test responsibilities",
                "confidence": 0.7,
                "evidence": ["Evidence 1", "Evidence 2"]
            },
            "tools_used": {
                "value": "Test tools",
                "confidence": 0.6,
                "evidence": ["Evidence 1", "Evidence 2"]
            },
            "collaboration_style": {
                "value": "Test collaboration",
                "confidence": 0.7,
                "evidence": ["Evidence 1", "Evidence 2"]
            },
            "analysis_approach": {
                "value": "Test approach",
                "confidence": 0.8,
                "evidence": ["Evidence 1", "Evidence 2"]
            },
            "pain_points": {
                "value": "Test pain points",
                "confidence": 0.7,
                "evidence": ["Evidence 1", "Evidence 2"]
            },
            "patterns": ["Pattern 1", "Pattern 2"],
            "confidence": 0.8,
            "evidence": ["Overall evidence 1", "Overall evidence 2"]
        })


class MockConfig:
    """Mock configuration for testing."""

    def __init__(self):
        self.validation = type("obj", (object,), {"min_confidence": 0.4})
        self.llm = type("obj", (object,), {"provider": "test", "model": "test-model"})


async def test_persona_formation_service():
    """Test the PersonaFormationService."""
    try:
        # Create mock objects
        config = MockConfig()
        llm_service = MockLLMService()

        # Create the service
        service = PersonaFormationService(config, llm_service)

        # Test generating a persona from text
        text = """
        Interviewer: Tell me about your role.
        Interviewee: I'm a software developer working on web applications.
        Interviewer: What technologies do you use?
        Interviewee: I primarily use Python, JavaScript, and React.
        Interviewer: What challenges do you face?
        Interviewee: The biggest challenge is dealing with legacy code that's poorly documented.
        """

        personas = await service.generate_persona_from_text(text)

        # Check the result
        if personas and len(personas) > 0:
            logger.info(f"Successfully generated {len(personas)} personas")
            logger.info(f"First persona: {personas[0].get('name')}")
            return True
        else:
            logger.error("Failed to generate personas")
            return False

    except Exception as e:
        logger.error(f"Error testing persona formation service: {str(e)}", exc_info=True)
        return False


async def test_transcript_processor():
    """Test the TranscriptProcessor."""
    try:
        # Create the processor
        processor = TranscriptProcessor()

        # Test parsing a transcript
        text = """
        Interviewer: Tell me about your role.
        Interviewee: I'm a software developer working on web applications.
        Interviewer: What technologies do you use?
        Interviewee: I primarily use Python, JavaScript, and React.
        """

        structured_transcript = processor.parse_raw_transcript_to_structured(text)

        # Check the result
        if structured_transcript and len(structured_transcript) > 0:
            logger.info(f"Successfully parsed transcript with {len(structured_transcript)} entries")
            return True
        else:
            logger.error("Failed to parse transcript")
            return False

    except Exception as e:
        logger.error(f"Error testing transcript processor: {str(e)}", exc_info=True)
        return False


async def run_tests():
    """Run all tests."""
    logger.info("Running tests for refactored persona formation service")

    # Test the PersonaFormationService
    service_result = await test_persona_formation_service()
    logger.info(f"PersonaFormationService test: {'PASSED' if service_result else 'FAILED'}")

    # Test the TranscriptProcessor
    processor_result = await test_transcript_processor()
    logger.info(f"TranscriptProcessor test: {'PASSED' if processor_result else 'FAILED'}")

    # Overall result
    if service_result and processor_result:
        logger.info("All tests PASSED")
        return True
    else:
        logger.error("Some tests FAILED")
        return False


if __name__ == "__main__":
    # Run the tests
    asyncio.run(run_tests())
