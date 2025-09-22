"""
Persona Formation V2 modular package.

This package provides a thin, modular façade over the existing
PersonaFormationService pipeline, enabling:
- Facade orchestration behind a feature flag (PERSONA_FORMATION_V2)
- Pluggable extractors (Demographics, Goals, Challenges, KeyQuotes)
- Assembler that composes extractor outputs and delegates to PersonaBuilder
- Validation utilities ensuring the Golden Schema constraints

Backwards compatibility is preserved: outputs retain the current shape.
"""
from .facade import PersonaFormationFacade
from .extractors import (
    DemographicsExtractor,
    GoalsExtractor,
    ChallengesExtractor,
    KeyQuotesExtractor,
)
from .assembler import PersonaAssembler
from .validation import PersonaValidation

__all__ = [
    "PersonaFormationFacade",
    "DemographicsExtractor",
    "GoalsExtractor",
    "ChallengesExtractor",
    "KeyQuotesExtractor",
    "PersonaAssembler",
    "PersonaValidation",
]

