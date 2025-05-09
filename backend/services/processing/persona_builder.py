"""
Persona builder module for constructing personas from attributes.

This module provides functionality for:
1. Building persona objects from attributes
2. Creating fallback personas
3. Validating personas
"""

from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field, asdict
import logging
from datetime import datetime
from pydantic import ValidationError

# Import Pydantic schema for validation
try:
    from schemas import Persona as PersonaSchema
except ImportError:
    try:
        from schemas import Persona as PersonaSchema
    except ImportError:
        logger = logging.getLogger(__name__)
        logger.warning("Could not import PersonaSchema, validation will be limited")
        # We'll define a minimal schema later if needed

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class PersonaTrait:
    """A trait of a persona with evidence and confidence"""
    value: Union[str, dict, list]
    confidence: float
    evidence: List[str] = field(default_factory=list)


@dataclass
class Persona:
    """A user persona derived from interview data"""
    name: str
    description: str
    role_context: PersonaTrait
    key_responsibilities: PersonaTrait
    tools_used: PersonaTrait
    collaboration_style: PersonaTrait
    analysis_approach: PersonaTrait
    pain_points: PersonaTrait
    patterns: List[str] = field(default_factory=list)
    confidence: float = 0.7  # Default confidence
    evidence: List[str] = field(default_factory=list)
    persona_metadata: Optional[Dict[str, Any]] = None  # Changed from metadata
    role_in_interview: str = "Participant"  # Default role in the interview (Interviewee, Interviewer, etc.)

    # New fields
    archetype: str = "Unknown"
    demographics: Optional[PersonaTrait] = None
    goals_and_motivations: Optional[PersonaTrait] = None
    skills_and_expertise: Optional[PersonaTrait] = None
    workflow_and_environment: Optional[PersonaTrait] = None
    challenges_and_frustrations: Optional[PersonaTrait] = None
    needs_and_desires: Optional[PersonaTrait] = None
    technology_and_tools: Optional[PersonaTrait] = None
    attitude_towards_research: Optional[PersonaTrait] = None
    attitude_towards_ai: Optional[PersonaTrait] = None
    key_quotes: Optional[PersonaTrait] = None


def persona_to_dict(persona: Persona) -> Dict[str, Any]:
    """
    Convert a Persona object to a dictionary.

    Args:
        persona: Persona object

    Returns:
        Dictionary representation of the persona
    """
    # Convert to dictionary using dataclasses.asdict
    persona_dict = asdict(persona)

    # Rename metadata field for backward compatibility
    if "persona_metadata" in persona_dict:
        persona_dict["metadata"] = persona_dict.pop("persona_metadata")

    # Add aliases for backward compatibility
    persona_dict["overall_confidence"] = persona_dict["confidence"]
    persona_dict["supporting_evidence_summary"] = persona_dict["evidence"]

    return persona_dict


