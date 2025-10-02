from __future__ import annotations

from typing import Any, Dict, List


def compute_influence_metrics_for_persona(
    persona_dict: Dict[str, Any],
) -> Dict[str, float]:
    """Compute simple influence metrics heuristically from persona text fields.

    Pure function; no side effects, no logging. Keeps behavior identical to the
    inline helper previously used in ResultsService.get_analysis_result.
    """
    try:
        name = (persona_dict.get("name") or "").lower()
        description = (persona_dict.get("description") or "").lower()
        archetype = (persona_dict.get("archetype") or "").lower()
        demo_val = ""
        demo = persona_dict.get("demographics")
        if isinstance(demo, dict):
            demo_val = (demo.get("value") or "").lower()
        combined = f"{name} {description} {archetype} {demo_val}"

        # Defaults
        decision_power = 0.5
        technical_influence = 0.5
        budget_influence = 0.5

        # Keyword heuristics
        decision_markers = [
            "manager",
            "director",
            "ceo",
            "owner",
            "executive",
            "leader",
            "decision maker",
            "authority",
            "supervisor",
            "head of",
            "chief",
        ]
        tech_markers = [
            "architect",
            "engineer",
            "technical",
            "it",
            "developer",
            "designer",
            "specialist",
            "technician",
        ]
        budget_markers = [
            "budget",
            "purchasing",
            "procurement",
            "finance",
            "cfo",
            "cost",
            "spending",
        ]
        influencer_markers = ["influencer", "advisor", "consultant"]

        if any(k in combined for k in decision_markers):
            decision_power = max(decision_power, 0.85)
            budget_influence = max(budget_influence, 0.8)
        if any(k in combined for k in tech_markers):
            technical_influence = max(technical_influence, 0.85)
            decision_power = max(decision_power, 0.6)
        if any(k in combined for k in budget_markers):
            budget_influence = max(budget_influence, 0.85)
            decision_power = max(decision_power, 0.7)
        if any(k in combined for k in influencer_markers):
            decision_power = max(decision_power, 0.6)

        def clamp(x: float) -> float:
            try:
                return max(0.0, min(1.0, float(x)))
            except Exception:
                return 0.5

        return {
            "decision_power": clamp(decision_power),
            "technical_influence": clamp(technical_influence),
            "budget_influence": clamp(budget_influence),
        }
    except Exception:
        return {
            "decision_power": 0.5,
            "technical_influence": 0.5,
            "budget_influence": 0.5,
        }


