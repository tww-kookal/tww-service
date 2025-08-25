import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.routers.customers import router

@pytest.fixture
def test_client():
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)

@pytest.fixture
def mock_authorized_admin():
    return {'user_name': 'admin', 'roles': ['admin']}

@pytest.fixture
def mock_authorized_manager():
    return {'user_name': 'manager', 'roles': ['manager']}

@pytest.fixture
def sample_customer():
    return {
        'customer_id': '1',
        'customer_name': 'John Doe',
        'phone': '1234567890',
        'email': 'john@example.com',
        'city': 'City',
        'area': 'Area',
        'state': 'State',
        'country': 'Country',
        'zip_code': '12345'
    }

def test_get_all_customers_success(test_client):
    with patch('app.auth.authorizedUser', return_value=lambda: {'user_name': 'admin', 'roles': ['admin']}):
        with patch('app.biz.customersHelper.getAllCustomers', return_value=[{'customer_id': '1'}]) as mock_get_all:
            response = test_client.get('/api/v1/customers/')
            assert response.status_code == 200
            assert response.json()['message'] == 'Customers retrieved successfully'
            assert isinstance(response.json()['customers'], list)
            mock_get_all.assert_called_once()

def test_get_all_customers_error(test_client):
    with patch('app.auth.authorizedUser', return_value=lambda: {'user_name': 'admin', 'roles': ['admin']}):
        with patch('app.biz.customersHelper.getAllCustomers', side_effect=Exception('DB Error')):
            response = test_client.get('/api/v1/customers/')
            assert response.status_code == 500
            assert response.json()['detail'] == 'Unable to retrieve customers, check logs'

def test_get_customer_by_id_success(test_client):
    with patch('app.auth.authorizedUser', return_value=lambda: {'user_name': 'admin', 'roles': ['admin']}):
        with patch('app.biz.customersHelper.getCustomerByID', return_value={'customer_id': '1'}) as mock_get:
            response = test_client.get('/api/v1/customers/byID/1')
            assert response.status_code == 200
            assert response.json()['message'] == 'Customer retrieved successfully'
            assert response.json()['customer']['customer_id'] == '1'
            mock_get.assert_called_once_with(1)

def test_get_customer_by_id_error(test_client):
    with patch('app.auth.authorizedUser', return_value=lambda: {'user_name': 'admin', 'roles': ['admin']}):
        with patch('app.biz.customersHelper.getCustomerByID', side_effect=Exception('DB Error')):
            response = test_client.get('/api/v1/customers/byID/1')
            assert response.status_code == 500
            assert response.json()['detail'] == 'Unable to retrieve customer, check logs'

def test_create_customer_success(test_client, sample_customer):
    with patch('app.auth.authorizedUser', return_value=lambda: {'user_name': 'admin', 'roles': ['admin']}):
        with patch('app.biz.customersHelper.createCustomer', return_value=sample_customer) as mock_create:
            response = test_client.post('/api/v1/customers/create', json=sample_customer)
            assert response.status_code == 200
            assert response.json()['message'] == 'Customer created successfully'
            assert response.json()['customer']['customer_id'] == '1'
            mock_create.assert_called_once()

def test_create_customer_error(test_client, sample_customer):
    with patch('app.auth.authorizedUser', return_value=lambda: {'user_name': 'admin', 'roles': ['admin']}):
        with patch('app.biz.customersHelper.createCustomer', side_effect=Exception('DB Error')):
            with patch('app.routers.customers.logger') as mock_logger:
                response = test_client.post('/api/v1/customers/create', json=sample_customer)
                assert response.status_code == 500
                assert response.json()['detail'] == 'Not able to create the customer'
                mock_logger.error.assert_called_once()

def test_update_customer_success(test_client, sample_customer):
    with patch('app.auth.authorizedUser', return_value=lambda: {'user_name': 'admin', 'roles': ['admin']}):
        with patch('app.biz.customersHelper.updateCustomer', return_value=sample_customer) as mock_update:
            response = test_client.post('/api/v1/customers/update', json=sample_customer)
            assert response.status_code == 200
            assert response.json()['message'] == 'Customer updated successfully'
            assert response.json()['customer']['customer_id'] == '1'
            mock_update.assert_called_once()

def test_update_customer_error(test_client, sample_customer):
    with patch('app.auth.authorizedUser', return_value=lambda: {'user_name': 'admin', 'roles': ['admin']}):
        with patch('app.biz.customersHelper.updateCustomer', side_effect=Exception('DB Error')):
            with patch('app.routers.customers.logger') as mock_logger:
                response = test_client.post('/api/v1/customers/update', json=sample_customer)
                assert response.status_code == 500
                assert response.json()['detail'] == 'Not able to update the customer'
                mock_logger.error.assert_called_once()