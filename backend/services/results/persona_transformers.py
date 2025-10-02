from __future__ import annotations

import json
import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def convert_enhanced_persona_to_frontend_format(
    persona_dict: Dict[str, Any]
) -> Dict[str, Any]:
    """Convert EnhancedPersona-like dict to frontend-friendly shape.

    Pure function; mirrors ResultsService._convert_enhanced_persona_to_frontend_format.
    """
    # List of trait fields that need conversion
    trait_fields = [
        "demographics",
        "goals_and_motivations",
        "challenges_and_frustrations",
        "key_quotes",
        "skills_and_expertise",
        "workflow_and_environment",
        "pain_points",
        "technology_and_tools",
        "collaboration_style",
        "needs_and_desires",
        "attitude_towards_research",
        "attitude_towards_ai",
        "role_context",
        "key_responsibilities",
        "tools_used",
        "analysis_approach",
    ]

    def _coerce_evidence(evd: Any) -> List[str]:
        quotes: List[str] = []
        if not evd:
            return quotes
        if isinstance(evd, list):
            for item in evd:
                if isinstance(item, str):
                    quotes.append(item)
                elif isinstance(item, dict):
                    q = item.get("quote")
                    if isinstance(q, str) and q:
                        quotes.append(q)
        elif isinstance(evd, dict):
            q = evd.get("quote")
            if isinstance(q, str) and q:
                quotes.append(q)
        elif isinstance(evd, str):
            quotes.append(evd)
        return quotes

    # Convert trait fields from EnhancedPersonaTrait to simple dict
    for field in trait_fields:
        if field in persona_dict and persona_dict[field] is not None:
            trait = persona_dict[field]
            if isinstance(trait, dict):
                persona_dict[field] = {
                    "value": trait.get("value", ""),
                    "confidence": trait.get("confidence", 0.7),
                    "evidence": _coerce_evidence(trait.get("evidence", [])),
                }
            else:
                persona_dict[field] = {"value": "", "confidence": 0.7, "evidence": []}
        else:
            persona_dict[field] = {"value": "", "confidence": 0.7, "evidence": []}

    # Restore key_quotes from preserved metadata if missing
    if "key_quotes" not in persona_dict or persona_dict["key_quotes"] is None:
        preserved_key_quotes = persona_dict.get("persona_metadata", {}).get(
            "preserved_key_quotes"
        )
        if preserved_key_quotes:
            persona_dict["key_quotes"] = preserved_key_quotes
            logger.info(
                f"Restored key_quotes from metadata for persona: {persona_dict.get('name', 'Unknown')}"
            )

    # Ensure stakeholder_intelligence.influence_metrics is dict with expected keys
    if (
        "stakeholder_intelligence" in persona_dict and persona_dict["stakeholder_intelligence"]
    ):
        si = persona_dict["stakeholder_intelligence"]
        if isinstance(si, dict) and si.get("influence_metrics"):
            im = si["influence_metrics"]
            if isinstance(im, dict):
                persona_dict["stakeholder_intelligence"]["influence_metrics"] = {
                    "decision_power": im.get("decision_power", 0.5),
                    "technical_influence": im.get("technical_influence", 0.5),
                    "budget_influence": im.get("budget_influence", 0.5),
                }

    return persona_dict


