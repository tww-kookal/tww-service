import pytest
from unittest.mock import patch, MagicMock, ANY
from fastapi import HTTPException
from app.auth import getUserDetailsFromAccessToken, getUserDetailsFromIdToken, authorizedUser
from app.config.config import settings

class TestGoogleAuth:
    @patch('app.auth.http_req.get')
    def test_getUserDetailsFromAccessToken_success(self, mock_get):
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "sub": "123456789",
            "email": "test@example.com",
            "name": "Test User",
            "given_name": "Test",
            "family_name": "User",
            "picture": "https://example.com/photo.jpg"
        }
        mock_get.return_value = mock_response
        
        # Act
        result = getUserDetailsFromAccessToken("fake_token")
        
        # Assert
        assert result["username"] == "123456789"
        assert result["email"] == "test@example.com"
        assert result["name"] == "Test User"
        assert result["first_name"] == "Test"
        assert result["last_name"] == "User"
        assert result["picture"] == "https://example.com/photo.jpg"
        mock_get.assert_called_once_with(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={'Authorization': 'Bearer fake_token'}
        )

    @patch('app.auth.http_req.get')
    def test_getUserDetailsFromAccessToken_failure(self, mock_get):
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_get.return_value = mock_response
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            getUserDetailsFromAccessToken("invalid_token")

    @patch('app.auth.google_id_token.verify_oauth2_token')
    def test_getUserDetailsFromIdToken_success(self, mock_verify_token):
        # Arrange
        mock_verify_token.return_value = {
            "sub": "123456789",
            "email": "test@example.com",
            "name": "Test User",
            "given_name": "Test",
            "family_name": "User",
            "picture": "https://example.com/photo.jpg"
        }
        
        # Act
        result = getUserDetailsFromIdToken("fake_id_token")
        
        # Assert
        assert result["username"] == "123456789"
        assert result["email"] == "test@example.com"
        assert result["name"] == "Test User"
        mock_verify_token.assert_called_once_with(
            "fake_id_token",
            ANY,
            settings.GOOGLE_APP_CLIENT_ID
        )

    @patch('app.auth.getUserDetailsFromAccessToken')
    @patch('app.auth.userDB.queryRolesForUserDB')
    async def test_authorizedUser_success(self, mock_query_roles, mock_get_user_details):
        # Arrange
        mock_get_user_details.return_value = {
            "username": "123456789",
            "email": "test@example.com",
            "name": "Test User"
        }
        mock_query_roles.return_value = ["admin"]
        auth_wrapper = authorizedUser(["admin"])
        
        # Act
        result = await auth_wrapper(authorization="Bearer fake_token")
        
        # Assert
        assert result["is_authorized"] == True
        assert result["user_name"] == "123456789"
        assert result["email"] == "test@example.com"
        assert "admin" in result["roles"]

    @patch('app.auth.getUserDetailsFromAccessToken')
    @patch('app.auth.userDB.queryRolesForUserDB')
    async def test_authorizedUser_unauthorized(self, mock_query_roles, mock_get_user_details):
        # Arrange
        mock_get_user_details.return_value = {
            "username": "123456789",
            "email": "test@example.com",
            "name": "Test User"
        }
        mock_query_roles.return_value = ["user"]
        auth_wrapper = authorizedUser(["admin"])
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await auth_wrapper(authorization="Bearer fake_token")
        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "Not authorized"