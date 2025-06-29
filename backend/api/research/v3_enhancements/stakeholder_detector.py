"""
V3 Enhancement: Advanced Stakeholder Detection
Extracted from customer_research_v3_rebuilt.py - preserves stakeholder detection logic.
"""

import logging
from typing import Dict, Any, List, Optional
from backend.api.research.research_types import Message, ResearchContext

logger = logging.getLogger(__name__)


class StakeholderDetector:
    """Advanced stakeholder detection with unique questions for each stakeholder type"""

    def __init__(self):
        logger.info("🏗️ V3 Stakeholder Detector initialized")

    async def generate_dynamic_stakeholders_with_unique_questions(
        self,
        llm_service,
        context_analysis: Dict[str, Any],
        messages: List[Message],
        business_idea: str,
        target_customer: str,
        problem: str,
    ) -> Dict[str, Any]:
        """Generate stakeholders with unique questions for each stakeholder type"""
        try:
            logger.info("👥 Generating dynamic stakeholders with unique questions")

            # Step 1: Generate stakeholder names and descriptions
            stakeholder_data = await self._generate_stakeholder_names_and_descriptions(
                llm_service, context_analysis, messages
            )

            # Step 2: Generate unique questions for each stakeholder
            enhanced_stakeholders = await self._generate_questions_for_stakeholders(
                llm_service, stakeholder_data, business_idea, target_customer, problem
            )

            logger.info(
                f"✅ Generated {len(enhanced_stakeholders.get('primary', []))} primary and {len(enhanced_stakeholders.get('secondary', []))} secondary stakeholders with unique questions"
            )
            return enhanced_stakeholders

        except Exception as e:
            logger.error(f"Dynamic stakeholder generation failed: {e}")
            return {"primary": [], "secondary": []}

    async def _generate_stakeholder_names_and_descriptions(
        self, llm_service, context_analysis: Dict[str, Any], messages: List[Message]
    ) -> Dict[str, Any]:
        """Generate stakeholder names and descriptions"""
        try:
            business_idea = context_analysis.get("business_idea", "")
            target_customer = context_analysis.get("target_customer", "")
            problem = context_analysis.get("problem", "")

            # Build conversation context
            conversation_text = ""
            for msg in messages[-5:]:  # Last 5 messages for context
                conversation_text += f"{msg.role}: {msg.content}\n"

            prompt = f"""Analyze this business context and identify specific stakeholders for customer research.

Business Context:
- Business Idea: {business_idea}
- Target Customer: {target_customer}
- Problem Being Solved: {problem}

Recent Conversation:
{conversation_text}

Identify specific stakeholders (not generic roles):

1. PRIMARY stakeholders (2-3 max):
   - Direct users who would actually use the solution
   - People who experience the problem firsthand
   - Decision makers for purchasing/adoption

2. SECONDARY stakeholders (1-2 max):
   - People who influence decisions but may not use directly
   - People affected by the solution indirectly
   - Gatekeepers or advisors

For each stakeholder, provide:
- name: Specific, descriptive name (not "Primary User")
- description: Brief description of their role and relationship to the business

Return as JSON:
{{
  "primary": [
    {{"name": "Busy Office Workers", "description": "Professionals who need quick coffee between meetings"}},
    ...
  ],
  "secondary": [
    {{"name": "Office Managers", "description": "People who decide on office amenities and vendor relationships"}},
    ...
  ]
}}

Make stakeholder names specific to this business context."""

            response_data = await llm_service.analyze(
                text=prompt,
                task="text_generation",
                data={"temperature": 0.6, "max_tokens": 600},
            )
            response = response_data.get("text", "")

            # Parse JSON response (handle markdown code blocks)
            import json
            import re

            try:
                # Remove markdown code blocks if present
                cleaned_response = response.strip()
                if cleaned_response.startswith("```json"):
                    json_match = re.search(
                        r"```json\s*\n(.*?)\n```", cleaned_response, re.DOTALL
                    )
                    if json_match:
                        cleaned_response = json_match.group(1).strip()
                    else:
                        cleaned_response = (
                            cleaned_response.replace("```json", "")
                            .replace("```", "")
                            .strip()
                        )

                stakeholder_data = json.loads(cleaned_response)
                return stakeholder_data
            except json.JSONDecodeError:
                logger.warning("Failed to parse stakeholder names response as JSON")
                return {"primary": [], "secondary": []}

        except Exception as e:
            logger.error(f"Stakeholder name generation failed: {e}")
            return {"primary": [], "secondary": []}

    async def _generate_questions_for_stakeholders(
        self,
        llm_service,
        stakeholder_data: Dict[str, Any],
        business_idea: str,
        target_customer: str,
        problem: str,
    ) -> Dict[str, Any]:
        """Generate unique questions for each stakeholder"""
        try:
            enhanced_stakeholders = {"primary": [], "secondary": []}

            # Generate questions for primary stakeholders
            for stakeholder in stakeholder_data.get("primary", []):
                questions = await self._generate_stakeholder_specific_questions(
                    llm_service,
                    stakeholder["name"],
                    stakeholder["description"],
                    business_idea,
                    target_customer,
                    problem,
                    "primary",
                )
                enhanced_stakeholders["primary"].append(
                    {
                        "name": stakeholder["name"],
                        "description": stakeholder["description"],
                        "questions": questions,
                    }
                )

            # Generate questions for secondary stakeholders
            for stakeholder in stakeholder_data.get("secondary", []):
                questions = await self._generate_stakeholder_specific_questions(
                    llm_service,
                    stakeholder["name"],
                    stakeholder["description"],
                    business_idea,
                    target_customer,
                    problem,
                    "secondary",
                )
                enhanced_stakeholders["secondary"].append(
                    {
                        "name": stakeholder["name"],
                        "description": stakeholder["description"],
                        "questions": questions,
                    }
                )

            # Log successful generation
            primary_count = len(enhanced_stakeholders.get("primary", []))
            secondary_count = len(enhanced_stakeholders.get("secondary", []))
            logger.info(
                f"✅ Successfully enhanced stakeholders: {primary_count} primary, {secondary_count} secondary"
            )

            # Log first primary stakeholder for debugging
            if primary_count > 0:
                first_primary = enhanced_stakeholders["primary"][0]
                questions_count = len(
                    first_primary.get("questions", {}).get("problemDiscovery", [])
                )
                logger.info(
                    f"✅ First primary stakeholder '{first_primary.get('name', 'Unknown')}' has {questions_count} problem discovery questions"
                )

            return enhanced_stakeholders

        except Exception as e:
            logger.error(f"Stakeholder question generation failed: {e}")
            logger.error(f"Original stakeholder_data: {stakeholder_data}")
            logger.error(f"Enhanced stakeholders so far: {enhanced_stakeholders}")
            import traceback

            logger.error(f"Full traceback: {traceback.format_exc()}")
            return stakeholder_data  # Return original data without questions

    async def _generate_stakeholder_specific_questions(
        self,
        llm_service,
        stakeholder_name: str,
        stakeholder_description: str,
        business_idea: str,
        target_customer: str,
        problem: str,
        stakeholder_type: str,
    ) -> Dict[str, List[str]]:
        """Generate categorized questions specific to a stakeholder type using PydanticAI structured output"""
        try:
            from backend.api.research.research_types import StakeholderQuestions

            # Primary stakeholders get more questions per category
            if stakeholder_type == "primary":
                problem_count, solution_count, followup_count = 3, 3, 2
            else:
                problem_count, solution_count, followup_count = 2, 2, 1

            prompt = f"""Generate categorized interview questions for this stakeholder type.

Business Context:
- Business Idea: {business_idea}
- Target Customer: {target_customer}
- Problem Being Solved: {problem}

Stakeholder:
- Name: {stakeholder_name}
- Description: {stakeholder_description}
- Type: {stakeholder_type}

Generate questions in these categories:

1. PROBLEM DISCOVERY ({problem_count} questions):
   - Questions to understand their current state and pain points
   - Focus on their specific challenges related to {business_idea}

2. SOLUTION VALIDATION ({solution_count} questions):
   - Questions to validate your proposed solution approach
   - Focus on their interest, concerns, and requirements

3. FOLLOW-UP ({followup_count} questions):
   - Questions for deeper insights and next steps
   - Questions about decision-making and influences

Make all questions highly specific to {stakeholder_name} and their role.

Return in this exact JSON format:
{{
  "problemDiscovery": ["Problem question 1?", "Problem question 2?", ...],
  "solutionValidation": ["Solution question 1?", "Solution question 2?", ...],
  "followUp": ["Follow-up question 1?", ...]
}}"""

            # Try to use structured output if available
            try:
                # Check if LLM service supports structured output
                if hasattr(llm_service, "generate_structured"):
                    result = await llm_service.generate_structured(
                        prompt=prompt,
                        response_model=StakeholderQuestions,
                        temperature=0.7,
                        max_tokens=600,
                    )
                    return {
                        "problemDiscovery": result.problemDiscovery,
                        "solutionValidation": result.solutionValidation,
                        "followUp": result.followUp,
                    }
                else:
                    # Fallback to text generation with JSON parsing
                    response_data = await llm_service.analyze(
                        text=prompt,
                        task="text_generation",
                        data={"temperature": 0.7, "max_tokens": 600},
                    )
                    response = response_data.get("text", "")

                    # Parse JSON response (handle markdown code blocks)
                    import json
                    import re

                    # Remove markdown code blocks if present
                    cleaned_response = response.strip()
                    if cleaned_response.startswith("```json"):
                        json_match = re.search(
                            r"```json\s*\n(.*?)\n```", cleaned_response, re.DOTALL
                        )
                        if json_match:
                            cleaned_response = json_match.group(1).strip()
                        else:
                            cleaned_response = (
                                cleaned_response.replace("```json", "")
                                .replace("```", "")
                                .strip()
                            )

                    # Parse and validate with Pydantic
                    questions_data = json.loads(cleaned_response)
                    validated_questions = StakeholderQuestions(**questions_data)
                    return {
                        "problemDiscovery": validated_questions.problemDiscovery,
                        "solutionValidation": validated_questions.solutionValidation,
                        "followUp": validated_questions.followUp,
                    }

            except Exception as parse_error:
                logger.warning(
                    f"Structured parsing failed for {stakeholder_name}: {parse_error}"
                )

                # Final fallback: generate simple categorized questions with proper context
                logger.warning(
                    f"Using fallback questions for {stakeholder_name} - this indicates LLM generation failed"
                )
                fallback_questions = {
                    "problemDiscovery": [
                        f"What challenges do you currently face related to {problem or 'the current situation'}?",
                        f"How does the current situation impact your daily life or responsibilities as someone in the {stakeholder_name.lower()} category?",
                    ],
                    "solutionValidation": [
                        f"How interested would you be in a solution that addresses {problem or 'these challenges'}?",
                        f"What concerns would you have about implementing this type of solution?",
                    ],
                    "followUp": [
                        f"What other aspects of {problem or 'this situation'} should we consider?"
                    ],
                }

                # Adjust question count based on stakeholder type
                if stakeholder_type == "secondary":
                    fallback_questions["problemDiscovery"] = fallback_questions[
                        "problemDiscovery"
                    ][:2]
                    fallback_questions["solutionValidation"] = fallback_questions[
                        "solutionValidation"
                    ][:2]
                    fallback_questions["followUp"] = fallback_questions["followUp"][:1]

                return fallback_questions

        except Exception as e:
            logger.error(f"Question generation failed for {stakeholder_name}: {e}")
            return {"problemDiscovery": [], "solutionValidation": [], "followUp": []}

    def calculate_stakeholder_time_estimates(
        self, stakeholders: Dict[str, List[Dict]]
    ) -> str:
        """Calculate time estimates based on stakeholder questions"""
        try:
            total_questions = 0

            for primary in stakeholders.get("primary", []):
                total_questions += len(primary.get("questions", []))

            for secondary in stakeholders.get("secondary", []):
                total_questions += len(secondary.get("questions", []))

            # Estimate 2-3 minutes per question
            min_time = max(20, total_questions * 2)
            max_time = max(30, total_questions * 3)

            return f"{min_time}-{max_time} minutes"

        except Exception as e:
            logger.error(f"Time estimation failed: {e}")
            return "25-40 minutes"

    def get_stakeholder_metadata(
        self, stakeholders: Dict[str, List[Dict]]
    ) -> Dict[str, Any]:
        """Get metadata about detected stakeholders"""
        try:
            primary_count = len(stakeholders.get("primary", []))
            secondary_count = len(stakeholders.get("secondary", []))

            total_questions = 0
            for primary in stakeholders.get("primary", []):
                total_questions += len(primary.get("questions", []))
            for secondary in stakeholders.get("secondary", []):
                total_questions += len(secondary.get("questions", []))

            return {
                "enhancement_type": "stakeholder_detection",
                "version": "v3_rebuilt",
                "primary_stakeholders": primary_count,
                "secondary_stakeholders": secondary_count,
                "total_stakeholder_questions": total_questions,
                "estimated_time": self.calculate_stakeholder_time_estimates(
                    stakeholders
                ),
            }

        except Exception as e:
            logger.error(f"Stakeholder metadata generation failed: {e}")
            return {
                "enhancement_type": "stakeholder_detection",
                "version": "v3_rebuilt",
            }
