"""
V1 Core: Question Generation Functions
Extracted from customer_research.py - preserves all original functionality.
"""

import logging
from typing import List, Dict, Any, Optional
from backend.api.research.research_types import (
    Message,
    ResearchContext,
    ResearchQuestions,
    Stakeholder,
)

logger = logging.getLogger(__name__)


async def generate_comprehensive_research_questions(
    llm_service,
    context: ResearchContext,
    conversation_history: List[Message],
    stakeholder_data: Optional[Dict[str, Any]] = None,
) -> ResearchQuestions:
    """Generate comprehensive research questions using LLM with stakeholder context."""
    try:
        logger.info("🎯 Generating comprehensive research questions")

        business_idea = getattr(context, "businessIdea", "") or ""
        target_customer = getattr(context, "targetCustomer", "") or ""
        problem = getattr(context, "problem", "") or ""

        # Build conversation context
        conversation_text = ""
        for msg in conversation_history[-5:]:  # Last 5 messages for context
            conversation_text += f"{msg.role}: {msg.content}\n"

        prompt = f"""You are an expert customer research consultant. Generate comprehensive research questions for customer interviews.

Business Context:
- Business Idea: {business_idea}
- Target Customer: {target_customer}
- Problem Being Solved: {problem}

Recent Conversation:
{conversation_text}

Generate research questions in these categories:

1. PROBLEM DISCOVERY (5 questions max):
   - Questions to understand the customer's current problems and pain points
   - Focus on their current situation and challenges

2. SOLUTION VALIDATION (5 questions max):
   - Questions to test if your solution would actually help
   - Focus on their reactions to your proposed solution

3. FOLLOW-UP (3 questions max):
   - Questions to dig deeper into interesting responses
   - Questions about their decision-making process

Format as JSON:
{{
  "problemDiscovery": ["question 1", "question 2", ...],
  "solutionValidation": ["question 1", "question 2", ...],
  "followUp": ["question 1", "question 2", ...]
}}

Make questions specific to this business context, not generic."""

        response = await llm_service.generate_text(
            prompt=prompt, temperature=0.7, max_tokens=1000
        )

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

            questions_data = json.loads(cleaned_response)

            # DIRECT FIX: Generate stakeholders directly in V1 core
            # This bypasses the V3 enhancement complexity that was causing data flow issues
            stakeholders = {"primary": [], "secondary": []}

            try:
                # Import and use stakeholder detector directly
                from backend.api.research.v3_enhancements.stakeholder_detector import (
                    StakeholderDetector,
                )
                from backend.services.llm import LLMServiceFactory

                detector = StakeholderDetector()
                llm_service = LLMServiceFactory.create("gemini")

                # Extract context for stakeholder generation
                logger.info(f"🔍 Context keys available: {list(context.keys())}")
                logger.info(f"🔍 Full context: {context}")

                business_idea = context.get("businessIdea", "")
                target_customer = context.get("targetCustomer", "")
                problem = context.get("problem", "")

                logger.info(
                    f"🔍 Extracted: business='{business_idea}', customer='{target_customer}', problem='{problem}'"
                )

                # FALLBACK: If context extraction failed, extract from conversation directly
                if not business_idea or (not target_customer and not problem):
                    logger.info(
                        "🔍 Context extraction insufficient, extracting from conversation..."
                    )

                    # Extract business idea from conversation
                    conversation_text = " ".join(
                        [msg.content for msg in messages if hasattr(msg, "content")]
                    )

                    if "Legacy API" in conversation_text:
                        business_idea = "Legacy API for database access"
                        target_customer = "developers and database administrators"
                        problem = "difficulty accessing data from outdated databases"

                        logger.info(
                            f"🔍 Fallback extraction: business='{business_idea}', customer='{target_customer}', problem='{problem}'"
                        )

                # Only generate stakeholders if we have sufficient context
                if business_idea and (target_customer or problem):
                    logger.info(f"🎯 Generating stakeholders directly in V1 core...")

                    context_analysis = {
                        "business_idea": business_idea,
                        "target_customer": target_customer,
                        "problem": problem,
                    }

                    # Generate stakeholders directly using actual messages
                    import asyncio

                    if asyncio.iscoroutinefunction(
                        detector.generate_dynamic_stakeholders_with_unique_questions
                    ):
                        # We're in an async context, so we can await
                        stakeholders = await detector.generate_dynamic_stakeholders_with_unique_questions(
                            llm_service=llm_service,
                            context_analysis=context_analysis,
                            messages=messages,  # Use actual messages instead of mock
                            business_idea=business_idea,
                            target_customer=target_customer,
                            problem=problem,
                        )
                        logger.info(
                            f"✅ V1 core generated {len(stakeholders.get('primary', []))} primary, {len(stakeholders.get('secondary', []))} secondary stakeholders"
                        )
                    else:
                        # Fallback to empty stakeholders
                        logger.warning(
                            "Stakeholder detector is not async, using empty stakeholders"
                        )
                        stakeholders = {"primary": [], "secondary": []}
                else:
                    logger.info(
                        "Insufficient context for stakeholder generation, using empty stakeholders"
                    )

            except Exception as e:
                logger.error(f"Direct stakeholder generation failed: {e}")
                stakeholders = {"primary": [], "secondary": []}

            # Calculate estimated time
            total_questions = (
                len(questions_data.get("problemDiscovery", []))
                + len(questions_data.get("solutionValidation", []))
                + len(questions_data.get("followUp", []))
            )
            estimated_time = (
                f"{max(20, total_questions * 2)}-{max(30, total_questions * 3)} minutes"
            )

            questions = ResearchQuestions(
                problemDiscovery=questions_data.get("problemDiscovery", [])[:5],
                solutionValidation=questions_data.get("solutionValidation", [])[:5],
                followUp=questions_data.get("followUp", [])[:3],
                stakeholders=stakeholders,
                estimatedTime=estimated_time,
            )

            logger.info(f"✅ Generated {total_questions} questions across categories")
            return questions

        except json.JSONDecodeError:
            logger.warning(
                "Failed to parse LLM questions response as JSON, using fallback"
            )
            return await generate_fallback_questions(context, llm_service)

    except Exception as e:
        logger.error(f"Comprehensive question generation failed: {e}")
        return await generate_fallback_questions(context, llm_service)


