"""
Adapters for converting persona data between legacy/variant shapes and the SSoT
(Golden Schema) used in backend.domain.models.persona_schema.

Phase 0 goals:
- Be additive and non-breaking
- Coerce legacy evidence (strings/dicts) to EvidenceItem objects
- Preserve as much information as possible without over-interpreting

The SSoT target shape follows backend/schemas.Persona, which uses:
- StructuredDemographics (with AttributedField subfields + confidence)
- AttributedField for goals_and_motivations, challenges_and_frustrations, key_quotes

Notes:
- We work at dict level to avoid strict coupling; Pydantic models can consume these dicts.
- EvidenceItem shape: {quote, start_char?, end_char?, speaker?, document_id?}
- When mapping demographics from a single trait blob, we put it under professional_context.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from backend.domain.models.persona_schema import EvidenceItem

# Helper utilities


def _to_evidence_items(evd: Any) -> List[Dict[str, Any]]:
    """Normalize various evidence representations to List[EvidenceItem-like dicts].

    Accepts:
    - None -> []
    - str -> [{quote: str}]
    - dict with 'quote' or 'text' -> [normalized]
    - list of str/dict -> each normalized
    """
    if not evd:
        return []
    if isinstance(evd, str):
        return [{"quote": evd}]
    if isinstance(evd, dict):
        if "quote" in evd:
            return [evd]
        if "text" in evd:
            return [{"quote": evd.get("text", "")}]
        return []
    if isinstance(evd, list):
        out: List[Dict[str, Any]] = []
        for item in evd:
            if isinstance(item, str):
                out.append({"quote": item})
            elif isinstance(item, dict):
                if "quote" in item:
                    out.append(item)
                elif "text" in item:
                    out.append({"quote": item.get("text", "")})
        return out
    return []


def _to_attributed_field_from_trait(trait: Any) -> Optional[Dict[str, Any]]:
    """Convert a legacy trait object (DirectPersonaTrait-like) to AttributedField dict.

    Expected inputs:
    - dict with keys {value, evidence?, confidence?}
    - str value
    Returns None if no usable value.
    """
    if trait is None:
        return None
    if isinstance(trait, str):
        value = trait.strip()
        if not value:
            return None
        return {"value": value, "evidence": []}
    if isinstance(trait, dict):
        value = trait.get("value")
        if isinstance(value, (dict, list)):
            # Avoid passing complex values to AttributedField; coerce to string
            value = str(value)
        value = (value or trait.get("text") or "").strip()
        if not value:
            return None
        evidence = _to_evidence_items(trait.get("evidence"))
        return {"value": value, "evidence": evidence}
    return None


def _combine_demographics_fields(demo: Dict[str, Any]) -> str:
    """Create a simple string summary from StructuredDemographics-like dict.

    Useful for from_ssot_to_frontend demographic flattening.
    """
    labels = [
        ("experience_level", "Experience"),
        ("industry", "Industry"),
        ("location", "Location"),
        ("professional_context", "Context"),
        ("roles", "Roles"),
        ("age_range", "Age"),
    ]
    parts: List[str] = []
    for key, label in labels:
        af = demo.get(key)
        if isinstance(af, dict):
            val = (af.get("value") or "").strip()
            if val:
                parts.append(f"{label}: {val}")
    return " | ".join(parts)


# Public adapters


def to_ssot_persona(data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert a legacy persona dictionary into SSoT shape.

    Attempts to handle variants:
    - ProductionPersona/DirectPersona: trait dicts with {value, confidence, evidence}
    - SimplifiedPersona: AttributedField for core traits; StructuredDemographics
    - backend/schemas.Persona: already SSoTish; ensure evidence items are normalized
    """
    if not isinstance(data, dict):
        return {}

    name = data.get("name") or data.get("persona_name") or "Unknown"
    description = data.get("description") or data.get("summary") or name
    archetype = data.get("archetype") or data.get("type") or None

    # Handle demographics
    demographics_ssot: Optional[Dict[str, Any]] = None

    demo = data.get("demographics")
    if isinstance(demo, dict):
        # Two possibilities:
        # 1) Already StructuredDemographics-like with subfields
        # 2) A single trait-like object {value, evidence, confidence}
        subfields = [
            "experience_level",
            "industry",
            "location",
            "professional_context",
            "roles",
            "age_range",
        ]
        if any(k in demo for k in subfields):
            # Normalize evidence inside subfields
            demographics_ssot = {
                key: (
                    {
                        "value": (demo.get(key) or {}).get("value"),
                        "evidence": _to_evidence_items(
                            (demo.get(key) or {}).get("evidence")
                        ),
                    }
                    if isinstance(demo.get(key), dict)
                    else None
                )
                for key in subfields
            }
            # confidence field (fallback 0.7)
            demographics_ssot["confidence"] = float(demo.get("confidence", 0.7))
        else:
            # Single trait -> place under professional_context
            demographics_ssot = {
                "experience_level": None,
                "industry": None,
                "location": None,
                "professional_context": _to_attributed_field_from_trait(demo),
                "roles": None,
                "age_range": None,
                "confidence": float(demo.get("confidence", 0.7)),
            }

    # Core traits
    goals_trait = (
        data.get("goals_and_motivations")
        or data.get("goals")
        or data.get("motivations")
    )
    challenges_trait = (
        data.get("challenges_and_frustrations")
        or data.get("challenges")
        or data.get("pain_points")
    )
    key_quotes_trait = data.get("key_quotes") or data.get("quotes")

    goals_ssot = _to_attributed_field_from_trait(goals_trait)
    challenges_ssot = _to_attributed_field_from_trait(challenges_trait)
    quotes_ssot = _to_attributed_field_from_trait(key_quotes_trait)

    persona_ssot: Dict[str, Any] = {
        "name": name,
        "description": description,
        "archetype": archetype,
        # Golden Schema core
        "demographics": demographics_ssot,
        "goals_and_motivations": goals_ssot,
        "challenges_and_frustrations": challenges_ssot,
        "key_quotes": quotes_ssot,
    }
    # Apply default speaker/document_id to evidence items when missing using EV2 scope meta
    ev2_meta = (data.get("_evidence_linking_v2") or {}).get("scope_meta") or {}
    default_speaker = (
        ev2_meta.get("speaker") or ev2_meta.get("speaker_role") or name or "Participant"
    )
    default_doc = ev2_meta.get("document_id") or "original_text"

    def _apply_defaults(items: Optional[List[Dict[str, Any]]]):
        if not items:
            return
        for it in items:
            if isinstance(it, dict):
                it.setdefault("speaker", default_speaker)
                it.setdefault("document_id", default_doc)

    # Core traits
    for k in [
        "goals_and_motivations",
        "challenges_and_frustrations",
        "key_quotes",
    ]:
        af = persona_ssot.get(k)
        if isinstance(af, dict):
            ev = af.get("evidence") or []
            _apply_defaults(ev)
            af["evidence"] = ev

    # Demographics subfields
    demo_dict = persona_ssot.get("demographics")
    if isinstance(demo_dict, dict):
        for sub in [
            "experience_level",
            "industry",
            "location",
            "professional_context",
            "roles",
            "age_range",
        ]:
            af = demo_dict.get(sub)
            if isinstance(af, dict):
                ev = af.get("evidence") or []
                _apply_defaults(ev)
                af["evidence"] = ev

    return persona_ssot


