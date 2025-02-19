"""
Authentication middleware and dependencies for the FastAPI application.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import logging
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import User

logger = logging.getLogger(__name__)
security = HTTPBearer()

class AuthService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def get_current_user(
        self,
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
    ) -> Optional[User]:
        """
        Validate the auth token and return the current user.
        For testing purposes, this will create a user if they don't exist.
        """
        try:
            # Extract user_id from token
            # In a real implementation, this would verify the JWT token
            # and extract claims. For now, we'll use the token as the user_id
            user_id = credentials.credentials

            # Get or create user in database
            user = db.query(User).filter(User.user_id == user_id).first()
            if not user:
                # For testing purposes, create a new user if they don't exist
                user = User(
                    user_id=user_id,
                    email=f"{user_id}@example.com"  # Generate a dummy email
                )
                db.add(user)
                try:
                    db.commit()
                    self.logger.info(f"Created new user with ID: {user_id}")
                except Exception as db_error:
                    db.rollback()
                    self.logger.error(f"Database error creating user: {str(db_error)}")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Error creating user record",
                    )

            return user

        except Exception as e:
            self.logger.error(f"Authentication error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )

# Singleton instance
auth_service = AuthService()

# Dependency for protected routes
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency that returns the current authenticated user.
    Use this as a dependency in protected routes.
    """
    return await auth_service.get_current_user(credentials, db)