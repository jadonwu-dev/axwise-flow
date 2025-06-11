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

        # Import V1/V2 proven context analysis
        from backend.services.customer_research import CustomerResearchService
        v1_service = CustomerResearchService()

        # Use V1/V2 proven method with V3 enhancements
        context_result = await v1_service.analyze_context(conversation_context, latest_input, existing_context)

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

        # Import V1/V2 proven intent analysis
        from backend.services.customer_research import CustomerResearchService
        v1_service = CustomerResearchService()

        # Use V1/V2 proven method
        intent_result = await v1_service.analyze_intent(conversation_context, latest_input, messages)

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
    """Enhanced business validation with V3 readiness logic."""

    try:
        # Create cache key
        context_hash = hashlib.md5(f"{conversation_context}:{latest_input}".encode()).hexdigest()
        cache_key = service._get_cache_key("business_validation", context_hash)

        # Check cache first
        cached_result = service._get_from_cache(cache_key)
        if cached_result:
            logger.debug("Business validation cache hit")
            return cached_result

        # Import V1/V2 proven validation
        from backend.services.customer_research import CustomerResearchService
        v1_service = CustomerResearchService()

        # Use V1/V2 proven method
        validation_result = await v1_service.validate_business_readiness(conversation_context, latest_input)

        # V3 Enhancement: Add detailed readiness scoring
        readiness_score = _calculate_readiness_score(validation_result)
        validation_result['readiness_score'] = readiness_score

        # V3 Enhancement: Add missing elements analysis
        missing_elements = _analyze_missing_elements(validation_result)
        validation_result['missing_elements'] = missing_elements

        # Store in cache
        service._store_in_cache(cache_key, validation_result)

        # Store confidence in metrics
        service.metrics.confidence_scores['business_validation'] = readiness_score

        logger.debug(f"Business validation completed: ready={validation_result.get('ready_for_questions', False)} (score: {readiness_score:.2f})")
        return validation_result

    except Exception as e:
        logger.error(f"Business validation failed: {e}")
        # Fallback to not ready
        return {
            'ready_for_questions': False,
            'confidence': 0.0,
            'reasoning': 'Validation failed due to error',
            'readiness_score': 0.0,
            'missing_elements': ['business_idea', 'target_customer', 'problem']
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

        # Import V1/V2 proven industry analysis
        from backend.services.customer_research import CustomerResearchService
        v1_service = CustomerResearchService()

        # Use V1/V2 proven method
        industry_result = await v1_service.analyze_industry(conversation_context, context_analysis)

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

        # Import V1/V2 proven stakeholder detection
        from backend.services.customer_research import CustomerResearchService
        v1_service = CustomerResearchService()

        # Use V1/V2 proven method
        stakeholder_result = await v1_service.detect_stakeholders(conversation_context, context_analysis, industry_analysis)

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
        # Check intent
        intent = intent_analysis.get('intent', '')
        if intent != 'question_request':
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
