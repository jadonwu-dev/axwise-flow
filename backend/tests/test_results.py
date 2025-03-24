"""
Tests for the results service with database personas.
"""

import pytest
import json
from datetime import datetime

from backend.models import AnalysisResult, Persona
from backend.services.results_service import ResultsService

class TestPersonaRetrieval:
    """Tests for persona retrieval from database."""

    def test_get_results_with_personas(
        self, client, auth_headers, uploaded_interview_data, db_session
    ):
        """Test getting results with personas from database."""
        # Create analysis result with test data
        analysis_result = AnalysisResult(
            data_id=uploaded_interview_data.data_id,
            llm_provider="test-provider",
            llm_model="test-model",
            results={
                "themes": ["Theme 1"],
                "patterns": ["Pattern 1"],
                "sentiment": ["positive"],
                "insights": ["Insight 1"]
            },
            status="completed"
        )
        db_session.add(analysis_result)
        db_session.commit()
        
        # Create test personas in database
        personas = [
            Persona(
                result_id=analysis_result.result_id,
                name="Design Lead",
                demographics={"age": 35, "role": "Lead Designer"},
                goals=["Improve workflow efficiency"],
                pain_points=["Tool fragmentation"],
                behaviors={"meetings": "daily"},
                quotes=["We need better collaboration tools"],
                confidence_score=0.85
            ),
            Persona(
                result_id=analysis_result.result_id,
                name="UX Researcher",
                demographics={"age": 28, "role": "UX Researcher"},
                goals=["Better user insights"],
                pain_points=["Limited research time"],
                behaviors={"research": "weekly"},
                quotes=["Data is our most valuable asset"],
                confidence_score=0.92
            )
        ]
        
        for persona in personas:
            db_session.add(persona)
        db_session.commit()
        
        # Test the endpoint
        response = client.get(
            f"/api/results/{analysis_result.result_id}",
            headers=auth_headers
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        # Check for personas in the response
        assert "personas" in data["results"]
        response_personas = data["results"]["personas"]
        
        # Verify personas count
        assert len(response_personas) == 2
        
        # Verify persona data
        persona_names = [p["name"] for p in response_personas]
        assert "Design Lead" in persona_names
        assert "UX Researcher" in persona_names
        
        # Verify persona details
        for p in response_personas:
            if p["name"] == "Design Lead":
                assert p["confidence"] == 0.85
                assert p["demographics"]["role"] == "Lead Designer"
                assert "Improve workflow efficiency" in p["goals"]
                assert "Tool fragmentation" in p["pain_points"]
            elif p["name"] == "UX Researcher":
                assert p["confidence"] == 0.92
                assert p["demographics"]["role"] == "UX Researcher"
                assert "Better user insights" in p["goals"]
                assert "Limited research time" in p["pain_points"]
    
    def test_get_results_with_no_personas(
        self, client, auth_headers, uploaded_interview_data, db_session
    ):
        """Test getting results with no personas in database."""
        # Create analysis result with test data
        analysis_result = AnalysisResult(
            data_id=uploaded_interview_data.data_id,
            llm_provider="test-provider",
            llm_model="test-model",
            results={
                "themes": ["Theme 1"],
                "patterns": ["Pattern 1"],
                "sentiment": ["positive"],
                "insights": ["Insight 1"]
            },
            status="completed"
        )
        db_session.add(analysis_result)
        db_session.commit()
        
        # Test the endpoint with no personas
        response = client.get(
            f"/api/results/{analysis_result.result_id}",
            headers=auth_headers
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        # Check for personas in the response
        assert "personas" in data["results"]
        assert len(data["results"]["personas"]) == 0 