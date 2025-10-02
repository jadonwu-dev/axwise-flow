from __future__ import annotations

from typing import Any, Dict


def compute_influence_metrics_for_persona(
    persona_dict: Dict[str, Any],
) -> Dict[str, float]:
    """Compute simple influence metrics heuristically from persona text fields.

    Pure function; mirrors the inline helper previously used in ResultsService.
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

