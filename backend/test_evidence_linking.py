"""
Test script for the evidence linking service.

This script demonstrates how the evidence linking service works with a sample transcript.
"""

import os
import sys
import asyncio
import json
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Import our services
from services.processing.evidence_linking_service import EvidenceLinkingService
from services.processing.trait_formatting_service import TraitFormattingService
from services.processing.attribute_extractor import AttributeExtractor
# Create a mock LLM service for testing
class MockLLMService:
    """Mock LLM service for testing."""

    async def analyze(self, request):
        """Mock analyze method."""
        logger.info(f"MockLLMService.analyze called with task: {request.get('task')}")

        if request.get("task") == "evidence_linking":
            # Return mock quotes
            return [
                "I've been working as a product designer for about 8 years now. I'm 34 years old and I specialize in UX/UI design.",
                "My main goal is to create interfaces that are intuitive and solve real problems for users.",
                "I'm really proficient in Figma, which is my primary design tool. I also do a lot of user research and prototyping."
            ]
        elif request.get("task") == "trait_formatting":
            # Return formatted trait value
            return "Formatted: " + request.get("text", "")
        elif request.get("task") == "persona_formation":
            # Return mock persona attributes
            return {
                "name": "Product Designer",
                "description": "Experienced UX/UI designer focused on creating intuitive interfaces",
                "demographics": {
                    "value": "34-year-old designer with 8 years of experience",
                    "confidence": 0.9,
                    "evidence": ["I've been working as a product designer for about 8 years now. I'm 34 years old."]
                },
                "goals_and_motivations": {
                    "value": "Creating intuitive interfaces that solve real user problems",
                    "confidence": 0.8,
                    "evidence": ["My main goal is to create interfaces that are intuitive and solve real problems for users."]
                }
            }
        else:
            # Return empty response for unknown tasks
            return {}


async def main():
    """Run the test script."""
    logger.info("Starting evidence linking test")

    # Create a sample text
    sample_text = """
    I've been working as a product designer for about 8 years now. I'm 34 years old and I specialize in UX/UI design.

    My main goal is to create interfaces that are intuitive and solve real problems for users. I believe that good design should be invisible - users shouldn't have to think about how to use a product.

    I'm really proficient in Figma, which is my primary design tool. I also do a lot of user research and prototyping to validate my designs before they go to development.

    One of the challenges I face is getting stakeholders to understand the importance of user testing. Sometimes they want to skip that step to save time, but it always ends up causing problems later.
    """

    logger.info(f"Created sample text with {len(sample_text)} characters")

    # Create a sample attribute dictionary
    sample_attributes = {
        "name": "Product Designer",
        "description": "A product designer focused on user experience",
        "archetype": "Creative Problem-Solver",
        "demographics": {
            "value": "Experienced designer with focus on minimalist approach",
            "confidence": 0.8,
            "evidence": []
        },
        "goals_and_motivations": {
            "value": "Creating intuitive interfaces that solve real user problems",
            "confidence": 0.7,
            "evidence": []
        },
        "skills_and_expertise": {
            "value": "Proficient in Figma, user research, and prototyping",
            "confidence": 0.9,
            "evidence": []
        },
        "technology_and_tools": {
            "value": "Uses mobile apps and desktop tools for design work",
            "confidence": 0.8,
            "evidence": []
        }
    }

    # Initialize the mock LLM service
    llm_service = MockLLMService()

    # Initialize our services
    evidence_linking_service = EvidenceLinkingService(llm_service)
    trait_formatting_service = TraitFormattingService(llm_service)
    attribute_extractor = AttributeExtractor(llm_service)

    # Test evidence linking
    logger.info("Testing evidence linking service")
    try:
        enhanced_attributes = await evidence_linking_service.link_evidence_to_attributes(
            sample_attributes, sample_text
        )

        logger.info("Evidence linking results:")
        for field, trait in enhanced_attributes.items():
            if isinstance(trait, dict) and "evidence" in trait:
                logger.info(f"{field}: {len(trait['evidence'])} pieces of evidence")
                for i, evidence in enumerate(trait["evidence"]):
                    logger.info(f"  Evidence {i+1}: {evidence[:100]}...")
    except Exception as e:
        logger.error(f"Error testing evidence linking: {str(e)}", exc_info=True)

    # Test trait formatting
    logger.info("\nTesting trait formatting service")
    try:
        formatted_attributes = await trait_formatting_service.format_trait_values(
            sample_attributes
        )

        logger.info("Trait formatting results:")
        for field, trait in formatted_attributes.items():
            if isinstance(trait, dict) and "value" in trait:
                logger.info(f"{field}: {trait['value']}")
    except Exception as e:
        logger.error(f"Error testing trait formatting: {str(e)}", exc_info=True)

    # Test attribute extraction with new services
    logger.info("\nTesting attribute extraction with new services")
    try:
        extracted_attributes = await attribute_extractor.extract_attributes_from_text(
            sample_text, "Interviewee"
        )

        logger.info("Attribute extraction results:")
        for field, trait in extracted_attributes.items():
            if isinstance(trait, dict) and "value" in trait:
                logger.info(f"{field}: {trait['value']}")
                if "evidence" in trait and trait["evidence"]:
                    logger.info(f"  Evidence: {trait['evidence'][0][:100]}...")
    except Exception as e:
        logger.error(f"Error testing attribute extraction: {str(e)}", exc_info=True)

    logger.info("Test completed")


if __name__ == "__main__":
    asyncio.run(main())
