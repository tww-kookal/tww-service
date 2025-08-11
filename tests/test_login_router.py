import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def mock_user():
    return {
        "user_id": 1,
        "username": "testuser",
        "password": "hashed_password",
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "phone": "1234567890"
    }

class TestLoginRouter:
    
    @patch('app.routers.login.queryUser')
    @patch('app.routers.login.validateUser')
    @patch('app.routers.login.utils.create_access_token')
    def test_login_success(self, mock_create_access_token, mock_validateUser, mock_queryUser, mock_user):
        # Arrange
        mock_queryUser.return_value = mock_user
        mock_validateUser.return_value = True
        mock_create_access_token.return_value = "mock_token"
        
        # Act
        response = client.post(
            "/login",
            data={"username": "testuser", "password": "password123"}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json() == {"access_token": "mock_token", "token_type": "bearer"}
        mock_queryUser.assert_called_once_with("testuser")
        mock_validateUser.assert_called_once_with(mock_user, "password123")
        mock_create_access_token.assert_called_once()
    
    @patch('app.routers.login.queryUser')
    @patch('app.routers.login.validateUser')
    def test_login_invalid_credentials(self, mock_validateUser, mock_queryUser, mock_user):
        # Arrange
        mock_queryUser.return_value = mock_user
        mock_validateUser.return_value = False
        
        # Act
        response = client.post(
            "/login",
            data={"username": "testuser", "password": "wrong_password"}
        )
        
        # Assert
        assert response.status_code == 400
        assert response.json() == {"detail": "Invalid credentials"}
        mock_queryUser.assert_called_once_with("testuser")
        mock_validateUser.assert_called_once_with(mock_user, "wrong_password")