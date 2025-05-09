"""
Persona formation service that orchestrates the persona generation process.

This service coordinates the following steps:
1. Parsing and structuring raw transcripts
2. Extracting attributes from text
3. Building personas from attributes
4. Handling error cases and creating fallback personas
"""

from typing import List, Dict, Any, Optional, Union, Tuple
import asyncio
import json
import logging
from datetime import datetime
import re

# Import our new modules
from .transcript_processor import TranscriptProcessor
from .attribute_extractor import AttributeExtractor
from .persona_builder import PersonaBuilder, persona_to_dict, Persona
from .prompts import PromptGenerator

# Import LLM interface
try:
    # Try to import from backend structure
    from backend.domain.interfaces.llm import ILLMService
except ImportError:
    try:
        # Try to import from regular structure
        from domain.interfaces.llm import ILLMService
    except ImportError:
        # Create a minimal interface if both fail
        logger = logging.getLogger(__name__)
        logger.warning(
            "Could not import ILLMService interface, using minimal definition"
        )

        class ILLMService:
            """Minimal LLM service interface"""

            async def generate_response(self, *args, **kwargs):
                raise NotImplementedError("This is a minimal interface")

# Add error handling for event imports
try:
    from backend.infrastructure.events.event_manager import event_manager, EventType
    logger = logging.getLogger(__name__)
    logger.info("Successfully imported event_manager from backend.infrastructure.events")
except ImportError:
    try:
        from infrastructure.events.event_manager import event_manager, EventType
        logger = logging.getLogger(__name__)
        logger.info("Successfully imported event_manager from infrastructure.events")
    except ImportError:
        # Use the fallback events implementation
        try:
            from backend.infrastructure.state.events import event_manager, EventType
            logger = logging.getLogger(__name__)
            logger.info("Using fallback event_manager from backend.infrastructure.state.events")
        except ImportError:
            try:
                from infrastructure.state.events import event_manager, EventType
                logger = logging.getLogger(__name__)
                logger.info("Using fallback event_manager from infrastructure.state.events")
            except ImportError:
                # Create minimal event system if all imports fail
                logger = logging.getLogger(__name__)
                logger.error("Failed to import events system, using minimal event logging")
                from enum import Enum

                class EventType(Enum):
                    """Minimal event types for error handling"""
                    PROCESSING_STATUS = "PROCESSING_STATUS"
                    PROCESSING_ERROR = "PROCESSING_ERROR"
                    PROCESSING_STEP = "PROCESSING_STEP"
                    PROCESSING_COMPLETED = "PROCESSING_COMPLETED"

                class MinimalEventManager:
                    """Minimal event manager for logging only"""
                    async def emit(self, event_type, payload=None):
                        logger.info(f"Event: {event_type}, Payload: {payload}")

                    async def emit_error(self, error, context=None):
                        logger.error(f"Error: {str(error)}, Context: {context}")

                event_manager = MinimalEventManager()

# Configure logging
logger = logging.getLogger(__name__)


