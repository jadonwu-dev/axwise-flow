"""
Manual test script for validating the PersonaBuilder with simplified attributes.

This script tests the PersonaBuilder's ability to handle simplified attribute structures
from the output of the AttributeExtractor.
"""

import json
import logging
import sys
from typing import Dict, Any

from services.processing.persona_builder import PersonaBuilder, persona_to_dict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_build_persona_from_string_attributes():
    """Test building a persona from simplified attributes with string values."""
    # Create a PersonaBuilder
    builder = PersonaBuilder()

    # Create simplified attributes with string values
    simplified_attributes = {
        "name": "UX Researcher",
        "description": "A UX researcher focused on user testing.",
        "role_context": "Works in a design team.",
        "key_responsibilities": "Conducting user interviews and usability tests.",
        "tools_used": "Figma, UserTesting, Miro",
        "collaboration_style": "Collaborative and detail-oriented.",
        "analysis_approach": "Qualitative analysis with some quantitative metrics.",
        "pain_points": "Difficulty recruiting participants.",
        "archetype": "Research Specialist",
        "demographics": "30-40 years old, 5+ years experience",
        "goals_and_motivations": "Improving user experiences through research.",
        "skills_and_expertise": "User research, usability testing",
        "workflow_and_environment": "Agile methodology.",
        "challenges_and_frustrations": "Tight deadlines for research.",
        "needs_and_desires": "Better research tools.",
        "technology_and_tools": "Research software.",
        "attitude_towards_research": "Passionate about research.",
        "attitude_towards_ai": "Interested in AI for research automation.",
        "key_quotes": ["Research is critical.", "We need more time for testing."],
        "overall_confidence_score": 0.9
    }

    # Build persona
    persona = builder.build_persona_from_attributes(simplified_attributes, role="Interviewee")

    # Convert to dict for easier assertions
    persona_dict = persona_to_dict(persona)

    # Verify the persona
    assert persona_dict["name"] == "UX Researcher", f"Expected 'UX Researcher', got {persona_dict['name']}"
    assert persona_dict["description"] == "A UX researcher focused on user testing.", f"Description mismatch"
    assert persona_dict["role_context"]["value"] == "Works in a design team.", f"Role context mismatch"
    assert persona_dict["key_responsibilities"]["value"] == "Conducting user interviews and usability tests.", f"Key responsibilities mismatch"
    assert persona_dict["tools_used"]["value"] == "Figma, UserTesting, Miro", f"Tools used mismatch"
    assert persona_dict["archetype"] == "Research Specialist", f"Archetype mismatch"
    assert persona_dict["role_in_interview"] == "Interviewee", f"Role in interview mismatch"
    assert persona_dict["overall_confidence"] == 0.9, f"Expected confidence 0.9, got {persona_dict['overall_confidence']}"

    # Verify that key_quotes are used as evidence
    assert len(persona_dict["key_quotes"]["evidence"]) == 2, f"Expected 2 key quotes, got {len(persona_dict['key_quotes']['evidence'])}"
    assert "Research is critical." in persona_dict["key_quotes"]["evidence"], f"Missing expected key quote"
    assert "We need more time for testing." in persona_dict["key_quotes"]["evidence"], f"Missing expected key quote"

    # Verify that all traits have the same confidence (from overall_confidence_score)
    assert persona_dict["role_context"]["confidence"] == 0.9, f"Role context confidence mismatch"
    assert persona_dict["key_responsibilities"]["confidence"] == 0.9, f"Key responsibilities confidence mismatch"
    assert persona_dict["tools_used"]["confidence"] == 0.9, f"Tools used confidence mismatch"

    logger.info("✅ Test build_persona_from_string_attributes passed!")
    return True


