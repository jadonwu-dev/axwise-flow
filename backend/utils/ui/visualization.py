"""
Visualization utilities for the application.

This module provides functions to create visualization data structures
that can be used by frontend applications. It doesn't depend on any
specific UI framework.
"""

import plotly.graph_objs as go
import json
import logging
from typing import List, Dict, Any, Optional

def create_theme_visualization(themes: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Create theme visualization data structure.

    Args:
        themes: List of theme objects

    Returns:
        Optional[Dict[str, Any]]: Visualization data structure or None if no themes
    """
    if not themes:
        logging.info("No themes to visualize")
        return None

    # Create frequency data
    theme_names = [t.get('name', 'Unknown') for t in themes]
    confidences = [t.get('confidence', 0) for t in themes]

    # Create bar chart
    fig = go.Figure(data=[
        go.Bar(
            x=theme_names,
            y=confidences,
            marker_color='rgb(55, 83, 109)'
        )
    ])

    fig.update_layout(
        title='Theme Analysis',
        xaxis_title='Themes',
        yaxis_title='Confidence',
        height=400
    )

    # Create detailed theme information
    theme_details = []
    for theme in themes:
        theme_details.append({
            'name': theme.get('name', 'Unknown Theme'),
            'summary': theme.get('summary', 'No summary available'),
            'keywords': theme.get('keywords', []),
            'statements': theme.get('statements', []),
            'confidence': theme.get('confidence', 0)
        })

    # Return visualization data
    return {
        'chart': json.loads(fig.to_json()),
        'theme_details': theme_details
    }

def create_pattern_graph(patterns: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Create pattern visualization data structure.

    Args:
        patterns: List of pattern objects

    Returns:
        Optional[Dict[str, Any]]: Visualization data structure or None if no patterns
    """
    if not patterns:
        logging.info("No patterns to visualize")
        return None

    # Create frequency data
    pattern_types = [p.get('type', 'Unknown') for p in patterns]
    frequencies = [p.get('frequency', 0) for p in patterns]

    # Create bar chart
    fig = go.Figure(data=[
        go.Bar(
            x=pattern_types,
            y=frequencies,
            marker_color='rgb(26, 118, 255)'
        )
    ])

    fig.update_layout(
        title='Pattern Analysis',
        xaxis_title='Pattern Types',
        yaxis_title='Frequency',
        height=400
    )

    # Create detailed pattern information
    pattern_details = []
    for pattern in patterns:
        pattern_details.append({
            'type': pattern.get('type', 'Unknown Pattern'),
            'description': pattern.get('description', 'No description available'),
            'evidence': pattern.get('evidence', []),
            'confidence': pattern.get('confidence', 0)
        })

    # Return visualization data
    return {
        'chart': json.loads(fig.to_json()),
        'pattern_details': pattern_details
    }

def create_sentiment_chart(sentiment: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Create sentiment visualization data structure.

    Args:
        sentiment: Sentiment analysis data

    Returns:
        Optional[Dict[str, Any]]: Visualization data structure or None if no sentiment data
    """
    if not sentiment:
        logging.info("No sentiment data to visualize")
        return None

    # Get aspect sentiments
    aspects = list(sentiment.get('aspects', {}).keys())
    scores = list(sentiment.get('aspects', {}).values())

    if not aspects:
        logging.info("No aspects to analyze")
        return None

    # Create bar chart
    fig = go.Figure(data=[
        go.Bar(
            x=aspects,
            y=scores,
            marker_color=['rgb(0, 200, 0)' if s > 0 else 'rgb(200, 0, 0)' for s in scores]
        )
    ])

    fig.update_layout(
        title='Aspect-based Sentiment Analysis',
        xaxis_title='Aspects',
        yaxis_title='Sentiment Score',
        height=400,
        yaxis=dict(
            range=[-1, 1],  # Set y-axis range to match sentiment scores
            tickformat='+%'  # Format ticks as percentages with + sign
        )
    )

    # Get overall sentiment
    score = sentiment.get('score', 0)

    # Return visualization data
    return {
        'chart': json.loads(fig.to_json()),
        'overall_score': score,
        'positive_points': sentiment.get('positive', []),
        'negative_points': sentiment.get('negative', [])
    }

def create_insight_summary(insights: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Create insight visualization data structure.

    Args:
        insights: List of insight objects

    Returns:
        Optional[Dict[str, Any]]: Visualization data structure or None if no insights
    """
    if not insights:
        logging.info("No insights to visualize")
        return None

    # Group insights by type
    types = {}
    for insight in insights:
        insight_type = insight.get('type', 'Unknown Type')
        if insight_type not in types:
            types[insight_type] = []
        types[insight_type].append(insight)

    # Create structured insight data
    insight_groups = {}
    for insight_type, type_insights in types.items():
        insight_groups[insight_type] = []
        for insight in type_insights:
            insight_groups[insight_type].append({
                'description': insight.get('description', 'No description available'),
                'evidence': insight.get('evidence', []),
                'related_personas': insight.get('related_personas', []),
                'related_patterns': insight.get('related_patterns', []),
                'confidence': insight.get('confidence', 0)
            })

    # Return visualization data
    return {
        'insight_groups': insight_groups
    }
