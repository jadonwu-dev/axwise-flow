import os

import pytest

from backend.infrastructure.container import Container
from backend.services.processing.persona_formation_v2.facade import (
    PersonaFormationFacade,
)
from backend.services.processing.persona_formation_service import (
    PersonaFormationService,
)
from backend.services.stakeholder_analysis_v2.facade import StakeholderAnalysisFacade
from backend.services.stakeholder_analysis_service import StakeholderAnalysisService


@pytest.mark.parametrize(
    "flag_value, expected_type",
    [
        ("1", PersonaFormationFacade),
        ("true", PersonaFormationFacade),
        ("on", PersonaFormationFacade),
        ("0", PersonaFormationService),
        ("false", PersonaFormationService),
        (None, PersonaFormationService),
    ],
)
def test_persona_service_flag_resolution(monkeypatch, flag_value, expected_type):
    if flag_value is None:
        monkeypatch.delenv("PERSONA_FORMATION_V2", raising=False)
    else:
        monkeypatch.setenv("PERSONA_FORMATION_V2", flag_value)
    # Provide dummy Gemini API key for LLM service construction during tests
    monkeypatch.setenv("GEMINI_API_KEY", "test")

    c = Container()
    svc = c.get_persona_formation_service()
    assert isinstance(svc, expected_type)


@pytest.mark.parametrize(
    "flag_value, expected_type",
    [
        ("1", StakeholderAnalysisFacade),
        ("true", StakeholderAnalysisFacade),
        ("on", StakeholderAnalysisFacade),
        ("0", StakeholderAnalysisService),
        ("false", StakeholderAnalysisService),
        (None, StakeholderAnalysisService),
    ],
)
def test_stakeholder_analysis_flag_resolution(monkeypatch, flag_value, expected_type):
    if flag_value is None:
        monkeypatch.delenv("STAKEHOLDER_ANALYSIS_V2", raising=False)
    else:
        monkeypatch.setenv("STAKEHOLDER_ANALYSIS_V2", flag_value)
    # Provide dummy Gemini API key for LLM service construction during tests
    monkeypatch.setenv("GEMINI_API_KEY", "test")

    c = Container()
    svc = c.get_stakeholder_analysis_service()
    assert isinstance(svc, expected_type)
