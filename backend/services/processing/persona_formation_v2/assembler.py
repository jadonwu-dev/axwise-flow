"""
Persona assembler for Persona Formation V2.

Composes extractor outputs and delegates to the legacy PersonaBuilder to
retain exact response shape/back-compat while enabling modular internals.
"""
from typing import Dict, Any

from backend.services.processing.persona_builder import PersonaBuilder, persona_to_dict


class PersonaAssembler:
    def __init__(self):
        self._builder = PersonaBuilder()

    def assemble(self, extracted: Dict[str, Dict[str, Any]], base_attributes: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge extracted fields into a full attribute dict and build persona using
        PersonaBuilder for maximal backward compatibility.
        """
        attrs = dict(base_attributes or {})
        for k, v in (extracted or {}).items():
            attrs[k] = v
        persona = self._builder.build_persona_from_attributes(attrs, role="Participant")
        return persona_to_dict(persona)