def map_json_to_persona_schema(p_data: Dict[str, Any]):
    """Map arbitrary persona JSON to backend.schemas.Persona (Golden Schema).

    Pure function; imports pydantic models locally to avoid import cycles.
    """
    # Local imports to avoid cycles
    from backend.schemas import Persona as PersonaSchema
    from backend.domain.models.persona_schema import (
        AttributedField,
        StructuredDemographics,
    )

    # Convert EnhancedPersona-like input to frontend-friendly dict
    p_data = convert_enhanced_persona_to_frontend_format(dict(p_data or {}))

    def create_trait(
        trait_data,
        default_value="Unknown",
        default_confidence=0.5,
        default_evidence=None,
    ):
        if default_evidence is None:
            default_evidence = []
        if not isinstance(trait_data, dict):
            return None
        trait_value = trait_data.get("value")
        trait_evidence = trait_data.get("evidence", [])
        # Quality checks
        if not trait_value or len(str(trait_value).strip()) < 10:
            return None
        generic_patterns = [
            "domain-specific",
            "professional",
            "technology and tools",
            "work environment",
            "collaboration approach",
            "analysis approach",
            "professional challenges",
            "professional responsibilities",
            "tools and methods",
            "professional role",
            "professional growth",
            "efficiency and professional",
            "values data-driven",
            "open to technological",
        ]
        trait_value_lower = str(trait_value).lower()
        if any(pattern in trait_value_lower for pattern in generic_patterns):
            logger.warning(
                "Detected generic placeholder pattern in trait value: %s...",
                str(trait_value)[:50],
            )
            return None
        if not trait_evidence or len(trait_evidence) == 0:
            return None
        good_evidence: List[str] = []
        for evidence in trait_evidence:
            if evidence and isinstance(evidence, str) and len(evidence.strip()) > 5:
                evidence_lower = evidence.lower()
                if not any(
                    pattern in evidence_lower
                    for pattern in [
                        "inferred from",
                        "based on statements",
                        "derived from",
                        "extracted from",
                        "representative statements",
                    ]
                ):
                    good_evidence.append(evidence.strip())
        if not good_evidence:
            logger.warning(
                "No substantial evidence found for trait: %s...",
                str(trait_value)[:50],
            )
            return None
        logger.info(
            "Creating quality trait with %d evidence items: %s...",
            len(good_evidence),
            str(trait_value)[:50],
        )
        return AttributedField(value=str(trait_value), evidence=good_evidence[:5])

    def create_demographics(demographics_data, default_confidence=0.7):
        if not isinstance(demographics_data, dict):
            return None
        confidence = demographics_data.get("confidence", default_confidence)
        demographics_value = demographics_data.get("value", "")
        demographics_evidence = demographics_data.get("evidence", [])
        if not demographics_evidence or len(demographics_evidence) < 2:
            logger.warning(
                "Insufficient evidence for demographics: %d items. Skipping.",
                len(demographics_evidence),
            )
            return None

        def extract_specific_value(evidence_list, keywords, default_value=None):
            for evidence in evidence_list:
                evidence_lower = evidence.lower()
                for keyword in keywords:
                    if keyword in evidence_lower:
                        parts = evidence.split(keyword.title())
                        if len(parts) > 1:
                            return evidence
            return default_value

        experience_keywords = ["years", "experience", "working", "been in"]
        industry_keywords = [
            "company",
            "industry",
            "sector",
            "business",
            "tech",
            "technology",
        ]
        location_keywords = ["based", "located", "city", "area", "live", "office"]
        role_keywords = ["role", "position", "job", "title", "manager", "developer", "analyst"]

        fields: Dict[str, AttributedField] = {}

        exp_evidence = [
            e for e in demographics_evidence if any(kw in e.lower() for kw in experience_keywords)
        ]
        if exp_evidence:
            fields["experience_level"] = AttributedField(
                value="Experience mentioned in context", evidence=exp_evidence[:2]
            )

        industry_evidence = [
            e for e in demographics_evidence if any(kw in e.lower() for kw in industry_keywords)
        ]
        if industry_evidence:
            fields["industry"] = AttributedField(
                value="Industry context from interview", evidence=industry_evidence[:2]
            )

        location_evidence = [
            e for e in demographics_evidence if any(kw in e.lower() for kw in location_keywords)
        ]
        if location_evidence:
            fields["location"] = AttributedField(
                value="Location mentioned in interview", evidence=location_evidence[:2]
            )

        role_evidence = [
            e for e in demographics_evidence if any(kw in e.lower() for kw in role_keywords)
        ]
        if role_evidence:
            fields["roles"] = AttributedField(
                value="Role context from interview", evidence=role_evidence[:2]
            )

        if demographics_value and len(demographics_value) > 20:
            fields["professional_context"] = AttributedField(
                value=demographics_value, evidence=demographics_evidence[:3]
            )

        if len(fields) < 2:
            logger.warning(
                "Insufficient demographic fields extracted: %d. Skipping.",
                len(fields),
            )
            return None

        structured_demo = StructuredDemographics(
            experience_level=fields.get("experience_level"),
            industry=fields.get("industry"),
            location=fields.get("location"),
            professional_context=fields.get("professional_context"),
            roles=fields.get("roles"),
            age_range=None,
            confidence=confidence,
        )
        logger.info(
            "Created StructuredDemographics with %d fields: %s",
            len(fields),
            list(fields.keys()),
        )
        return structured_demo

    # Extract basics
    name = p_data.get("name", "Unknown")
    description = p_data.get("description", name)
    archetype = p_data.get("archetype")
    try:
        confidence = float(p_data.get("confidence", p_data.get("overall_confidence", 0.7)))
    except (ValueError, TypeError):
        confidence = 0.7
    patterns = p_data.get("patterns", []) if isinstance(p_data.get("patterns"), list) else []
    evidence = (
        p_data.get("evidence", p_data.get("supporting_evidence_summary", []))
        if isinstance(p_data.get("evidence"), list) or isinstance(p_data.get("supporting_evidence_summary"), list)
        else []
    )
    metadata = p_data.get("metadata", p_data.get("persona_metadata", {}))
    if not isinstance(metadata, dict):
        metadata = {}

    # Trait inputs
    role_context_data = p_data.get("role_context")
    key_resp_data = p_data.get("key_responsibilities")
    tools_data = p_data.get("tools_used")
    collab_style_data = p_data.get("collaboration_style")
    analysis_approach_data = p_data.get("analysis_approach")
    pain_points_data = p_data.get("pain_points")

    demographics_data = p_data.get("demographics")
    goals_data = p_data.get("goals_and_motivations")
    skills_data = p_data.get("skills_and_expertise")
    workflow_data = p_data.get("workflow_and_environment")
    challenges_data = p_data.get("challenges_and_frustrations")
    needs_data = p_data.get("needs_and_desires")
    tech_tools_data = p_data.get("technology_and_tools")
    research_attitude_data = p_data.get("attitude_towards_research")
    ai_attitude_data = p_data.get("attitude_towards_ai")

    key_quotes_data = p_data.get("key_quotes")
    if isinstance(key_quotes_data, list) and len(key_quotes_data) > 0:
        key_quotes_data = {
            "value": "Representative quotes from the interview",
            "confidence": 0.9,
            "evidence": key_quotes_data,
        }
    elif not key_quotes_data:
        all_quotes: List[str] = []
        for field_name in [
            "demographics",
            "goals_and_motivations",
            "skills_and_expertise",
            "challenges_and_frustrations",
            "needs_and_desires",
        ]:
            field_data = p_data.get(field_name, {})
            if isinstance(field_data, dict) and "evidence" in field_data:
                all_quotes.extend(field_data.get("evidence", []))
        if all_quotes:
            key_quotes_data = {
                "value": "Quotes extracted from other fields",
                "confidence": 0.7,
                "evidence": all_quotes[:5],
            }
        else:
            key_quotes_data = {"value": "", "confidence": 0.5, "evidence": []}

    persona = PersonaSchema(
        name=name,
        archetype=archetype or "Professional",
        description=description,
        demographics=create_demographics(demographics_data, confidence),
        goals_and_motivations=create_trait(goals_data, "Professional growth and efficiency", 0.5),
        skills_and_expertise=create_trait(skills_data, "Domain-specific skills", 0.5),
        workflow_and_environment=create_trait(workflow_data, "Professional work environment", 0.5),
        challenges_and_frustrations=create_trait(challenges_data, "Common professional challenges", 0.5),
        needs_and_desires=create_trait(needs_data, "Efficiency and professional growth", 0.5),
        technology_and_tools=create_trait(tech_tools_data, "Technology and tools used", 0.5),
        attitude_towards_research=create_trait(
            research_attitude_data, "Values data-driven approaches", 0.5
        ),
        attitude_towards_ai=create_trait(
            ai_attitude_data, "Open to technological advancements", 0.5
        ),
        key_quotes=create_trait(
            key_quotes_data, "Representative quotes from the interview", 0.7, []
        ),
        role_context=create_trait(role_context_data, "Professional role", confidence, evidence),
        key_responsibilities=create_trait(
            key_resp_data, "Professional responsibilities", confidence, evidence
        ),
        tools_used=create_trait(tools_data, "Tools and methods used", confidence, evidence),
        collaboration_style=create_trait(
            collab_style_data, "Collaboration approach", confidence, evidence
        ),
        analysis_approach=create_trait(
            analysis_approach_data, "Analysis approach", confidence, evidence
        ),
        pain_points=create_trait(pain_points_data, "Professional challenges", confidence, evidence),
        patterns=patterns,
        confidence=confidence,
        evidence=evidence,
        metadata=metadata,
    )
    return persona


