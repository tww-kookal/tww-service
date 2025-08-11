import pytest
from unittest.mock import patch, MagicMock
from app.data import usersDB

@pytest.fixture
def mock_connection():
    conn = MagicMock()
    cursor = MagicMock()
    conn.cursor.return_value = cursor
    return conn, cursor

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

class TestUsersDB:
    
    @patch('app.data.usersDB.database.get_connection')
    def test_queryUserDB(self, mock_get_connection, mock_connection, mock_user):
        # Arrange
        conn, cursor = mock_connection
        mock_get_connection.return_value = conn
        cursor.fetchone.return_value = {
            "user_id": 1,
            "username": "testuser",
            "password": "hashed_password",
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com",
            "phone": "1234567890"
        }
        
        # Act
        result = usersDB.queryUserDB("testuser")
        
        # Assert
        assert result["user_id"] == 1
        assert result["username"] == "testuser"
        cursor.execute.assert_called_once_with("SELECT user_id, username, first_name, last_name, email, phone, password FROM users WHERE username=%s", ("testuser",))
        cursor.close.assert_called_once()
        conn.close.assert_called_once()
    
    @patch('app.data.usersDB.database.get_connection')
    def test_queryUserByIdDB(self, mock_get_connection, mock_connection):
        # Arrange
        conn, cursor = mock_connection
        mock_get_connection.return_value = conn
        cursor.fetchone.return_value = (1, "testuser", "Test", "User", "test@example.com", "1234567890")
        
        # Act
        result = usersDB.queryUserByIdDB(1)
        
        # Assert
        assert result[0] == 1
        assert result[1] == "testuser"
        cursor.execute.assert_called_once_with("SELECT user_id, username, first_name, last_name, email, phone FROM users WHERE user_id = %s", (1,))
        cursor.close.assert_called_once()
        conn.close.assert_called_once()
    
    @patch('app.data.usersDB.utils.hash_password')
    @patch('app.data.usersDB.database.get_connection')
    def test_persistUserDB_success(self, mock_get_connection, mock_hash_password, mock_connection):
        # Arrange
        conn, cursor = mock_connection
        mock_get_connection.return_value = conn
        cursor.fetchone.return_value = None  # Username doesn't exist
        mock_hash_password.return_value = "hashed_password"
        
        # Act
        result = usersDB.persistUserDB("testuser", "password123", "Test", "User", "test@example.com", "1234567890")
        
        # Assert
        assert result is True
        mock_hash_password.assert_called_once_with("password123")
        cursor.execute.assert_called_with("INSERT INTO users (username, password, first_name, last_name, email, phone) VALUES (%s, %s, %s, %s, %s, %s)",
                                         ("testuser", "hashed_password", "Test", "User", "test@example.com", "1234567890"))
        conn.commit.assert_called_once()
        cursor.close.assert_called_once()
        conn.close.assert_called_once()
    
    @patch('app.data.usersDB.database.get_connection')
    def test_persistUserDB_username_exists(self, mock_get_connection, mock_connection):
        # Arrange
        conn, cursor = mock_connection
        mock_get_connection.return_value = conn
        cursor.fetchone.return_value = (1,)  # Username exists
        
        # Act & Assert
        with pytest.raises(Exception, match="Username already exists"):
            usersDB.persistUserDB("testuser", "password123", "Test", "User", "test@example.com", "1234567890")
    
    @patch('app.data.usersDB.database.get_connection')
    def test_queryRolesForUserDB(self, mock_get_connection, mock_connection):
        # Arrange
        conn, cursor = mock_connection
        mock_get_connection.return_value = conn
        cursor.fetchall.return_value = [("admin",), ("user",)]
        
        # Act
        result = usersDB.queryRolesForUserDB("testuser")
        
        # Assert
        assert result == ["admin", "user"]
        cursor.execute.assert_called_once()
        cursor.close.assert_called_once()
        conn.close.assert_called_once()