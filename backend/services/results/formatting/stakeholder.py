from __future__ import annotations
from typing import Dict, List


def derive_detected_stakeholders_from_personas(
    personas: List[Dict[str, any]],
) -> List[Dict[str, any]]:
    """Derive UI-safe detected stakeholders from persona list (legacy parity)."""
    out: List[Dict[str, any]] = []
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


from typing import Any, Dict, List


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
