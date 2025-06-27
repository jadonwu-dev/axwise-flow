"""
V1 Core: Response Generation Functions
Extracted from customer_research.py - preserves all original functionality.
"""

import logging
from typing import List, Optional
from backend.api.research.research_types import Message, ResearchContext

logger = logging.getLogger(__name__)


async def generate_research_response_with_retry(
    llm_service,
    messages: List[Message],
    user_input: str,
    context: Optional[ResearchContext],
    conversation_context: str,
    max_retries: int = 2,
) -> str:
    """Generate research response with retry logic."""
    for attempt in range(max_retries + 1):
        try:
            return await generate_research_response(
                llm_service, messages, user_input, context, conversation_context
            )
        except Exception as e:
            logger.warning(f"Response generation attempt {attempt + 1} failed: {e}")
            if attempt == max_retries:
                logger.error("All response generation attempts failed, using fallback")
                return await generate_simple_fallback_response(user_input, context)


async def generate_research_response(
    llm_service,
    messages: List[Message],
    user_input: str,
    context: Optional[ResearchContext],
    conversation_context: str,
) -> str:
    """Generate conversational response for customer research."""
    try:
        logger.info("🤖 Generating research response with LLM")

        # Build context information
        business_idea = getattr(context, "businessIdea", "") if context else ""
        target_customer = getattr(context, "targetCustomer", "") if context else ""
        problem = getattr(context, "problem", "") if context else ""

        prompt = f"""You are an experienced customer research consultant helping someone validate their business idea through customer interviews.

Current conversation context:
{conversation_context}

Business context so far:
- Business idea: {business_idea or 'Not yet clear'}
- Target customer: {target_customer or 'Not yet clear'}
- Problem being solved: {problem or 'Not yet clear'}

User's latest input: "{user_input}"

Your role:
1. Ask ONE focused question to understand their business better
2. Build on what they've already shared
3. Guide them toward clarity on their business idea, target customers, and the problem they're solving
4. Be conversational and encouraging
5. Don't ask multiple questions at once

Generate a helpful, conversational response that asks one specific question to move the research forward."""

        logger.info(
            f"🔧 DEBUG: About to call LLM service with prompt length: {len(prompt)}"
        )
        response = await llm_service.generate_text(
            prompt=prompt,
            temperature=0.7,
            max_tokens=500,  # Increased from 200 to avoid truncation
        )

        logger.info(f"🔧 DEBUG: LLM response type: {type(response)}")
        logger.info(f"🔧 DEBUG: LLM response length: {len(str(response))}")
        logger.info(f"🔧 DEBUG: LLM response preview: {str(response)[:100]}...")

        # Check if response is a string (expected) or raw object (error)
        if not isinstance(response, str):
            logger.error(f"❌ LLM returned non-string response: {type(response)}")
            logger.error(f"Raw response: {str(response)[:200]}...")
            raise Exception(
                f"LLM service returned invalid response type: {type(response)}"
            )

        logger.info(f"✅ Generated response: {response[:100]}...")
        return response.strip()

    except Exception as e:
        logger.error(f"Response generation failed: {e}")
        return await generate_simple_fallback_response(user_input, context)


async def generate_simple_fallback_response(
    user_input: str, context: Optional[ResearchContext]
) -> str:
    """Generate simple fallback responses when LLM is not working."""
    try:
        logger.info("🔄 Using fallback response generation")

        user_lower = user_input.lower()

        # Simple keyword-based responses
        if any(
            word in user_lower for word in ["app", "website", "platform", "software"]
        ):
            return "That sounds like an interesting tech solution! Can you tell me more about what specific problem it would solve for people?"

        elif any(
            word in user_lower for word in ["restaurant", "food", "cafe", "kitchen"]
        ):
            return "Food businesses can be really rewarding! Who do you imagine would be your main customers?"

        elif any(word in user_lower for word in ["service", "help", "assist"]):
            return "Service businesses often have great potential. What type of people would benefit most from this service?"

        elif any(word in user_lower for word in ["sell", "product", "make", "create"]):
            return "That's a great start! Can you describe who you think would want to buy this?"

        else:
            return "That's interesting! Can you help me understand what problem this would solve for people?"

    except Exception as e:
        logger.error(f"Even fallback response failed: {e}")
        return "I'd love to learn more about your idea. Can you tell me what problem you're trying to solve?"


