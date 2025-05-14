"""
Integration test for the persona formation pipeline.

This script tests the integration between the AttributeExtractor and PersonaBuilder
to ensure the entire pipeline works correctly with simplified attribute structures.
"""

import json
import logging
import sys
from typing import Dict, Any

from services.processing.persona_builder import PersonaBuilder, persona_to_dict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def simulate_attribute_extractor_output(scenario: str = "standard") -> Dict[str, Any]:
    """
    Simulate the output from the AttributeExtractor.
    
    Args:
        scenario: The scenario to simulate (standard, minimal, complex)
        
    Returns:
        Dictionary of attributes that would be produced by the AttributeExtractor
    """
    if scenario == "standard":
        # Standard output with string values for most fields
        return {
            "name": "Product Manager",
            "description": "A product manager focused on user experience and product strategy.",
            "role_context": "Works in a cross-functional team leading product development.",
            "key_responsibilities": "Defining product requirements, roadmap planning, and stakeholder management.",
            "tools_used": "JIRA, Figma, Google Analytics, Amplitude",
            "collaboration_style": "Collaborative and inclusive, seeks input from all team members.",
            "analysis_approach": "Data-driven decision making with qualitative user insights.",
            "pain_points": "Balancing competing priorities and managing stakeholder expectations.",
            "archetype": "Strategic Product Leader",
            "demographics": "35-45 years old, 10+ years experience in tech",
            "goals_and_motivations": "Creating impactful products that solve real user problems.",
            "skills_and_expertise": "Product strategy, user research, market analysis, agile methodologies",
            "workflow_and_environment": "Agile/Scrum methodology in a remote-first company.",
            "challenges_and_frustrations": "Limited development resources and tight deadlines.",
            "needs_and_desires": "Better analytics tools and more user research resources.",
            "technology_and_tools": "Project management software, analytics platforms, design tools.",
            "attitude_towards_research": "Values user research highly and advocates for research-driven decisions.",
            "attitude_towards_ai": "Sees AI as an opportunity to enhance product capabilities.",
            "key_quotes": [
                "User experience is paramount to product success.",
                "We need to focus on metrics that actually matter to users.",
                "The best products solve real problems in elegant ways."
            ],
            "overall_confidence_score": 0.85
        }
    elif scenario == "minimal":
        # Minimal output with only required fields
        return {
            "name": "UX Designer",
            "description": "A UX designer focused on creating intuitive interfaces.",
            "role_context": "Works in the design team.",
            "key_quotes": ["Design is about solving problems.", "Users come first."],
            "overall_confidence_score": 0.75
        }
    elif scenario == "complex":
        # Complex output with mixed formats
        return {
            "name": "Data Scientist",
            "description": "A data scientist specializing in machine learning models.",
            "role_context": {
                "value": "Works in the analytics team developing predictive models.",
                "confidence": 0.9,
                "evidence": ["Mentioned working on predictive models multiple times."]
            },
            "key_responsibilities": "Building and deploying ML models, data analysis, feature engineering.",
            "tools_used": ["Python", "TensorFlow", "PyTorch", "SQL", "Jupyter"],
            "collaboration_style": "Collaborative with engineers, works independently on models.",
            "key_quotes": [
                "The model is only as good as the data you feed it.",
                "Feature engineering is where the real magic happens.",
                "We need to balance accuracy with explainability."
            ],
            "overall_confidence_score": 0.8,
            # Some fields intentionally missing to test defaults
        }
    else:
        raise ValueError(f"Unknown scenario: {scenario}")


def test_persona_pipeline_integration(scenario: str = "standard") -> bool:
    """
    Test the integration between AttributeExtractor and PersonaBuilder.
    
    Args:
        scenario: The scenario to test (standard, minimal, complex)
        
    Returns:
        True if the test passes, False otherwise
    """
    try:
        # Simulate AttributeExtractor output
        attributes = simulate_attribute_extractor_output(scenario)
        logger.info(f"Testing persona pipeline integration with {scenario} scenario")
        logger.info(f"Attribute keys: {list(attributes.keys())}")
        
        # Create PersonaBuilder
        builder = PersonaBuilder()
        
        # Build persona from attributes
        persona = builder.build_persona_from_attributes(attributes, role="Interviewee")
        
        # Convert to dict for easier assertions
        persona_dict = persona_to_dict(persona)
        
        # Basic validation
        assert persona_dict["name"] == attributes["name"], f"Name mismatch"
        assert persona_dict["description"] == attributes["description"], f"Description mismatch"
        
        # Validate confidence score
        expected_confidence = attributes.get("overall_confidence_score", 0.7)
        assert abs(persona_dict["overall_confidence"] - expected_confidence) < 0.1, \
            f"Confidence mismatch: expected {expected_confidence}, got {persona_dict['overall_confidence']}"
        
        # Validate key quotes
        if "key_quotes" in attributes:
            expected_quotes = attributes["key_quotes"]
            if isinstance(expected_quotes, list):
                for quote in expected_quotes:
                    assert quote in persona_dict["key_quotes"]["evidence"], \
                        f"Missing quote in evidence: {quote}"
        
        # Validate trait fields
        trait_fields = [
            "role_context", "key_responsibilities", "tools_used", "collaboration_style",
            "analysis_approach", "pain_points", "demographics", "goals_and_motivations",
            "skills_and_expertise", "workflow_and_environment", "challenges_and_frustrations",
            "needs_and_desires", "technology_and_tools", "attitude_towards_research",
            "attitude_towards_ai"
        ]
        
        for field in trait_fields:
            if field in attributes:
                expected_value = attributes[field]
                if isinstance(expected_value, dict) and "value" in expected_value:
                    expected_value = expected_value["value"]
                elif isinstance(expected_value, list):
                    expected_value = ", ".join(str(item) for item in expected_value[:3])
                
                if isinstance(expected_value, str):
                    assert expected_value in persona_dict[field]["value"], \
                        f"{field} value mismatch: expected '{expected_value}', got '{persona_dict[field]['value']}'"
        
        logger.info(f"✅ Persona pipeline integration test passed for {scenario} scenario!")
        return True
    
    except Exception as e:
        logger.error(f"❌ Error in persona pipeline integration test: {str(e)}", exc_info=True)
        return False


if __name__ == "__main__":
    logger.info("Running integration tests for persona formation pipeline...")
    
    success = True
    
    # Test with different scenarios
    scenarios = ["standard", "minimal", "complex"]
    for scenario in scenarios:
        if not test_persona_pipeline_integration(scenario):
            success = False
            logger.error(f"❌ Integration test failed for {scenario} scenario")
    
    if success:
        logger.info("✅ All integration tests passed!")
        sys.exit(0)
    else:
        logger.error("❌ Some integration tests failed")
        sys.exit(1)
