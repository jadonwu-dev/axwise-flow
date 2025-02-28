"""
Tests for the authentication middleware and Clerk service.
"""

import pytest
import json
import time
from unittest.mock import patch, MagicMock, Mock

from backend.services.external.clerk_service import ClerkService
from backend.services.external.auth_middleware import get_current_user
from fastapi import HTTPException

@pytest.fixture
def mock_clerk_service():
    with patch("backend.services.external.auth_middleware.clerk_service") as mock_service:
        yield mock_service

@pytest.fixture
def mock_db_session():
    mock_db = MagicMock()
    mock_user = MagicMock()
    mock_user.user_id = "test_user_id"
    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = mock_user
    mock_db.query.return_value = mock_query
    return mock_db

class TestClerkService:
    """Tests for the ClerkService class."""
    
    def test_init(self):
        """Test initialization of ClerkService."""
        with patch("backend.services.external.clerk_service.requests.get") as mock_get:
            # Mock the JWKS response
            mock_response = Mock()
            mock_response.json.return_value = {"keys": []}
            mock_get.return_value = mock_response
            
            # Initialize ClerkService
            service = ClerkService()
            
            # Verify JWKS was loaded
            assert mock_get.called
            assert service.jwks == {"keys": []}
    
    def test_validate_token_no_kid(self):
        """Test token validation with missing kid."""
        with patch("backend.services.external.clerk_service.jwt.get_unverified_header") as mock_header:
            # Mock JWT header with no kid
            mock_header.return_value = {}
            
            service = ClerkService()
            is_valid, payload = service.validate_token("dummy_token")
            
            assert not is_valid
            assert payload is None
    
    def test_validate_token_key_not_found(self):
        """Test token validation when key is not found in JWKS."""
        with patch("backend.services.external.clerk_service.jwt.get_unverified_header") as mock_header, \
             patch.object(ClerkService, "_load_jwks"):
            # Mock JWT header with kid that won't be found
            mock_header.return_value = {"kid": "unknown_kid"}
            
            service = ClerkService()
            service.jwks = {"keys": [{"kid": "different_kid"}]}
            
            is_valid, payload = service.validate_token("dummy_token")
            
            assert not is_valid
            assert payload is None
    
    def test_validate_token_expired(self):
        """Test token validation with expired token."""
        with patch("backend.services.external.clerk_service.jwt.get_unverified_header") as mock_header, \
             patch("backend.services.external.clerk_service.jwt.decode") as mock_decode, \
             patch.object(ClerkService, "_get_key_from_jwks") as mock_get_key, \
             patch.object(ClerkService, "_load_jwks"):
            # Mock JWT header
            mock_header.return_value = {"kid": "test_kid"}
            
            # Mock key retrieval
            mock_get_key.return_value = "test_key"
            
            # Mock expired token
            past_time = int(time.time()) - 3600  # 1 hour ago
            mock_decode.return_value = {"exp": past_time}
            
            service = ClerkService()
            is_valid, payload = service.validate_token("dummy_token")
            
            assert not is_valid
            assert payload is None

class TestAuthMiddleware:
    """Tests for the authentication middleware."""
    
    @pytest.mark.asyncio
    async def test_get_current_user_empty_token(self):
        """Test get_current_user with empty token."""
        mock_credentials = MagicMock()
        mock_credentials.credentials = ""
        
        with pytest.raises(HTTPException) as excinfo:
            await get_current_user(credentials=mock_credentials)
        
        assert excinfo.value.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_current_user_with_validation_enabled(self, mock_clerk_service, mock_db_session):
        """Test get_current_user with validation enabled."""
        # Setup
        mock_credentials = MagicMock()
        mock_credentials.credentials = "valid_token"
        
        # Mock JWT validation
        mock_clerk_service.validate_token.return_value = (True, {"sub": "test_user_id"})
        
        # Enable Clerk validation
        with patch("backend.services.external.auth_middleware.ENABLE_CLERK_VALIDATION", True):
            # Call the function
            user = await get_current_user(
                credentials=mock_credentials,
                db=mock_db_session
            )
            
            # Assertions
            assert user.user_id == "test_user_id"
            mock_clerk_service.validate_token.assert_called_once_with("valid_token")
    
    @pytest.mark.asyncio
    async def test_get_current_user_with_validation_disabled(self, mock_db_session):
        """Test get_current_user with validation disabled."""
        # Setup
        mock_credentials = MagicMock()
        mock_credentials.credentials = "test_user_id"
        
        # Disable Clerk validation
        with patch("backend.services.external.auth_middleware.ENABLE_CLERK_VALIDATION", False):
            # Call the function
            user = await get_current_user(
                credentials=mock_credentials,
                db=mock_db_session
            )
            
            # Assertions
            assert user.user_id == "test_user_id"
            # We should directly use the token as the user_id
            mock_db_session.query.return_value.filter.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_current_user_create_new_user(self, mock_clerk_service, mock_db_session):
        """Test get_current_user creates a new user when one doesn't exist."""
        # Setup
        mock_credentials = MagicMock()
        mock_credentials.credentials = "valid_token"
        
        # Mock user not found in database
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = None
        mock_db_session.query.return_value = mock_query
        
        # Mock JWT validation and user info
        mock_clerk_service.validate_token.return_value = (True, {"sub": "new_user_id"})
        mock_clerk_service.get_user_info.return_value = {
            "first_name": "Test",
            "last_name": "User",
            "email_addresses": [{"email_address": "test@example.com"}]
        }
        
        # Enable Clerk validation
        with patch("backend.services.external.auth_middleware.ENABLE_CLERK_VALIDATION", True):
            # Call the function
            await get_current_user(
                credentials=mock_credentials,
                db=mock_db_session
            )
            
            # Assertions
            mock_db_session.add.assert_called_once()
            mock_db_session.commit.assert_called_once()
            mock_db_session.refresh.assert_called_once() 