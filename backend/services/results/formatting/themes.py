from __future__ import annotations

from typing import Any, Dict, List


def _is_number(x: Any) -> bool:
    try:
        float(x)
        return True
    except Exception:
        return False


def adjust_theme_frequencies_for_prevalence(themes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Fix LLM-normalized theme frequencies (that sum to ~1.0) to prevalence-style [0..1].

    Detection heuristic:
    - If all frequencies are numeric in [0,1]
    - AND sum(f) is ~1.0 (within 5%)
    - AND max(f) <= 0.2 (typical when LLM spreads weights across ~5-10 themes)
    Then rescale by dividing each frequency by max(f), clamped to 1.0, rounded to 2 decimals.

    Example: [0.15, 0.15, 0.10, 0.10, 0.05] -> [1.0, 1.0, 0.67, 0.67, 0.33]
    """
    if not isinstance(themes, list) or not themes:
        return themes

    freqs: List[float] = []
    for t in themes:
        if not isinstance(t, dict):
            return themes
        f = t.get("frequency")
        if not _is_number(f):
            return themes
        f = float(f)
        if not (0.0 <= f <= 1.0):
            return themes
        freqs.append(f)

    if not freqs:
        return themes

    sum_f = sum(freqs)
    max_f = max(freqs)

    # Heuristic trigger: looks like normalized weights instead of prevalence
    if (0.95 <= sum_f <= 1.05) and (max_f <= 0.2):
        scale = 1.0 / max_f if max_f > 0 else 1.0
        adjusted: List[Dict[str, Any]] = []
        for t, f in zip(themes, freqs):
            new_f = min(1.0, f * scale)
            # Round to two decimals to match prior outputs like 1.0, 0.75, 0.67, 0.33
            new_f = round(new_f + 1e-8, 2)
            nt = dict(t)
            nt["frequency"] = new_f
            adjusted.append(nt)
        return adjusted

    return themes

