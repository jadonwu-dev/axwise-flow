"""
Secure environment variables management.

Last Updated: 2025-05-20
"""

import os
import logging
import json
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
import re

# Configure logging
logger = logging.getLogger(__name__)

# Environment detection
IS_PRODUCTION = os.getenv("ENVIRONMENT", "development").lower() == "production"

# Sensitive variable patterns
SENSITIVE_PATTERNS = [
    r".*_key$",
    r".*_secret$",
    r".*password.*",
    r".*token.*",
    r".*credential.*",
]

class SecureEnvironment:
    """Secure environment variables management."""

    def __init__(self):
        """Initialize the secure environment manager."""
        self._env_vars: Dict[str, str] = {}
        self._sensitive_vars: List[str] = []
        self._load_env_vars()
        self._identify_sensitive_vars()

    def _load_env_vars(self):
        """Load environment variables from .env file and OS environment."""
        # Load from .env file if exists
        env_file = Path(".env")
        if env_file.exists():
            try:
                with open(env_file, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            try:
                                key, value = line.split("=", 1)
                                self._env_vars[key.strip()] = value.strip()
                            except ValueError:
                                logger.warning(f"Invalid line in .env file: {line}")
            except Exception as e:
                logger.error(f"Error loading .env file: {str(e)}")

        # Override with OS environment variables
        for key, value in os.environ.items():
            self._env_vars[key] = value

    def _identify_sensitive_vars(self):
        """Identify sensitive environment variables based on patterns."""
        for key in self._env_vars.keys():
            for pattern in SENSITIVE_PATTERNS:
                if re.match(pattern, key, re.IGNORECASE):
                    self._sensitive_vars.append(key)
                    break

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get an environment variable value.

        Args:
            key: The environment variable name
            default: Default value if not found

        Returns:
            The environment variable value or default
        """
        return self._env_vars.get(key, default)

    def get_int(self, key: str, default: Optional[int] = None) -> Optional[int]:
        """
        Get an environment variable as integer.

        Args:
            key: The environment variable name
            default: Default value if not found or invalid

        Returns:
            The environment variable as integer or default
        """
        value = self.get(key)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:
            logger.warning(f"Invalid integer value for {key}: {value}")
            return default

    def get_float(self, key: str, default: Optional[float] = None) -> Optional[float]:
        """
        Get an environment variable as float.

        Args:
            key: The environment variable name
            default: Default value if not found or invalid

        Returns:
            The environment variable as float or default
        """
        value = self.get(key)
        if value is None:
            return default
        try:
            return float(value)
        except ValueError:
            logger.warning(f"Invalid float value for {key}: {value}")
            return default

    def get_bool(self, key: str, default: Optional[bool] = None) -> Optional[bool]:
        """
        Get an environment variable as boolean.

        Args:
            key: The environment variable name
            default: Default value if not found

        Returns:
            The environment variable as boolean or default
        """
        value = self.get(key)
        if value is None:
            return default
        return value.lower() in ("true", "1", "yes", "y", "on")

    def get_list(self, key: str, default: Optional[List[str]] = None) -> Optional[List[str]]:
        """
        Get an environment variable as list.

        Args:
            key: The environment variable name
            default: Default value if not found

        Returns:
            The environment variable as list or default
        """
        value = self.get(key)
        if value is None:
            return default
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value.split(",")

    def get_json(self, key: str, default: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Get an environment variable as JSON.

        Args:
            key: The environment variable name
            default: Default value if not found or invalid

        Returns:
            The environment variable as JSON or default
        """
        value = self.get(key)
        if value is None:
            return default
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON value for {key}: {value}")
            return default

    def is_sensitive(self, key: str) -> bool:
        """
        Check if an environment variable is sensitive.

        Args:
            key: The environment variable name

        Returns:
            True if sensitive, False otherwise
        """
        return key in self._sensitive_vars

    def get_safe_dict(self) -> Dict[str, str]:
        """
        Get a dictionary of environment variables with sensitive values masked.

        Returns:
            Dictionary of environment variables
        """
        return {
            key: "***" if self.is_sensitive(key) else value
            for key, value in self._env_vars.items()
        }

    def validate_required_vars(self, required_vars: List[str]) -> List[str]:
        """
        Validate that required environment variables are set.

        Args:
            required_vars: List of required variable names

        Returns:
            List of missing variable names
        """
        missing = []
        for key in required_vars:
            if key not in self._env_vars or not self._env_vars[key]:
                missing.append(key)
        return missing

# Global instance
secure_env = SecureEnvironment()
