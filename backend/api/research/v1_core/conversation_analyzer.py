"""
V1 Core: Conversation Analysis Functions
Extracted from customer_research.py - preserves all original functionality.
"""

import logging
from typing import List, Dict, Any, Optional
from backend.api.research.research_types import Message, ResearchContext

logger = logging.getLogger(__name__)


async def extract_context_with_llm(
    llm_service, conversation_context: str, latest_input: str
) -> dict:
    """Extract business context using LLM analysis instead of keyword matching."""
    try:
        logger.info("🧠 Extracting context with LLM analysis")

        prompt = f"""Analyze this customer research conversation and extract key business context.

Conversation:
{conversation_context}

Latest input: {latest_input}

Extract the following information:
1. Business idea (what they want to build/do)
2. Target customer (who they want to serve)
3. Problem (what problem they're solving)
4. Stage (discovery, validation, refinement)

Return as JSON with keys: businessIdea, targetCustomer, problem, stage
Be specific and use exact phrases from the conversation when possible.
If information is not clearly stated, use null for that field."""

        logger.info(f"🔧 DEBUG CONTEXT: About to call LLM for context extraction")
        response = await llm_service.generate_text(
            prompt=prompt, temperature=0.3, max_tokens=500
        )

        logger.info(f"🔧 DEBUG CONTEXT: Response type: {type(response)}")
        logger.info(f"🔧 DEBUG CONTEXT: Response preview: {str(response)[:200]}...")

        # Check if response is a string (expected) or raw object (error)
        if not isinstance(response, str):
            logger.error(
                f"❌ CONTEXT: LLM returned non-string response: {type(response)}"
            )
            return {
                "businessIdea": None,
                "targetCustomer": None,
                "problem": None,
                "stage": "discovery",
            }

        # Parse JSON response (handle markdown code blocks)
        import json
        import re

        try:
            # Remove markdown code blocks if present
            cleaned_response = response.strip()
            if cleaned_response.startswith("```json"):
                # Extract JSON from markdown code block
                json_match = re.search(
                    r"```json\s*\n(.*?)\n```", cleaned_response, re.DOTALL
                )
                if json_match:
                    cleaned_response = json_match.group(1).strip()
                else:
                    # Fallback: remove ```json and ``` manually
                    cleaned_response = (
                        cleaned_response.replace("```json", "")
                        .replace("```", "")
                        .strip()
                    )

            context_data = json.loads(cleaned_response)
            logger.info(f"✅ Context extracted: {context_data}")
            return context_data
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse LLM context response as JSON: {e}")
            logger.warning(f"Raw response: {response}")
            logger.warning(
                f"Cleaned response: {cleaned_response if 'cleaned_response' in locals() else 'N/A'}"
            )
            return {
                "businessIdea": None,
                "targetCustomer": None,
                "problem": None,
                "stage": "discovery",
            }

    except Exception as e:
        logger.error(f"Context extraction failed: {e}")
        return {
            "businessIdea": None,
            "targetCustomer": None,
            "problem": None,
            "stage": "discovery",
        }


