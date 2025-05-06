from typing import List, Dict, Any

def transform_interview_data(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Transform flat interview data into structured persona format
    
    Args:
        data: List of interview QA items with user_ids
        
    Returns:
        List of persona objects with grouped respondents
    """
    if not isinstance(data, list) or not data:
        raise ValueError("Data must be a non-empty list")
    
    # Log input data structure
    print(f"Input data structure: {list(data[0].keys())}")
    
    # Check if data is already in the correct format
    if all(key in data[0] for key in ['persona_type', 'respondents']):
        print("Data already in persona format")
        return data
    elif all(key in data[0] for key in ['persona', 'respondents']):
        print("Converting legacy persona format")
        return [{**item, 'persona_type': item.pop('persona')} for item in data]
    
    # Initialize persona structures
    personas = {
        'B2C': {'persona_type': 'B2C', 'respondents': []},
        'B2B': {'persona_type': 'B2B', 'respondents': []},
        'HYBRID': {'persona_type': 'HYBRID', 'respondents': []}
    }
    
    # First group by user_id to collect all answers
    user_answers = {}
    for item in data:
        if not all(key in item for key in ['user_id', 'question', 'answer']):
            raise ValueError(f"Missing required fields in item: {item}")
            
        user_id = item['user_id']
        if user_id not in user_answers:
            # Extract persona type from user_id
            if '_' in user_id:
                # Handle format like "B2C_ST" -> "B2C"
                persona_type = user_id.split('_')[0].upper()
            else:
                # Handle format like "U001" -> map to appropriate persona type based on index
                index = int(user_id[1:]) if user_id[1:].isdigit() else -1
                if index >= 0:
                    # Map ranges to persona types (adjust ranges as needed)
                    if index < 200:
                        persona_type = 'B2C'
                    elif index < 400:
                        persona_type = 'B2B'
                    else:
                        persona_type = 'HYBRID'
                else:
                    print(f"Warning: Unknown persona type in user_id: {user_id}")
                    continue
            
            if persona_type not in personas:
                print(f"Warning: Unknown persona type in user_id: {user_id}")
                continue
                
            user_answers[user_id] = {
                'name': user_id,
                'answers': []
            }
        
        # Ensure answer is not empty
        if item['answer'].strip():
            answer_data = {
                'question': item['question'],
                'answer': item['answer']
            }
            # Include text field if present
            if 'text' in item and item['text'].strip():
                answer_data['text'] = item['text']
            user_answers[user_id]['answers'].append(answer_data)
    
    if not user_answers:
        raise ValueError("No valid user data found after filtering")
    
    # Add each user to their persona type
    for user_id, user_data in user_answers.items():
        # Skip users with no valid answers
        if not user_data['answers']:
            continue
            
        # Extract persona type using the same logic as above
        if '_' in user_id:
            persona_type = user_id.split('_')[0].upper()
        else:
            index = int(user_id[1:]) if user_id[1:].isdigit() else -1
            if index >= 0:
                if index < 200:
                    persona_type = 'B2C'
                elif index < 400:
                    persona_type = 'B2B'
                else:
                    persona_type = 'HYBRID'
            else:
                continue
        
        if persona_type in personas:
            personas[persona_type]['respondents'].append(user_data)
    
    # Return only personas that have respondents
    result = [p for p in personas.values() if p['respondents']]
    
    if not result:
        raise ValueError("No valid personas could be generated from the data")
    
    print(f"Generated {len(result)} personas: {[p['persona_type'] for p in result]}")
    return result

def validate_interview_data(data: List[Dict[str, Any]]) -> bool:
    """
    Validate interview data format
    
    Args:
        data: List of interview data items
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(data, list) or not data:
        return False
    
    # Check if data is in the new flat format
    required_fields_flat = {'user_id', 'question', 'answer'}
    if all(required_fields_flat.issubset(item.keys()) for item in data):
        return True
    
    # Check if data is in the original nested format
    required_fields_nested = {'persona', 'respondents'}
    if all(required_fields_nested.issubset(item.keys()) for item in data):
        return True
    
    return False

def transform_edu_interviews(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Transform education interview data into standard format
    
    Args:
        data: Dictionary containing persona type and respondents
        
    Returns:
        List of interview data items in standard format
    """
    transformed_data = []
    
    for idx, respondent in enumerate(data.get('respondents', [])):
        user_id = f"{data.get('persona', 'B2C')}_{idx+1:03d}"
        
        for answer in respondent.get('answers', []):
            transformed_data.append({
                'user_id': user_id,
                'question': answer.get('question', ''),
                'answer': answer.get('answer', ''),
                'text': f"From {respondent.get('name', 'Anonymous')}"
            })
    
    return transformed_data