class PersonaFormationService:
    """
    Service for forming personas from analysis patterns or raw text.

    This service orchestrates the entire persona formation process, delegating
    specific tasks to specialized modules.
    """

    def __init__(self, config, llm_service: ILLMService):
        """
        Initialize the persona formation service.

        Args:
            config: System configuration object
            llm_service: Initialized LLM service
        """
        self.config = config
        self.llm_service = llm_service
        self.min_confidence = getattr(config.validation, "min_confidence", 0.4)
        self.validation_threshold = self.min_confidence

        # Initialize our helper modules
        self.transcript_processor = TranscriptProcessor()
        self.attribute_extractor = AttributeExtractor(llm_service)
        self.persona_builder = PersonaBuilder()
        self.prompt_generator = PromptGenerator()

        logger.info(f"Initialized PersonaFormationService with {llm_service.__class__.__name__}")

    async def form_personas(self, patterns: List[Dict[str, Any]], context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Form personas from identified patterns.

        Args:
            patterns: List of identified patterns from analysis
            context: Optional additional context

        Returns:
            List of persona dictionaries
        """
        try:
            logger.info(f"Forming personas from {len(patterns)} patterns")

            # Skip if no patterns
            if not patterns or len(patterns) == 0:
                logger.warning("No patterns provided for persona formation")
                return []

            # Group patterns by similarity
            grouped_patterns = self._group_patterns(patterns)
            logger.info(f"Grouped patterns into {len(grouped_patterns)} potential personas")

            # Form a persona from each group
            personas = []

            for i, group in enumerate(grouped_patterns):
                try:
                    # Convert the group to a persona
                    attributes = await self._analyze_patterns_for_persona(group)
                    logger.debug(f"[form_personas] Attributes received from LLM for group {i}: {attributes}")

                    if attributes and isinstance(attributes, dict) and attributes.get("confidence", 0) >= self.validation_threshold:
                        try:
                            # Build persona from attributes
                            persona = self.persona_builder.build_persona_from_attributes(attributes)
                            personas.append(persona)
                            logger.info(f"Created persona: {persona.name} with confidence {persona.confidence}")
                        except Exception as persona_creation_error:
                            logger.error(f"Error creating Persona object for group {i}: {persona_creation_error}", exc_info=True)
                    else:
                        logger.warning(
                            f"Skipping persona creation for group {i} - confidence {attributes.get('confidence', 0)} "
                            f"below threshold {self.validation_threshold} or attributes invalid."
                        )
                except Exception as attr_error:
                    logger.error(f"Error analyzing persona attributes for group {i}: {str(attr_error)}", exc_info=True)

                # Emit event for tracking
                try:
                    await event_manager.emit(
                        EventType.PROCESSING_STEP,
                        {
                            "stage": "persona_formation",
                            "progress": (i + 1) / len(grouped_patterns),
                            "data": {
                                "personas_found": len(personas),
                                "groups_processed": i + 1,
                            },
                        },
                    )
                except Exception as event_error:
                    logger.warning(f"Could not emit processing step event: {str(event_error)}")

            # If no personas were created, try to create a default one
            if not personas:
                logger.warning("No personas created from patterns, creating default persona")
                personas = await self._create_default_persona(context)

            logger.info(f"[form_personas] Returning {len(personas)} personas.")
            # Convert Persona objects to dictionaries before returning
            return [persona_to_dict(p) for p in personas]

        except Exception as e:
            logger.error(f"Error creating personas: {str(e)}", exc_info=True)
            try:
                await event_manager.emit_error(e, {"stage": "persona_formation"})
            except Exception as event_error:
                logger.warning(f"Could not emit error event: {str(event_error)}")
            # Return empty list instead of raising to prevent analysis failure
            return []

    async def generate_persona_from_text(
        self, text: Union[str, List[Dict[str, Any]]], context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate persona directly from raw interview text.

        Args:
            text: Raw interview transcript text or structured transcript data
            context: Optional additional context information

        Returns:
            List of persona dictionaries
        """
        try:
            logger.info(f"Generating persona from text of type {type(text)}")

            # Check if text is already a structured transcript
            is_structured_transcript = False
            if isinstance(text, list) and len(text) > 0:
                # Check if it has the expected structure
                if all(isinstance(item, dict) and "speaker" in item and "text" in item for item in text):
                    is_structured_transcript = True
                    logger.info("Input is already a structured transcript")

            # If we have a structured transcript, use it directly
            if is_structured_transcript:
                return await self.form_personas_from_transcript(text, context=context)

            # If we still don't have a structured transcript, use our robust parsing and LLM conversion
            if isinstance(text, str) and not is_structured_transcript:
                logger.info("No structured format detected, using robust parsing and LLM conversion")

                # First try to parse the transcript using pattern matching
                structured_transcript = self.transcript_processor.parse_raw_transcript_to_structured(text)

                if structured_transcript and len(structured_transcript) > 0:
                    logger.info(f"Successfully parsed transcript using pattern matching: {len(structured_transcript)} speakers")
                    return await self.form_personas_from_transcript(structured_transcript, context=context)

                # If pattern matching fails, use LLM to convert free-text to structured format
                logger.info("Pattern matching failed, using LLM to convert free-text to structured format")
                structured_transcript = await self._convert_free_text_to_structured_transcript(text, context)

                if structured_transcript and len(structured_transcript) > 0:
                    logger.info(f"Successfully converted free-text to structured format with {len(structured_transcript)} speakers")
                    return await self.form_personas_from_transcript(structured_transcript, context=context)

            # If it's a Teams-like transcript with timestamps and speakers
            if isinstance(text, str) and re.search(r'\[\d+:\d+ [AP]M\] \w+:', text):
                logger.info("Detected Teams-like transcript format")
                # Parse the Teams format into a structured transcript
                transcript_data = []
                for line in text.split('\n'):
                    match = re.match(r'\[(\d+:\d+ [AP]M)\] (\w+): (.*)', line)
                    if match:
                        timestamp, speaker, content = match.groups()
                        transcript_data.append({
                            'timestamp': timestamp,
                            'speaker': speaker,
                            'text': content
                        })

                if transcript_data:
                    logger.info(f"Parsed Teams transcript into {len(transcript_data)} entries")
                    return await self.form_personas_from_transcript(transcript_data, context=context)

            # If all structured parsing attempts fail, fall back to direct text analysis
            logger.info("All structured parsing attempts failed, falling back to direct text analysis")

            # Create a prompt for persona formation
            prompt = self.prompt_generator.create_participant_prompt(text if isinstance(text, str) else str(text))

            # Method 1: Use standard analyze method (preferred)
            try:
                text_to_analyze = text if isinstance(text, str) else str(text)

                # Use more text for analysis with Gemini 2.5 Pro's larger context window
                if len(text_to_analyze) > 16000:  # If text is very long, use a reasonable chunk
                    logger.info(f"Text is very long ({len(text_to_analyze)} chars), using first 16000 chars")
                    text_to_analyze = text_to_analyze[:16000]

                llm_response = await self.llm_service.analyze({
                    "task": "persona_formation",
                    "text": text_to_analyze,  # Use more text for analysis with Gemini 2.5 Pro
                    "prompt": prompt,
                    "enforce_json": True  # Flag to enforce JSON output using response_mime_type
                })

                # Parse the response
                attributes = self._parse_llm_json_response(llm_response, "generate_persona_from_text via analyze")

                if attributes and isinstance(attributes, dict):
                    # Build persona from attributes
                    persona = self.persona_builder.build_persona_from_attributes(attributes)
                    return [persona_to_dict(persona)]
            except Exception as e:
                logger.error(f"Error generating persona from text: {str(e)}", exc_info=True)

            # Fallback to default persona creation if all else fails
            logger.warning("All persona generation methods failed, creating default persona")
            context_with_text = context or {}
            context_with_text["original_text"] = text
            personas = await self._create_default_persona(context_with_text)

            # Convert to dictionaries and return
            return [persona_to_dict(p) for p in personas]

        except Exception as e:
            logger.error(f"Error generating persona from text: {str(e)}", exc_info=True)
            try:
                await event_manager.emit_error(e, {"stage": "generate_persona_from_text"})
            except Exception as event_error:
                logger.warning(f"Could not emit error event: {str(event_error)}")
            # Return empty list instead of raising to prevent analysis failure
            return []

    async def form_personas_from_transcript(
        self, transcript: List[Dict[str, Any]],
        participants: Optional[List[Dict[str, Any]]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate personas from a structured transcript with speaker identification.

        Args:
            transcript: List of transcript entries with speaker and text fields
            participants: Optional list of participant information with roles
            context: Optional additional context information

        Returns:
            List of persona dictionaries
        """
        try:
            logger.info(f"Forming personas from transcript with {len(transcript)} entries")

            # Group text by speaker
            speaker_texts = self.transcript_processor.group_text_by_speaker(transcript)
            logger.info(f"Grouped text by {len(speaker_texts)} speakers")

            # Identify roles if not provided
            speaker_roles = {}
            if participants and isinstance(participants, list):
                # Use provided participant roles
                for participant in participants:
                    if "name" in participant and "role" in participant:
                        speaker_roles[participant["name"]] = participant["role"]
                logger.info(f"Using {len(speaker_roles)} provided participant roles")
            else:
                # Identify roles from text patterns
                speaker_roles = self.transcript_processor.identify_roles(speaker_texts)
                logger.info(f"Identified {len(speaker_roles)} speaker roles from text patterns")

            # Generate a persona for each speaker
            personas = []

            for i, (speaker, text) in enumerate(speaker_texts.items()):
                try:
                    # Get the role for this speaker
                    role = speaker_roles.get(speaker, "Participant")
                    logger.info(f"Generating persona for {speaker} with role {role}")

                    # Create a context object for this speaker
                    speaker_context = {
                        "speaker": speaker,
                        "role": role,
                        **(context or {})
                    }

                    # Create a prompt based on the role
                    prompt = self.prompt_generator.create_persona_prompt(text, role)

                    # Call LLM to generate persona
                    # Use more text for analysis with Gemini 2.5 Pro's larger context window
                    text_to_analyze = text
                    if len(text) > 16000:  # If text is very long, use a reasonable chunk
                        logger.info(f"Text for {speaker} is very long ({len(text)} chars), using first 16000 chars")
                        text_to_analyze = text[:16000]

                    llm_response = await self.llm_service.analyze({
                        "task": "persona_formation",
                        "text": text_to_analyze,  # Use more text for analysis with Gemini 2.5 Pro
                        "prompt": prompt,
                        "enforce_json": True  # Flag to enforce JSON output using response_mime_type
                    })

                    # Parse the response
                    persona_data = self._parse_llm_json_response(llm_response, f"form_personas_from_transcript for {speaker}")

                    if persona_data and isinstance(persona_data, dict):
                        # Extract name from text if not provided
                        name_override = self.transcript_processor.extract_name_from_text(text, role)

                        # Build persona from attributes
                        persona = self.persona_builder.build_persona_from_attributes(persona_data, name_override, role)
                        personas.append(persona_to_dict(persona))
                        logger.info(f"Successfully created persona for {speaker}: {persona.name}")
                    else:
                        logger.warning(f"Failed to generate valid persona data for {speaker}")
                        # Create a minimal persona for this speaker
                        minimal_persona = self.persona_builder.create_fallback_persona(role)
                        personas.append(persona_to_dict(minimal_persona))

                except Exception as e:
                    logger.error(f"Error generating persona for speaker {speaker}: {str(e)}", exc_info=True)
                    # Create a minimal persona for this speaker with speaker and role information
                    role = speaker_roles.get(speaker, "Participant")
                    minimal_persona = self.persona_builder.create_fallback_persona(role)
                    personas.append(persona_to_dict(minimal_persona))

                # Emit progress event
                try:
                    await event_manager.emit(
                        EventType.PROCESSING_STEP,
                        {
                            "stage": "persona_formation_from_transcript",
                            "progress": (i + 1) / len(speaker_texts),
                            "data": {
                                "personas_found": len(personas),
                                "speakers_processed": i + 1,
                            },
                        },
                    )
                except Exception as event_error:
                    logger.warning(f"Could not emit processing step event: {str(event_error)}")

            logger.info(f"Returning {len(personas)} personas from transcript")
            return personas

        except Exception as e:
            logger.error(f"Error forming personas from transcript: {str(e)}", exc_info=True)
            try:
                await event_manager.emit_error(e, {"stage": "form_personas_from_transcript"})
            except Exception as event_error:
                logger.warning(f"Could not emit error event: {str(event_error)}")
            # Return empty list instead of raising to prevent analysis failure
            return []

    async def _analyze_patterns_for_persona(self, patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze patterns to extract persona attributes.

        Args:
            patterns: List of patterns to analyze

        Returns:
            Dictionary of persona attributes
        """
        try:
            logger.info(f"Analyzing {len(patterns)} patterns for persona attributes")

            # Convert patterns to a string representation for the prompt
            pattern_descriptions = "\n".join([
                f"Pattern {i+1}: {p.get('name', 'Unnamed')} - {p.get('description', 'No description')} "
                f"(Evidence: {', '.join(p.get('evidence', [])[:3])})"
                for i, p in enumerate(patterns)
            ])

            # Create a prompt for pattern-based persona formation
            prompt = self.prompt_generator.create_pattern_prompt(pattern_descriptions)

            # Call LLM to analyze patterns
            llm_response = await self.llm_service.analyze({
                "task": "persona_formation",
                "text": pattern_descriptions,
                "prompt": prompt,
                "enforce_json": True
            })

            # Parse the response
            attributes = self._parse_llm_json_response(llm_response, "_analyze_patterns_for_persona")

            if attributes and isinstance(attributes, dict):
                logger.info(f"Successfully parsed persona attributes from patterns.")
                return attributes
            else:
                logger.warning("Failed to parse valid JSON attributes from LLM for pattern analysis.")
                return self._create_fallback_attributes(patterns)

        except Exception as e:
            logger.error(f"Error analyzing patterns for persona: {str(e)}", exc_info=True)
            return self._create_fallback_attributes(patterns)

    async def _convert_free_text_to_structured_transcript(
        self, text: str, context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Convert free-text transcript to structured JSON format with speaker and text fields.

        Args:
            text: Raw interview transcript text
            context: Optional additional context information

        Returns:
            List of dictionaries with speaker and text fields
        """
        try:
            logger.info("Converting free-text to structured transcript format")

            # Create a prompt for transcript structuring
            prompt = self.prompt_generator.create_transcript_structuring_prompt(text)

            # Call LLM to convert text to structured format
            llm_response = await self.llm_service.analyze({
                "task": "persona_formation",
                "prompt": prompt,
                "is_json_task": True,
                "temperature": 0
            })

            # Parse the response
            structured_data = self._parse_llm_json_response(llm_response, "convert_free_text_to_structured_transcript")

            if structured_data and isinstance(structured_data, list):
                logger.info(f"Successfully converted free-text to structured format with {len(structured_data)} speakers")
                return structured_data
            else:
                logger.warning("Failed to convert free-text to structured format")
                return []

        except Exception as e:
            logger.error(f"Error converting free-text to structured transcript: {str(e)}", exc_info=True)
            return []

    async def _create_default_persona(self, context: Optional[Dict[str, Any]] = None) -> List[Persona]:
        """
        Create a default persona when no patterns are available.

        Args:
            context: Optional additional context information

        Returns:
            List containing a single default Persona
        """
        try:
            logger.info("Creating default persona")

            # Check if we have original text in the context
            original_text = ""
            if context and "original_text" in context:
                original_text = context["original_text"]
                if isinstance(original_text, list):
                    # If it's a structured transcript, convert to text
                    original_text = "\n".join([
                        f"{entry.get('speaker', 'Unknown')}: {entry.get('text', '')}"
                        for entry in original_text
                    ])

                logger.info(f"Using original text from context ({len(original_text)} chars)")

                # Create a prompt for persona formation
                prompt = self.prompt_generator.create_participant_prompt(original_text[:16000])

                # Call LLM for persona creation
                llm_response = await self.llm_service.analyze({
                    "task": "persona_formation",
                    "text": original_text[:16000],
                    "prompt": prompt,
                    "enforce_json": True
                })

                # Parse the response
                persona_data = self._parse_llm_json_response(llm_response, "_create_default_persona")

                if persona_data and isinstance(persona_data, dict):
                    # Build persona from attributes
                    persona = self.persona_builder.build_persona_from_attributes(persona_data)
                    return [persona]

            # If we don't have original text or persona creation failed, create a fallback persona
            logger.info("Creating fallback persona")
            return [self.persona_builder.create_fallback_persona()]

        except Exception as e:
            logger.error(f"Error creating default persona: {str(e)}", exc_info=True)
            return [self.persona_builder.create_fallback_persona()]

    def _create_fallback_attributes(self, patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create fallback attributes when pattern analysis fails.

        Args:
            patterns: List of patterns

        Returns:
            Dictionary of fallback attributes
        """
        logger.info("Creating fallback attributes from patterns")

        # Create a default trait
        default_trait = {
            "value": "Unknown",
            "confidence": 0.3,
            "evidence": ["Fallback due to analysis error"]
        }

        # Extract pattern descriptions for evidence
        pattern_descriptions = [
            p.get("description", "Unknown pattern")
            for p in patterns
            if p.get("description")
        ]

        # Return structure that can be processed by Persona constructor
        return {
            # Basic information
            "name": "Default Persona",
            "archetype": "Unknown",
            "description": "Default persona due to analysis error or low confidence",
            # Detailed attributes (new fields)
            "demographics": default_trait,
            "goals_and_motivations": default_trait,
            "skills_and_expertise": default_trait,
            "workflow_and_environment": default_trait,
            "challenges_and_frustrations": default_trait,
            "needs_and_desires": default_trait,
            "technology_and_tools": default_trait,
            "attitude_towards_research": default_trait,
            "attitude_towards_ai": default_trait,
            "key_quotes": default_trait,
            # Legacy fields
            "role_context": default_trait,
            "key_responsibilities": default_trait,
            "tools_used": default_trait,
            "collaboration_style": default_trait,
            "analysis_approach": default_trait,
            "pain_points": default_trait,
            # Overall persona information
            "patterns": pattern_descriptions[:5],
            "confidence": 0.3,
            "evidence": ["Fallback due to analysis error"]
        }

    def _parse_llm_json_response(self, response: Union[str, Dict[str, Any]], context: str = "") -> Dict[str, Any]:
        """
        Parse JSON response from LLM.

        Args:
            response: LLM response (string or dictionary)
            context: Context for error logging

        Returns:
            Parsed JSON as dictionary
        """
        if not response:
            logger.warning(f"Empty response from LLM in {context}")
            return {}

        # If response is already a dictionary, return it directly
        if isinstance(response, dict):
            logger.info(f"Response is already a dictionary in {context}")
            return response

        try:
            # Try to parse as JSON directly
            return json.loads(response)
        except (json.JSONDecodeError, TypeError):
            # If direct parsing fails, try to extract JSON from the response
            try:
                # If response is not a string, convert it to string
                if not isinstance(response, str):
                    logger.warning(f"Response is not a string or dict in {context}: {type(response)}")
                    response_str = str(response)
                else:
                    response_str = response

                # Look for JSON object in the response
                json_match = re.search(r'({[\s\S]*})', response_str)
                if json_match:
                    json_str = json_match.group(1)
                    return json.loads(json_str)
                else:
                    logger.warning(f"No JSON object found in response: {context}")
                    return {}
            except Exception as e:
                logger.error(f"Error parsing JSON from LLM response in {context}: {str(e)}")
                return {}

    def _group_patterns(self, patterns: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """
        Group patterns by similarity.

        Args:
            patterns: List of patterns from analysis

        Returns:
            List of pattern groups
        """
        # Simple grouping by pattern type
        grouped = {}
        for pattern in patterns:
            pattern_type = pattern.get("type", "unknown")  # Use 'type' if available, else 'category'
            if not pattern_type or pattern_type == "unknown":
                pattern_type = pattern.get("category", "unknown")

            if pattern_type not in grouped:
                grouped[pattern_type] = []
            grouped[pattern_type].append(pattern)

        # Convert to list of groups
        return list(grouped.values())
