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
    @patch('app.data.customersDB.database.get_connection')
    def test_queryCustomerByIDDB_found(self, mock_get_connection, mock_connection, mock_customer):
        # Arrange
        conn, cursor = mock_connection
        mock_get_connection.return_value = conn
        cursor.fetchone.return_value = mock_customer
        
        # Act
        result = customersDB.queryCustomerByIDDB(1)
        
        # Assert
        assert result is not None
        assert result["customer_id"] == 1
        cursor.execute.assert_called_once_with("""
            SELECT user_id as customer_id, concat(first_name, ' ', last_name) as customer_name, 
            email, phone, area, city, state, country, zip_code, user_type 
            FROM users 
            WHERE user_id = %s AND user_type = 'CUSTOMER'
        """, (1,))
        cursor.close.assert_called_once()
        conn.close.assert_called_once()

    @patch('app.data.customersDB.database.get_connection')
    def test_queryCustomerByIDDB_not_found(self, mock_get_connection, mock_connection):
        # Arrange
        conn, cursor = mock_connection
        mock_get_connection.return_value = conn
        cursor.fetchone.return_value = None
        
        # Act
        result = customersDB.queryCustomerByIDDB(99)
        
        # Assert
        assert result is None
        cursor.execute.assert_called_once()
        cursor.close.assert_called_once()
        conn.close.assert_called_once()

    @patch('app.data.customersDB.database.get_connection')
    def test_updateCustomerDB_success(self, mock_get_connection, mock_connection, mock_customer):
        # Arrange
        conn, cursor = mock_connection
        mock_get_connection.return_value = conn
        
        # Act
        result = customersDB.updateCustomerDB(mock_customer)
        
        # Assert
        assert result is not None
        conn.commit.assert_called_once()
        cursor.execute.assert_called_once()
        conn.close.assert_called_once()
        cursor.close.assert_called_once()

    def test_updateCustomerDB_no_user_type(self, mock_customer):
        # Arrange
        mock_customer["user_type"] = ""
        
        # Act & Assert
        with pytest.raises(Exception, match="User Type is empty"):
            customersDB.updateCustomerDB(mock_customer)

    def test_updateCustomerDB_no_phone(self, mock_customer):
        # Arrange
        mock_customer["phone"] = ""
        
        # Act & Assert
        with pytest.raises(Exception, match="Phone is empty"):
            customersDB.updateCustomerDB(mock_customer)

    @patch('app.data.customersDB.queryCustomerByNameAndPhoneDB')
    def test_createCustomerDB_duplicate(self, mock_query, mock_customer):
        # Arrange
        mock_query.return_value = [mock_customer]
        
        # Act & Assert
        with pytest.raises(Exception, match="Customer Already Exists"):
            customersDB.createCustomerDB(mock_customer)

    def test_createCustomerDB_no_user_type(self, mock_customer):
        # Arrange
        mock_customer["user_type"] = ""
        
        # Act & Assert
        with pytest.raises(Exception, match="User Type is empty"):
            customersDB.createCustomerDB(mock_customer)

    def test_createCustomerDB_no_phone(self, mock_customer):
        # Arrange
        mock_customer["phone"] = ""
        
        # Act & Assert
        with pytest.raises(Exception, match="Phone is empty"):
            customersDB.createCustomerDB(mock_customer)

    def test_extract_names(self):
        assert customersDB.extract_names("John Doe") == ("John", "Doe")
        assert customersDB.extract_names("John") == ("John", "")
        assert customersDB.extract_names("John Fitzgerald Kennedy") == ("John", "Kennedy")

    @patch('app.data.customersDB.database.get_connection')
    def test_queryAllCustomersDB_no_customers(self, mock_get_connection, mock_connection):
        # Arrange
        conn, cursor = mock_connection
        mock_get_connection.return_value = conn
        cursor.fetchall.return_value = []
        
        # Act
        result = customersDB.queryAllCustomersDB()
        
        # Assert
        assert len(result) == 0
        cursor.execute.assert_called_once()
        cursor.close.assert_called_once()
        conn.close.assert_called_once()

    @patch('app.data.customersDB.database.get_connection')
    def test_queryCustomerByNameAndPhoneDB_not_found(self, mock_get_connection, mock_connection):
        # Arrange
        conn, cursor = mock_connection
        mock_get_connection.return_value = conn
        cursor.fetchall.return_value = []
        
        # Act
        result = customersDB.queryCustomerByNameAndPhoneDB("Non Existent", "123")
        
        # Assert
        assert len(result) == 0
        cursor.execute.assert_called_once()
        cursor.close.assert_called_once()
        conn.close.assert_called_once()
