"""
Prompts module for persona formation.

This module provides functionality for:
1. Generating prompts for LLM
2. Defining constants for prompt templates
"""

from typing import Dict, Any, Optional
import logging

# Configure logging
logger = logging.getLogger(__name__)


class PromptGenerator:
    """
    Generates prompts for LLM.
    """

    def __init__(self):
        """Initialize the prompt generator."""
        logger.info("Initialized PromptGenerator")

    def create_persona_prompt(self, text: str, role: str = "Participant") -> str:
        """
        Create a prompt for persona formation.

        Args:
            text: Text to analyze
            role: Role of the person (Interviewer, Interviewee, Participant)

        Returns:
            Prompt string
        """
        if role == "Interviewer":
            return self.create_interviewer_prompt(text)
        elif role == "Interviewee":
            return self.create_interviewee_prompt(text)
        else:
            return self.create_participant_prompt(text)

    def create_interviewer_prompt(self, text: str) -> str:
        """
        Create a prompt for interviewer persona formation.

        Args:
            text: Text to analyze

        Returns:
            Prompt string
        """
        return f"""
        CRITICAL INSTRUCTION: Your ENTIRE response must be a single, valid JSON object. Start with '{{' and end with '}}'. DO NOT include ANY text, comments, or markdown formatting before or after the JSON.

        Analyze the following interview text excerpt and create a comprehensive, detailed interviewer persona profile with specific, concrete details.

        INTERVIEW TEXT:
        {text}

        IMPORTANT: For each attribute, include EXACT QUOTES from the text as evidence. Do not paraphrase or summarize.
        Extract at least 3-5 direct quotes for each attribute whenever possible.

        FORMAT YOUR RESPONSE AS A SINGLE JSON OBJECT with the following structure:
        {{
            "name": "Descriptive name for the interviewer (e.g., 'Methodical UX Researcher')",
            "description": "Brief 1-3 sentence overview of the interviewer",
            "archetype": "General category (e.g., 'Research Professional', 'Design Facilitator')",
            
            "demographics": {{
                "value": "Age, experience level, professional background",
                "confidence": 0.7,
                "evidence": ["Quote 1", "Quote 2", "Quote 3"]
            }},
            "goals_and_motivations": {{
                "value": "Primary research objectives and motivations",
                "confidence": 0.8,
                "evidence": ["Quote 1", "Quote 2", "Quote 3"]
            }},
            "skills_and_expertise": {{
                "value": "Technical and soft skills demonstrated",
                "confidence": 0.75,
                "evidence": ["Quote 1", "Quote 2", "Quote 3"]
            }},
            "workflow_and_environment": {{
                "value": "Interview approach and environment",
                "confidence": 0.8,
                "evidence": ["Quote 1", "Quote 2", "Quote 3"]
            }},
            "challenges_and_frustrations": {{
                "value": "Difficulties faced during the interview",
                "confidence": 0.7,
                "evidence": ["Quote 1", "Quote 2", "Quote 3"]
            }},
            "needs_and_desires": {{
                "value": "What the interviewer is trying to achieve",
                "confidence": 0.7,
                "evidence": ["Quote 1", "Quote 2", "Quote 3"]
            }},
            "technology_and_tools": {{
                "value": "Tools or methods mentioned",
                "confidence": 0.6,
                "evidence": ["Quote 1", "Quote 2", "Quote 3"]
            }},
            "attitude_towards_research": {{
                "value": "Approach to research and data",
                "confidence": 0.8,
                "evidence": ["Quote 1", "Quote 2", "Quote 3"]
            }},
            "attitude_towards_ai": {{
                "value": "Views on AI and technology",
                "confidence": 0.6,
                "evidence": ["Quote 1", "Quote 2", "Quote 3"]
            }},
            "key_quotes": {{
                "value": "Representative quotes from the interviewer",
                "confidence": 0.9,
                "evidence": ["Quote 1", "Quote 2", "Quote 3"]
            }},
            
            "role_context": {{
                "value": "Primary job function and work environment",
                "confidence": 0.8,
                "evidence": ["Quote 1", "Quote 2", "Quote 3"]
            }},
            "key_responsibilities": {{
                "value": "Main tasks and responsibilities",
                "confidence": 0.8,
                "evidence": ["Quote 1", "Quote 2", "Quote 3"]
            }},
            "tools_used": {{
                "value": "Specific tools or methods used",
                "confidence": 0.7,
                "evidence": ["Quote 1", "Quote 2", "Quote 3"]
            }},
            "collaboration_style": {{
                "value": "How they work with others",
                "confidence": 0.7,
                "evidence": ["Quote 1", "Quote 2", "Quote 3"]
            }},
            "analysis_approach": {{
                "value": "How they approach problems/analysis",
                "confidence": 0.7,
                "evidence": ["Quote 1", "Quote 2", "Quote 3"]
            }},
            "pain_points": {{
                "value": "Specific challenges mentioned",
                "confidence": 0.7,
                "evidence": ["Quote 1", "Quote 2", "Quote 3"]
            }},
            
            "patterns": ["Pattern 1", "Pattern 2", "Pattern 3"],
            "confidence": 0.8,
            "evidence": ["Overall evidence 1", "Overall evidence 2", "Overall evidence 3"]
        }}
        """

    def create_interviewee_prompt(self, text: str) -> str:
        """
        Create a prompt for interviewee persona formation.

        Args:
            text: Text to analyze

        Returns:
            Prompt string
        """
        return f"""
        CRITICAL INSTRUCTION: Your ENTIRE response must be a single, valid JSON object. Start with '{{' and end with '}}'. DO NOT include ANY text, comments, or markdown formatting before or after the JSON.

        Analyze the following interview text excerpt and create a comprehensive, detailed user persona profile with specific, concrete details.

        INTERVIEW TEXT:
        {text}

        IMPORTANT: For each attribute, include EXACT QUOTES from the text as evidence. Do not paraphrase or summarize.
        Extract at least 3-5 direct quotes for each attribute whenever possible.

        FORMAT YOUR RESPONSE AS A SINGLE JSON OBJECT with the following structure:
        {{
            "name": "Descriptive name for the persona (e.g., 'Data-Driven Product Manager')",
            "description": "Brief 1-3 sentence overview of the persona",
            "archetype": "General category (e.g., 'Decision Maker', 'Technical Expert')",
            
            "demographics": {{
                "value": "Age, gender, education, experience level",
                "confidence": 0.7,
                "evidence": ["Quote 1", "Quote 2", "Quote 3"]
            }},
            "goals_and_motivations": {{
                "value": "Primary objectives and driving factors",
                "confidence": 0.8,
                "evidence": ["Quote 1", "Quote 2", "Quote 3"]
            }},
            "skills_and_expertise": {{
                "value": "Technical and soft skills, knowledge areas",
                "confidence": 0.75,
                "evidence": ["Quote 1", "Quote 2", "Quote 3"]
            }},
            "workflow_and_environment": {{
                "value": "Work processes and environment",
                "confidence": 0.8,
                "evidence": ["Quote 1", "Quote 2", "Quote 3"]
            }},
            "challenges_and_frustrations": {{
                "value": "Pain points and obstacles",
                "confidence": 0.7,
                "evidence": ["Quote 1", "Quote 2", "Quote 3"]
            }},
            "needs_and_desires": {{
                "value": "Specific needs and desires",
                "confidence": 0.7,
                "evidence": ["Quote 1", "Quote 2", "Quote 3"]
            }},
            "technology_and_tools": {{
                "value": "Software, hardware, and tools used",
                "confidence": 0.6,
                "evidence": ["Quote 1", "Quote 2", "Quote 3"]
            }},
            "attitude_towards_research": {{
                "value": "Views on research and data",
                "confidence": 0.8,
                "evidence": ["Quote 1", "Quote 2", "Quote 3"]
            }},
            "attitude_towards_ai": {{
                "value": "Perspective on AI and automation",
                "confidence": 0.6,
                "evidence": ["Quote 1", "Quote 2", "Quote 3"]
            }},
            "key_quotes": {{
                "value": "Representative quotes that capture the persona's voice",
                "confidence": 0.9,
                "evidence": ["Quote 1", "Quote 2", "Quote 3"]
            }},
            
            "role_context": {{
                "value": "Primary job function and work environment",
                "confidence": 0.8,
                "evidence": ["Quote 1", "Quote 2", "Quote 3"]
            }},
            "key_responsibilities": {{
                "value": "Main tasks and responsibilities",
                "confidence": 0.8,
                "evidence": ["Quote 1", "Quote 2", "Quote 3"]
            }},
            "tools_used": {{
                "value": "Specific tools or methods used",
                "confidence": 0.7,
                "evidence": ["Quote 1", "Quote 2", "Quote 3"]
            }},
            "collaboration_style": {{
                "value": "How they work with others",
                "confidence": 0.7,
                "evidence": ["Quote 1", "Quote 2", "Quote 3"]
            }},
            "analysis_approach": {{
                "value": "How they approach problems/analysis",
                "confidence": 0.7,
                "evidence": ["Quote 1", "Quote 2", "Quote 3"]
            }},
            "pain_points": {{
                "value": "Specific challenges mentioned",
                "confidence": 0.7,
                "evidence": ["Quote 1", "Quote 2", "Quote 3"]
            }},
            
            "patterns": ["Pattern 1", "Pattern 2", "Pattern 3"],
            "confidence": 0.8,
            "evidence": ["Overall evidence 1", "Overall evidence 2", "Overall evidence 3"]
        }}
        """

    def create_participant_prompt(self, text: str) -> str:
        """
        Create a prompt for general participant persona formation.

        Args:
            text: Text to analyze

        Returns:
            Prompt string
        """
        return f"""
        CRITICAL INSTRUCTION: Your ENTIRE response must be a single, valid JSON object. Start with '{{' and end with '}}'. DO NOT include ANY text, comments, or markdown formatting before or after the JSON.

        Analyze the following text excerpt and create a comprehensive, detailed persona profile with specific, concrete details.

        TEXT:
        {text}

        IMPORTANT: For each attribute, include EXACT QUOTES from the text as evidence. Do not paraphrase or summarize.
        Extract at least 3-5 direct quotes for each attribute whenever possible.

        FORMAT YOUR RESPONSE AS A SINGLE JSON OBJECT with the following structure:
        {{
            "name": "Descriptive name for the persona (e.g., 'Analytical Business Strategist')",
            "description": "Brief 1-3 sentence overview of the persona",
            "archetype": "General category (e.g., 'Decision Maker', 'Technical Expert')",
            
            "demographics": {{
                "value": "Age, gender, education, experience level",
                "confidence": 0.7,
                "evidence": ["Quote 1", "Quote 2", "Quote 3"]
            }},
            "goals_and_motivations": {{
                "value": "Primary objectives and driving factors",
                "confidence": 0.8,
                "evidence": ["Quote 1", "Quote 2", "Quote 3"]
            }},
            "skills_and_expertise": {{
                "value": "Technical and soft skills, knowledge areas",
                "confidence": 0.75,
                "evidence": ["Quote 1", "Quote 2", "Quote 3"]
            }},
            "workflow_and_environment": {{
                "value": "Work processes and environment",
                "confidence": 0.8,
                "evidence": ["Quote 1", "Quote 2", "Quote 3"]
            }},
            "challenges_and_frustrations": {{
                "value": "Pain points and obstacles",
                "confidence": 0.7,
                "evidence": ["Quote 1", "Quote 2", "Quote 3"]
            }},
            "needs_and_desires": {{
                "value": "Specific needs and desires",
                "confidence": 0.7,
                "evidence": ["Quote 1", "Quote 2", "Quote 3"]
            }},
            "technology_and_tools": {{
                "value": "Software, hardware, and tools used",
                "confidence": 0.6,
                "evidence": ["Quote 1", "Quote 2", "Quote 3"]
            }},
            "attitude_towards_research": {{
                "value": "Views on research and data",
                "confidence": 0.8,
                "evidence": ["Quote 1", "Quote 2", "Quote 3"]
            }},
            "attitude_towards_ai": {{
                "value": "Perspective on AI and automation",
                "confidence": 0.6,
                "evidence": ["Quote 1", "Quote 2", "Quote 3"]
            }},
            "key_quotes": {{
                "value": "Representative quotes that capture the persona's voice",
                "confidence": 0.9,
                "evidence": ["Quote 1", "Quote 2", "Quote 3"]
            }},
            
            "role_context": {{
                "value": "Primary job function and work environment",
                "confidence": 0.8,
                "evidence": ["Quote 1", "Quote 2", "Quote 3"]
            }},
            "key_responsibilities": {{
                "value": "Main tasks and responsibilities",
                "confidence": 0.8,
                "evidence": ["Quote 1", "Quote 2", "Quote 3"]
            }},
            "tools_used": {{
                "value": "Specific tools or methods used",
                "confidence": 0.7,
                "evidence": ["Quote 1", "Quote 2", "Quote 3"]
            }},
            "collaboration_style": {{
                "value": "How they work with others",
                "confidence": 0.7,
                "evidence": ["Quote 1", "Quote 2", "Quote 3"]
            }},
            "analysis_approach": {{
                "value": "How they approach problems/analysis",
                "confidence": 0.7,
                "evidence": ["Quote 1", "Quote 2", "Quote 3"]
            }},
            "pain_points": {{
                "value": "Specific challenges mentioned",
                "confidence": 0.7,
                "evidence": ["Quote 1", "Quote 2", "Quote 3"]
            }},
            
            "patterns": ["Pattern 1", "Pattern 2", "Pattern 3"],
            "confidence": 0.8,
            "evidence": ["Overall evidence 1", "Overall evidence 2", "Overall evidence 3"]
        }}
        """

    def create_pattern_prompt(self, patterns: str) -> str:
        """
        Create a prompt for pattern-based persona formation.

        Args:
            patterns: Pattern descriptions

        Returns:
            Prompt string
        """
        return f"""
        CRITICAL INSTRUCTION: Your ENTIRE response must be a single, valid JSON object. Start with '{{' and end with '}}'. DO NOT include ANY text, comments, or markdown formatting before or after the JSON.

        Analyze the following patterns identified in an interview and create a comprehensive, detailed persona profile.

        PATTERNS:
        {patterns}

        IMPORTANT: For each attribute, include specific references to the patterns as evidence.
        Extract at least 3-5 specific references for each attribute whenever possible.

        FORMAT YOUR RESPONSE AS A SINGLE JSON OBJECT with the following structure:
        {{
            "name": "Descriptive name for the persona (e.g., 'Data-Driven Product Manager')",
            "description": "Brief 1-3 sentence overview of the persona",
            "archetype": "General category (e.g., 'Decision Maker', 'Technical Expert')",
            
            "demographics": {{
                "value": "Age, gender, education, experience level",
                "confidence": 0.7,
                "evidence": ["Pattern reference 1", "Pattern reference 2", "Pattern reference 3"]
            }},
            "goals_and_motivations": {{
                "value": "Primary objectives and driving factors",
                "confidence": 0.8,
                "evidence": ["Pattern reference 1", "Pattern reference 2", "Pattern reference 3"]
            }},
            "skills_and_expertise": {{
                "value": "Technical and soft skills, knowledge areas",
                "confidence": 0.75,
                "evidence": ["Pattern reference 1", "Pattern reference 2", "Pattern reference 3"]
            }},
            "workflow_and_environment": {{
                "value": "Work processes and environment",
                "confidence": 0.8,
                "evidence": ["Pattern reference 1", "Pattern reference 2", "Pattern reference 3"]
            }},
            "challenges_and_frustrations": {{
                "value": "Pain points and obstacles",
                "confidence": 0.7,
                "evidence": ["Pattern reference 1", "Pattern reference 2", "Pattern reference 3"]
            }},
            "needs_and_desires": {{
                "value": "Specific needs and desires",
                "confidence": 0.7,
                "evidence": ["Pattern reference 1", "Pattern reference 2", "Pattern reference 3"]
            }},
            "technology_and_tools": {{
                "value": "Software, hardware, and tools used",
                "confidence": 0.6,
                "evidence": ["Pattern reference 1", "Pattern reference 2", "Pattern reference 3"]
            }},
            "attitude_towards_research": {{
                "value": "Views on research and data",
                "confidence": 0.8,
                "evidence": ["Pattern reference 1", "Pattern reference 2", "Pattern reference 3"]
            }},
            "attitude_towards_ai": {{
                "value": "Perspective on AI and automation",
                "confidence": 0.6,
                "evidence": ["Pattern reference 1", "Pattern reference 2", "Pattern reference 3"]
            }},
            "key_quotes": {{
                "value": "Representative quotes that capture the persona's voice",
                "confidence": 0.9,
                "evidence": ["Pattern reference 1", "Pattern reference 2", "Pattern reference 3"]
            }},
            
            "role_context": {{
                "value": "Primary job function and work environment",
                "confidence": 0.8,
                "evidence": ["Pattern reference 1", "Pattern reference 2", "Pattern reference 3"]
            }},
            "key_responsibilities": {{
                "value": "Main tasks and responsibilities",
                "confidence": 0.8,
                "evidence": ["Pattern reference 1", "Pattern reference 2", "Pattern reference 3"]
            }},
            "tools_used": {{
                "value": "Specific tools or methods used",
                "confidence": 0.7,
                "evidence": ["Pattern reference 1", "Pattern reference 2", "Pattern reference 3"]
            }},
            "collaboration_style": {{
                "value": "How they work with others",
                "confidence": 0.7,
                "evidence": ["Pattern reference 1", "Pattern reference 2", "Pattern reference 3"]
            }},
            "analysis_approach": {{
                "value": "How they approach problems/analysis",
                "confidence": 0.7,
                "evidence": ["Pattern reference 1", "Pattern reference 2", "Pattern reference 3"]
            }},
            "pain_points": {{
                "value": "Specific challenges mentioned",
                "confidence": 0.7,
                "evidence": ["Pattern reference 1", "Pattern reference 2", "Pattern reference 3"]
            }},
            
            "patterns": ["Pattern 1", "Pattern 2", "Pattern 3"],
            "confidence": 0.8,
            "evidence": ["Overall evidence 1", "Overall evidence 2", "Overall evidence 3"]
        }}
        """

    def create_transcript_structuring_prompt(self, text: str) -> str:
        """
        Create a prompt for transcript structuring.

        Args:
            text: Raw transcript text

        Returns:
            Prompt string
        """
        return f"""
        Analyze the following interview transcript and convert it to a structured JSON format.

        INTERVIEW TRANSCRIPT:
        {text}

        Identify all distinct speakers in the conversation and extract their dialogue.

        FORMAT YOUR RESPONSE AS JSON with the following structure:
        [
            {{
                "speaker": "Name of first speaker",
                "text": "All text spoken by this speaker concatenated together"
            }},
            {{
                "speaker": "Name of second speaker",
                "text": "All text spoken by this speaker concatenated together"
            }},
            ...
        ]

        IMPORTANT GUIDELINES:
        1. Identify each unique speaker in the conversation
        2. For each speaker, extract all their dialogue and combine it
        3. If the speaker's role is clear (e.g., "Interviewer" or "Interviewee"), use that as the speaker name
        4. If there are timestamps or other metadata, you can ignore them
        5. Focus on extracting the actual content of the conversation
        6. Ensure your response is valid JSON that can be parsed programmatically
        """