async def generate_confirmation_response(
    llm_service,
    messages: List[Message],
    user_input: str,
    context: Optional[ResearchContext],
    conversation_context: str,
) -> str:
    """Generate confirmation response before question generation."""
    try:
        logger.info("✅ Generating confirmation response")

        business_idea = getattr(context, "businessIdea", "") if context else ""
        target_customer = getattr(context, "targetCustomer", "") if context else ""
        problem = getattr(context, "problem", "") if context else ""

        prompt = f"""You are a customer research consultant. Based on the conversation, summarize what you understand about their business and ask for confirmation before generating research questions.

Conversation context:
{conversation_context}

What you understand:
- Business idea: {business_idea}
- Target customer: {target_customer}
- Problem being solved: {problem}

Create a brief, friendly summary and ask if you have it right before proceeding to generate research questions. Be conversational and encouraging."""

        response = await llm_service.generate_text(
            prompt=prompt,
            temperature=0.6,
            max_tokens=300,  # Increased from 150 to avoid truncation
        )

        return response.strip()

    except Exception as e:
        logger.error(f"Confirmation response generation failed: {e}")
        return f"Let me make sure I understand: You want to build {business_idea or 'your business idea'} for {target_customer or 'your target customers'} to help with {problem or 'the problem you identified'}. Does that sound right?"


async def generate_contextual_suggestions(
    llm_service,
    messages: List[Message],
    user_input: str,
    response_content: str,
    conversation_context: str,
) -> List[str]:
    """Generate contextual suggestions for the user."""
    try:
        logger.info("💡 Generating contextual suggestions")

        prompt = f"""Based on this customer research conversation, suggest 3 helpful response options for the user.

Conversation context:
{conversation_context}

Assistant's latest response: {response_content}

Generate 3 short, helpful answer options that the USER could give in response to the assistant's question. These should be potential answers the user might want to say, not additional questions.

For example:
- If assistant asks "What made you think of this business?" suggest answers like "I noticed a gap in the market" or "I have relevant experience"
- If assistant asks "Who are your target customers?" suggest answers like "Young professionals" or "Families with children"

Make the suggestions specific to this conversation context, not generic.

Return as a simple list, one suggestion per line."""

        logger.info(f"🔧 DEBUG SUGGESTIONS: About to call LLM for suggestions")
        response = await llm_service.generate_text(
            prompt=prompt,
            temperature=0.8,
            max_tokens=300,  # Increased from 150 to avoid truncation
        )

        logger.info(f"🔧 DEBUG SUGGESTIONS: Response type: {type(response)}")
        logger.info(f"🔧 DEBUG SUGGESTIONS: Response preview: {str(response)[:100]}...")

        # Check if response is a string (expected) or raw object (error)
        if not isinstance(response, str):
            logger.error(
                f"❌ SUGGESTIONS: LLM returned non-string response: {type(response)}"
            )
            # Use fallback suggestions instead
            return [
                "Can you be more specific?",
                "Tell me more about that",
                "What else should I know?",
            ]

        # Parse suggestions and clean formatting
        suggestions = [s.strip() for s in response.split("\n") if s.strip()]
        cleaned_suggestions = []
        for s in suggestions:
            # Remove common prefixes and formatting - be more aggressive
            cleaned = s.strip()
            # Remove asterisks and spaces at the beginning
            while cleaned.startswith("*") or cleaned.startswith(" "):
                cleaned = cleaned.lstrip("*").lstrip(" ")
            # Remove other common prefixes
            cleaned = (
                cleaned.lstrip("- ")
                .lstrip("• ")
                .lstrip("1. ")
                .lstrip("2. ")
                .lstrip("3. ")
            )
            # Remove quotes
            cleaned = cleaned.strip('"').strip("'")
            # Skip meta-descriptions that start with "I'll" or "I will"
            if (
                cleaned
                and not cleaned.startswith("I'll")
                and not cleaned.startswith("I will")
                and len(cleaned) > 5  # Skip very short suggestions
            ):
                cleaned_suggestions.append(cleaned)

        suggestions = cleaned_suggestions

        # Limit to 3 suggestions
        suggestions = suggestions[:3]

        # Add fallback if we don't have enough
        while len(suggestions) < 3:
            fallback_suggestions = [
                "Can you be more specific?",
                "Tell me more about that",
                "What else should I know?",
            ]
            suggestions.extend(fallback_suggestions)
            suggestions = suggestions[:3]

        logger.info(f"✅ Generated {len(suggestions)} suggestions")
        return suggestions

    except Exception as e:
        logger.error(f"Suggestion generation failed: {e}")
        return [
            "Can you be more specific?",
            "What industry is this for?",
            "Who are your target customers?",
        ]
