"""
API endpoint for parsing questionnaire files using LLM
"""

import logging
from typing import List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.llm.gemini_service import GeminiService

logger = logging.getLogger(__name__)

router = APIRouter()

class QuestionnaireParseRequest(BaseModel):
    content: str
    filename: str

class QuestionnaireParseResponse(BaseModel):
    business_idea: str
    target_customer: str
    problem: str
    questions: List[str]
    total_questions: int

@router.post("/parse-questionnaire", response_model=QuestionnaireParseResponse)
async def parse_questionnaire(request: QuestionnaireParseRequest):
    """Parse questionnaire file content using LLM"""
    
    try:
        logger.info(f"Parsing questionnaire file: {request.filename}")
        
        # Initialize Gemini service
        gemini_service = GeminiService()
        
        # Create parsing prompt
        prompt = f"""
Parse this questionnaire file and extract the following information:

1. Business Idea (the main business concept)
2. Target Customer (who the business serves)
3. Problem (what problem the business solves)
4. Questions (all interview questions, cleaned and formatted)

File content:
{request.content}

Return the information in this exact JSON format:
{{
    "business_idea": "extracted business idea",
    "target_customer": "extracted target customer",
    "problem": "extracted problem description",
    "questions": ["question 1", "question 2", "question 3", ...]
}}

Rules:
- Extract the actual values, not the labels
- Clean up questions (remove numbering like "1.", "2.", etc.)
- Include all questions that end with "?"
- If any field is missing, use a reasonable default based on context
- Ensure business_idea is never empty
"""

        # Get LLM response
        response = await gemini_service.generate_response(
            prompt=prompt,
            max_tokens=4000,
            temperature=0.1  # Low temperature for consistent parsing
        )
        
        logger.info(f"LLM parsing response: {response}")
        
        # Parse JSON response
        import json
        try:
            parsed_data = json.loads(response)
        except json.JSONDecodeError:
            # Try to extract JSON from response if it's wrapped in markdown
            import re
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
            if json_match:
                parsed_data = json.loads(json_match.group(1))
            else:
                raise ValueError("Could not parse JSON from LLM response")
        
        # Validate required fields
        if not parsed_data.get('business_idea'):
            raise ValueError("Business idea is required but not found")
        
        if not parsed_data.get('questions'):
            raise ValueError("No questions found in the file")
        
        return QuestionnaireParseResponse(
            business_idea=parsed_data['business_idea'],
            target_customer=parsed_data.get('target_customer', 'Customer'),
            problem=parsed_data.get('problem', 'Business problem'),
            questions=parsed_data['questions'],
            total_questions=len(parsed_data['questions'])
        )
        
    except Exception as e:
        logger.error(f"Failed to parse questionnaire: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Failed to parse questionnaire: {str(e)}"
        )
