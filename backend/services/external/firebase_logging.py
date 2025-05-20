"""
Firebase Cloud Logging integration for DesignThinkingAgentAI.

Last Updated: 2025-05-20
"""

import os
import json
import logging
import datetime
import traceback
from typing import Dict, Any, Optional, List, Union
import requests
from pydantic import BaseModel

# Configure logging
logger = logging.getLogger(__name__)

# Environment detection
IS_PRODUCTION = os.getenv("ENVIRONMENT", "development").lower() == "production"
FIREBASE_...=***REMOVED***"FIREBASE_API_KEY", "")
FIREBASE_...=***REMOVED***"FIREBASE_PROJECT_ID", "")
FIREBASE_FUNCTIONS_URL = os.getenv(
    "FIREBASE_FUNCTIONS_URL", 
    f"https://us-central1-{FIREBASE_PROJECT_ID}.cloudfunctions.net"
)

# Security event types
class SecurityEventType:
    """Security event types for logging."""
    
    # Authentication events
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILED = "login_failed"
    LOGOUT = "logout"
    PASSWORD_RESET = "password_reset"
    
    # API events
    API_RATE_LIMIT_EXCEEDED = "api_rate_limit_exceeded"
    API_UNAUTHORIZED_ACCESS = "api_unauthorized_access"
    API_INVALID_INPUT = "api_invalid_input"
    
    # Data events
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    SENSITIVE_DATA_ACCESS = "sensitive_data_access"
    
    # System events
    SYSTEM_ERROR = "system_error"
    DEPENDENCY_VULNERABILITY = "dependency_vulnerability"
    CONFIG_CHANGE = "config_change"

class SecurityEventDetails(BaseModel):
    """Security event details model."""
    
    # Common fields
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    resource: Optional[str] = None
    status_code: Optional[int] = None
    
    # Authentication specific fields
    auth_method: Optional[str] = None
    
    # API specific fields
    endpoint: Optional[str] = None
    request_method: Optional[str] = None
    
    # Data specific fields
    data_type: Optional[str] = None
    data_id: Optional[str] = None
    
    # Error specific fields
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None
    
    # Additional custom fields
    metadata: Dict[str, Any] = {}

class FirebaseLoggingService:
    """Firebase Cloud Logging service for security events."""
    
    def __init__(self):
        """Initialize the Firebase logging service."""
        self.enabled = bool(FIREBASE_API_KEY and FIREBASE_PROJECT_ID)
        if not self.enabled and IS_PRODUCTION:
            logger.warning(
                "Firebase logging is not configured but running in production. "
                "Set FIREBASE_API_KEY and FIREBASE_PROJECT_ID environment variables."
            )
    
    def log_security_event(
        self, 
        event_type: str, 
        details: Union[SecurityEventDetails, Dict[str, Any]]
    ) -> bool:
        """
        Log a security event to Firebase.
        
        Args:
            event_type: The type of security event
            details: Event details as SecurityEventDetails or dict
            
        Returns:
            True if logged successfully, False otherwise
        """
        if not self.enabled:
            # Log locally if Firebase is not configured
            logger.info(f"Security event: {event_type} - {details}")
            return False
        
        try:
            # Convert to dict if it's a model
            if isinstance(details, SecurityEventDetails):
                details_dict = details.dict()
            else:
                details_dict = details
            
            # Call Firebase function
            url = f"{FIREBASE_FUNCTIONS_URL}/logSecurityEvent"
            
            payload = {
                "data": {
                    "eventType": event_type,
                    "details": details_dict
                }
            }
            
            # Add authentication token if available
            auth_token = os.getenv("FIREBASE_AUTH_TOKEN", "")
            headers = {
                "Content-Type": "application/json"
            }
            
            if auth_token:
                headers["Authorization"] = f"Bearer {auth_token}"
            
            response = requests.post(
                url, 
                json=payload,
                headers=headers
            )
            
            if response.status_code == 200:
                return True
            else:
                logger.error(
                    f"Failed to log security event to Firebase: {response.status_code} - {response.text}"
                )
                return False
                
        except Exception as e:
            logger.error(f"Error logging security event to Firebase: {str(e)}")
            return False
    
    def log_auth_event(
        self, 
        event_type: str, 
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        auth_method: Optional[str] = None,
        status_code: Optional[int] = None,
        error_message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Log an authentication-related security event.
        
        Args:
            event_type: Auth event type (login_success, login_failed, etc.)
            user_id: User ID if available
            ip_address: Client IP address
            user_agent: Client user agent
            auth_method: Authentication method used
            status_code: HTTP status code
            error_message: Error message if applicable
            metadata: Additional metadata
            
        Returns:
            True if logged successfully, False otherwise
        """
        details = SecurityEventDetails(
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            auth_method=auth_method,
            status_code=status_code,
            error_message=error_message,
            metadata=metadata or {}
        )
        
        return self.log_security_event(event_type, details)
    
    def log_api_event(
        self,
        event_type: str,
        endpoint: str,
        request_method: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        status_code: Optional[int] = None,
        error_message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Log an API-related security event.
        
        Args:
            event_type: API event type
            endpoint: API endpoint path
            request_method: HTTP method (GET, POST, etc.)
            user_id: User ID if available
            ip_address: Client IP address
            user_agent: Client user agent
            status_code: HTTP status code
            error_message: Error message if applicable
            metadata: Additional metadata
            
        Returns:
            True if logged successfully, False otherwise
        """
        details = SecurityEventDetails(
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            endpoint=endpoint,
            request_method=request_method,
            status_code=status_code,
            error_message=error_message,
            metadata=metadata or {}
        )
        
        return self.log_security_event(event_type, details)
    
    def log_error(
        self,
        error: Exception,
        user_id: Optional[str] = None,
        resource: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Log an error as a security event.
        
        Args:
            error: The exception to log
            user_id: User ID if available
            resource: Resource being accessed when error occurred
            metadata: Additional metadata
            
        Returns:
            True if logged successfully, False otherwise
        """
        # Get stack trace
        stack_trace = "".join(traceback.format_exception(
            type(error), error, error.__traceback__
        ))
        
        details = SecurityEventDetails(
            user_id=user_id,
            resource=resource,
            error_message=str(error),
            stack_trace=stack_trace,
            metadata=metadata or {}
        )
        
        return self.log_security_event(SecurityEventType.SYSTEM_ERROR, details)

# Global instance
firebase_logging = FirebaseLoggingService()
