"""
Customer Research Prompts for LLM Services
"""

from typing import Dict, Any


class CustomerResearchPrompts:
    """
    Prompt templates for customer research tasks.
    """

    @staticmethod
    def get_prompt(request: Dict[str, Any]) -> str:
        """
        Generate customer research prompt based on request parameters.
        
        Args:
            request: Dictionary containing research context and parameters
            
        Returns:
            Formatted prompt string for customer research
        """
        
        # Extract context from request
        business_idea = request.get("business_idea", "")
        target_customer = request.get("target_customer", "")
        problem = request.get("problem", "")
        industry = request.get("industry", "general")
        conversation_context = request.get("conversation_context", "")
        
        # Base prompt for customer research
        prompt = f"""You are an expert customer research consultant helping entrepreneurs validate their business ideas through structured customer research.

CONTEXT:
- Business Idea: {business_idea if business_idea else "Not yet defined"}
- Target Customer: {target_customer if target_customer else "Not yet defined"}
- Problem: {problem if problem else "Not yet defined"}
- Industry: {industry}

CONVERSATION CONTEXT:
{conversation_context if conversation_context else "This is the beginning of the conversation."}

YOUR ROLE:
1. Help the user clearly define their business idea, target customers, and the problem they're solving
2. Guide them through a structured customer research process
3. Generate relevant, actionable research questions when they're ready
4. Provide insights and suggestions based on customer research best practices

GUIDELINES:
- Ask one focused question at a time to avoid overwhelming the user
- Be conversational and supportive, not interrogative
- Help users think deeply about their assumptions
- Suggest specific, actionable research methods
- Focus on problem-solution fit and customer development principles
- When generating research questions, make them specific and actionable

CURRENT TASK:
Based on the conversation context and current state, provide the next helpful response to guide the user through their customer research journey. If they have sufficient context defined, you can offer to generate specific research questions for them to use with their target customers.

Remember: The goal is to help them validate their business idea through real customer insights, not just theoretical analysis."""

        return prompt

    @staticmethod
    def get_context_extraction_prompt(conversation_history: str) -> str:
        """
        Generate prompt for extracting structured context from conversation.
        
        Args:
            conversation_history: Full conversation history as string
            
        Returns:
            Prompt for context extraction
        """
        
        return f"""Analyze the following customer research conversation and extract key information.

CONVERSATION HISTORY:
{conversation_history}

Extract and return a JSON object with the following structure:
{{
    "business_idea": "Brief description of the business idea or product concept",
    "target_customer": "Description of the target customer or user segment",
    "problem": "The problem or pain point being addressed",
    "industry": "The industry or market category",
    "stage": "current conversation stage (initial, business_idea, target_customer, validation, completed)",
    "readiness_for_questions": "boolean indicating if enough context exists to generate research questions"
}}

GUIDELINES:
- Extract only information that was explicitly mentioned or clearly implied
- Use "Not specified" for missing information
- Be concise but capture the essence of each element
- Stage should reflect where the conversation currently stands
- Set readiness_for_questions to true only if business_idea, target_customer, and problem are all reasonably defined

Return only the JSON object, no additional text."""

    @staticmethod
    def get_question_generation_prompt(context: Dict[str, Any]) -> str:
        """
        Generate prompt for creating research questions.
        
        Args:
            context: Dictionary with business context
            
        Returns:
            Prompt for generating research questions
        """
        
        business_idea = context.get("business_idea", "")
        target_customer = context.get("target_customer", "")
        problem = context.get("problem", "")
        industry = context.get("industry", "general")
        
        return f"""Generate a comprehensive set of customer research questions based on the following business context:

BUSINESS CONTEXT:
- Business Idea: {business_idea}
- Target Customer: {target_customer}
- Problem: {problem}
- Industry: {industry}

Create research questions that will help validate:
1. Problem validation - Does this problem really exist and matter to customers?
2. Solution validation - Would customers want this specific solution?
3. Market validation - Is there a viable market for this solution?
4. Customer behavior - How do customers currently handle this problem?

Return a JSON object with this structure:
{{
    "primary_research": {{
        "problem_validation": [
            "List of 5-7 questions to validate the problem exists and matters"
        ],
        "solution_validation": [
            "List of 5-7 questions to validate the proposed solution"
        ],
        "customer_behavior": [
            "List of 5-7 questions about current customer behavior and workflows"
        ]
    }},
    "secondary_research": {{
        "market_research": [
            "List of 3-5 questions for market size and competition research"
        ],
        "industry_trends": [
            "List of 3-5 questions about industry trends and opportunities"
        ]
    }},
    "interview_tips": [
        "List of 5-7 practical tips for conducting customer interviews"
    ]
}}

QUESTION GUIDELINES:
- Make questions open-ended and non-leading
- Focus on understanding current behavior, not hypothetical scenarios
- Include questions about pain points, current solutions, and decision-making processes
- Avoid questions that can be answered with simple yes/no
- Make questions specific to the industry and customer type
- Include follow-up question suggestions where appropriate

Return only the JSON object."""
