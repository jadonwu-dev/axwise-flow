"""
Authentication middleware for the FastAPI application.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import logging
import os

from backend.database import get_db
from backend.models import User
from backend.services.external.clerk_service import ClerkService

# Configure logging
logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer(
    scheme_name="Bearer Authentication",
    description="Enter your bearer token",
    auto_error=True
)

# Initialize Clerk service
CLERK_...=***REMOVED***

# Enable/disable Clerk JWT validation based on environment
ENABLE_CLERK_...=***REMOVED***"ENABLE_CLERK_VALIDATION", "false").lower() == "true"

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get the current authenticated user.
    
    When ENABLE_CLERK_VALIDATION is True, validates the JWT token using Clerk.
    Otherwise, uses a simplified implementation that accepts any non-empty token.
    
    Args:
        credentials: The HTTP Authorization credentials
        db: Database session
    
    Returns:
        User: The authenticated user
    
    Raises:
        HTTPException: If authentication fails
    """
    token = credentials.credentials
    
    if not token:
        logger.warning("Authentication failed: Empty token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if ENABLE_CLERK_VALIDATION:
        # Validate JWT token with Clerk
        is_valid, payload = clerk_service.validate_token(token)
        
        if not is_valid or not payload:
            logger.warning("Authentication failed: Invalid token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Extract user ID from JWT claim
        user_id = payload.get('sub')
        
        if not user_id:
            logger.warning("Authentication failed: Token missing subject claim")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user identifier",
                headers={"WWW-Authenticate": "Bearer"},
            )
    else:
        # For Phase 1/2, use the token as the user_id directly
        user_id = token
    
    # Get or create user
    user = db.query(User).filter(User.user_id == user_id).first()
    
    if not user:
        # If using Clerk validation and we have a real JWT, try to get user info
        if ENABLE_CLERK_VALIDATION:
            user_info = clerk_service.get_user_info(user_id)
            
            # Create a new user record with Clerk data if available
            new_user = User(
                user_id=user_id,
                email=user_info.get('email_addresses', [{}])[0].get('email_address') if user_info else None,
                first_name=user_info.get('first_name') if user_info else None,
                last_name=user_info.get('last_name') if user_info else None,
            )
        else:
            # Create a basic user record without additional info
            new_user = User(user_id=user_id)
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        logger.info(f"Created new user with ID: {user_id}")
        return new_user
    
    return user