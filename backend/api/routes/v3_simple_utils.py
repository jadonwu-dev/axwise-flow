"""
Utility functions for Customer Research API v3 Simplified.

This module contains helper functions for text formatting, caching,
and other utility operations used by the V3 Simple system.

Extracted from customer_research_v3_simple.py for better modularity.
"""

import json
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


def format_prompt_content(prompt: str) -> str:
    """Format prompt content with proper truncation and line breaks."""
    if len(prompt) <= 500:
        return prompt

    # Find logical truncation points
    truncate_at = -1

    # Try to find end of a complete section (double newline)
    for i in range(300, min(500, len(prompt))):
        if prompt[i:i+2] == '\n\n':
            truncate_at = i
            break

    # If no section break, try end of sentence
    if truncate_at == -1:
        for i in range(400, min(500, len(prompt))):
            if prompt[i:i+2] in ['. ', '.\n']:
                truncate_at = i + 1
                break

    # If no sentence break, use hard limit
    if truncate_at == -1:
        truncate_at = 450

    return prompt[:truncate_at] + "\n\n[... content truncated for readability ...]"


def format_response_content(response: str) -> str:
    """Format response content with proper JSON formatting and truncation."""
    try:
        # Try to parse and pretty-print JSON
        if response.strip().startswith('{') or response.strip().startswith('['):
            parsed_json = json.loads(response)
            formatted_json = json.dumps(parsed_json, indent=2, ensure_ascii=False)

            # If formatted JSON is too long, truncate intelligently
            if len(formatted_json) > 800:
                lines = formatted_json.split('\n')
                truncated_lines = []
                char_count = 0

                for line in lines:
                    if char_count + len(line) > 600:
                        truncated_lines.append("  ...")
                        truncated_lines.append("}")
                        break
                    truncated_lines.append(line)
                    char_count += len(line)

                return '\n'.join(truncated_lines)

            return formatted_json
    except:
        pass

    # If not JSON or parsing failed, format as regular text
    if len(response) <= 600:
        return response

    # Find logical truncation point for text
    truncate_at = response.find('\n', 500)
    if truncate_at == -1:
        truncate_at = response.find('. ', 500)
    if truncate_at == -1:
        truncate_at = 550

    return response[:truncate_at] + "\n\n[... content truncated for readability ...]"


