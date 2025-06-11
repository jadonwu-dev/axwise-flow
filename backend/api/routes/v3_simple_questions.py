"""
Question generation functions for Customer Research API v3 Simplified.

This module contains all question generation and response creation logic
for the V3 Simple customer research system.

Extracted from customer_research_v3_simple.py for better modularity.
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


async def generate_response_enhanced(
    service,
    conversation_context: str,
    latest_input: str,
    context_analysis: Dict[str, Any],
    intent_analysis: Dict[str, Any],
    business_validation: Dict[str, Any],
    industry_analysis: Optional[Dict[str, Any]],
    stakeholder_detection: Optional[Dict[str, Any]],
    conversation_flow: Dict[str, Any]
) -> Dict[str, Any]:
    """Generate enhanced response with V3 features."""
    
    try:
        # Check if we should generate questions
        should_generate_questions = _should_generate_questions(
            context_analysis, intent_analysis, business_validation, conversation_flow
        )
        
        if should_generate_questions:
            logger.info("Generating comprehensive questions")
            return await _generate_comprehensive_questions(
                service, context_analysis, stakeholder_detection, 
                industry_analysis, conversation_flow
            )
        else:
            logger.info("Generating guidance response")
            return await _generate_guidance_response(
                service, conversation_context, latest_input, context_analysis,
                intent_analysis, business_validation, conversation_flow
            )
            
    except Exception as e:
        logger.error(f"Response generation failed: {e}")
        return _create_fallback_response(context_analysis)


def _should_generate_questions(
    context_analysis: Dict[str, Any],
    intent_analysis: Dict[str, Any], 
    business_validation: Dict[str, Any],
    conversation_flow: Dict[str, Any]
) -> bool:
    """Determine if we should generate questions."""
    
    try:
        # Check user intent
        user_intent = intent_analysis.get('intent', '')
        user_wants_questions = user_intent == 'question_request'
        
        # Check business readiness
        business_ready = business_validation.get('ready_for_questions', False)
        
        # Check conversation readiness
        conversation_ready = conversation_flow.get('readiness_for_questions', False)
        
        # All conditions must be met
        should_generate = user_wants_questions and business_ready and conversation_ready
        
        logger.debug(f"Question generation decision: {should_generate}")
        logger.debug(f"  - User wants questions: {user_wants_questions}")
        logger.debug(f"  - Business ready: {business_ready}")
        logger.debug(f"  - Conversation ready: {conversation_ready}")
        
        return should_generate
        
    except Exception as e:
        logger.warning(f"Error in question generation decision: {e}")
        return False


async def _generate_comprehensive_questions(
    service,
    context_analysis: Dict[str, Any],
    stakeholder_detection: Optional[Dict[str, Any]],
    industry_analysis: Optional[Dict[str, Any]],
    conversation_flow: Dict[str, Any]
) -> Dict[str, Any]:
    """Generate comprehensive questions using V3 stakeholder data."""
    
    try:
        # Extract business context
        business_idea = context_analysis.get('businessIdea') or context_analysis.get('business_idea', 'your business')
        target_customer = context_analysis.get('targetCustomer') or context_analysis.get('target_customer', 'customers')
        problem = context_analysis.get('problem', 'challenges they face')
        
        # Get stakeholder data
        primary_stakeholders = []
        secondary_stakeholders = []
        
        if stakeholder_detection:
            primary_stakeholders = stakeholder_detection.get('primary', [])
            secondary_stakeholders = stakeholder_detection.get('secondary', [])
        
        # If no stakeholders detected, create default ones
        if not primary_stakeholders:
            primary_stakeholders = [{
                'name': target_customer.title() if target_customer else 'Primary Users',
                'description': f'The primary users of the {business_idea}'
            }]
        
        if not secondary_stakeholders:
            secondary_stakeholders = [{
                'name': 'Family Members',
                'description': f'People who care about or help {target_customer}'
            }]
        
        # Generate questions for each stakeholder
        comprehensive_questions = {
            "primaryStakeholders": [],
            "secondaryStakeholders": [],
            "timeEstimate": {
                "totalQuestions": 0,
                "estimatedMinutes": "0-0",
                "breakdown": {"primary": 0, "secondary": 0}
            }
        }
        
        # Add primary stakeholder questions
        for stakeholder in primary_stakeholders[:2]:  # Limit to 2 primary
            questions = _generate_stakeholder_questions(stakeholder, business_idea, target_customer, problem, 'primary')
            comprehensive_questions["primaryStakeholders"].append(questions)
        
        # Add secondary stakeholder questions
        for stakeholder in secondary_stakeholders[:2]:  # Limit to 2 secondary
            questions = _generate_stakeholder_questions(stakeholder, business_idea, target_customer, problem, 'secondary')
            comprehensive_questions["secondaryStakeholders"].append(questions)
        
        # Calculate time estimate
        primary_count = sum(len(s["questions"]["problemDiscovery"]) + len(s["questions"]["solutionValidation"]) + len(s["questions"]["followUp"]) 
                          for s in comprehensive_questions["primaryStakeholders"])
        secondary_count = sum(len(s["questions"]["problemDiscovery"]) + len(s["questions"]["solutionValidation"]) + len(s["questions"]["followUp"]) 
                            for s in comprehensive_questions["secondaryStakeholders"])
        
        total_questions = primary_count + secondary_count
        estimated_minutes = f"{total_questions * 2}-{total_questions * 3}"
        
        comprehensive_questions["timeEstimate"] = {
            "totalQuestions": total_questions,
            "estimatedMinutes": estimated_minutes,
            "breakdown": {"primary": primary_count, "secondary": secondary_count}
        }
        
        # Return response with comprehensive questions
        return {
            "content": "COMPREHENSIVE_QUESTIONS_COMPONENT",
            "questions": comprehensive_questions,
            "suggestions": [],
            "metadata": {
                "comprehensiveQuestions": comprehensive_questions,
                "businessContext": f"{business_idea}, addressing {problem}",
                "type": "component",
                "request_id": service.request_id
            }
        }
        
    except Exception as e:
        logger.error(f"Comprehensive question generation failed: {e}")
        return _create_emergency_questions(context_analysis)


def _generate_stakeholder_questions(
    stakeholder: Dict[str, Any],
    business_idea: str,
    target_customer: str,
    problem: str,
    stakeholder_type: str
) -> Dict[str, Any]:
    """Generate questions for a specific stakeholder."""
    
    try:
        stakeholder_name = stakeholder.get('name', 'Stakeholder') if isinstance(stakeholder, dict) else str(stakeholder)
        stakeholder_desc = stakeholder.get('description', 'Key stakeholder') if isinstance(stakeholder, dict) else f'Key stakeholder: {stakeholder}'
        
        if stakeholder_type == 'primary':
            return {
                "name": stakeholder_name,
                "description": stakeholder_desc,
                "questions": {
                    "problemDiscovery": [
                        f"What challenges do you currently face with {_extract_service_type(business_idea)}?",
                        f"How do you currently handle {_extract_problem_area(problem)}?",
                        "What's the most frustrating part of your current situation?",
                        "How often do you encounter these problems?",
                        "What would make this easier for you?"
                    ],
                    "solutionValidation": [
                        f"Would a {business_idea} help solve your problem?",
                        "What features would be most important to you?",
                        "How much would you be willing to pay for this service?",
                        "What would convince you to try this service?",
                        "What concerns would you have about using this?"
                    ],
                    "followUp": [
                        "Would you recommend this to others in your situation?",
                        "What else should we know about your needs?",
                        "Any other feedback or suggestions?"
                    ]
                }
            }
        else:  # secondary
            return {
                "name": stakeholder_name,
                "description": stakeholder_desc,
                "questions": {
                    "problemDiscovery": [
                        f"How do you currently help {target_customer} with their needs?",
                        "What challenges do you see them facing?",
                        "How does this affect you or your family?"
                    ],
                    "solutionValidation": [
                        f"Would you support using a {business_idea}?",
                        "What would you want to see in this service?",
                        "What concerns would you have?"
                    ],
                    "followUp": [
                        "Would you help them access this service?",
                        "Any other thoughts?"
                    ]
                }
            }
            
    except Exception as e:
        logger.warning(f"Error generating stakeholder questions: {e}")
        return {
            "name": "Stakeholder",
            "description": "Key stakeholder",
            "questions": {
                "problemDiscovery": ["What challenges do you face?"],
                "solutionValidation": ["Would this help you?"],
                "followUp": ["Any other thoughts?"]
            }
        }


def _extract_service_type(business_idea: str) -> str:
    """Extract service type from business idea."""
    try:
        if not business_idea:
            return "this service"
        
        # Extract the last meaningful word
        words = business_idea.split()
        if words:
            return words[-1].lower()
        return "this service"
        
    except Exception:
        return "this service"


def _extract_problem_area(problem: str) -> str:
    """Extract problem area from problem description."""
    try:
        if not problem:
            return "these needs"
        
        # Extract first part before punctuation
        problem_area = problem.split('.')[0].split(',')[0]
        return problem_area.lower() if problem_area else "these needs"
        
    except Exception:
        return "these needs"


async def _generate_guidance_response(
    service,
    conversation_context: str,
    latest_input: str,
    context_analysis: Dict[str, Any],
    intent_analysis: Dict[str, Any],
    business_validation: Dict[str, Any],
    conversation_flow: Dict[str, Any]
) -> Dict[str, Any]:
    """Generate guidance response when not ready for questions."""
    
    try:
        # Import V1/V2 proven response generation
        from backend.services.customer_research import CustomerResearchService
        v1_service = CustomerResearchService()
        
        # Use V1/V2 proven method
        response_result = await v1_service.generate_response(
            conversation_context, latest_input, context_analysis,
            intent_analysis, business_validation
        )
        
        # V3 Enhancement: Add contextual suggestions
        contextual_suggestions = _generate_contextual_suggestions(
            context_analysis, intent_analysis, business_validation, conversation_flow
        )
        
        if contextual_suggestions:
            response_result['suggestions'] = contextual_suggestions
        
        return response_result
        
    except Exception as e:
        logger.error(f"Guidance response generation failed: {e}")
        return _create_fallback_response(context_analysis)


def _generate_contextual_suggestions(
    context_analysis: Dict[str, Any],
    intent_analysis: Dict[str, Any],
    business_validation: Dict[str, Any],
    conversation_flow: Dict[str, Any]
) -> List[str]:
    """Generate contextual suggestions based on current state."""
    
    try:
        suggestions = []
        
        # Get current state
        business_idea = context_analysis.get('businessIdea') or context_analysis.get('business_idea', '')
        target_customer = context_analysis.get('targetCustomer') or context_analysis.get('target_customer', '')
        problem = context_analysis.get('problem', '')
        ready_for_questions = business_validation.get('ready_for_questions', False)
        
        # Context-specific suggestions
        if not business_idea:
            suggestions.append("Tell me more about your business idea")
        elif not target_customer:
            suggestions.append("Who are your target customers?")
        elif not problem:
            suggestions.append("What problem does this solve?")
        elif ready_for_questions:
            suggestions.append("Yes, that's right.")
            suggestions.append("Generate research questions")
        else:
            suggestions.extend([
                "Tell me more about the challenges",
                "Who else might be involved?",
                "What's the biggest pain point?"
            ])
        
        return suggestions[:3]  # Limit to 3 suggestions
        
    except Exception:
        return ["Tell me more", "Continue", "What else?"]


def _create_emergency_questions(context_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Create emergency fallback questions."""
    
    try:
        business_idea = context_analysis.get('businessIdea') or context_analysis.get('business_idea', 'your business')
        
        emergency_questions = {
            "primaryStakeholders": [{
                "name": "Primary Users",
                "description": f"Users of the {business_idea}",
                "questions": {
                    "problemDiscovery": [
                        "What challenges do you currently face?",
                        "How do you handle this now?",
                        "What's most frustrating about the current situation?"
                    ],
                    "solutionValidation": [
                        "Would this solution help you?",
                        "What features are most important?",
                        "How much would you pay for this?"
                    ],
                    "followUp": [
                        "Would you recommend this to others?",
                        "Any other thoughts?"
                    ]
                }
            }],
            "secondaryStakeholders": [],
            "timeEstimate": {
                "totalQuestions": 8,
                "estimatedMinutes": "16-24",
                "breakdown": {"primary": 8, "secondary": 0}
            }
        }
        
        return {
            "content": "COMPREHENSIVE_QUESTIONS_COMPONENT",
            "questions": emergency_questions,
            "suggestions": [],
            "metadata": {
                "comprehensiveQuestions": emergency_questions,
                "businessContext": business_idea,
                "type": "component",
                "emergency_fallback": True
            }
        }
        
    except Exception:
        return _create_fallback_response({})


def _create_fallback_response(context_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Create ultimate fallback response."""
    
    return {
        "content": "I'd be happy to help you create research questions. Could you tell me more about your business idea?",
        "questions": None,
        "suggestions": [
            "Tell me about your business idea",
            "Who are your customers?",
            "What problem are you solving?"
        ],
        "metadata": {
            "fallback_response": True,
            "extracted_context": context_analysis
        }
    }
