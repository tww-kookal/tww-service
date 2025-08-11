import pytest
from unittest.mock import patch, MagicMock
from app.data import customersDB

@pytest.fixture
def mock_connection():
    conn = MagicMock()
    cursor = MagicMock()
    conn.cursor.return_value = cursor
    return conn, cursor

@pytest.fixture
def mock_customer():
    return {
        "customer_id": 1,
        "customer_name": "Test Customer",
        "phone": "1234567890",
        "email": "test@example.com",
        "address": "123 Test St",
        "city": "Test City",
        "state": "TS",
        "pincode": "123456"
    }

class TestCustomersDB:
    
    @patch('app.data.customersDB.database.get_connection')
    def test_queryAllCustomersDB(self, mock_get_connection, mock_connection, mock_customer):
        # Arrange
        conn, cursor = mock_connection
        mock_get_connection.return_value = conn
        cursor.fetchall.return_value = [(1, "Test Customer", "1234567890", "test@example.com", 
                                        "123 Test St", "Test City", "TS", "123456")]
        
        # Act
        result = customersDB.queryAllCustomersDB()
        
        # Assert
        assert len(result) == 1
        assert result[0]["customer_id"] == 1
        assert result[0]["customer_name"] == "Test Customer"
        cursor.execute.assert_called_once()
        cursor.close.assert_called_once()
        conn.close.assert_called_once()
    
    @patch('app.data.customersDB.database.get_connection')
    def test_createCustomerDB(self, mock_get_connection, mock_connection, mock_customer):
        # Arrange
        conn, cursor = mock_connection
        mock_get_connection.return_value = conn
        cursor.lastrowid = 1
        
        # Act
        result = customersDB.createCustomerDB(mock_customer)
        
        # Assert
        assert result == 1
        cursor.execute.assert_called_once()
        conn.commit.assert_called_once()
        cursor.close.assert_called_once()
        conn.close.assert_called_once()
    
    @patch('app.data.customersDB.database.get_connection')
    def test_queryCustomerByNameDB(self, mock_get_connection, mock_connection, mock_customer):
        # Arrange
        conn, cursor = mock_connection
        mock_get_connection.return_value = conn
        cursor.fetchone.return_value = (1, "Test Customer", "1234567890", "test@example.com", 
                                       "123 Test St", "Test City", "TS", "123456")
        
        # Act
        result = customersDB.queryCustomerByNameDB("Test Customer")
        
        # Assert
        assert result["customer_id"] == 1
        assert result["customer_name"] == "Test Customer"
        cursor.execute.assert_called_once_with("SELECT * FROM customers WHERE customer_name = %s", ("Test Customer",))
        cursor.close.assert_called_once()
        conn.close.assert_called_once()