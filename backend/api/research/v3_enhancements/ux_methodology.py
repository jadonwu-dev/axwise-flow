"""
V3 Enhancement: UX Research Methodology
Extracted from customer_research_v3_rebuilt.py - preserves all UX enhancements.
"""

import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class UXResearchMethodology:
    """UX Research methodology enhancements for V1 responses"""

    def enhance_suggestions(
        self, v1_suggestions: List[str], conversation_stage: str = "discovery"
    ) -> List[str]:
        """Add UX research special options to V1's proven suggestions"""

        try:
            # Only skip enhancement for explicit confirmation phase
            if conversation_stage == "confirmation":
                # Don't modify confirmation phase - V1 handles this perfectly
                return v1_suggestions

            # Add UX research methodology options
            enhanced_suggestions = v1_suggestions.copy()

            # Add "All of the above" if we have multiple good options
            if len(enhanced_suggestions) >= 2:
                enhanced_suggestions.append("All of the above")

            # Add "I don't know" for honest responses
            enhanced_suggestions.append("I don't know")

            # Add "Let me think about it" for reflection
            if conversation_stage in ["discovery", "validation"]:
                enhanced_suggestions.append("Let me think about it")

            # Limit to 5 total suggestions for good UX
            return enhanced_suggestions[:5]

        except Exception as e:
            logger.warning(f"UX suggestion enhancement failed: {e}")
            return v1_suggestions

    def enhance_response_tone(self, v1_response: str, conversation_stage: str = "discovery") -> str:
        """Enhance response tone for better UX research methodology"""

        try:
            # Don't modify if response is already good
            if self.validate_response_methodology(v1_response):
                return v1_response

            # Add encouraging tone if missing
            response = v1_response
            if not any(phrase in response.lower() for phrase in ["great", "interesting", "helpful"]):
                response = f"That's helpful! {response}"

            # Ensure single question focus
            question_count = response.count("?")
            if question_count > 2:
                # Too many questions - simplify
                sentences = response.split("?")
                if len(sentences) > 1:
                    response = sentences[0] + "?"

            return response

        except Exception as e:
            logger.warning(f"UX response enhancement failed: {e}")
            return v1_response

    def validate_response_methodology(self, response_content: str) -> bool:
        """Validate that response follows UX research methodology"""

        try:
            # Check for UX research best practices
            content_lower = response_content.lower()

            # Good: Single focused question
            question_count = content_lower.count("?")
            if question_count > 2:
                return False  # Too many questions at once

            # Good: Builds on previous answers
            if any(
                phrase in content_lower
                for phrase in ["you mentioned", "you said", "you shared"]
            ):
                return True

            # Good: Professional tone
            if any(
                phrase in content_lower
                for phrase in ["understand", "help me", "could you"]
            ):
                return True

            return True  # Default to accepting V1's proven responses

        except Exception:
            return True  # Default to accepting V1 responses

    def get_stage_specific_guidance(self, conversation_stage: str) -> Dict[str, Any]:
        """Get UX research guidance for specific conversation stages"""

        stage_guidance = {
            "business_discovery": {
                "focus": "Understanding the business idea clearly",
                "avoid": "Leading questions about solutions",
                "encourage": "Open-ended exploration of the concept"
            },
            "customer_discovery": {
                "focus": "Identifying specific target customers",
                "avoid": "Generic 'users' or 'people'",
                "encourage": "Specific demographics and characteristics"
            },
            "problem_discovery": {
                "focus": "Understanding the real problem being solved",
                "avoid": "Assuming the problem is obvious",
                "encourage": "Evidence of the problem's impact"
            },
            "validation_and_refinement": {
                "focus": "Confirming understanding before questions",
                "avoid": "Rushing to question generation",
                "encourage": "Summary and confirmation"
            },
            "ready_for_questions": {
                "focus": "Generating comprehensive research questions",
                "avoid": "Generic or template questions",
                "encourage": "Context-specific, actionable questions"
            }
        }

        return stage_guidance.get(conversation_stage, {
            "focus": "Understanding the user's needs",
            "avoid": "Making assumptions",
            "encourage": "Active listening and clarification"
        })

    def should_apply_enhancement(self, conversation_stage: str, v1_response: str) -> bool:
        """Determine if UX enhancement should be applied"""

        try:
            # Always enhance suggestions (low risk)
            if "suggestions" in conversation_stage:
                return True

            # Enhance response tone if it's too dry
            if len(v1_response) > 50 and not any(
                word in v1_response.lower() 
                for word in ["great", "interesting", "helpful", "that's"]
            ):
                return True

            # Don't enhance if V1 response is already good
            if self.validate_response_methodology(v1_response):
                return False

            return True

        except Exception:
            return False  # Conservative - don't enhance if unsure

    def get_enhancement_metadata(self) -> Dict[str, Any]:
        """Get metadata about UX methodology enhancements"""

        return {
            "enhancement_type": "ux_methodology",
            "version": "v3_rebuilt",
            "features": [
                "suggestion_enhancement",
                "response_tone_improvement", 
                "methodology_validation",
                "stage_specific_guidance"
            ],
            "methodology_principles": [
                "single_focused_questions",
                "builds_on_previous_answers",
                "professional_encouraging_tone",
                "honest_response_options"
            ]
        }
