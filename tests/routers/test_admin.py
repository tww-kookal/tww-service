import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from datetime import timedelta
from app.routers.admin import router
from app.config import config

@pytest.fixture
def test_client():
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)

@pytest.fixture
def mock_user():
    return {
        'user_id': 1,
        'username': 'admin',
        'first_name': 'Admin',
        'last_name': 'User',
        'email': 'admin@example.com',
        'phone': '1234567890',
        'booking_commission': 10
    }

def test_login_success(test_client, mock_user):
    with patch('app.biz.usersHelper.queryUser', return_value=mock_user) as mock_query:
        with patch('app.biz.usersHelper.validateUser', return_value=True) as mock_validate:
            with patch('app.utils.create_access_token', return_value='test_token') as mock_token:
                response = test_client.post(
                    '/login',
                    data={'username': 'admin', 'password': 'password'}
                )
                
                assert response.status_code == 200
                assert response.json() == {
                    'access_token': 'test_token',
                    'token_type': 'bearer'
                }
                mock_query.assert_called_once_with('admin')
                mock_validate.assert_called_once()
                mock_token.assert_called_once()

def test_login_invalid_credentials(test_client, mock_user):
    with patch('app.biz.usersHelper.queryUser', return_value=mock_user):
        with patch('app.biz.usersHelper.validateUser', return_value=False):
            response = test_client.post(
                '/login',
                data={'username': 'admin', 'password': 'wrong_password'}
            )
            
            assert response.status_code == 400
            assert response.json()['detail'] == 'Invalid credentials'

def test_login_user_not_found(test_client):
    with patch('app.biz.usersHelper.queryUser', return_value=None):
        with patch('app.biz.usersHelper.validateUser', return_value=False):
            response = test_client.post(
                '/login',
                data={'username': 'nonexistent', 'password': 'password'}
            )
            
            assert response.status_code == 400
            assert response.json()['detail'] == 'Invalid credentials'

@pytest.fixture
def mock_authorized_admin():
    return {
        'username': 'admin',
        'roles': ['admin']
    }

def test_execute_script_success(test_client, mock_authorized_admin):
    with patch('app.auth.authorizedUser', return_value=lambda: mock_authorized_admin):
        with patch('app.biz.adminHelper.execute', return_value=True):
            response = test_client.post(
                '/execute',
                json={'query': 'SELECT * FROM test'}
            )
            
            assert response.status_code == 200
            assert response.json() == {
                'status': 200,
                'message': 'Success'
            }

def test_execute_script_unauthorized(test_client):
    with patch('app.auth.authorizedUser', side_effect=Exception('Unauthorized')):
        response = test_client.post(
            '/execute',
            json={'query': 'SELECT * FROM test'}
        )
        
        assert response.status_code == 401

def test_execute_script_error(test_client, mock_authorized_admin):
    with patch('app.auth.authorizedUser', return_value=lambda: mock_authorized_admin):
        with patch('app.biz.adminHelper.execute', side_effect=Exception('Database error')):
            with patch('app.routers.admin.logger') as mock_logger:
                response = test_client.post(
                    '/execute',
                    json={'query': 'INVALID QUERY'}
                )
                
                assert response.status_code == 500
                assert response.json()['detail'] == 'Not able to execute the string'
                mock_logger.error.assert_called_once()