import pytest
from unittest.mock import MagicMock, patch
from app.backend import customersDB

class TestCustomersDBBackend:
    def test_queryAllCustomersDB(self):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            {"customer_id": 1, "customer_name": "Alice"},
            {"customer_id": 2, "customer_name": "Bob"}
        ]
        result = customersDB.queryAllCustomersDB(mock_conn)
        assert len(result) == 2
        assert result[0]["customer_name"] == "Alice"
        mock_cursor.execute.assert_called_once()
        mock_cursor.close.assert_called_once()

    def test_queryCustomerByIDDB(self):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = {"customer_id": 1, "customer_name": "Alice"}
        result = customersDB.queryCustomerByIDDB(1, mock_conn)
        assert result["customer_name"] == "Alice"
        mock_cursor.execute.assert_called_once()
        mock_cursor.close.assert_called_once()

    def test_queryCustomerByNameAndPhoneDB(self):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [{"customer_id": 1, "customer_name": "Alice"}]
        result = customersDB.queryCustomerByNameAndPhoneDB("Alice", "1234567890", mock_conn)
        assert result[0]["customer_name"] == "Alice"
        mock_cursor.execute.assert_called_once()
        mock_cursor.close.assert_called_once()

    @patch('app.backend.customersDB.queryCustomerByNameAndPhoneDB')
    def test_createCustomerDB_duplicate(self, mock_query):
        mock_conn = MagicMock()
        mock_query.return_value = [{"customer_id": 1, "customer_name": "Alice"}]
        customer = {"customer_name": "Alice", "phone": "1234567890"}
        with pytest.raises(Exception) as exc_info:
            customersDB.createCustomerDB(customer, mock_conn)
        assert "Customer Already Exists" in str(exc_info.value)

    @patch('app.backend.customersDB.queryCustomerByNameAndPhoneDB')
    def test_createCustomerDB_success(self, mock_query):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.lastrowid = 42
        mock_query.return_value = []
        customer = {
            "customer_name": "Bob",
            "email": "bob@example.com",
            "phone": "9876543210",
            "area": "Area51",
            "city": "Roswell",
            "state": "NM",
            "country": "USA",
            "zip_code": "12345"
        }
        result = customersDB.createCustomerDB(customer, mock_conn)
        assert result["customer_id"] == 42
        mock_cursor.execute.assert_called_once()
        mock_cursor.close.assert_called_once()

    def test_updateCustomerDB(self):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        customer = {
            "customer_id": 1,
            "customer_name": "Alice",
            "email": "alice@example.com",
            "phone": "1234567890",
            "area": "Area51",
            "city": "Roswell",
            "state": "NM",
            "country": "USA",
            "zip_code": "12345"
        }
        result = customersDB.updateCustomerDB(customer, mock_conn)
        assert result["customer_id"] == 1
        mock_cursor.execute.assert_called_once()
        mock_cursor.close.assert_called_once()