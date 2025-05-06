"""
UI components for the application.

This module provides functions to create UI components for the application.
It doesn't depend on any specific UI framework.
"""

import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

def create_progress_bar(progress: float, text: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a progress bar data structure.

    Args:
        progress: Progress value between 0 and 1
        text: Optional text to display with the progress bar

    Returns:
        Dict[str, Any]: Progress bar data structure
    """
    result = {
        'type': 'progress_bar',
        'progress': progress
    }

    if text:
        result['text'] = text

    return result

def create_status_indicator(status: str, state: str = "info") -> Dict[str, Any]:
    """
    Create a status indicator data structure.

    Args:
        status: Status message
        state: Status state (success, error, warning, info)

    Returns:
        Dict[str, Any]: Status indicator data structure
    """
    return {
        'type': 'status_indicator',
        'status': status,
        'state': state
    }

def create_error_message(message: str, details: Optional[str] = None) -> Dict[str, Any]:
    """
    Create an error message data structure.

    Args:
        message: Error message
        details: Optional error details

    Returns:
        Dict[str, Any]: Error message data structure
    """
    result = {
        'type': 'error_message',
        'message': message
    }

    if details:
        result['details'] = details

    return result

def create_success_message(message: str, details: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a success message data structure.

    Args:
        message: Success message
        details: Optional success details

    Returns:
        Dict[str, Any]: Success message data structure
    """
    result = {
        'type': 'success_message',
        'message': message
    }

    if details:
        result['details'] = details

    return result
