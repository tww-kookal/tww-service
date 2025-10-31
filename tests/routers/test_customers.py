import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.routers import customers
from app.biz import customersHelper
from fastapi.routing import APIRoute

@pytest.fixture
def test_client():
    app = FastAPI()
    app.include_router(customers.router)

    def override_authorized_user():
        return {"user_name": "admin", "roles": ["admin", "manager"]}

    for route in app.routes:
        if isinstance(route, APIRoute):
            # This check is to avoid trying to override dependencies on routes that don't have them
            if any(dep.name == "authorized_user" for dep in route.dependant.dependencies):
                # Find the actual dependency callable to override
                for dep in route.dependant.dependencies:
                    if dep.name == "authorized_user":
                        app.dependency_overrides[dep.call] = override_authorized_user
                        break

    return TestClient(app)

@pytest.fixture
def sample_customer():
    return {
        "customer_id": "1",
        "customer_name": "John Doe",
        "user_type": "standard",
        "phone": "1234567890",
        "email": "john@example.com",
        "city": "City",
        "area": "Area",
        "state": "State",
        "country": "Country",
        "zip_code": "12345"
    }

def test_get_all_customers_success(test_client):
    with patch.object(customersHelper, "getAllCustomers", return_value=[{"customer_id": "1"}]) as mock_get_all:
        response = test_client.get("/api/v1/customers/")
        assert response.status_code == 200
        assert response.json()["message"] == "Customers retrieved successfully"
        assert isinstance(response.json()["customers"], list)
        mock_get_all.assert_called_once()

def test_get_all_customers_error(test_client):
    with patch.object(customersHelper, "getAllCustomers", side_effect=Exception("DB Error")):
        response = test_client.get("/api/v1/customers/")
        assert response.status_code == 500
        assert response.json()["detail"] == "Unable to retrieve customers, check logs"

def test_get_customer_by_id_success(test_client):
    with patch.object(customersHelper, "getCustomerByID", return_value={"customer_id": "1"}) as mock_get:
        response = test_client.get("/api/v1/customers/byID/1")
        assert response.status_code == 200
        assert response.json()["message"] == "Customer retrieved successfully"
        assert response.json()["customer"]["customer_id"] == "1"
        mock_get.assert_called_once_with(1)

def test_get_customer_by_id_error(test_client):
    with patch.object(customersHelper, "getCustomerByID", side_effect=Exception("DB Error")):
        response = test_client.get("/api/v1/customers/byID/1")
        assert response.status_code == 500
        assert response.json()["detail"] == "Unable to retrieve customer, check logs"

def test_create_customer_success(test_client, sample_customer):
    with patch.object(customersHelper, "createCustomer", return_value=sample_customer) as mock_create:
        response = test_client.post("/api/v1/customers/create", json=sample_customer)
        assert response.status_code == 200
        assert response.json()["message"] == "Customer created successfully"
        assert response.json()["customer"]["customer_id"] == "1"
        mock_create.assert_called_once_with(sample_customer)

def test_create_customer_error(test_client, sample_customer):
    with patch.object(customersHelper, "createCustomer", side_effect=Exception("DB Error")):
        with patch("app.routers.customers.logger") as mock_logger:
            response = test_client.post("/api/v1/customers/create", json=sample_customer)
            assert response.status_code == 500
            assert response.json()["detail"] == "Not able to create the customer"
            mock_logger.error.assert_called_once()

def test_update_customer_success(test_client, sample_customer):
    with patch.object(customersHelper, "updateCustomer", return_value=sample_customer) as mock_update:
        response = test_client.post("/api/v1/customers/update", json=sample_customer)
        assert response.status_code == 200
        assert response.json()["message"] == "Customer updated successfully"
        assert response.json()["customer"]["customer_id"] == "1"
        mock_update.assert_called_once_with(sample_customer)

def test_update_customer_error(test_client, sample_customer):
    with patch.object(customersHelper, "updateCustomer", side_effect=Exception("DB Error")):
        with patch("app.routers.customers.logger") as mock_logger:
            response = test_client.post("/api/v1/customers/update", json=sample_customer)
            assert response.status_code == 500
            assert response.json()["detail"] == "Not able to update the customer"
            mock_logger.error.assert_called_once()