"""
Trait formatting prompt templates for LLM services.

This module provides prompts for formatting persona trait values to make them
more natural, concise, and readable.
"""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class TraitFormattingPrompts:
    """
    Trait formatting prompt templates.
    """

    @staticmethod
    def get_prompt(data: Dict[str, Any]) -> str:
        """
        Get trait formatting prompt.

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
        return TraitFormattingPrompts.standard_prompt(formatted_field, trait_value)

    @staticmethod
    def standard_prompt(formatted_field: str, trait_value: str) -> str:
        """
        Get standard trait formatting prompt.

        Args:
            formatted_field: Formatted field name
            trait_value: Trait value to format

        Returns:
            System message string
        """
        return f"""
CRITICAL INSTRUCTION: Your ENTIRE response MUST be ONLY the rephrased text. DO NOT include ANY explanations, apologies, or introductory phrases.

You are an expert UX researcher specializing in creating clear, concise persona descriptions. Your task is to improve the formatting and clarity of a persona trait value while preserving its original meaning.

PERSONA TRAIT: {formatted_field}
CURRENT VALUE: {trait_value}

INSTRUCTIONS:
1. Rewrite the trait value to be more clear, concise, and natural-sounding.
2. Preserve ALL the original information and meaning.
3. Fix any awkward phrasing, grammatical errors, or formatting issues.
4. Format lists appropriately (use bullet points if there are multiple distinct items).
5. Remove redundancies and unnecessary words.
6. Ensure the tone is professional and objective.
7. DO NOT add any new information that wasn't in the original.

FORMATTING GUIDELINES:
- For lists, use bullet points (•) with one item per line
- For demographics, ensure age, experience level, and role are clearly stated
- For tools/technologies, format as a clean list if multiple items are present
- For goals/motivations, ensure they are expressed as clear statements
- For challenges/frustrations, ensure they are specific and actionable

FINAL REMINDER: Your response must contain ONLY the improved text. No explanations, no "Here's the improved text:", no "I've reformatted this to...", just the text itself.
"""