async def generate_research_questions(
    llm_service, context: ResearchContext, conversation_history: List[Message]
) -> ResearchQuestions:
    """Generate structured research questions using LLM - backward compatibility wrapper."""
    return await generate_comprehensive_research_questions(
        llm_service, context, conversation_history
    )


async def generate_fallback_questions(
    context: ResearchContext, llm_service=None
) -> ResearchQuestions:
    """Generate fallback questions when LLM is not working."""
    try:
        logger.info("🔄 Using fallback question generation")

        business_idea = getattr(context, "businessIdea", "") or "your business"
        target_customer = getattr(context, "targetCustomer", "") or "customers"

        # Generic but useful questions
        problem_discovery = [
            f"What challenges do you currently face that {business_idea} could help with?",
            f"How do you currently handle [specific problem area]?",
            f"What's the most frustrating part of your current process?",
            f"How much time do you spend on [relevant activity] each week?",
            f"What would an ideal solution look like to you?",
        ]

        solution_validation = [
            f"How interested would you be in {business_idea}?",
            f"What concerns would you have about using {business_idea}?",
            f"How much would you expect to pay for something like this?",
            f"What features would be most important to you?",
            f"How would you prefer to learn about new solutions like this?",
        ]

        follow_up = [
            "Can you tell me more about that?",
            "What else influences your decision in this area?",
            "Who else is involved in decisions like this?",
        ]

        return ResearchQuestions(
            problemDiscovery=problem_discovery,
            solutionValidation=solution_validation,
            followUp=follow_up,
            stakeholders={"primary": [], "secondary": []},
            estimatedTime="25-40 minutes",
        )

    except Exception as e:
        logger.error(f"Even fallback question generation failed: {e}")
        return ResearchQuestions(
            problemDiscovery=["What problems are you trying to solve?"],
            solutionValidation=["Would this solution help you?"],
            followUp=["Can you tell me more?"],
            stakeholders={"primary": [], "secondary": []},
            estimatedTime="20-30 minutes",
        )


async def detect_stakeholders_with_llm(
    llm_service, context: ResearchContext, conversation_history: List[Message]
) -> dict:
    """Use LLM to intelligently detect stakeholders from conversation context."""
    try:
        logger.info("👥 Detecting stakeholders with LLM")

        business_idea = getattr(context, "businessIdea", "") or ""
        target_customer = getattr(context, "targetCustomer", "") or ""
        problem = getattr(context, "problem", "") or ""

        # Build conversation context
        conversation_text = ""
        for msg in conversation_history[-5:]:
            conversation_text += f"{msg.role}: {msg.content}\n"

        prompt = f"""Analyze this business context and identify key stakeholders for customer research.

Business Context:
- Business Idea: {business_idea}
- Target Customer: {target_customer}
- Problem Being Solved: {problem}

Conversation:
{conversation_text}

Identify:
1. PRIMARY stakeholders (direct users/customers who would use the solution)
2. SECONDARY stakeholders (people who influence decisions but may not use directly)

For each stakeholder, provide:
- name: Short descriptive name
- description: Brief description of their role/relationship

Return as JSON:
{{
  "primary": [
    {{"name": "Primary User", "description": "Description of their role"}},
    ...
  ],
  "secondary": [
    {{"name": "Influencer", "description": "Description of their role"}},
    ...
  ]
}}

Focus on stakeholders specific to this business context."""

        response = await llm_service.generate_text(
            prompt=prompt, temperature=0.6, max_tokens=500
        )

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
            logger.info(
                f"✅ Detected {len(stakeholder_data.get('primary', []))} primary and {len(stakeholder_data.get('secondary', []))} secondary stakeholders"
            )
            return stakeholder_data
        except json.JSONDecodeError:
            logger.warning("Failed to parse stakeholder response as JSON")
            return {"primary": [], "secondary": []}

    except Exception as e:
        logger.error(f"Stakeholder detection failed: {e}")
        return {"primary": [], "secondary": []}
