from __future__ import annotations

from typing import Dict, List


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
            if sentiment_score > 0.2 and statement not in sentiment_statements["positive"]:
                sentiment_statements["positive"].append(statement)
            elif sentiment_score < -0.2 and statement not in sentiment_statements["negative"]:
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
            if any(w in impact for w in [
                "positive", "improves", "enhances", "increases", "strengthens"
            ]):
                sentiment_score = 0.5
            elif any(w in impact for w in [
                "negative", "frustration", "slows", "diminishes", "friction"
            ]):
                sentiment_score = -0.5
        statements = pattern.get("evidence", [])
        for statement in statements or []:
            if not isinstance(statement, str) or len(statement.strip()) < 20:
                continue
            if sentiment_score > 0.2 and statement not in sentiment_statements["positive"]:
                sentiment_statements["positive"].append(statement)
            elif sentiment_score < -0.2 and statement not in sentiment_statements["negative"]:
                sentiment_statements["negative"].append(statement)
            elif statement not in sentiment_statements["neutral"]:
                sentiment_statements["neutral"].append(statement)

    # Cap
    sentiment_statements["positive"] = sentiment_statements["positive"][:20]
    sentiment_statements["neutral"] = sentiment_statements["neutral"][:20]
    sentiment_statements["negative"] = sentiment_statements["negative"][:20]
    return sentiment_statements

