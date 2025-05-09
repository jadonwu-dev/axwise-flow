"""
Test script for persona trait population.

This script tests that all persona traits are properly populated.
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
from services.processing.attribute_extractor import AttributeExtractor
from services.processing.persona_builder import PersonaBuilder, persona_to_dict

# Create a mock LLM service
class MockLLMService:
    """Mock LLM service for testing."""

    async def analyze(self, request):
        """Mock analyze method."""
        logger.info(f"Mock LLM service called with task: {request.get('task')}")

        # Return a mock response based on the task
        if request.get("task") == "persona_formation":
            # Return a partial persona with missing traits
            return {
                "name": "Partial Persona",
                "description": "A persona with missing traits",
                "role_context": {
                    "value": "Works in a structured environment",
                    "confidence": 0.8,
                    "evidence": ["Evidence from patterns"]
                },
                # Missing many traits
                "patterns": ["Pattern 1", "Pattern 2"],
                "confidence": 0.7,
                "evidence": ["Evidence 1", "Evidence 2"]
            }

        # Default response
        return {"error": "Unknown task"}

async def test_attribute_extractor():
    """Test the AttributeExtractor's trait population."""
    try:
        # Create a mock LLM service
        llm_service = MockLLMService()

        # Create an AttributeExtractor
        extractor = AttributeExtractor(llm_service)

        # Create a partial persona attributes
        partial_attributes = {
            "name": "Partial Persona",
            "description": "A persona with missing traits",
            "role_context": {
                "value": "Works in a structured environment",
                "confidence": 0.8,
                "evidence": ["Evidence from patterns"]
            },
            # Missing many traits
            "patterns": ["Pattern 1", "Pattern 2"],
            "confidence": 0.7,
            "evidence": ["Evidence 1", "Evidence 2"]
        }

        # Clean the attributes
        cleaned_attributes = extractor._clean_persona_attributes(partial_attributes)

        # Check if all traits are populated
        trait_fields = [
            "demographics", "goals_and_motivations", "skills_and_expertise",
            "workflow_and_environment", "challenges_and_frustrations",
            "needs_and_desires", "technology_and_tools", "attitude_towards_research",
            "attitude_towards_ai", "key_quotes", "role_context", "key_responsibilities",
            "tools_used", "collaboration_style", "analysis_approach", "pain_points"
        ]

        missing_traits = []
        for field in trait_fields:
            if field not in cleaned_attributes:
                missing_traits.append(field)

        if missing_traits:
            logger.error(f"Missing traits: {missing_traits}")
            return False

        logger.info("All traits are populated in the cleaned attributes")
        logger.info(f"Cleaned attributes: {json.dumps(cleaned_attributes, indent=2)}")
        return True

    except Exception as e:
        logger.error(f"Error in test_attribute_extractor: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_persona_builder():
    """Test the PersonaBuilder's trait population."""
    try:
        # Create a PersonaBuilder
        builder = PersonaBuilder()

        # Create a partial persona attributes
        partial_attributes = {
            "name": "Partial Persona",
            "description": "A persona with missing traits",
            "role_context": {
                "value": "Works in a structured environment",
                "confidence": 0.8,
                "evidence": ["Evidence from patterns"]
            },
            # Missing many traits
            "patterns": ["Pattern 1", "Pattern 2"],
            "confidence": 0.7,
            "evidence": ["Evidence 1", "Evidence 2"]
        }

        # Build a persona from the partial attributes
        persona = builder.build_persona_from_attributes(partial_attributes)

        # Convert to dictionary
        persona_dict = persona_to_dict(persona)

        # Check if all traits are populated
        trait_fields = [
            "demographics", "goals_and_motivations", "skills_and_expertise",
            "workflow_and_environment", "challenges_and_frustrations",
            "needs_and_desires", "technology_and_tools", "attitude_towards_research",
            "attitude_towards_ai", "key_quotes", "role_context", "key_responsibilities",
            "tools_used", "collaboration_style", "analysis_approach", "pain_points"
        ]

        missing_traits = []
        for field in trait_fields:
            if field not in persona_dict:
                missing_traits.append(field)

        if missing_traits:
            logger.error(f"Missing traits: {missing_traits}")
            return False

        logger.info("All traits are populated in the persona")
        logger.info(f"Persona: {json.dumps(persona_dict, indent=2)}")
        return True

    except Exception as e:
        logger.error(f"Error in test_persona_builder: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_persona_formation_service():
    """Test the PersonaFormationService's trait population."""
    try:
        # Create a mock LLM service
        llm_service = MockLLMService()

        # Create a mock config
        class MockConfig:
            def __init__(self):
                self.validation = type("obj", (object,), {"min_confidence": 0.4})
                self.llm = type("obj", (object,), {"provider": "test", "model": "test-model"})

        # Create a PersonaFormationService
        persona_service = PersonaFormationService(MockConfig(), llm_service)

        # Generate a persona from text
        personas = await persona_service.generate_persona_from_text("Test text")

        if not personas or len(personas) == 0:
            logger.error("No personas generated")
            return False

        # Check if all traits are populated
        trait_fields = [
            "demographics", "goals_and_motivations", "skills_and_expertise",
            "workflow_and_environment", "challenges_and_frustrations",
            "needs_and_desires", "technology_and_tools", "attitude_towards_research",
            "attitude_towards_ai", "key_quotes", "role_context", "key_responsibilities",
            "tools_used", "collaboration_style", "analysis_approach", "pain_points"
        ]

        missing_traits = []
        for field in trait_fields:
            if field not in personas[0]:
                missing_traits.append(field)

        if missing_traits:
            logger.error(f"Missing traits: {missing_traits}")
            return False

        logger.info("All traits are populated in the persona")
        logger.info(f"Persona: {json.dumps(personas[0], indent=2)}")
        return True

    except Exception as e:
        logger.error(f"Error in test_persona_formation_service: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def run_tests():
    """Run all tests."""
    logger.info("Testing AttributeExtractor's trait population...")
    extractor_result = await test_attribute_extractor()

    logger.info("\nTesting PersonaBuilder's trait population...")
    builder_result = await test_persona_builder()

    logger.info("\nTesting PersonaFormationService's trait population...")
    service_result = await test_persona_formation_service()

    # Print summary
    logger.info("\nTest Summary:")
    logger.info(f"AttributeExtractor: {'PASSED' if extractor_result else 'FAILED'}")
    logger.info(f"PersonaBuilder: {'PASSED' if builder_result else 'FAILED'}")
    logger.info(f"PersonaFormationService: {'PASSED' if service_result else 'FAILED'}")

    return extractor_result and builder_result and service_result

if __name__ == "__main__":
    # Run the tests
    asyncio.run(run_tests())
