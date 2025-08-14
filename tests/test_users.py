import pytest
from unittest.mock import patch, MagicMock
from app.biz import usersHelper

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

class TestUsers:
    
    @patch('app.biz.users.utils.verify_password')
    def test_validateUser_valid(self, mock_verify_password, mock_user):
        # Arrange
        mock_verify_password.return_value = True
        
        # Act
        result = usersHelper.validateUser(mock_user, "password123")
        
        # Assert
        assert result is True
        mock_verify_password.assert_called_once_with("password123", mock_user["password"])
    
    @patch('app.biz.users.utils.verify_password')
    def test_validateUser_invalid_password(self, mock_verify_password, mock_user):
        # Arrange
        mock_verify_password.return_value = False
        
        # Act
        result = usersHelper.validateUser(mock_user, "wrong_password")
        
        # Assert
        assert result is False
        mock_verify_password.assert_called_once_with("wrong_password", mock_user["password"])
    
    def test_validateUser_no_user(self):
        # Act
        result = usersHelper.validateUser(None, "password123")
        
        # Assert
        assert result is False
    
    @patch('app.biz.users.queryUserDB')
    def test_queryUser(self, mock_queryUserDB, mock_user):
        # Arrange
        mock_queryUserDB.return_value = mock_user
        
        # Act
        result = usersHelper.queryUser("testuser")
        
        # Assert
        assert result == mock_user
        mock_queryUserDB.assert_called_once_with("testuser")