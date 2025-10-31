import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from datetime import date

from app.routers.payments import router
from app.biz import paymentsHelper as helper
from app.biz import BizExceptions as exceptions
from app import auth

# Define the dependency that will be overridden.
dependency_to_override = auth.authorizedUser

@pytest.fixture
def test_client_factory():
    def _create_client(roles: list[str]):
        app = FastAPI()

        # Create the override
        def override_authorized_user():
            return {'user_name': 'testuser', 'roles': roles}

        # Include the router first
        app.include_router(router)

        # Now apply overrides for each dependency call inside router
        for route in app.routes:
            if hasattr(route, "dependant") and route.dependant:
                for dep in route.dependant.dependencies:
                    if dep.call.__qualname__.startswith("authorizedUser"):
                        app.dependency_overrides[dep.call] = override_authorized_user

        return TestClient(app)

    return _create_client

@pytest.fixture
def test_client(test_client_factory):
    """Provides a default test client with a user having all necessary roles."""
    return test_client_factory(['manager', 'owner', 'admin', 'agent'])

@pytest.fixture
def sample_payment():
    """Provides a sample payment payload for tests."""
    return {
        "booking_id": 1,
        "payment_amount": 100.0,
        "payment_date": date.today().isoformat(),  # Use ISO format for date validation.
        "payment_for": "Room Charge",
        "payment_to": 1,
        "payment_type": "Cash",
        "remarks": "Test payment"
    }

def test_add_payment_success(test_client, sample_payment, monkeypatch):
    monkeypatch.setattr(helper, "addPayment", lambda payment_dict, is_update: {**payment_dict, "booking_payments_id": 1})
    
    response = test_client.post("/api/v1/payment/add", json=sample_payment)
    
    assert response.status_code == 200
    assert response.json()["status"] == 200
    assert "addedPayment" in response.json()

def test_add_payment_booking_not_found(test_client, sample_payment, monkeypatch):
    monkeypatch.setattr(helper, "addPayment", lambda payment_dict, is_update: (_ for _ in ()).throw(exceptions.BookingNotFoundException("Booking not found")))
    
    response = test_client.post("/api/v1/payment/add", json=sample_payment)
    
    assert response.status_code == 400
    assert response.json()["detail"] == "Booking Not Found"

def test_update_payment_success(test_client, sample_payment, monkeypatch):
    payment_with_id = {**sample_payment, "booking_payments_id": 1}
    monkeypatch.setattr(helper, "addPayment", lambda payment_dict, is_update: payment_dict)
    
    response = test_client.post("/api/v1/payment/update", json=payment_with_id)
    
    assert response.status_code == 200
    assert response.json()["status"] == 200
    assert response.json()["message"] == "Payment updated successfully"

def test_delete_payment_success(test_client, monkeypatch):
    monkeypatch.setattr(helper, "deletePayment", lambda payment_id: True)
    
    response = test_client.post("/api/v1/payment/deleteById/1")
    
    assert response.status_code == 200
    assert response.json()["status"] == 200
    assert response.json()["message"] == "Payment deleted successfully"

def test_get_payments_for_booking_success(test_client, monkeypatch):
    monkeypatch.setattr(helper, "getPaymentsForBooking", lambda booking_id: [{"booking_payments_id": 1, "payment_amount": 100.0}])
    
    response = test_client.get("/api/v1/payment/forBookingID/1")
    
    assert response.status_code == 200
    assert response.json()["status"] == 200
    assert len(response.json()["payments"]) > 0
    assert response.json()["booking_id"] == 1