def serialize_field_safely(field_data: Any) -> Dict[str, Any]:
    """Serialize a possibly-Pydantic field to dict safely (pure)."""
    if field_data is None:
        return {}
    if hasattr(field_data, "model_dump"):
        try:
            return field_data.model_dump()
        except Exception as e:
            logger.warning("Failed to serialize Pydantic model using model_dump: %s", e)
    if isinstance(field_data, dict):
        return field_data
    if hasattr(field_data, "__dict__"):
        try:
            return field_data.__dict__
        except Exception as e:
            logger.warning("Failed to serialize object using __dict__: %s", e)
    logger.warning("Unsupported field type for serialization: %s", type(field_data))
    return {}


def store_persona_in_db(db, p_data: Dict[str, Any], result_id: int) -> None:
    """Persist persona dict into DB using JSON columns where applicable.

    Pure side-effect function parameterized by db session; safe logging and rollback
    on error. Mirrors ResultsService._store_persona_in_db.
    """
    from backend.models import Persona  # local import

    name = p_data.get("name", "Unknown Persona")
    description = p_data.get("description", "")
    archetype = p_data.get("archetype")

    try:
        existing = (
            db.query(Persona)
            .filter(
                Persona.result_id == result_id,
                Persona.name == name,
                Persona.description == description,
                Persona.archetype == archetype,
            )
            .first()
        )
        if existing:
            logger.debug(
                "Exact persona '%s' already in DB for result_id %s. Skipping save.",
                name,
                result_id,
            )
            return
    except Exception as query_err:
        logger.error("Error checking for existing persona '%s': %s", name, str(query_err), exc_info=True)

    try:
        persona_fields = {
            "result_id": result_id,
            "name": name,
            "description": description,
            "archetype": archetype,
            # JSON columns
            "role_context": json.dumps(p_data.get("role_context", {})),
            "key_responsibilities": json.dumps(p_data.get("key_responsibilities", {})),
            "tools_used": json.dumps(p_data.get("tools_used", {})),
            "collaboration_style": json.dumps(p_data.get("collaboration_style", {})),
            "analysis_approach": json.dumps(p_data.get("analysis_approach", {})),
            "pain_points": json.dumps(p_data.get("pain_points", {})),
            "demographics": json.dumps(serialize_field_safely(p_data.get("demographics", {}))),
            "goals_and_motivations": json.dumps(p_data.get("goals_and_motivations", {})),
            "skills_and_expertise": json.dumps(p_data.get("skills_and_expertise", {})),
            "workflow_and_environment": json.dumps(p_data.get("workflow_and_environment", {})),
            "challenges_and_frustrations": json.dumps(p_data.get("challenges_and_frustrations", {})),
            "needs_and_desires": json.dumps(p_data.get("needs_and_desires", {})),
            "technology_and_tools": json.dumps(p_data.get("technology_and_tools", {})),
            "attitude_towards_research": json.dumps(p_data.get("attitude_towards_research", {})),
            "attitude_towards_ai": json.dumps(p_data.get("attitude_towards_ai", {})),
            "key_quotes": json.dumps(p_data.get("key_quotes", {})),
            "patterns": json.dumps(p_data.get("patterns", [])),
            "evidence": json.dumps(p_data.get("evidence", p_data.get("supporting_evidence_summary", []))),
            "supporting_evidence_summary": json.dumps(p_data.get("supporting_evidence_summary", p_data.get("evidence", []))),
            "confidence": float(p_data.get("confidence", p_data.get("overall_confidence", 0.5))),
            "overall_confidence": float(p_data.get("overall_confidence", p_data.get("confidence", 0.5))),
            "persona_metadata": json.dumps(p_data.get("persona_metadata", p_data.get("metadata", {}))),
        }

        model_columns = {c.name for c in Persona.__table__.columns}
        valid_persona_fields = {k: v for k, v in persona_fields.items() if k in model_columns}

        logger.debug(
            "Attempting to save persona '%s' with fields: %s",
            name,
            list(valid_persona_fields.keys()),
        )

        new_persona = Persona(**valid_persona_fields)
        db.add(new_persona)
        db.commit()
        logger.info("Persona '%s' saved to database for result_id: %s", name, result_id)
    except Exception as e:
        db.rollback()
        logger.error(
            "Error saving persona '%s' to database: %s", name, str(e), exc_info=True
        )
        logger.debug("Persona data causing error: %s", p_data)

