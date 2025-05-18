"""
Pattern categorizer module for categorizing and enhancing patterns.
"""
import re
import logging
from typing import Dict, List, Any, Optional, Union

logger = logging.getLogger(__name__)

class PatternCategorizer:
    """
    Categorizes and enhances patterns to make them more actionable.
    """

    def __init__(self):
        """
        Initialize the pattern categorizer.
        """
        # Pattern categories and their keywords
        self.pattern_categories = {
            "work_habits": ["workflow", "process", "approach", "method", "routine", "habit", "practice", "procedure"],
            "preferences": ["prefer", "like", "value", "enjoy", "appreciate", "favor", "choose", "opt for", "gravitate toward"],
            "challenges": ["challenge", "struggle", "difficult", "problem", "issue", "obstacle", "barrier", "hurdle", "pain point"],
            "needs": ["need", "require", "must have", "essential", "necessary", "important", "critical", "crucial", "vital"],
            "behaviors": ["always", "often", "tends to", "typically", "usually", "frequently", "regularly", "consistently", "habitually"],
            "attitudes": ["believes", "thinks", "feels", "views", "perceives", "considers", "regards", "attitude toward", "opinion on"],
            "goals": ["aims to", "wants to", "goal", "objective", "target", "aspiration", "ambition", "desire", "intention"]
        }

        # Actionability keywords
        self.actionability_keywords = {
            "high": ["always", "never", "must", "critical", "essential", "crucial", "significant", "major", "key", "primary"],
            "medium": ["often", "usually", "typically", "generally", "tends to", "prefers", "frequently", "regularly", "commonly"],
            "low": ["sometimes", "occasionally", "might", "could", "may", "possibly", "perhaps", "at times", "now and then"]
        }

    def categorize_patterns(self, patterns: List[str]) -> List[Dict[str, Any]]:
        """
        Categorize patterns by type and add actionability scores.

        Args:
            patterns: List of pattern strings

        Returns:
            List of categorized patterns with actionability scores
        """
        categorized_patterns = []

        for pattern in patterns:
            if not pattern or not isinstance(pattern, str):
                continue

            # Determine category
            category = self._determine_category(pattern)

            # Determine actionability
            actionability = self._determine_actionability(pattern)

            # Add to categorized patterns
            categorized_patterns.append({
                "pattern": pattern,
                "category": category,
                "actionability": actionability
            })

        return categorized_patterns

    def format_patterns_for_display(self, categorized_patterns: List[Dict[str, Any]]) -> List[str]:
        """
        Format categorized patterns for display.

        Args:
            categorized_patterns: List of categorized patterns

        Returns:
            List of formatted pattern strings
        """
        import logging
        logger = logging.getLogger(__name__)

        logger.info(f"Formatting {len(categorized_patterns)} categorized patterns for display")

        formatted_patterns = []

        # Group patterns by category
        patterns_by_category = {}
        for pattern_data in categorized_patterns:
            category = pattern_data["category"]
            if category not in patterns_by_category:
                patterns_by_category[category] = []
            patterns_by_category[category].append(pattern_data)

        logger.info(f"Grouped patterns into {len(patterns_by_category)} categories: {list(patterns_by_category.keys())}")

        # Sort categories by priority
        category_priority = {
            "work_habits": 1,
            "preferences": 2,
            "challenges": 3,
            "needs": 4,
            "behaviors": 5,
            "attitudes": 6,
            "goals": 7,
            "general": 8
        }

        sorted_categories = sorted(patterns_by_category.keys(),
                                  key=lambda c: category_priority.get(c, 100))

        logger.info(f"Sorted categories: {sorted_categories}")

        # Format patterns by category
        for category in sorted_categories:
            category_patterns = patterns_by_category[category]

            # Sort patterns by actionability (high to low)
            actionability_order = {"high": 0, "medium": 1, "low": 2}
            sorted_patterns = sorted(category_patterns,
                                    key=lambda p: actionability_order.get(p["actionability"], 3))

            logger.info(f"Category '{category}' has {len(sorted_patterns)} patterns")

            # Format each pattern
            for pattern_data in sorted_patterns:
                pattern = pattern_data["pattern"]
                actionability = pattern_data["actionability"]

                # Format the pattern string with category and actionability
                category_display = category.replace('_', ' ').title()

                # Include actionability in the formatted pattern
                formatted_pattern = f"{category_display} ({actionability.title()}): {pattern}"
                formatted_patterns.append(formatted_pattern)

                logger.info(f"Added formatted pattern: {formatted_pattern[:50]}...")

        return formatted_patterns

    def format_patterns_as_json(self, categorized_patterns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format categorized patterns as JSON objects.

        Args:
            categorized_patterns: List of categorized patterns

        Returns:
            List of pattern objects with category and actionability
        """
        import logging
        logger = logging.getLogger(__name__)

        logger.info(f"Formatting {len(categorized_patterns)} categorized patterns as JSON")

        formatted_patterns = []

        # Sort patterns by category and actionability
        actionability_order = {"high": 0, "medium": 1, "low": 2}
        sorted_patterns = sorted(categorized_patterns,
                                key=lambda p: (p["category"], actionability_order.get(p["actionability"], 3)))

        # Format each pattern as a JSON object
        for pattern_data in sorted_patterns:
            formatted_pattern = {
                "pattern": pattern_data["pattern"],
                "category": pattern_data["category"].replace('_', ' ').title(),
                "actionability": pattern_data["actionability"].title()
            }
            formatted_patterns.append(formatted_pattern)

        logger.info(f"Formatted {len(formatted_patterns)} patterns as JSON")

        return formatted_patterns

    def _determine_category(self, pattern: str) -> str:
        """
        Determine the category of a pattern.

        Args:
            pattern: Pattern string

        Returns:
            Category name
        """
        pattern_lower = pattern.lower()

        for category, keywords in self.pattern_categories.items():
            for keyword in keywords:
                if keyword in pattern_lower:
                    return category

        return "general"

    def _determine_actionability(self, pattern: str) -> str:
        """
        Determine the actionability of a pattern.

        Args:
            pattern: Pattern string

        Returns:
            Actionability level (high, medium, low)
        """
        pattern_lower = pattern.lower()

        for level, keywords in self.actionability_keywords.items():
            for keyword in keywords:
                if keyword in pattern_lower:
                    return level

        return "medium"  # Default actionability
