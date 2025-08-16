"""
Centralized timezone utilities for consistent datetime handling across the application.

This module provides utilities to ensure all timestamps are handled consistently
in UTC throughout the application, with proper timezone awareness.
"""

from datetime import datetime, timezone
from typing import Optional, Union
import logging

logger = logging.getLogger(__name__)


def utc_now() -> datetime:
    """
    Get current UTC time with timezone awareness.
    
    This should be used instead of datetime.now() or datetime.utcnow()
    throughout the application to ensure consistency.
    
    Returns:
        datetime: Current UTC time with timezone info
    """
    return datetime.now(timezone.utc)


def ensure_utc(dt: Optional[datetime]) -> Optional[datetime]:
    """
    Ensure a datetime object is in UTC timezone.
    
    Args:
        dt: Datetime object (can be naive or timezone-aware)
        
    Returns:
        datetime: UTC datetime with timezone info, or None if input is None
    """
    if dt is None:
        return None
        
    if dt.tzinfo is None:
        # Naive datetime - assume it's already UTC and add timezone info
        logger.debug(f"Converting naive datetime {dt} to UTC")
        return dt.replace(tzinfo=timezone.utc)
    else:
        # Timezone-aware datetime - convert to UTC
        return dt.astimezone(timezone.utc)


def format_iso_utc(dt: Optional[datetime]) -> Optional[str]:
    """
    Format datetime as ISO string in UTC timezone.
    
    Args:
        dt: Datetime object to format
        
    Returns:
        str: ISO formatted string with 'Z' suffix, or None if input is None
    """
    if dt is None:
        return None
        
    utc_dt = ensure_utc(dt)
    return utc_dt.isoformat().replace("+00:00", "Z")


def parse_iso_to_utc(iso_string: str) -> datetime:
    """
    Parse ISO datetime string to UTC datetime object.
    
    Args:
        iso_string: ISO formatted datetime string
        
    Returns:
        datetime: UTC datetime with timezone info
        
    Raises:
        ValueError: If the string cannot be parsed
    """
    try:
        # Handle 'Z' suffix
        if iso_string.endswith('Z'):
            iso_string = iso_string[:-1] + '+00:00'
            
        dt = datetime.fromisoformat(iso_string)
        return ensure_utc(dt)
    except Exception as e:
        logger.error(f"Failed to parse ISO datetime string '{iso_string}': {e}")
        raise ValueError(f"Invalid ISO datetime string: {iso_string}")


def to_local_timezone(dt: datetime, target_tz: str = "Europe/Berlin") -> datetime:
    """
    Convert UTC datetime to local timezone.
    
    Args:
        dt: UTC datetime object
        target_tz: Target timezone name (default: Europe/Berlin for CEST)
        
    Returns:
        datetime: Datetime in target timezone
    """
    try:
        import zoneinfo
        target_timezone = zoneinfo.ZoneInfo(target_tz)
    except ImportError:
        # Fallback for Python < 3.9
        import pytz
        target_timezone = pytz.timezone(target_tz)
    
    utc_dt = ensure_utc(dt)
    return utc_dt.astimezone(target_timezone)


def get_duration_minutes(start_time: datetime, end_time: Optional[datetime] = None) -> float:
    """
    Calculate duration in minutes between two timestamps.
    
    Args:
        start_time: Start datetime
        end_time: End datetime (defaults to current UTC time)
        
    Returns:
        float: Duration in minutes
    """
    if end_time is None:
        end_time = utc_now()
        
    start_utc = ensure_utc(start_time)
    end_utc = ensure_utc(end_time)
    
    duration = end_utc - start_utc
    return duration.total_seconds() / 60.0


# Backward compatibility aliases
def datetime_utc_now() -> datetime:
    """Alias for utc_now() for backward compatibility."""
    return utc_now()


def format_datetime_utc(dt: Optional[datetime]) -> Optional[str]:
    """Alias for format_iso_utc() for backward compatibility."""
    return format_iso_utc(dt)