def truncate_text(text: str, max_length: int) -> str:
    """Truncate text to maximum length with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def format_parsed_result(operation_name: str, result: Any) -> str:
    """Format the parsed result in a readable way based on operation type."""

    if operation_name == "Context Analysis" and isinstance(result, dict):
        # Get values with explicit None handling
        business_idea = result.get('businessIdea') or result.get('business_idea')
        target_customer = result.get('targetCustomer') or result.get('target_customer')
        problem = result.get('problem')

        # Convert None values to strings explicitly
        business_idea = 'Not specified' if business_idea is None else str(business_idea)
        target_customer = 'Not specified' if target_customer is None else str(target_customer)
        problem = 'Not specified' if problem is None else str(problem)

        # Truncate long values for readability
        business_idea = truncate_text(business_idea, 80)
        target_customer = truncate_text(target_customer, 60)
        problem = truncate_text(problem, 100)

        return f"• Business Idea: {business_idea}\n• Target Customer: {target_customer}\n• Problem: {problem}"

    elif operation_name == "Intent Analysis" and isinstance(result, dict):
        intent = result.get('intent')
        confidence = result.get('confidence')
        reasoning = result.get('reasoning')
        next_action = result.get('next_action')

        # Convert None values to strings explicitly
        intent = 'unknown' if intent is None else str(intent)
        confidence = 0 if confidence is None else confidence
        reasoning = 'No reasoning provided' if reasoning is None else str(reasoning)
        next_action = 'Continue conversation' if next_action is None else str(next_action)

        reasoning = truncate_text(reasoning, 120)
        next_action = truncate_text(next_action, 80)

        return f"• Intent: {intent}\n• Confidence: {confidence:.1%}\n• Reasoning: {reasoning}\n• Next Action: {next_action}"

    elif operation_name == "Business Validation" and isinstance(result, dict):
        ready = result.get('ready_for_questions', False)
        confidence = result.get('confidence')
        reasoning = result.get('reasoning')
        missing = result.get('missing_elements')
        quality = result.get('conversation_quality')

        # Convert None values to appropriate defaults
        confidence = 0 if confidence is None else confidence
        reasoning = 'No reasoning provided' if reasoning is None else str(reasoning)
        missing = [] if missing is None else missing
        quality = 'unknown' if quality is None else str(quality)

        reasoning = truncate_text(reasoning, 150)
        missing_text = ', '.join(str(m) for m in missing[:3]) if missing else 'None'
        if len(missing) > 3:
            missing_text += f" (+{len(missing)-3} more)"

        return f"• Ready for Questions: {'Yes' if ready else 'No'}\n• Confidence: {confidence:.1%}\n• Quality: {quality}\n• Missing Elements: {missing_text}\n• Reasoning: {reasoning}"

    elif operation_name == "Industry Analysis" and isinstance(result, dict):
        industry = result.get('industry', 'Unknown')
        confidence = result.get('confidence', 0)
        reasoning = result.get('reasoning', 'No reasoning provided')
        sub_categories = result.get('sub_categories', [])

        reasoning = truncate_text(reasoning, 120)
        sub_cats_text = ', '.join(sub_categories[:3]) if sub_categories else 'None'
        if len(sub_categories) > 3:
            sub_cats_text += f" (+{len(sub_categories)-3} more)"

        return f"• Industry: {industry}\n• Confidence: {confidence:.1%}\n• Sub-categories: {sub_cats_text}\n• Reasoning: {reasoning}"

    elif operation_name == "Stakeholder Detection" and isinstance(result, dict):
        stakeholders = result.get('stakeholders', [])
        confidence = result.get('confidence', 0)

        stakeholder_names = [s.get('name', 'Unknown') for s in stakeholders[:4]]
        stakeholder_text = ', '.join(stakeholder_names) if stakeholder_names else 'None'
        if len(stakeholders) > 4:
            stakeholder_text += f" (+{len(stakeholders)-4} more)"

        return f"• Stakeholders: {stakeholder_text}\n• Confidence: {confidence:.1%}"

    elif operation_name == "Conversation Flow" and isinstance(result, dict):
        stage = result.get('current_stage', 'unknown')
        action = result.get('next_recommended_action', 'continue')
        quality = result.get('conversation_quality', 0)
        readiness = result.get('readiness_for_questions', False)

        return f"• Current Stage: {stage}\n• Next Action: {action}\n• Quality: {quality:.1%}\n• Ready for Questions: {'Yes' if readiness else 'No'}"

    # Fallback for unknown operation types
    return f"• Result: {str(result)[:200]}{'...' if len(str(result)) > 200 else ''}"


def get_operation_description(operation_name: str, phase: str, result: Any = None, duration_ms: int = None, 
                            llm_interactions: list = None, format_prompt_fn=None, format_response_fn=None, 
                            format_result_fn=None) -> str:
    """Generate properly formatted, readable descriptions for thinking process steps with raw LLM content."""

    if phase == "starting":
        descriptions = {
            "Context Analysis": "🔍 CONTEXT EXTRACTION\n\nAnalyzing conversation to extract business idea, target customers, and problem statement...",
            "Intent Analysis": "🎯 INTENT DETECTION\n\nDetermining user's current intent and conversation stage...",
            "Business Validation": "✅ READINESS ASSESSMENT\n\nEvaluating business concept completeness for research question generation...",
            "Industry Analysis": "🏢 INDUSTRY CLASSIFICATION\n\nClassifying business into relevant industry categories...",
            "Stakeholder Detection": "👥 STAKEHOLDER MAPPING\n\nIdentifying key stakeholders in the business ecosystem...",
            "Conversation Flow": "🔄 FLOW ANALYSIS\n\nAnalyzing conversation progression and determining next steps...",
            "Response Generation": "💬 RESPONSE CREATION\n\nGenerating contextual response and suggestions..."
        }
        return descriptions.get(operation_name, f"🔧 {operation_name.upper()}\n\nStarting {operation_name.lower()}...")

    elif phase == "completed" and result:
        # Find the most recent LLM interaction for this operation
        llm_content = ""
        if llm_interactions:
            for interaction in reversed(llm_interactions):
                if interaction["operation"] == operation_name:
                    # Format the prompt with proper line breaks and logical truncation
                    prompt = format_prompt_fn(interaction["prompt"]) if format_prompt_fn else format_prompt_content(interaction["prompt"])

                    # Format the response with proper JSON formatting if it's JSON
                    response = format_response_fn(interaction["response"]) if format_response_fn else format_response_content(interaction["response"])

                    # Format parsed result in a readable way
                    parsed_result = format_result_fn(operation_name, result) if format_result_fn else format_parsed_result(operation_name, result)

                    llm_content = f"""

📝 LLM PROMPT:
{prompt}


🤖 LLM RESPONSE:
{response}


📊 PARSED RESULT:
{parsed_result}"""
                    break

        # If no LLM interaction found, show formatted parsed result only
        if not llm_content:
            parsed_result = format_result_fn(operation_name, result) if format_result_fn else format_parsed_result(operation_name, result)
            llm_content = f"""

📊 OPERATION RESULT:
{parsed_result}"""

        return f"✅ {operation_name.upper()} COMPLETED ({duration_ms}ms){llm_content}"

    # Fallback for any unhandled cases
    return f"🔧 {operation_name} {'completed' if duration_ms else 'in progress'}{'(' + str(duration_ms) + 'ms)' if duration_ms else '...'}"
