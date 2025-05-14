"""
Evidence linking prompt templates for LLM services.

This module provides prompts for finding the most relevant quotes from
interview transcripts to support persona attributes.
"""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class EvidenceLinkingPrompts:
    """
    Evidence linking prompt templates.
    """

    @staticmethod
    def get_prompt(data: Dict[str, Any]) -> str:
        """
        Get evidence linking prompt.

        Args:
            data: Request data containing field name and trait value

        Returns:
            Prompt string
        """
        # Add support for direct prompts if provided
        if "prompt" in data and data["prompt"]:
            # Use the prompt provided directly
            return data["prompt"]

        # Get field and trait value
        field = data.get("field", "")
        trait_value = data.get("trait_value", "")

        # Format field name for better readability
        formatted_field = field.replace("_", " ").title()

        # Return the standard prompt
        return EvidenceLinkingPrompts.standard_prompt(formatted_field, trait_value)

    @staticmethod
    def standard_prompt(formatted_field: str, trait_value: str) -> str:
        """
        Get standard evidence linking prompt.

        Args:
            formatted_field: Formatted field name
            trait_value: Trait value to find evidence for

        Returns:
            System message string
        """
        return f"""
CRITICAL INSTRUCTION: Your ENTIRE response MUST be a single, valid JSON object. DO NOT include ANY text, comments, or markdown formatting (like ```json) before or after the JSON.

You are an expert UX researcher analyzing interview transcripts. Your task is to find the most relevant direct quotes that provide evidence for a specific persona trait.

PERSONA TRAIT: {formatted_field}
TRAIT VALUE: {trait_value}

INSTRUCTIONS:
1. Carefully read the interview transcript provided.
2. Identify 2-3 direct quotes that most strongly support or demonstrate the persona trait described above.
3. For each quote:
   - Include the exact words from the transcript (verbatim)
   - Include enough context to understand the quote (1-2 sentences before/after if needed)
   - Prioritize quotes that explicitly demonstrate the trait rather than vaguely relate to it
   - Ensure the quote is substantial enough to be meaningful evidence (at least 10-15 words)
4. Focus on finding quotes that directly support the specific trait value, not just the general trait category.
5. If you cannot find direct quotes supporting the trait, return an empty array.

FORMAT YOUR RESPONSE AS A SINGLE JSON OBJECT with the following structure:
{{
  "quotes": [
    "First direct quote with context...",
    "Second direct quote with context...",
    "Third direct quote with context..."
  ]
}}

IMPORTANT: 
- The quotes must be EXACT text from the transcript, not paraphrased or summarized.
- Include only the most relevant 2-3 quotes that provide the strongest evidence.
- If you cannot find relevant quotes, return an empty array: {{"quotes": []}}
"""