class PersonaBuilder:
    """
    Builds persona objects from attributes.
    """

    def __init__(self):
        """Initialize the persona builder."""
        logger.info("Initialized PersonaBuilder")

    def build_persona_from_attributes(
        self, attributes: Dict[str, Any], name_override: str = "", role: str = "Participant"
    ) -> Persona:
        """
        Build a persona object from attributes.

        Args:
            attributes: Persona attributes
            name_override: Optional name to override the one in attributes
            role: Role of the person in the interview

        Returns:
            Persona object
        """
        logger.info(f"Building persona from attributes for {role}")

        try:
            # Use name override if provided
            name = name_override if name_override else attributes.get("name", "Unknown Persona")

            # Extract nested trait data
            role_context_data = attributes.get("role_context", {})
            key_responsibilities_data = attributes.get("key_responsibilities", {})
            tools_used_data = attributes.get("tools_used", {})
            collaboration_style_data = attributes.get("collaboration_style", {})
            analysis_approach_data = attributes.get("analysis_approach", {})
            pain_points_data = attributes.get("pain_points", {})

            # Extract new trait data
            demographics_data = attributes.get("demographics", {})
            goals_and_motivations_data = attributes.get("goals_and_motivations", {})
            skills_and_expertise_data = attributes.get("skills_and_expertise", {})
            workflow_and_environment_data = attributes.get("workflow_and_environment", {})
            challenges_and_frustrations_data = attributes.get("challenges_and_frustrations", {})
            needs_and_desires_data = attributes.get("needs_and_desires", {})
            technology_and_tools_data = attributes.get("technology_and_tools", {})
            attitude_towards_research_data = attributes.get("attitude_towards_research", {})
            attitude_towards_ai_data = attributes.get("attitude_towards_ai", {})
            key_quotes_data = attributes.get("key_quotes", {})

            # Create Persona object
            persona = Persona(
                name=name,
                description=attributes.get("description", "No description provided."),
                archetype=attributes.get("archetype", "Unknown"),

                # Create PersonaTrait instances from nested data
                role_context=PersonaTrait(
                    value=role_context_data.get("value", ""),
                    confidence=float(role_context_data.get("confidence", 0.7)),
                    evidence=self._clean_evidence_list(role_context_data.get("evidence", [])),
                ),
                key_responsibilities=PersonaTrait(
                    value=key_responsibilities_data.get("value", ""),
                    confidence=float(key_responsibilities_data.get("confidence", 0.7)),
                    evidence=self._clean_evidence_list(key_responsibilities_data.get("evidence", [])),
                ),
                tools_used=PersonaTrait(
                    value=tools_used_data.get("value", ""),
                    confidence=float(tools_used_data.get("confidence", 0.7)),
                    evidence=self._clean_evidence_list(tools_used_data.get("evidence", [])),
                ),
                collaboration_style=PersonaTrait(
                    value=collaboration_style_data.get("value", ""),
                    confidence=float(collaboration_style_data.get("confidence", 0.7)),
                    evidence=self._clean_evidence_list(collaboration_style_data.get("evidence", [])),
                ),
                analysis_approach=PersonaTrait(
                    value=analysis_approach_data.get("value", ""),
                    confidence=float(analysis_approach_data.get("confidence", 0.7)),
                    evidence=self._clean_evidence_list(analysis_approach_data.get("evidence", [])),
                ),
                pain_points=PersonaTrait(
                    value=pain_points_data.get("value", ""),
                    confidence=float(pain_points_data.get("confidence", 0.7)),
                    evidence=self._clean_evidence_list(pain_points_data.get("evidence", [])),
                ),

                # Create PersonaTrait instances for new fields
                demographics=PersonaTrait(
                    value=demographics_data.get("value", ""),
                    confidence=float(demographics_data.get("confidence", 0.7)),
                    evidence=self._clean_evidence_list(demographics_data.get("evidence", [])),
                ),
                goals_and_motivations=PersonaTrait(
                    value=goals_and_motivations_data.get("value", ""),
                    confidence=float(goals_and_motivations_data.get("confidence", 0.7)),
                    evidence=self._clean_evidence_list(goals_and_motivations_data.get("evidence", [])),
                ),
                skills_and_expertise=PersonaTrait(
                    value=skills_and_expertise_data.get("value", ""),
                    confidence=float(skills_and_expertise_data.get("confidence", 0.7)),
                    evidence=self._clean_evidence_list(skills_and_expertise_data.get("evidence", [])),
                ),
                workflow_and_environment=PersonaTrait(
                    value=workflow_and_environment_data.get("value", ""),
                    confidence=float(workflow_and_environment_data.get("confidence", 0.7)),
                    evidence=self._clean_evidence_list(workflow_and_environment_data.get("evidence", [])),
                ),
                challenges_and_frustrations=PersonaTrait(
                    value=challenges_and_frustrations_data.get("value", ""),
                    confidence=float(challenges_and_frustrations_data.get("confidence", 0.7)),
                    evidence=self._clean_evidence_list(challenges_and_frustrations_data.get("evidence", [])),
                ),
                needs_and_desires=PersonaTrait(
                    value=needs_and_desires_data.get("value", ""),
                    confidence=float(needs_and_desires_data.get("confidence", 0.7)),
                    evidence=self._clean_evidence_list(needs_and_desires_data.get("evidence", [])),
                ),
                technology_and_tools=PersonaTrait(
                    value=technology_and_tools_data.get("value", ""),
                    confidence=float(technology_and_tools_data.get("confidence", 0.7)),
                    evidence=self._clean_evidence_list(technology_and_tools_data.get("evidence", [])),
                ),
                attitude_towards_research=PersonaTrait(
                    value=attitude_towards_research_data.get("value", ""),
                    confidence=float(attitude_towards_research_data.get("confidence", 0.7)),
                    evidence=self._clean_evidence_list(attitude_towards_research_data.get("evidence", [])),
                ),
                attitude_towards_ai=PersonaTrait(
                    value=attitude_towards_ai_data.get("value", ""),
                    confidence=float(attitude_towards_ai_data.get("confidence", 0.7)),
                    evidence=self._clean_evidence_list(attitude_towards_ai_data.get("evidence", [])),
                ),
                key_quotes=PersonaTrait(
                    value=key_quotes_data.get("value", ""),
                    confidence=float(key_quotes_data.get("confidence", 0.7)),
                    evidence=self._clean_evidence_list(key_quotes_data.get("evidence", [])),
                ),

                # Set other fields
                patterns=attributes.get("patterns", []),
                confidence=float(attributes.get("confidence", 0.7)),
                evidence=self._clean_evidence_list(attributes.get("evidence", [])),
                persona_metadata=self._create_metadata(attributes, role),
                role_in_interview=role
            )

            # Validate persona with Pydantic if available
            try:
                if 'PersonaSchema' in globals():
                    persona_dict = persona_to_dict(persona)
                    validated_persona = PersonaSchema(**persona_dict)
                    logger.info(f"Successfully validated persona: {persona.name}")
            except ValidationError as e:
                logger.warning(f"Persona validation failed: {str(e)}")

            return persona

        except Exception as e:
            logger.error(f"Error building persona from attributes: {str(e)}", exc_info=True)
            return self.create_fallback_persona(role)

    def create_fallback_persona(self, role: str = "Participant") -> Persona:
        """
        Create a fallback persona when building fails.

        Args:
            role: Role of the person in the interview

        Returns:
            Fallback persona
        """
        logger.info(f"Creating fallback persona for {role}")

        # Create a minimal trait
        minimal_trait = PersonaTrait(
            value="Unknown",
            confidence=0.3,
            evidence=["Fallback due to processing error"]
        )

        # Create fallback persona
        return Persona(
            name=f"Default {role}",
            description=f"Default {role} due to processing error",
            archetype="Unknown",
            # Legacy fields
            role_context=minimal_trait,
            key_responsibilities=minimal_trait,
            tools_used=minimal_trait,
            collaboration_style=minimal_trait,
            analysis_approach=minimal_trait,
            pain_points=minimal_trait,
            # New fields
            demographics=minimal_trait,
            goals_and_motivations=minimal_trait,
            skills_and_expertise=minimal_trait,
            workflow_and_environment=minimal_trait,
            challenges_and_frustrations=minimal_trait,
            needs_and_desires=minimal_trait,
            technology_and_tools=minimal_trait,
            attitude_towards_research=minimal_trait,
            attitude_towards_ai=minimal_trait,
            key_quotes=minimal_trait,
            # Other fields
            patterns=[],
            confidence=0.3,
            evidence=["Fallback due to processing error"],
            persona_metadata={
                "source": "fallback_persona",
                "timestamp": datetime.now().isoformat(),
                "role": role
            },
            role_in_interview=role
        )

    def _clean_evidence_list(self, evidence: Any) -> List[str]:
        """
        Clean and validate evidence list.

        Args:
            evidence: Evidence data

        Returns:
            Cleaned evidence list
        """
        if not evidence:
            return []

        if isinstance(evidence, str):
            return [evidence]

        if isinstance(evidence, list):
            return [str(e) for e in evidence if e]

        return []

    def _create_metadata(self, attributes: Dict[str, Any], role: str) -> Dict[str, Any]:
        """
        Create metadata for persona.

        Args:
            attributes: Persona attributes
            role: Role of the person in the interview

        Returns:
            Metadata dictionary
        """
        metadata = {
            "timestamp": datetime.now().isoformat(),
            "source": "attribute_extraction",
            "role": role
        }

        # Include existing metadata if available
        if "metadata" in attributes and isinstance(attributes["metadata"], dict):
            metadata.update(attributes["metadata"])

        # Include persona_metadata if available (for backward compatibility)
        if "persona_metadata" in attributes and isinstance(attributes["persona_metadata"], dict):
            metadata.update(attributes["persona_metadata"])

        return metadata