def test_build_persona_with_mixed_attributes():
    """Test building a persona from attributes with mixed formats (string, dict, list)."""
    # Create a PersonaBuilder
    builder = PersonaBuilder()

    # Create attributes with mixed formats
    mixed_attributes = {
        "name": "Product Designer",
        "description": "A product designer with UX focus.",
        # String format
        "role_context": "Works in a product team.",
        # Dict format
        "key_responsibilities": {
            "value": "Creating wireframes and prototypes.",
            "confidence": 0.85,
            "evidence": ["Evidence from interview"]
        },
        # List format
        "tools_used": ["Figma", "Sketch", "InVision"],
        # Missing fields
        "archetype": "Design Leader",
        "key_quotes": ["Design is about solving problems.", "User needs come first."],
        "overall_confidence_score": 0.8
    }

    # Build persona
    persona = builder.build_persona_from_attributes(mixed_attributes, role="Interviewee")

    # Convert to dict for easier assertions
    persona_dict = persona_to_dict(persona)

    # Verify the persona
    assert persona_dict["name"] == "Product Designer", f"Name mismatch"
    assert persona_dict["description"] == "A product designer with UX focus.", f"Description mismatch"
    assert persona_dict["role_context"]["value"] == "Works in a product team.", f"Role context mismatch"
    assert persona_dict["key_responsibilities"]["value"] == "Creating wireframes and prototypes.", f"Key responsibilities mismatch"
    assert "Figma" in persona_dict["tools_used"]["value"], f"Tools used missing Figma"
    assert "Sketch" in persona_dict["tools_used"]["value"], f"Tools used missing Sketch"
    assert persona_dict["archetype"] == "Design Leader", f"Archetype mismatch"
    assert persona_dict["overall_confidence"] == 0.8, f"Overall confidence mismatch"

    # Verify that key_quotes are used as evidence
    assert len(persona_dict["key_quotes"]["evidence"]) == 2, f"Expected 2 key quotes, got {len(persona_dict['key_quotes']['evidence'])}"
    assert "Design is about solving problems." in persona_dict["key_quotes"]["evidence"], f"Missing expected key quote"

    # Verify that missing fields are populated with defaults
    assert persona_dict["demographics"]["value"] == "", f"Demographics should be empty"
    assert persona_dict["demographics"]["confidence"] == 0.8, f"Demographics confidence should use overall_confidence_score"

    # Verify that the dict format field keeps its original confidence
    assert persona_dict["key_responsibilities"]["confidence"] == 0.85, f"Key responsibilities confidence mismatch"

    logger.info("✅ Test build_persona_with_mixed_attributes passed!")
    return True


def test_invalid_attribute_handling():
    """Test handling of invalid attributes."""
    # Create a PersonaBuilder
    builder = PersonaBuilder()

    # Create invalid attributes
    invalid_attributes = {
        "name": {"invalid": "structure"},  # Not a string
        "description": 123,  # Not a string
        "overall_confidence_score": "not a number"  # Invalid confidence
    }

    # Build persona (should handle invalid attributes gracefully)
    persona = builder.build_persona_from_attributes(invalid_attributes, role="Interviewer")

    # Convert to dict for easier assertions
    persona_dict = persona_to_dict(persona)

    # Verify the persona has fallback values for invalid fields
    assert persona_dict["name"] == "Interviewer", f"Name should be the role, got {persona_dict['name']}"
    assert persona_dict["description"] == "123", f"Description should be converted to string, got {persona_dict['description']}"

    # Verify all traits are populated with default values
    assert persona_dict["role_context"]["value"] == "", f"Role context should be empty"
    assert persona_dict["key_responsibilities"]["value"] == "", f"Key responsibilities should be empty"
    assert persona_dict["key_quotes"]["value"] == "", f"Key quotes should be empty"

    # Now test the actual fallback persona creation
    try:
        # Force an error by passing None as attributes
        persona = builder.create_fallback_persona(role="Tester")

        # Convert to dict for easier assertions
        persona_dict = persona_to_dict(persona)

        # Verify it's a fallback persona
        assert "Default" in persona_dict["name"], f"Name should contain 'Default', got {persona_dict['name']}"
        assert "due to processing error" in persona_dict["description"], f"Description should indicate error"
        assert persona_dict["overall_confidence"] == 0.3, f"Fallback confidence should be 0.3"
        assert persona_dict["metadata"]["is_fallback"] is True, f"Metadata should indicate fallback"

        # Verify all traits are populated with fallback values
        assert persona_dict["role_context"]["value"] == "Unknown", f"Role context should be 'Unknown'"
        assert persona_dict["key_responsibilities"]["value"] == "Unknown", f"Key responsibilities should be 'Unknown'"
        assert persona_dict["key_quotes"]["value"] == "No quotes available", f"Key quotes should be 'No quotes available'"
    except Exception as e:
        logger.error(f"Error creating fallback persona: {str(e)}")
        return False

    logger.info("✅ Test fallback_persona_creation passed!")
    return True


if __name__ == "__main__":
    logger.info("Running manual tests for PersonaBuilder with simplified attributes...")

    success = True

    try:
        if not test_build_persona_from_string_attributes():
            success = False
            logger.error("❌ test_build_persona_from_string_attributes failed")

        if not test_build_persona_with_mixed_attributes():
            success = False
            logger.error("❌ test_build_persona_with_mixed_attributes failed")

        if not test_invalid_attribute_handling():
            success = False
            logger.error("❌ test_invalid_attribute_handling failed")

        if success:
            logger.info("✅ All tests passed!")
            sys.exit(0)
        else:
            logger.error("❌ Some tests failed")
            sys.exit(1)

    except Exception as e:
        logger.error(f"❌ Error running tests: {str(e)}", exc_info=True)
        sys.exit(1)
