import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from app import utils

class TestUtils:
    
    def test_hash_password(self):
        # Arrange
        password = "password123"
        
        # Act
        hashed = utils.hash_password(password)
        
        # Assert
        assert hashed != password
        assert utils.pwd_context.verify(password, hashed)
    
    def test_verify_password_valid(self):
        # Arrange
        password = "password123"
        hashed = utils.pwd_context.hash(password)
        
        # Act
        result = utils.verify_password(password, hashed)
        
        # Assert
        assert result is True
    
    def test_verify_password_invalid(self):
        # Arrange
        password = "password123"
        wrong_password = "wrong_password"
        hashed = utils.pwd_context.hash(password)
        
        # Act
        result = utils.verify_password(wrong_password, hashed)
        
        # Assert
        assert result is False
    
    @patch('app.utils.datetime')
    @patch('app.utils.jwt.encode')
    def test_create_access_token(self, mock_encode, mock_datetime):
        # Arrange
        mock_datetime.utcnow.return_value = datetime(2023, 1, 1, 12, 0, 0)
        mock_encode.return_value = "mock_token"
        data = {"sub": "testuser"}
        expires_delta = timedelta(minutes=30)
        
        # Act
        result = utils.create_access_token(data, expires_delta)
        
        # Assert
        assert result == "mock_token"
        expected_expiry = datetime(2023, 1, 1, 12, 30, 0)
        expected_data = {"sub": "testuser", "exp": expected_expiry}
        mock_encode.assert_called_once_with(expected_data, utils.settings.SECRET_KEY, algorithm=utils.settings.ALGORITHM)
    
    @patch('app.utils.queryRolesForUserDB')
    def test_isAuthorized_authorized(self, mock_queryRolesForUserDB):
        # Arrange
        mock_queryRolesForUserDB.return_value = ["admin", "user"]
        
        # Act
        result = utils.isAuthorized("testuser", ["admin"])
        
        # Assert
        assert result is True
        mock_queryRolesForUserDB.assert_called_once_with("testuser")
    
    @patch('app.utils.queryRolesForUserDB')
    def test_isAuthorized_unauthorized(self, mock_queryRolesForUserDB):
        # Arrange
        mock_queryRolesForUserDB.return_value = ["user"]
        
        # Act
        result = utils.isAuthorized("testuser", ["admin"])
        
        # Assert
        assert result is False
        mock_queryRolesForUserDB.assert_called_once_with("testuser")
    
    @patch('app.utils.queryRolesForUserDB')
    def test_isAuthorized_self_role(self, mock_queryRolesForUserDB):
        # Arrange
        mock_queryRolesForUserDB.return_value = ["user"]
        
        # Act
        result = utils.isAuthorized("testuser", ["self"])
        
        # Assert
        assert result is True
        mock_queryRolesForUserDB.assert_called_once_with("testuser")
    
    @patch('app.utils.queryRolesForUserDB')
    def test_isAuthorized_no_roles(self, mock_queryRolesForUserDB):
        # Arrange
        mock_queryRolesForUserDB.return_value = None
        
        # Act
        result = utils.isAuthorized("testuser", ["self"])
        
        # Assert
        assert result is True
        mock_queryRolesForUserDB.assert_called_once_with("testuser")