from __future__ import annotations

from typing import Any, Dict


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