def derive_detected_stakeholders_from_personas(
    personas: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Derive UI-safe detected stakeholders from persona list.

    Mirrors legacy helper behavior.
    """
    out: List[Dict[str, Any]] = []
    import re

    def slugify(v: str) -> str:
        v = (v or "").lower()
        v = re.sub(r"[^a-z0-9]+", "_", v).strip("_")
        return v[:64] if v else "unknown"

    def to_allowed_type(v: str) -> str:
        v = (v or "").lower()
        if "decision" in v:
            return "decision_maker"
        if "influenc" in v:
            return "influencer"
        if "second" in v or "support" in v:
            return "secondary_user"
        return "primary_customer"

    for i, p in enumerate(personas or []):
        if not isinstance(p, dict):
            continue
        name = p.get("name") or f"Persona_{i+1}"
        mapping = p.get("stakeholder_mapping", {}) or {}
        intel = p.get("stakeholder_intelligence", {}) or {}
        cat = mapping.get("stakeholder_category")
        stype = intel.get("stakeholder_type") or p.get("archetype")

        sid_source = cat or stype or name
        stakeholder_id = slugify(sid_source)
        stakeholder_type = to_allowed_type(stype or cat or "")

        demo_profile = {}
        demo = p.get("demographics")
        if isinstance(demo, dict):
            val = demo.get("value") if isinstance(demo.get("value"), str) else None
            if val:
                demo_profile["summary"] = val[:200]

        out.append(
            {
                "stakeholder_id": stakeholder_id,
                "stakeholder_type": stakeholder_type,
                "confidence_score": float(p.get("overall_confidence", 0.7)),
                "demographic_profile": demo_profile,
                "individual_insights": {},
                "influence_metrics": intel.get("influence_metrics", {}),
            }
        )
    return out


def assemble_flattened_results(
    results_dict: Dict[str, Any],
    personas: Any,
    *,
    sentiment_overview_default: Dict[str, float],
) -> Dict[str, Any]:
    """Return flattened analysis fields with defaults, matching legacy behavior.

    Does not include metadata (status, ids, provider/model) or stakeholder_intelligence.
    """
    return {
        "themes": results_dict.get("themes", []),
        "enhanced_themes": results_dict.get("enhanced_themes", []),
        "patterns": results_dict.get("patterns", []),
        "sentiment": results_dict.get("sentiment", []),
        "sentimentOverview": results_dict.get(
            "sentimentOverview", sentiment_overview_default
        ),
        "sentimentStatements": results_dict.get(
            "sentimentStatements", {"positive": [], "neutral": [], "negative": []}
        ),
        "insights": results_dict.get("insights", []),
        "personas": personas,
    }


def should_compute_influence_metrics(si: Any) -> bool:
    """Return True if influence metrics need recomputation based on legacy rules."""
    im = si.get("influence_metrics") if isinstance(si, dict) else None
    if not isinstance(im, dict):
        return True
    try:
        dp = float(im.get("decision_power", 0.5))
        ti = float(im.get("technical_influence", 0.5))
        bi = float(im.get("budget_influence", 0.5))
        all_default = (
            abs(dp - 0.5) < 1e-6 and abs(ti - 0.5) < 1e-6 and abs(bi - 0.5) < 1e-6
        )
        return all_default or any(not isinstance(v, float) for v in (dp, ti, bi))
    except Exception:
        return True


def build_source_payload(results_dict: Dict[str, Any], data_id: Any) -> Dict[str, Any]:
    """Build source payload with transcript/original_text/source_text, else dataId."""
    source_payload: Dict[str, Any] = {}
    transcript = results_dict.get("transcript")
    if isinstance(transcript, list) and all(isinstance(x, dict) for x in transcript):
        source_payload["transcript"] = transcript
        return source_payload
    original_text = results_dict.get("original_text") or results_dict.get("source_text")
    if isinstance(original_text, str) and original_text.strip():
        source_payload["original_text"] = original_text
        return source_payload
    if data_id:
        source_payload["dataId"] = data_id
    return source_payload


def filter_researcher_evidence_for_ssot(
    personas_ssot: List[Dict[str, Any]],
    transcript: Any = None,
    original_text: Any = None,
) -> List[Dict[str, Any]]:
    """Remove Researcher/Interviewer quotes from persona evidence (pure).

    Mirrors legacy ResultsService._filter_researcher_evidence_for_ssot behavior.
    """
    if not personas_ssot:
        return personas_ssot
    try:
        from backend.services.validation.persona_evidence_validator import (
            PersonaEvidenceValidator,
        )
        import re  # local import to avoid global dependency when unused

        validator = PersonaEvidenceValidator()

        # Build normalized corpus of Researcher/Interviewer dialogues
        researcher_texts_norm: List[str] = []
        if isinstance(transcript, list):
            for seg in transcript:
                sp = (
                    (seg.get("speaker") or "").strip().lower()
                    if isinstance(seg, dict)
                    else ""
                )
                if sp in {"researcher", "interviewer", "moderator"}:
                    dialogue = (
                        (seg.get("dialogue") if isinstance(seg, dict) else None)
                        or (seg.get("text") if isinstance(seg, dict) else None)
                        or ""
                    )
                    researcher_texts_norm.append(validator._normalize(dialogue))
        elif isinstance(original_text, str) and original_text.strip():
            for line in original_text.splitlines():
                if re.match(
                    r"^(researcher|interviewer|moderator)\s*:\s*",
                    line.strip(),
                    re.IGNORECASE,
                ):
                    content = re.sub(
                        r"^(researcher|interviewer|moderator)\s*:\s*",
                        "",
                        line.strip(),
                        flags=re.IGNORECASE,
                    )
                    researcher_texts_norm.append(validator._normalize(content))

        def is_researcher_quote(q: str) -> bool:
            if not q:
                return False
            qn = validator._normalize(q)
            return any(qn in d for d in researcher_texts_norm)

        cleaned: List[Dict[str, Any]] = []
        fields = [
            "demographics",
            "goals_and_motivations",
            "challenges_and_frustrations",
            "key_quotes",
        ]
        for p in personas_ssot:
            p2 = dict(p) if isinstance(p, dict) else p
            for f in fields:
                trait = p2.get(f)
                if isinstance(trait, dict) and "evidence" in trait:
                    ev = trait.get("evidence") or []
                    new_ev = []
                    for item in ev:
                        quote = (
                            item.get("quote")
                            if isinstance(item, dict)
                            else (item if isinstance(item, str) else None)
                        )
                        if quote is None:
                            continue
                        if not is_researcher_quote(quote):
                            new_ev.append(item)
                    trait["evidence"] = new_ev
            cleaned.append(p2)
        return cleaned
    except Exception:
        # Be conservative and return original if anything fails
        return personas_ssot


def inject_age_ranges_from_source(
    personas_ssot: List[Dict[str, Any]],
    transcript: Any = None,
    original_text: Any = None,
) -> List[Dict[str, Any]]:
    """Inject demographics.age_range.value based on simple age parsing from source.

    Mirrors legacy ResultsService._inject_age_ranges_from_source behavior.
    """
    try:
        import re

        ages: List[int] = []

        def extract_ages_from_text(s: str) -> List[int]:
            if not isinstance(s, str):
                return []
            found: List[int] = []
            for m in re.finditer(
                r"\b(?:age\s*[:=]\s*(\d{2})|(\d{2})\s*years?\s*old|(\d{2})\s*yo|(?:\(|,)\s*(\d{2})\s*(?:\)|,))\b",
                s,
                re.IGNORECASE,
            ):
                age = next((int(g) for g in m.groups() if g), None)
                if age and 15 <= age <= 100:
                    found.append(age)
            return found

        if isinstance(transcript, list):
            for seg in transcript:
                text = (
                    (seg.get("dialogue") if isinstance(seg, dict) else None)
                    or (seg.get("text") if isinstance(seg, dict) else None)
                    or ""
                ).strip()
                if text:
                    ages.extend(extract_ages_from_text(text))
        if not ages and isinstance(original_text, str):
            ages.extend(extract_ages_from_text(original_text))

        ages = [a for a in ages if 15 <= a <= 100]
        if not ages:
            return personas_ssot

        ages.sort()
        min_age, max_age = ages[0], ages[-1]
        if len(ages) == 1:
            center = ages[0]
            label = f"{max(center-2,15)}–{min(center+2,100)}"
        else:
            if max_age - min_age <= 4:
                label = f"{min_age}–{max_age}"
            else:
                mid = ages[len(ages) // 2]
                low = max(mid - 2, 15)
                high = min(mid + 2, 100)
                label = f"{low}–{high}"

        for p in personas_ssot:
            if not isinstance(p, dict):
                continue
            demo = p.get("demographics")
            if not isinstance(demo, dict):
                continue
            age_field = demo.get("age_range") or {}
            current_val = (
                age_field.get("value") if isinstance(age_field, dict) else None
            ) or ""
            if str(current_val).strip().lower() in {
                "",
                "n/a",
                "undisclosed",
                "not specified",
                "unknown",
            }:
                if not isinstance(age_field, dict):
                    age_field = {}
                age_field["value"] = label
                demo["age_range"] = age_field
        return personas_ssot
    except Exception:
        return personas_ssot


from typing import List
from sqlalchemy.orm import Session


def extract_sentiment_statements_from_data(themes, patterns) -> Dict[str, List[str]]:
    """Pure extraction of sentiment statements from themes and patterns.

    Mirrors legacy thresholds and uniqueness; caps lists at 20.
    """
    sentiment_statements = {"positive": [], "neutral": [], "negative": []}

    # Themes
    for theme in themes or []:
        if not isinstance(theme, dict) or (
            not theme.get("statements") and "sentiment" not in theme
        ):
            continue
        sentiment_score = theme.get("sentiment", 0)
        statements = theme.get("statements", []) or theme.get("examples", [])
        for statement in statements or []:
            if not isinstance(statement, str) or len(statement.strip()) < 20:
                continue
            if (
                sentiment_score > 0.2
                and statement not in sentiment_statements["positive"]
            ):
                sentiment_statements["positive"].append(statement)
            elif (
                sentiment_score < -0.2
                and statement not in sentiment_statements["negative"]
            ):
                sentiment_statements["negative"].append(statement)
            elif statement not in sentiment_statements["neutral"]:
                sentiment_statements["neutral"].append(statement)

    # Patterns
    for pattern in patterns or []:
        if not isinstance(pattern, dict) or not pattern.get("evidence"):
            continue
        sentiment_score = pattern.get("sentiment", 0)
        if sentiment_score == 0 and isinstance(pattern.get("impact"), str):
            impact = pattern.get("impact", "").lower()
            if any(
                w in impact
                for w in [
                    "positive",
                    "improves",
                    "enhances",
                    "increases",
                    "strengthens",
                ]
            ):
                sentiment_score = 0.5
            elif any(
                w in impact
                for w in ["negative", "frustration", "slows", "diminishes", "friction"]
            ):
                sentiment_score = -0.5
        statements = pattern.get("evidence", [])
        for statement in statements or []:
            if not isinstance(statement, str) or len(statement.strip()) < 20:
                continue
            if (
                sentiment_score > 0.2
                and statement not in sentiment_statements["positive"]
            ):
                sentiment_statements["positive"].append(statement)
            elif (
                sentiment_score < -0.2
                and statement not in sentiment_statements["negative"]
            ):
                sentiment_statements["negative"].append(statement)
            elif statement not in sentiment_statements["neutral"]:
                sentiment_statements["neutral"].append(statement)

    # Cap
    sentiment_statements["positive"] = sentiment_statements["positive"][:20]
    sentiment_statements["neutral"] = sentiment_statements["neutral"][:20]
    sentiment_statements["negative"] = sentiment_statements["negative"][:20]
    return sentiment_statements


def create_ui_safe_stakeholder_intelligence(stakeholder_intelligence):
    """Pure variant of UI-safe stakeholder intelligence assembly."""
    if not stakeholder_intelligence:
        return None
    try:
        detected_stakeholders: List[Dict[str, Any]] = []
        if isinstance(stakeholder_intelligence, dict):
            if "detected_stakeholders" in stakeholder_intelligence:
                detected_stakeholders = stakeholder_intelligence[
                    "detected_stakeholders"
                ]
            elif "stakeholders" in stakeholder_intelligence:
                stakeholders_data = stakeholder_intelligence["stakeholders"]
                if isinstance(stakeholders_data, list):
                    detected_stakeholders = stakeholders_data
                elif isinstance(stakeholders_data, dict):
                    for stakeholder_id, stakeholder_data in stakeholders_data.items():
                        if isinstance(stakeholder_data, dict):
                            detected_stakeholders.append(
                                {
                                    "stakeholder_id": stakeholder_id,
                                    "stakeholder_type": stakeholder_data.get(
                                        "stakeholder_type", "primary_customer"
                                    ),
                                    "confidence_score": stakeholder_data.get(
                                        "confidence_score", 0.85
                                    ),
                                    "individual_insights": stakeholder_data.get(
                                        "individual_insights", {}
                                    ),
                                    "influence_metrics": stakeholder_data.get(
                                        "influence_metrics", {}
                                    ),
                                    "full_persona_data": stakeholder_data.get(
                                        "full_persona_data"
                                    ),
                                }
                            )
            ui = {
                "detected_stakeholders": detected_stakeholders,
                "total_stakeholders": len(detected_stakeholders),
                "processing_metadata": {
                    "analysis_type": "multi_stakeholder",
                    "confidence_threshold": 0.7,
                    "ui_safe": True,
                },
            }
            if "cross_stakeholder_patterns" in stakeholder_intelligence and isinstance(
                stakeholder_intelligence["cross_stakeholder_patterns"], dict
            ):
                p = stakeholder_intelligence["cross_stakeholder_patterns"]
                ui["cross_stakeholder_patterns"] = {
                    "consensus_areas": p.get("consensus_areas", []),
                    "conflict_zones": p.get("conflict_zones", []),
                    "influence_networks": p.get("influence_networks", []),
                }
            if "multi_stakeholder_summary" in stakeholder_intelligence and isinstance(
                stakeholder_intelligence["multi_stakeholder_summary"], dict
            ):
                s = stakeholder_intelligence["multi_stakeholder_summary"]
                ui["multi_stakeholder_summary"] = {
                    "key_insights": s.get("key_insights", []),
                    "business_implications": s.get("business_implications", []),
                    "recommended_actions": s.get("recommended_actions", []),
                }
            return ui
        # Fallback for non-dict
        return {
            "detected_stakeholders": [],
            "total_stakeholders": 0,
            "processing_metadata": {
                "analysis_type": "single_stakeholder",
                "ui_safe": True,
                "fallback_reason": f"Unexpected stakeholder_intelligence type: {type(stakeholder_intelligence)}",
            },
        }
    except Exception as e:
        return {
            "detected_stakeholders": [],
            "total_stakeholders": 0,
            "processing_metadata": {
                "analysis_type": "error",
                "ui_safe": True,
                "error": str(e),
            },
        }


def get_filename_for_data_id(db: Session, data_id: Any) -> str:
    """Fetch InterviewData filename by id; returns "Unknown" if not found."""
    if not data_id:
        return "Unknown"
    try:
        from backend.models import InterviewData

        row = db.query(InterviewData).filter(InterviewData.id == data_id).first()
        if row:
            return row.filename or "Unknown"
        return "Unknown"
    except Exception:
        return "Unknown"