def from_ssot_to_frontend(data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert SSoT persona dict to legacy frontend-friendly shape.

    Produces DirectPersona-like shape with traits having value/confidence/evidence (strings).
    - demographics: flattened into a single string value
    - evidence items become list[str] of quotes
    - confidence defaults to 0.7 when not present
    """
    if not isinstance(data, dict):
        return {}

    def as_frontend_trait(
        af: Optional[Dict[str, Any]], default_conf: float = 0.7
    ) -> Optional[Dict[str, Any]]:
        if not isinstance(af, dict):
            return None
        value = (af.get("value") or "").strip()
        if not value:
            return None
        evd_items = af.get("evidence") or []
        quotes: List[str] = []
        for item in evd_items:
            if isinstance(item, dict) and item.get("quote"):
                quotes.append(item["quote"])
            elif isinstance(item, str):
                quotes.append(item)
        return {"value": value, "confidence": default_conf, "evidence": quotes}

    demographics = data.get("demographics")
    if isinstance(demographics, dict):
        demo_value = _combine_demographics_fields(demographics)
        demo_trait = {
            "value": demo_value,
            "confidence": float(demographics.get("confidence", 0.7)),
            "evidence": [],
        }
    else:
        demo_trait = None

    out: Dict[str, Any] = {
        "name": data.get("name", "Unknown"),
        "description": data.get("description") or data.get("name") or "",
        "archetype": data.get("archetype") or "",
        "demographics": demo_trait,
        "goals_and_motivations": as_frontend_trait(data.get("goals_and_motivations")),
        "challenges_and_frustrations": as_frontend_trait(
            data.get("challenges_and_frustrations")
        ),
        "key_quotes": as_frontend_trait(data.get("key_quotes")),
    }

    return out