async def analyze_user_intent_with_llm(
    llm_service, conversation_context: str, latest_input: str, messages: List[Message]
) -> dict:
    """Analyze user intent using LLM instead of keyword matching."""
    try:
        logger.info("🎯 Analyzing user intent with LLM")

        prompt = f"""Analyze the user's intent in this customer research conversation.

Conversation context:
{conversation_context}

Latest user input: "{latest_input}"

Determine the user's primary intent from these options:
- "confirmation" - User is confirming/agreeing with something
- "rejection" - User is disagreeing or rejecting something
- "clarification" - User wants to clarify or add more details
- "question_request" - User explicitly wants research questions generated
- "clarify_business" - User is still explaining their business idea
- "provide_details" - User is providing more information

Also determine:
- conversation_stage: "initial", "discovery", "validation", "ready"
- confidence: 0.0 to 1.0

Return as JSON with keys: intent, conversation_stage, confidence, reasoning"""

        response = await llm_service.generate_text(
            prompt=prompt, temperature=0.2, max_tokens=300
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

            intent_data = json.loads(cleaned_response)
            logger.info(f"✅ Intent analyzed: {intent_data}")
            return intent_data
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse LLM intent response as JSON: {e}")
            logger.warning(f"Raw response: {response}")
            return {
                "intent": "clarify_business",
                "conversation_stage": "discovery",
                "confidence": 0.5,
                "reasoning": "Fallback intent analysis",
            }

    except Exception as e:
        logger.error(f"Intent analysis failed: {e}")
        return {
            "intent": "clarify_business",
            "conversation_stage": "discovery",
            "confidence": 0.5,
            "reasoning": f"Error: {e}",
        }


async def validate_business_readiness_with_llm(
    llm_service, conversation_context: str, latest_input: str
) -> dict:
    """Validate business readiness for question generation using LLM analysis."""
    try:
        logger.info("📊 Validating business readiness with LLM")

        prompt = f"""Analyze if this business conversation has the MINIMUM context needed to generate customer research questions.

Conversation:
{conversation_context}

Latest input: {latest_input}

RELAXED CRITERIA - Research questions should help discover missing details:
1. Is there ANY business idea mentioned? (even basic like "app", "service", "product")
2. Is there ANY target customer mentioned? (even broad like "people", "users", "customers")
3. Is there ANY problem or need mentioned? (even vague)

The goal is to generate research questions that will help discover:
- Specific details about the problem
- More precise target customer definition
- Current solutions and pain points
- Validation of the business idea

Be GENEROUS - if there's a basic business concept, target, and problem, we should generate questions to explore further.

Return JSON with:
- ready_for_questions: true/false (be generous - true if basic elements exist)
- readiness_score: 0.0 to 1.0 (0.5+ if basic elements exist)
- missing_elements: list of what's missing (only if truly nothing is provided)
- conversation_quality: "low", "medium", "high"
- reasoning: explanation"""

        response = await llm_service.generate_text(
            prompt=prompt, temperature=0.2, max_tokens=400
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

            readiness_data = json.loads(cleaned_response)
            logger.info(f"✅ Business readiness: {readiness_data}")
            return readiness_data
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse LLM readiness response as JSON: {e}")
            logger.warning(f"Raw response: {response}")
            return {
                "ready_for_questions": True,  # Be generous in fallback
                "readiness_score": 0.6,
                "missing_elements": [],
                "conversation_quality": "medium",
                "reasoning": "Fallback readiness analysis - generating questions to discover more details",
            }

    except Exception as e:
        logger.error(f"Business readiness validation failed: {e}")
        return {
            "ready_for_questions": True,  # Be generous even on error
            "readiness_score": 0.5,
            "missing_elements": [],
            "conversation_quality": "medium",
            "reasoning": f"Error in analysis, but generating questions anyway: {e}",
        }


async def classify_industry_with_llm(
    llm_service, conversation_context: str, latest_input: str
) -> dict:
    """Classify industry using LLM analysis instead of keyword matching."""
    try:
        logger.info("🏭 Classifying industry with LLM")

        prompt = f"""Classify the industry/business type from this conversation.

Conversation:
{conversation_context}

Latest input: {latest_input}

Determine:
1. Primary industry (e.g., "food_service", "technology", "healthcare", "retail", etc.)
2. Business model (e.g., "b2b", "b2c", "marketplace", "saas", etc.)
3. Industry-specific considerations for customer research

Return JSON with keys: industry, business_model, research_considerations"""

        response = await llm_service.generate_text(
            prompt=prompt, temperature=0.3, max_tokens=300
        )

        # Parse JSON response
        import json

        try:
            industry_data = json.loads(response.strip())
            logger.info(f"✅ Industry classified: {industry_data}")
            return industry_data
        except json.JSONDecodeError:
            logger.warning("Failed to parse LLM industry response as JSON")
            return {
                "industry": "general",
                "business_model": "unknown",
                "research_considerations": [],
            }

    except Exception as e:
        logger.error(f"Industry classification failed: {e}")
        return {
            "industry": "general",
            "business_model": "unknown",
            "research_considerations": [],
        }
