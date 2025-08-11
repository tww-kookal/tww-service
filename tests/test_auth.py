import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from jose import jwt
from app import auth

class TestAuth:
    
    @patch('app.auth.jwt.decode')
    def test_get_current_user_valid_token(self, mock_decode):
        # Arrange
        mock_decode.return_value = {"sub": "testuser"}
        token = "valid_token"
        
        # Act
        result = auth.get_current_user(token)
        
        # Assert
        assert result == "testuser"
        mock_decode.assert_called_once_with(token, auth.settings.SECRET_KEY, algorithms=[auth.settings.ALGORITHM])
    
    @patch('app.auth.jwt.decode')
    def test_get_current_user_missing_username(self, mock_decode):
        # Arrange
        mock_decode.return_value = {}  # No 'sub' field
        token = "invalid_token"
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            auth.get_current_user(token)
        
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Could not validate credentials"
        mock_decode.assert_called_once_with(token, auth.settings.SECRET_KEY, algorithms=[auth.settings.ALGORITHM])
    
    @patch('app.auth.jwt.decode')
    def test_get_current_user_jwt_error(self, mock_decode):
        # Arrange
        mock_decode.side_effect = auth.JWTError("Invalid token")
        token = "invalid_token"
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            auth.get_current_user(token)
        
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Could not validate credentials"
        mock_decode.assert_called_once_with(token, auth.settings.SECRET_KEY, algorithms=[auth.settings.ALGORITHM])