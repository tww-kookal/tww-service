import pytest
from unittest.mock import patch, MagicMock
from app.biz import customersHelper

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

@patch('app.biz.customersHelper.customersDB')
class TestCustomersHelper:
    
    def test_getAllCustomers_success(self, mock_customersDB):
        # Arrange
        expected_customers = [mock_customer()]
        mock_customersDB.queryAllCustomersDB.return_value = expected_customers
        
        # Act
        result = customersHelper.getAllCustomers()
        
        # Assert
        assert result == expected_customers
        mock_customersDB.queryAllCustomersDB.assert_called_once()
    
    def test_getAllCustomers_exception(self, mock_customersDB):
        # Arrange
        mock_customersDB.queryAllCustomersDB.side_effect = Exception("Database error")
        
        # Act
        result = customersHelper.getAllCustomers()
        
        # Assert
        assert result == []
    
    def test_createCustomer_success(self, mock_customersDB, mock_customer):
        # Arrange
        mock_customersDB.createCustomerDB.return_value = 1  # customer_id
        
        # Act
        result = customersHelper.createCustomer(mock_customer)
        
        # Assert
        assert result == 1
        mock_customersDB.createCustomerDB.assert_called_once_with(mock_customer)
    
    def test_createCustomer_exception(self, mock_customersDB, mock_customer):
        # Arrange
        mock_customersDB.createCustomerDB.side_effect = Exception("Database error")
        
        # Act & Assert
        with pytest.raises(Exception):
            customersHelper.createCustomer(mock_customer)
    
    def test_getCustomerByName_success(self, mock_customersDB, mock_customer):
        # Arrange
        mock_customersDB.queryCustomerByNameDB.return_value = mock_customer
        
        # Act
        result = customersHelper.getCustomerByName("Test Customer")
        
        # Assert
        assert result == mock_customer
        mock_customersDB.queryCustomerByNameDB.assert_called_once_with("Test Customer")
    
    def test_getCustomerByName_exception(self, mock_customersDB):
        # Arrange
        mock_customersDB.queryCustomerByNameDB.side_effect = Exception("Database error")
        
        # Act
        result = customersHelper.getCustomerByName("Test Customer")
        
        # Assert
        assert result is None