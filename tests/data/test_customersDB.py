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
        "area":"Test Area",
        "city": "Test City",
        "state": "TS",
        "country": "India",
        "zip_code": "123456",
        "user_type": "CUSTOMER"
    }

class TestCustomersDB:
    
    @patch('app.data.customersDB.database.get_connection')
    def test_queryAllCustomersDB(self, mock_get_connection, mock_connection, mock_customer):
        # Arrange
        conn, cursor = mock_connection
        mock_get_connection.return_value = conn
        cursor.fetchall.return_value = [{"customer_id": 1, "customer_name": "Test Customer", "phone": "1234567890", "email": "test@example.com", 
                                        "address": "123 Test St", "city": "Test City", "state": "TS", "pincode": "123456"}]
        
        # Act
        result = customersDB.queryAllCustomersDB()
        # Assert
        assert len(result) == 1
        assert result[0]["customer_id"] == 1
        assert result[0]["customer_name"] == "Test Customer"
        cursor.execute.assert_called_once()
        cursor.close.assert_called_once()
        conn.close.assert_called_once()
    
    @patch('app.data.customersDB.queryCustomerByNameAndPhoneDB')
    @patch('app.data.customersDB.database.get_connection')
    def test_createCustomerDB(self, mock_get_connection, mock_query, mock_connection, mock_customer):
        # Arrange
        conn, cursor = mock_connection
        mock_get_connection.return_value = conn
        mock_query.return_value = []
        cursor.lastrowid = 1
        
        # Act
        result = customersDB.createCustomerDB(mock_customer)
        
        # Assert
        assert result is not None
        assert result["customer_id"] == 1
        conn.commit.assert_called_once()
        cursor.execute.assert_called()
        conn.close.assert_called()
        cursor.close.assert_called()
    
    @patch('app.data.customersDB.database.get_connection')
    def test_queryCustomerByNameDB(self, mock_get_connection, mock_connection, mock_customer):
        # Arrange
        conn, cursor = mock_connection
        mock_get_connection.return_value = conn
        cursor.fetchall.return_value = [{"customer_id": 1, "customer_name": "Test Customer", "phone": "1234567890", "email": "test@example.com", 
                                       "address": "123 Test St", "city": "Test City", "state": "TS", "pincode": "123456"}]
        
        # Act
        result = customersDB.queryCustomerByNameAndPhoneDB("Test Customer", "1234567890")
        
        # Assert
        assert len(result) == 1
        assert result[0]["customer_id"] == 1
        assert result[0]["customer_name"] == "Test Customer"
        cursor.execute.assert_called_once_with("""
            SELECT user_id as customer_id, concat(first_name, ' ', last_name) as customer_name, 
            email, phone, area, city, state, country, zip_code, user_type 
            FROM users 
            WHERE user_type = 'CUSTOMER' AND CONCAT(first_name, ' ', last_name) = %s AND phone = %s
        """, ("Test Customer", "1234567890"))
        cursor.close.assert_called_once()
        conn.close.assert_called_once()