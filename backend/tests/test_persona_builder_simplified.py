"""
Test script for validating the PersonaBuilder with simplified attributes.

This script tests the PersonaBuilder's ability to handle simplified attribute structures
from the output of the AttributeExtractor.
"""

import json
import logging
import pytest
from typing import Dict, Any

from backend.services.processing.persona_builder import PersonaBuilder, persona_to_dict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestPersonaBuilderSimplified:
    """Tests for the PersonaBuilder with simplified attributes."""

    @pytest.fixture
    def persona_builder(self):
        """Create a PersonaBuilder instance."""
        return PersonaBuilder()

    def test_build_persona_from_string_attributes(self, persona_builder):
        """Test building a persona from simplified attributes with string values."""
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
        persona = persona_builder.build_persona_from_attributes(simplified_attributes, role="Interviewee")
        
        # Convert to dict for easier assertions
        persona_dict = persona_to_dict(persona)
        
        # Verify the persona
        assert persona_dict["name"] == "UX Researcher"
        assert persona_dict["description"] == "A UX researcher focused on user testing."
        assert persona_dict["role_context"]["value"] == "Works in a design team."
        assert persona_dict["key_responsibilities"]["value"] == "Conducting user interviews and usability tests."
        assert persona_dict["tools_used"]["value"] == "Figma, UserTesting, Miro"
        assert persona_dict["archetype"] == "Research Specialist"
        assert persona_dict["role_in_interview"] == "Interviewee"
        assert persona_dict["overall_confidence"] == 0.9  # Should match the overall_confidence_score
        
        # Verify that key_quotes are used as evidence
        assert len(persona_dict["key_quotes"]["evidence"]) == 2
        assert "Research is critical." in persona_dict["key_quotes"]["evidence"]
        assert "We need more time for testing." in persona_dict["key_quotes"]["evidence"]
        
        # Verify that all traits have the same confidence (from overall_confidence_score)
        assert persona_dict["role_context"]["confidence"] == 0.9
        assert persona_dict["key_responsibilities"]["confidence"] == 0.9
        assert persona_dict["tools_used"]["confidence"] == 0.9

    def test_build_persona_with_mixed_attributes(self, persona_builder):
        """Test building a persona from attributes with mixed formats (string, dict, list)."""
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
        persona = persona_builder.build_persona_from_attributes(mixed_attributes, role="Interviewee")
        
        # Convert to dict for easier assertions
        persona_dict = persona_to_dict(persona)
        
        # Verify the persona
        assert persona_dict["name"] == "Product Designer"
        assert persona_dict["description"] == "A product designer with UX focus."
        assert persona_dict["role_context"]["value"] == "Works in a product team."
        assert persona_dict["key_responsibilities"]["value"] == "Creating wireframes and prototypes."
        assert "Figma" in persona_dict["tools_used"]["value"]
        assert "Sketch" in persona_dict["tools_used"]["value"]
        assert persona_dict["archetype"] == "Design Leader"
        assert persona_dict["overall_confidence"] == 0.8
        
        # Verify that key_quotes are used as evidence
        assert len(persona_dict["key_quotes"]["evidence"]) == 2
        assert "Design is about solving problems." in persona_dict["key_quotes"]["evidence"]
        
        # Verify that missing fields are populated with defaults
        assert persona_dict["demographics"]["value"] == ""
        assert persona_dict["demographics"]["confidence"] == 0.8  # Should use overall_confidence_score
        
        # Verify that the dict format field keeps its original confidence
        assert persona_dict["key_responsibilities"]["confidence"] == 0.85

    def test_fallback_persona_creation(self, persona_builder):
        """Test the creation of a fallback persona."""
        # Create invalid attributes that will cause an error
        invalid_attributes = {
            "name": {"invalid": "structure"},  # This will cause an error
            "description": 123,  # Not a string
            "overall_confidence_score": "not a number"  # Invalid confidence
        }
        
        # Build persona (should fall back to fallback persona)
        persona = persona_builder.build_persona_from_attributes(invalid_attributes, role="Interviewer")
        
        # Convert to dict for easier assertions
        persona_dict = persona_to_dict(persona)
        
        # Verify it's a fallback persona
        assert "Default" in persona_dict["name"]
        assert "due to processing error" in persona_dict["description"]
        assert persona_dict["overall_confidence"] == 0.3
        assert persona_dict["metadata"]["is_fallback"] is True
        
        # Verify all traits are populated with fallback values
        assert persona_dict["role_context"]["value"] == "Unknown"
        assert persona_dict["key_responsibilities"]["value"] == "Unknown"
        assert persona_dict["key_quotes"]["value"] == "No quotes available"


if __name__ == "__main__":
    # Manual test execution
    builder = PersonaBuilder()
    
    # Test with simplified attributes
    simplified_attributes = {
        "name": "UX Researcher",
        "description": "A UX researcher focused on user testing.",
        "role_context": "Works in a design team.",
        "key_responsibilities": "Conducting user interviews and usability tests.",
        "tools_used": "Figma, UserTesting, Miro",
        "key_quotes": ["Research is critical.", "We need more time for testing."],
        "overall_confidence_score": 0.9
    }
    
    persona = builder.build_persona_from_attributes(simplified_attributes, role="Interviewee")
    persona_dict = persona_to_dict(persona)
    
    print(f"Built persona: {persona_dict['name']}")
    print(f"Description: {persona_dict['description']}")
    print(f"Role context: {persona_dict['role_context']['value']}")
    print(f"Key quotes: {persona_dict['key_quotes']['evidence']}")
    print(f"Overall confidence: {persona_dict['overall_confidence']}")
