import pytest
from unittest.mock import patch, MagicMock
from app.biz import customersHelper

class TestCustomersHelper:
    @patch('app.biz.customersHelper.db.queryAllCustomersDB')
    def test_getAllCustomers_success(self, mock_query):
        mock_query.return_value = [{"customer_id": 1, "customer_name": "Test Customer"}]
        result = customersHelper.getAllCustomers()
        assert isinstance(result, list)
        assert result[0]["customer_id"] == 1

    @patch('app.biz.customersHelper.db.queryAllCustomersDB')
    def test_getAllCustomers_exception(self, mock_query):
        mock_query.side_effect = Exception("DB error")
        result = customersHelper.getAllCustomers()
        assert result == []

    @patch('app.biz.customersHelper.db.queryCustomerByIDDB')
    def test_getCustomerByID_found(self, mock_query):
        mock_query.return_value = {"customer_id": 2, "customer_name": "Found Customer"}
        result = customersHelper.getCustomerByID(2)
        assert result["customer_id"] == 2

    @patch('app.biz.customersHelper.db.queryCustomerByIDDB')
    def test_getCustomerByID_not_found(self, mock_query):
        mock_query.return_value = None
        result = customersHelper.getCustomerByID(99)
        assert result is None

    @patch('app.biz.customersHelper.db.queryCustomerByIDDB')
    def test_getCustomerByID_exception(self, mock_query):
        mock_query.side_effect = Exception("DB error")
        result = customersHelper.getCustomerByID(1)
        assert result is None

    @patch('app.biz.customersHelper.db.createCustomerDB')
    def test_createCustomer_success(self, mock_create):
        mock_create.return_value = 10
        customer = {"customer_name": "New Customer"}
        result = customersHelper.createCustomer(customer)
        assert result == 10

    @patch('app.biz.customersHelper.db.createCustomerDB')
    def test_createCustomer_exception(self, mock_create):
        mock_create.side_effect = Exception("Insert error")
        customer = {"customer_name": "New Customer"}
        with pytest.raises(Exception) as exc:
            customersHelper.createCustomer(customer)
        assert "Not able to create the customer" in str(exc.value)

    @patch('app.biz.customersHelper.db.updateCustomerDB')
    def test_updateCustomer_success(self, mock_update):
        mock_update.return_value = True
        customer = {"customer_name": "Update Customer"}
        result = customersHelper.updateCustomer(customer)
        assert result is True

    @patch('app.biz.customersHelper.db.updateCustomerDB')
    def test_updateCustomer_exception(self, mock_update):
        mock_update.side_effect = Exception("Update error")
        customer = {"customer_name": "Update Customer"}
        with pytest.raises(Exception) as exc:
            customersHelper.updateCustomer(customer)
        assert "Not able to update the customer" in str(exc.value)