import pytest
from fastapi.testclient import TestClient
from app.routers.payments import router
from app.biz import paymentsHelper as helper
from app.biz import BizExceptions as exceptions
from app import auth
from fastapi import status
from datetime import date

client = TestClient(router)

@pytest.fixture
def mock_authorized_user(monkeypatch):
    def mock_auth(*args, **kwargs):
        return lambda: {"user_name": "testuser", "is_authorized": True}
    monkeypatch.setattr(auth, "authorizedUser", mock_auth)

@pytest.fixture
def sample_payment():
    return {
        "booking_id": 1,
        "payment_amount": 100.0,
        "payment_date": str(date.today()),
        "payment_for": "Room Charge",
        "payment_to": 1,
        "payment_type": "Cash",
        "remarks": "Test payment"
    }

def test_add_payment_success(mock_authorized_user, sample_payment, monkeypatch):
    def mock_add_payment(payment_dict, is_update):
        return {**payment_dict, "booking_payments_id": 1}
    monkeypatch.setattr(helper, "addPayment", mock_add_payment)
    
    response = client.post("/api/v1/payment/add", json=sample_payment)
    assert response.status_code == 200
    assert response.json()["status"] == 200
    assert "addedPayment" in response.json()

def test_add_payment_booking_not_found(mock_authorized_user, sample_payment, monkeypatch):
    def mock_add_payment(payment_dict, is_update):
        raise exceptions.BookingNotFoundException("Booking not found")
    monkeypatch.setattr(helper, "addPayment", mock_add_payment)
    
    response = client.post("/api/v1/payment/add", json=sample_payment)
    assert response.status_code == 400
    assert response.json()["detail"] == "Booking Not Found"

def test_update_payment_success(mock_authorized_user, sample_payment, monkeypatch):
    payment_with_id = {**sample_payment, "booking_payments_id": 1}
    def mock_add_payment(payment_dict, is_update):
        return payment_dict
    monkeypatch.setattr(helper, "addPayment", mock_add_payment)
    
    response = client.post("/api/v1/payment/update", json=payment_with_id)
    assert response.status_code == 200
    assert response.json()["status"] == 200
    assert response.json()["message"] == "Payment updated successfully"

def test_delete_payment_success(mock_authorized_user, monkeypatch):
    def mock_delete_payment(payment_id):
        return True
    monkeypatch.setattr(helper, "deletePayment", mock_delete_payment)
    
    response = client.post("/api/v1/payment/deleteById/1")
    assert response.status_code == 200
    assert response.json()["status"] == 200
    assert response.json()["message"] == "Payment deleted successfully"

def test_get_payments_for_booking_success(mock_authorized_user, monkeypatch):
    def mock_get_payments(booking_id):
        return [{"booking_payments_id": 1, "payment_amount": 100.0}]
    monkeypatch.setattr(helper, "getPaymentsForBooking", mock_get_payments)
    
    response = client.get("/api/v1/payment/forBookingID/1")
    assert response.status_code == 200
    assert response.json()["status"] == 200
    assert len(response.json()["payments"]) > 0
    assert response.json()["booking_id"] == 1