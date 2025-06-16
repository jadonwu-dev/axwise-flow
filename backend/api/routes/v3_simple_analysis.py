"""
Analysis functions for Customer Research API v3 Simplified.

This module contains all analysis functions including context analysis,
intent analysis, business validation, industry analysis, stakeholder detection,
and conversation flow analysis.

Extracted from customer_research_v3_simple.py for better modularity.
"""

import hashlib
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


async def analyze_context_enhanced(
    service,
    conversation_context: str,
    latest_input: str,
    existing_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Enhanced context analysis with caching and V3 features."""

    try:
        # Create cache key
        context_hash = hashlib.md5(f"{conversation_context}:{latest_input}".encode()).hexdigest()
        cache_key = service._get_cache_key("context_analysis", context_hash)

        # Check cache first
        cached_result = service._get_from_cache(cache_key)
        if cached_result:
            logger.debug("Context analysis cache hit")
            return cached_result

        # Use direct LLM-based context analysis (V3 implementation)
        from backend.services.llm import LLMServiceFactory

        llm_service = LLMServiceFactory.create("gemini")
        context_result = await _extract_context_with_llm(llm_service, conversation_context, latest_input, existing_context)

        # V3 Enhancement: Add confidence scoring
        confidence_score = _calculate_context_confidence(context_result)
        context_result['confidence'] = confidence_score

        # V3 Enhancement: Add business clarity metrics
        business_clarity = _analyze_business_clarity(context_result)
        context_result['business_clarity'] = business_clarity

        # Store in cache
        service._store_in_cache(cache_key, context_result)

        # Store confidence in metrics
        service.metrics.confidence_scores['context_analysis'] = confidence_score

        logger.debug(f"Context analysis completed with confidence: {confidence_score:.2f}")
        return context_result

    except Exception as e:
        logger.error(f"Context analysis failed: {e}")
        # Fallback to basic context
        return {
            'businessIdea': 'Not specified',
            'targetCustomer': 'Not specified',
            'problem': 'Not specified',
            'confidence': 0.0,
            'business_clarity': {
                'idea_clarity': 0.0,
                'customer_clarity': 0.0,
                'problem_clarity': 0.0
            }
        }


async def analyze_intent_enhanced(
    service,
    conversation_context: str,
    latest_input: str,
    messages: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Enhanced intent analysis with V3 features."""

    try:
        # Create cache key
        context_hash = hashlib.md5(f"{conversation_context}:{latest_input}".encode()).hexdigest()
        cache_key = service._get_cache_key("intent_analysis", context_hash)

        # Check cache first
        cached_result = service._get_from_cache(cache_key)
        if cached_result:
            logger.debug("Intent analysis cache hit")
            return cached_result

        # Use direct LLM-based intent analysis (V3 implementation)
        from backend.services.llm import LLMServiceFactory

        llm_service = LLMServiceFactory.create("gemini")
        intent_result = await _analyze_intent_with_llm(llm_service, conversation_context, latest_input, messages)

        # V3 Enhancement: Add conversation stage analysis
        conversation_stage = _analyze_conversation_stage(messages, intent_result)
        intent_result['conversation_stage'] = conversation_stage

        # V3 Enhancement: Add confidence scoring
        confidence_score = _calculate_intent_confidence(intent_result, messages)
        intent_result['confidence'] = confidence_score

        # Store in cache
        service._store_in_cache(cache_key, intent_result)

        # Store confidence in metrics
        service.metrics.confidence_scores['intent_analysis'] = confidence_score

        logger.debug(f"Intent analysis completed: {intent_result.get('intent', 'unknown')} (confidence: {confidence_score:.2f})")
        return intent_result

    except Exception as e:
        logger.error(f"Intent analysis failed: {e}")
        # Fallback to basic intent
        return {
            'intent': 'continue_conversation',
            'confidence': 0.0,
            'reasoning': 'Fallback due to analysis error',
            'next_action': 'continue',
            'conversation_stage': 'unknown'
        }


async def validate_business_readiness(
    service,
    conversation_context: str,
    latest_input: str
) -> Dict[str, Any]:
    """V1 SUSTAINABLE: Simple business validation with basic context check."""

    logger.error("🔥 FUNCTION CALLED: validate_business_readiness V1 SUSTAINABLE")

    try:
        logger.info("🚀 V1 SUSTAINABLE: Simple business validation")

        # Get context analysis from service (should be available from previous analysis)
        context_analysis = getattr(service, '_last_context_analysis', {})

        # If no context analysis available, extract basic info from conversation
        if not context_analysis:
            # Simple extraction from conversation context
            context_lower = conversation_context.lower()
            latest_lower = latest_input.lower()

            # Basic business idea detection
            business_idea = latest_input if len(latest_input) > 10 else "business idea mentioned"
            target_customer = "customers" if "customer" in context_lower else ""
            problem = "problem mentioned" if "problem" in context_lower else ""
        else:
            # Use existing context analysis
            business_idea = context_analysis.get('businessIdea') or context_analysis.get('business_idea')
            target_customer = context_analysis.get('targetCustomer') or context_analysis.get('target_customer')
            problem = context_analysis.get('problem')

        # V1 SUSTAINABLE PATTERN: Simple context-based validation
        has_business_idea = bool(business_idea and business_idea.strip() and len(business_idea.strip()) > 10)
        has_target_customer = bool(target_customer and target_customer.strip())
        has_problem = bool(problem and problem.strip())

        # V1 SUSTAINABLE: Simple decision - just need business idea OR explicit question request
        intent_keywords = ['question', 'generate', 'research', 'interview']
        user_wants_questions = any(keyword in latest_input.lower() for keyword in intent_keywords)

        ready_for_questions = has_business_idea or user_wants_questions

        # Calculate simple readiness score
        score_components = [
            0.6 if has_business_idea else 0.0,  # Business idea is most important
            0.2 if has_target_customer else 0.0,
            0.2 if has_problem else 0.0
        ]
        readiness_score = max(0.5, sum(score_components))  # Minimum 0.5 if user wants questions

        # Build missing elements list
        missing_elements = []
        if not has_business_idea and not user_wants_questions:
            missing_elements.append('business_idea')
        if not has_target_customer:
            missing_elements.append('target_customer')
        if not has_problem:
            missing_elements.append('problem')

        validation_result = {
            'ready_for_questions': ready_for_questions,
            'readiness_score': readiness_score,
            'confidence': 0.9 if ready_for_questions else 0.7,
            'missing_elements': missing_elements,
            'strengths': ['business_idea'] if has_business_idea else ['user_intent'] if user_wants_questions else [],
            'recommendations': ['Define target customer', 'Identify key problems'] if ready_for_questions else ['Define your business idea clearly'],
            'reasoning': f"V1 Sustainable validation: Business idea: {has_business_idea}, User wants questions: {user_wants_questions}"
        }

        logger.info(f"✅ V1 Sustainable validation: ready={ready_for_questions} (score: {readiness_score:.2f})")
        logger.info(f"  - Business idea: {has_business_idea} ({len(business_idea) if business_idea else 0} chars)")
        logger.info(f"  - Target customer: {has_target_customer}")
        logger.info(f"  - Problem: {has_problem}")
        logger.info(f"  - User wants questions: {user_wants_questions}")

        return validation_result

    except Exception as e:
        logger.error(f"🚨 V1 Sustainable business validation failed: {e}")
        import traceback
        logger.error(f"🚨 Full traceback: {traceback.format_exc()}")
        # V1 SUSTAINABLE FALLBACK: Default to ready if error
        return {
            'ready_for_questions': True,  # V1 SUSTAINABLE: Default to ready if error
            'confidence': 0.5,
            'reasoning': 'V1 Sustainable fallback due to error',
            'readiness_score': 0.5,
            'missing_elements': []
        }


def _calculate_context_confidence(context_result: Dict[str, Any]) -> float:
    """Calculate confidence score for context analysis."""
    try:
        business_idea = context_result.get('businessIdea') or context_result.get('business_idea', '')
        target_customer = context_result.get('targetCustomer') or context_result.get('target_customer', '')
        problem = context_result.get('problem', '')

        # Score based on completeness and specificity
        idea_score = min(1.0, len(str(business_idea)) / 50) if business_idea else 0.0
        customer_score = min(1.0, len(str(target_customer)) / 30) if target_customer else 0.0
        problem_score = min(1.0, len(str(problem)) / 40) if problem else 0.0

        # Weighted average
        return (idea_score * 0.4 + customer_score * 0.3 + problem_score * 0.3)

    except Exception:
        return 0.0


def _analyze_business_clarity(context_result: Dict[str, Any]) -> Dict[str, float]:
    """Analyze business clarity metrics."""
    try:
        business_idea = context_result.get('businessIdea') or context_result.get('business_idea', '')
        target_customer = context_result.get('targetCustomer') or context_result.get('target_customer', '')
        problem = context_result.get('problem', '')

        return {
            'idea_clarity': min(1.0, len(str(business_idea)) / 50) if business_idea else 0.0,
            'customer_clarity': min(1.0, len(str(target_customer)) / 30) if target_customer else 0.0,
            'problem_clarity': min(1.0, len(str(problem)) / 40) if problem else 0.0
        }

    except Exception:
        return {'idea_clarity': 0.0, 'customer_clarity': 0.0, 'problem_clarity': 0.0}


def _analyze_conversation_stage(messages: List[Dict[str, Any]], intent_result: Dict[str, Any]) -> str:
    """Analyze current conversation stage."""
    try:
        user_messages = [msg for msg in messages if msg.get('role') == 'user']
        message_count = len(user_messages)

        if message_count <= 1:
            return 'initial'
        elif message_count <= 3:
            return 'exploration'
        elif intent_result.get('intent') == 'question_request':
            return 'ready_for_questions'
        else:
            return 'refinement'

    except Exception:
        return 'unknown'


def _calculate_intent_confidence(intent_result: Dict[str, Any], messages: List[Dict[str, Any]]) -> float:
    """Calculate confidence score for intent analysis."""
    try:
        intent = intent_result.get('intent', '')
        reasoning = intent_result.get('reasoning', '')

        # Base confidence on intent clarity and reasoning quality
        intent_clarity = 0.8 if intent in ['question_request', 'continue_conversation'] else 0.5
        reasoning_quality = min(1.0, len(reasoning) / 100) if reasoning else 0.0

        return (intent_clarity * 0.7 + reasoning_quality * 0.3)

    except Exception:
        return 0.0


def _calculate_readiness_score(validation_result: Dict[str, Any]) -> float:
    """Calculate readiness score for business validation."""
    try:
        ready = validation_result.get('ready_for_questions', False)
        confidence = validation_result.get('confidence', 0.0)

        # Base score on readiness and confidence
        base_score = 0.8 if ready else 0.2
        confidence_boost = confidence * 0.2

        return min(1.0, base_score + confidence_boost)

    except Exception:
        return 0.0


def _analyze_missing_elements(validation_result: Dict[str, Any]) -> List[str]:
    """Analyze what elements are missing for business readiness."""
    try:
        missing = []

        if not validation_result.get('ready_for_questions', False):
            # Check what's missing based on validation reasoning
            reasoning = validation_result.get('reasoning', '').lower()

            if 'business' in reasoning or 'idea' in reasoning:
                missing.append('business_idea')
            if 'customer' in reasoning or 'target' in reasoning:
                missing.append('target_customer')
            if 'problem' in reasoning:
                missing.append('problem')

        return missing

    except Exception:
        return ['business_idea', 'target_customer', 'problem']


async def analyze_industry_enhanced(
    service,
    conversation_context: str,
    context_analysis: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """Enhanced industry analysis with V3 features."""

    if not service.config.enable_industry_analysis:
        return None

    try:
        # Create cache key
        business_idea = context_analysis.get('businessIdea') or context_analysis.get('business_idea', '')
        context_hash = hashlib.md5(f"industry:{business_idea}".encode()).hexdigest()
        cache_key = service._get_cache_key("industry_analysis", context_hash)

        # Check cache first
        cached_result = service._get_from_cache(cache_key)
        if cached_result:
            logger.debug("Industry analysis cache hit")
            return cached_result

        # Use direct LLM-based industry analysis (V3 implementation)
        from backend.services.llm import LLMServiceFactory

        llm_service = LLMServiceFactory.create("gemini")
        industry_result = await _classify_industry_with_llm(llm_service, conversation_context, context_analysis)

        # V3 Enhancement: Add sub-category analysis
        if industry_result:
            sub_categories = _analyze_industry_subcategories(industry_result, context_analysis)
            industry_result['sub_categories'] = sub_categories

            # Add confidence scoring
            confidence_score = _calculate_industry_confidence(industry_result)
            industry_result['confidence'] = confidence_score

            # Store confidence in metrics
            service.metrics.confidence_scores['industry_analysis'] = confidence_score

        # Store in cache
        service._store_in_cache(cache_key, industry_result)

        logger.debug(f"Industry analysis completed: {industry_result.get('industry', 'unknown') if industry_result else 'none'}")
        return industry_result

    except Exception as e:
        logger.error(f"Industry analysis failed: {e}")
        return None


async def detect_stakeholders_enhanced(
    service,
    conversation_context: str,
    context_analysis: Dict[str, Any],
    industry_analysis: Optional[Dict[str, Any]]
) -> Optional[Dict[str, Any]]:
    """Enhanced stakeholder detection with V3 features."""

    if not service.config.enable_stakeholder_detection:
        return None

    try:
        # Create cache key
        business_idea = context_analysis.get('businessIdea') or context_analysis.get('business_idea', '')
        target_customer = context_analysis.get('targetCustomer') or context_analysis.get('target_customer', '')
        context_hash = hashlib.md5(f"stakeholders:{business_idea}:{target_customer}".encode()).hexdigest()
        cache_key = service._get_cache_key("stakeholder_detection", context_hash)

        # Check cache first
        cached_result = service._get_from_cache(cache_key)
        if cached_result:
            logger.debug("Stakeholder detection cache hit")
            return cached_result

        # Use direct LLM-based stakeholder detection (V3 implementation)
        from backend.services.llm import LLMServiceFactory

        llm_service = LLMServiceFactory.create("gemini")
        stakeholder_result = await _detect_stakeholders_with_llm(llm_service, conversation_context, context_analysis, industry_analysis)

        # V3 Enhancement: Add stakeholder prioritization
        if stakeholder_result:
            prioritized_stakeholders = _prioritize_stakeholders(stakeholder_result, context_analysis)
            stakeholder_result.update(prioritized_stakeholders)

            # Add confidence scoring
            confidence_score = _calculate_stakeholder_confidence(stakeholder_result)
            stakeholder_result['confidence'] = confidence_score

            # Store confidence in metrics
            service.metrics.confidence_scores['stakeholder_detection'] = confidence_score

        # Store in cache
        service._store_in_cache(cache_key, stakeholder_result)

        logger.debug(f"Stakeholder detection completed: {len(stakeholder_result.get('stakeholders', [])) if stakeholder_result else 0} stakeholders found")
        return stakeholder_result

    except Exception as e:
        logger.error(f"Stakeholder detection failed: {e}")
        return None


async def analyze_conversation_flow(
    service,
    messages: List[Dict[str, Any]],
    context_analysis: Dict[str, Any],
    intent_analysis: Dict[str, Any]
) -> Dict[str, Any]:
    """Analyze conversation flow and determine next steps."""

    if not service.config.enable_conversation_flow:
        return {}

    try:
        # Create cache key based on message count and latest intent
        message_count = len(messages)
        latest_intent = intent_analysis.get('intent', 'unknown')
        context_hash = hashlib.md5(f"flow:{message_count}:{latest_intent}".encode()).hexdigest()
        cache_key = service._get_cache_key("conversation_flow", context_hash)

        # Check cache first
        cached_result = service._get_from_cache(cache_key)
        if cached_result:
            logger.debug("Conversation flow cache hit")
            return cached_result

        # Analyze conversation progression
        flow_result = {
            'current_stage': _determine_conversation_stage(messages, context_analysis, intent_analysis),
            'next_recommended_action': _recommend_next_action(messages, context_analysis, intent_analysis),
            'conversation_quality': _assess_conversation_quality(messages, context_analysis),
            'readiness_for_questions': _assess_question_readiness(messages, context_analysis, intent_analysis),
            'conversation_depth': len([msg for msg in messages if msg.get('role') == 'user']),
            'engagement_level': _assess_engagement_level(messages)
        }

        # Add confidence scoring
        confidence_score = _calculate_flow_confidence(flow_result)
        flow_result['confidence'] = confidence_score

        # Store confidence in metrics
        service.metrics.confidence_scores['conversation_flow'] = confidence_score

        # Store in cache
        service._store_in_cache(cache_key, flow_result)

        logger.debug(f"Conversation flow analysis completed: stage={flow_result['current_stage']}, action={flow_result['next_recommended_action']}")
        return flow_result

    except Exception as e:
        logger.error(f"Conversation flow analysis failed: {e}")
        return {}


def _analyze_industry_subcategories(industry_result: Dict[str, Any], context_analysis: Dict[str, Any]) -> List[str]:
    """Analyze industry sub-categories."""
    try:
        industry = industry_result.get('industry', '').lower()
        business_idea = context_analysis.get('businessIdea') or context_analysis.get('business_idea', '')

        # Basic sub-category mapping
        subcategory_map = {
            'technology': ['software', 'hardware', 'ai', 'mobile', 'web'],
            'healthcare': ['medical', 'wellness', 'fitness', 'mental health'],
            'education': ['online learning', 'training', 'certification'],
            'retail': ['e-commerce', 'marketplace', 'subscription'],
            'service': ['consulting', 'maintenance', 'support']
        }

        subcategories = subcategory_map.get(industry, [])

        # Filter based on business idea keywords
        if business_idea:
            business_lower = business_idea.lower()
            relevant_subcategories = [sub for sub in subcategories if any(word in business_lower for word in sub.split())]
            return relevant_subcategories[:3]  # Limit to 3 most relevant

        return subcategories[:3]

    except Exception:
        return []


def _calculate_industry_confidence(industry_result: Dict[str, Any]) -> float:
    """Calculate confidence score for industry analysis."""
    try:
        industry = industry_result.get('industry', '')
        reasoning = industry_result.get('reasoning', '')

        # Base confidence on industry specificity and reasoning quality
        industry_specificity = 0.8 if industry and len(industry) > 5 else 0.4
        reasoning_quality = min(1.0, len(reasoning) / 80) if reasoning else 0.0

        return (industry_specificity * 0.6 + reasoning_quality * 0.4)

    except Exception:
        return 0.0


def _prioritize_stakeholders(stakeholder_result: Dict[str, Any], context_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Prioritize stakeholders based on business context."""
    try:
        stakeholders = stakeholder_result.get('stakeholders', [])
        target_customer = context_analysis.get('targetCustomer') or context_analysis.get('target_customer', '')

        # Separate primary and secondary stakeholders
        primary = []
        secondary = []

        for stakeholder in stakeholders:
            stakeholder_name = stakeholder.get('name', '') if isinstance(stakeholder, dict) else str(stakeholder)

            # Primary stakeholders are direct users/customers
            if target_customer.lower() in stakeholder_name.lower() or stakeholder_name.lower() in target_customer.lower():
                primary.append(stakeholder)
            else:
                secondary.append(stakeholder)

        # If no clear primary stakeholder, use the first one
        if not primary and stakeholders:
            primary = [stakeholders[0]]
            secondary = stakeholders[1:]

        return {
            'primary': primary[:3],  # Limit to 3 primary
            'secondary': secondary[:3]  # Limit to 3 secondary
        }

    except Exception:
        return {'primary': [], 'secondary': []}


def _calculate_stakeholder_confidence(stakeholder_result: Dict[str, Any]) -> float:
    """Calculate confidence score for stakeholder detection."""
    try:
        stakeholders = stakeholder_result.get('stakeholders', [])
        primary = stakeholder_result.get('primary', [])

        # Base confidence on number and quality of stakeholders
        stakeholder_count_score = min(1.0, len(stakeholders) / 5)  # Optimal around 5 stakeholders
        primary_quality_score = 0.8 if primary else 0.2

        return (stakeholder_count_score * 0.4 + primary_quality_score * 0.6)

    except Exception:
        return 0.0


def _determine_conversation_stage(messages: List[Dict[str, Any]], context_analysis: Dict[str, Any], intent_analysis: Dict[str, Any]) -> str:
    """Determine current conversation stage."""
    try:
        user_messages = [msg for msg in messages if msg.get('role') == 'user']
        message_count = len(user_messages)
        intent = intent_analysis.get('intent', '')

        # Determine stage based on conversation progression
        if message_count <= 1:
            return 'initial_contact'
        elif message_count <= 2:
            return 'information_gathering'
        elif intent == 'question_request':
            return 'ready_for_questions'
        elif message_count <= 4:
            return 'context_refinement'
        else:
            return 'deep_exploration'

    except Exception:
        return 'unknown'


def _recommend_next_action(messages: List[Dict[str, Any]], context_analysis: Dict[str, Any], intent_analysis: Dict[str, Any]) -> str:
    """Recommend next action based on conversation state."""
    try:
        intent = intent_analysis.get('intent', '')
        business_idea = context_analysis.get('businessIdea') or context_analysis.get('business_idea', '')
        target_customer = context_analysis.get('targetCustomer') or context_analysis.get('target_customer', '')

        if intent == 'question_request':
            return 'generate_questions'
        elif not business_idea:
            return 'clarify_business_idea'
        elif not target_customer:
            return 'identify_target_customer'
        else:
            return 'continue_conversation'

    except Exception:
        return 'continue_conversation'


def _assess_conversation_quality(messages: List[Dict[str, Any]], context_analysis: Dict[str, Any]) -> float:
    """Assess overall conversation quality."""
    try:
        user_messages = [msg for msg in messages if msg.get('role') == 'user']

        # Quality factors
        message_count_score = min(1.0, len(user_messages) / 5)  # Optimal around 5 messages

        # Context completeness
        business_idea = context_analysis.get('businessIdea') or context_analysis.get('business_idea', '')
        target_customer = context_analysis.get('targetCustomer') or context_analysis.get('target_customer', '')
        problem = context_analysis.get('problem', '')

        context_completeness = sum([
            1 if business_idea else 0,
            1 if target_customer else 0,
            1 if problem else 0
        ]) / 3

        # Average message length (engagement indicator)
        avg_message_length = sum(len(msg.get('content', '')) for msg in user_messages) / max(1, len(user_messages))
        engagement_score = min(1.0, avg_message_length / 50)  # Optimal around 50 chars

        return (message_count_score * 0.3 + context_completeness * 0.5 + engagement_score * 0.2)

    except Exception:
        return 0.0


def _assess_question_readiness(messages: List[Dict[str, Any]], context_analysis: Dict[str, Any], intent_analysis: Dict[str, Any]) -> bool:
    """Assess if conversation is ready for question generation."""
    try:
        # Check intent - accept both question_request and generate_questions
        intent = intent_analysis.get('intent', '')
        if intent not in ['question_request', 'generate_questions']:
            return False

        # Check context completeness
        business_idea = context_analysis.get('businessIdea') or context_analysis.get('business_idea', '')
        target_customer = context_analysis.get('targetCustomer') or context_analysis.get('target_customer', '')

        # Minimum requirements
        has_business_idea = bool(business_idea and len(business_idea) > 10)
        has_target_customer = bool(target_customer and len(target_customer) > 5)

        # Conversation depth
        user_messages = [msg for msg in messages if msg.get('role') == 'user']
        sufficient_depth = len(user_messages) >= 2

        return has_business_idea and has_target_customer and sufficient_depth

    except Exception:
        return False


def _assess_engagement_level(messages: List[Dict[str, Any]]) -> float:
    """Assess user engagement level."""
    try:
        user_messages = [msg for msg in messages if msg.get('role') == 'user']

        if not user_messages:
            return 0.0

        # Engagement indicators
        avg_length = sum(len(msg.get('content', '')) for msg in user_messages) / len(user_messages)
        length_score = min(1.0, avg_length / 100)  # Optimal around 100 chars

        # Message frequency (more messages = higher engagement)
        frequency_score = min(1.0, len(user_messages) / 10)  # Optimal around 10 messages

        return (length_score * 0.6 + frequency_score * 0.4)

    except Exception:
        return 0.0


def _calculate_flow_confidence(flow_result: Dict[str, Any]) -> float:
    """Calculate confidence score for conversation flow analysis."""
    try:
        stage = flow_result.get('current_stage', '')
        quality = flow_result.get('conversation_quality', 0.0)
        engagement = flow_result.get('engagement_level', 0.0)

        # Base confidence on stage clarity and quality metrics
        stage_clarity = 0.8 if stage and stage != 'unknown' else 0.2
        quality_score = quality
        engagement_score = engagement

        return (stage_clarity * 0.4 + quality_score * 0.3 + engagement_score * 0.3)

    except Exception:
        return 0.0


# Helper functions for LLM-based analysis
async def _extract_context_with_llm(llm_service, conversation_context: str, latest_input: str, existing_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Extract business context using LLM analysis."""

    prompt = f"""Analyze this customer research conversation and extract the key business context.

Conversation:
{conversation_context}

Latest user input: "{latest_input}"

Extract and return ONLY a JSON object with these fields:
- business_idea: What product/service are they building? Include ALL features and capabilities mentioned
- target_customer: Who are their target customers? (specific roles/personas)
- problem: What problem are they solving? (main pain point)
- stage: What stage are they at? (initial, validation, development, launch)
- confidence: How confident are you in this extraction? (0.0-1.0)

Return only valid JSON, no other text."""

    try:
        response = await llm_service.generate_text(prompt, max_tokens=1000, temperature=0.1)

        # Parse JSON response - strip markdown code blocks if present
        import json
        import re

        # Remove markdown code blocks
        json_text = response.strip()
        if json_text.startswith('```json'):
            json_text = re.sub(r'^```json\s*', '', json_text)
            json_text = re.sub(r'\s*```$', '', json_text)
        elif json_text.startswith('```'):
            json_text = re.sub(r'^```\s*', '', json_text)
            json_text = re.sub(r'\s*```$', '', json_text)

        result = json.loads(json_text.strip())

        # Merge with existing context if provided
        if existing_context:
            for key, value in existing_context.items():
                if key not in result or not result[key]:
                    result[key] = value

        return result

    except Exception as e:
        logger.error(f"Error extracting context with LLM: {e}")
        # Return fallback context
        return {
            "business_idea": latest_input if latest_input else "Not specified",
            "target_customer": "Not specified",
            "problem": "Not specified",
            "stage": "initial",
            "confidence": 0.3
        }


async def _analyze_intent_with_llm(llm_service, conversation_context: str, latest_input: str, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze user intent using LLM."""

    prompt = f"""Analyze the user's intent in this customer research conversation.

Conversation context:
{conversation_context}

Latest input: "{latest_input}"

Determine the user's intent and return ONLY a JSON object with:
- intent: Primary intent (clarify_business, define_customers, validate_problem, generate_questions, other)
- confidence: Confidence level (0.0-1.0)
- next_step: What should happen next (ask_business_idea, ask_target_customer, ask_problem, generate_questions)
- readiness_score: How ready are they for question generation? (0.0-1.0)

Return only valid JSON, no other text."""

    try:
        response = await llm_service.generate_text(prompt, max_tokens=500, temperature=0.1)

        import json
        import re

        # Remove markdown code blocks
        json_text = response.strip()
        if json_text.startswith('```json'):
            json_text = re.sub(r'^```json\s*', '', json_text)
            json_text = re.sub(r'\s*```$', '', json_text)
        elif json_text.startswith('```'):
            json_text = re.sub(r'^```\s*', '', json_text)
            json_text = re.sub(r'\s*```$', '', json_text)

        result = json.loads(json_text.strip())
        return result

    except Exception as e:
        logger.error(f"Error analyzing intent with LLM: {e}")
        return {
            "intent": "clarify_business",
            "confidence": 0.5,
            "next_step": "ask_business_idea",
            "readiness_score": 0.3
        }


async def _validate_business_readiness_with_llm(llm_service, conversation_context: str, latest_input: str) -> Dict[str, Any]:
    """Validate business readiness using LLM."""

    prompt = f"""Analyze this customer research conversation to assess business readiness.

Conversation:
{conversation_context}

Latest input: "{latest_input}"

Assess the business readiness and return ONLY a JSON object with:
- ready_for_questions: Boolean - true if ready to generate research questions, false if more context needed
- readiness_score: Overall readiness for customer research (0.0-1.0)
- missing_elements: List of missing key elements
- strengths: List of clear strengths in their business concept
- recommendations: List of specific recommendations
- confidence: Confidence in this assessment (0.0-1.0)

Return only valid JSON, no other text."""

    try:
        response = await llm_service.generate_text(prompt, max_tokens=800, temperature=0.1)

        import json
        import re

        # Remove markdown code blocks
        json_text = response.strip()
        if json_text.startswith('```json'):
            json_text = re.sub(r'^```json\s*', '', json_text)
            json_text = re.sub(r'\s*```$', '', json_text)
        elif json_text.startswith('```'):
            json_text = re.sub(r'^```\s*', '', json_text)
            json_text = re.sub(r'\s*```$', '', json_text)

        result = json.loads(json_text.strip())
        return result

    except Exception as e:
        logger.error(f"Error validating business readiness with LLM: {e}")
        return {
            "ready_for_questions": False,
            "readiness_score": 0.5,
            "missing_elements": ["business_idea", "target_customer", "problem"],
            "strengths": [],
            "recommendations": ["Define your business idea clearly"],
            "confidence": 0.3
        }


async def _classify_industry_with_llm(llm_service, conversation_context: str, context_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Classify industry using LLM analysis."""

    business_idea = context_analysis.get('business_idea', '')

    prompt = f"""Analyze this business idea and classify the industry/domain.

Business idea: {business_idea}
Conversation context: {conversation_context}

Classify the industry and return ONLY a JSON object with:
- industry: Primary industry category (tech, healthcare, finance, retail, etc.)
- sub_industry: More specific sub-category
- confidence: Confidence in classification (0.0-1.0)
- characteristics: List of key industry characteristics
- research_considerations: List of industry-specific research considerations

Return only valid JSON, no other text."""

    try:
        response = await llm_service.generate_text(prompt, max_tokens=600, temperature=0.1)

        import json
        import re

        # Remove markdown code blocks
        json_text = response.strip()
        if json_text.startswith('```json'):
            json_text = re.sub(r'^```json\s*', '', json_text)
            json_text = re.sub(r'\s*```$', '', json_text)
        elif json_text.startswith('```'):
            json_text = re.sub(r'^```\s*', '', json_text)
            json_text = re.sub(r'\s*```$', '', json_text)

        result = json.loads(json_text.strip())
        return result

    except Exception as e:
        logger.error(f"Error classifying industry with LLM: {e}")
        return {
            "industry": "general",
            "sub_industry": "unknown",
            "confidence": 0.3,
            "characteristics": [],
            "research_considerations": ["Focus on user needs and pain points"]
        }


async def _detect_stakeholders_with_llm(llm_service, conversation_context: str, context_analysis: Dict[str, Any], industry_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Detect stakeholders using LLM analysis."""

    business_idea = context_analysis.get('business_idea', '')
    target_customer = context_analysis.get('target_customer', '')
    industry = industry_analysis.get('industry', 'general')

    prompt = f"""Analyze this business context and identify key stakeholders for customer research.

Business idea: {business_idea}
Target customer: {target_customer}
Industry: {industry}
Conversation: {conversation_context}

Identify stakeholders and return ONLY a JSON object with:
- primary: List of primary stakeholders (direct users/buyers) with name and description
- secondary: List of secondary stakeholders (influencers/decision makers) with name and description
- confidence: Confidence in stakeholder identification (0.0-1.0)
- reasoning: Brief explanation of stakeholder selection

Each stakeholder should have: {{"name": "Stakeholder Name", "description": "Role description"}}

Return only valid JSON, no other text."""

    try:
        response = await llm_service.generate_text(prompt, max_tokens=800, temperature=0.1)

        import json
        import re

        # Remove markdown code blocks
        json_text = response.strip()
        if json_text.startswith('```json'):
            json_text = re.sub(r'^```json\s*', '', json_text)
            json_text = re.sub(r'\s*```$', '', json_text)
        elif json_text.startswith('```'):
            json_text = re.sub(r'^```\s*', '', json_text)
            json_text = re.sub(r'\s*```$', '', json_text)

        result = json.loads(json_text.strip())
        return result

    except Exception as e:
        logger.error(f"Error detecting stakeholders with LLM: {e}")
        return {
            "primary": [
                {"name": "End Users", "description": "Primary users of the product/service"},
                {"name": "Customers", "description": "People who purchase the product/service"}
            ],
            "secondary": [
                {"name": "Decision Makers", "description": "People who influence purchasing decisions"}
            ],
            "confidence": 0.3,
            "reasoning": "Generic stakeholder fallback"
        }
