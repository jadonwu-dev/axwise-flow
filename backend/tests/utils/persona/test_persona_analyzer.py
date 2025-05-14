import json
import pytest
import os
from pathlib import Path
from backend.utils.persona.persona_analyzer import PersonaAnalyzer, create_personas_from_interviews

# Path to sample data
SAMPLE_DATA_PATH = Path(__file__).parent.parent.parent.parent / 'sample-data' / 'edu_interviews_syntethic.json'

@pytest.mark.skipif(not SAMPLE_DATA_PATH.exists(), reason="Sample data file not found")
def test_persona_analyzer_with_sample_data():
    """Test PersonaAnalyzer with sample interview data"""
    # Load sample data
    with open(SAMPLE_DATA_PATH, 'r') as f:
        sample_data = json.load(f)
    
    # Create analyzer instance
    analyzer = PersonaAnalyzer(sample_data)
    
    # Test core attributes extraction
    core_attrs = analyzer.extract_core_attributes()
    assert isinstance(core_attrs, dict)
    assert 'tools_used' in core_attrs
    assert 'planning_patterns' in core_attrs
    assert 'key_responsibilities' in core_attrs
    
    # Test pain points analysis
    pain_points = analyzer.analyze_pain_points()
    assert isinstance(pain_points, dict)
    assert 'key_challenges' in pain_points
    assert 'automation_needs' in pain_points
    assert 'challenge_sentiment' in pain_points
    
    # Test collaboration patterns
    collab = analyzer.analyze_collaboration_patterns()
    assert isinstance(collab, dict)
    assert 'collaboration_patterns' in collab
    assert 'representative_quotes' in collab
    
    # Test complete persona generation
    persona = analyzer.generate_persona_profile()
    assert isinstance(persona, dict)
    assert persona['persona_type'] == sample_data['persona']
    assert 'core_attributes' in persona
    assert 'pain_points' in persona
    assert 'collaboration_patterns' in persona
    assert 'supporting_quotes' in persona
    assert 'metadata' in persona

@pytest.mark.skipif(not SAMPLE_DATA_PATH.exists(), reason="Sample data file not found")
def test_create_personas_from_interviews():
    """Test creating multiple personas from interview file"""
    personas = create_personas_from_interviews(str(SAMPLE_DATA_PATH))
    assert isinstance(personas, list)
    assert len(personas) > 0
    
    for persona in personas:
        assert isinstance(persona, dict)
        assert 'persona_type' in persona
        assert 'core_attributes' in persona
        assert 'pain_points' in persona
        assert 'collaboration_patterns' in persona
        assert 'supporting_quotes' in persona
        assert 'metadata' in persona

@pytest.mark.skipif(not SAMPLE_DATA_PATH.exists(), reason="Sample data file not found")
def test_extract_representative_quotes():
    """Test quote extraction and categorization"""
    with open(SAMPLE_DATA_PATH, 'r') as f:
        sample_data = json.load(f)
    
    analyzer = PersonaAnalyzer(sample_data)
    quotes = analyzer._extract_representative_quotes()
    
    assert isinstance(quotes, dict)
    # Check if we have categorized quotes
    expected_categories = {'positive_experiences', 'negative_experiences', 
                         'challenges', 'collaboration', 'automation'}
    assert any(category in quotes for category in expected_categories)
    
    # Verify quote structure
    for category, quote_list in quotes.items():
        assert isinstance(quote_list, list)
        assert len(quote_list) <= 3  # Should be limited to top 3 quotes
        
        if quote_list and isinstance(quote_list[0], dict):
            # Check structured quote format
            sample_quote = quote_list[0]
            assert 'quote' in sample_quote
            assert 'context' in sample_quote
            if 'experiences' in category:
                assert 'sentiment' in sample_quote

@pytest.mark.skipif(not SAMPLE_DATA_PATH.exists(), reason="Sample data file not found")
def test_extract_common_patterns():
    """Test pattern extraction from responses"""
    with open(SAMPLE_DATA_PATH, 'r') as f:
        sample_data = json.load(f)
    
    analyzer = PersonaAnalyzer(sample_data)
    
    # Test with challenge responses
    challenge_responses = []
    for respondent in sample_data['respondents']:
        for answer in respondent['answers']:
            if 'challenge' in answer['question'].lower():
                challenge_responses.append(answer['answer'])
    
    patterns = analyzer._extract_common_patterns(challenge_responses)
    
    assert isinstance(patterns, list)
    for pattern in patterns:
        assert isinstance(pattern, dict)
        assert 'pattern' in pattern
        assert 'frequency' in pattern
        assert 'examples' in pattern
        assert isinstance(pattern['frequency'], int)
        assert isinstance(pattern['examples'], list)
