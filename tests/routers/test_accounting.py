import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from unittest.mock import patch
from datetime import date

from app.routers.accounting import router


@pytest.fixture
def test_client_factory():
    def _create_client(roles: list[str]):
        app = FastAPI()

        def override_authorized_user():
            return {'user_name': 'testuser', 'roles': roles}

        app.include_router(router)

        for route in app.routes:
            if hasattr(route, "dependant") and route.dependant:
                for dep in route.dependant.dependencies:
                    if dep.call.__qualname__.startswith("authorizedUser"):
                        app.dependency_overrides[dep.call] = override_authorized_user

        return TestClient(app)

    return _create_client

@pytest.fixture
def test_client(test_client_factory):
    return test_client_factory(['manager', 'owner', 'employee'])

@pytest.fixture
def unauthorized_test_client(test_client_factory):
    return test_client_factory([])

@pytest.fixture
def employee_test_client(test_client_factory):
    return test_client_factory(['employee'])

@pytest.fixture
def mock_accounting_helper():
    with patch("app.routers.accounting.helper") as mock:
        yield mock

def test_list_categories(test_client, mock_accounting_helper):
    mock_accounting_helper.getAllAccountingCategories.return_value = [{"id": 1, "name": "Test Category"}]
    response = test_client.get("/api/v1/accounting/categories")
    assert response.status_code == 200
    assert response.json()["categories"] is not None

def test_list_categories_exception(test_client, mock_accounting_helper):
    mock_accounting_helper.getAllAccountingCategories.side_effect = Exception("Generic Error")
    response = test_client.get("/api/v1/accounting/categories")
    assert response.status_code == 500
    assert "Generic Error" in response.json()["detail"]

def test_add_transaction(test_client, mock_accounting_helper):
    transaction_data = {
        "acc_category_id": 1,
        "acc_entry_amount": 100,
        "acc_entry_date": date.today().isoformat(),
        "acc_entry_description": "test",
        "txn_by": 1,
        "paid_by": 1,
        "received_by": 1,
        "received_for_booking_id": 1,
        "payment_type": "cash"
    }
    mock_accounting_helper.createTransaction.return_value = {"id": 1, **transaction_data}
    response = test_client.post("/api/v1/accounting/transaction/add", json=transaction_data)
    assert response.status_code == 200
    assert response.json()["status"] == status.HTTP_201_CREATED

def test_add_transaction_exception(test_client, mock_accounting_helper):
    mock_accounting_helper.createTransaction.side_effect = Exception("Generic Error")
    response = test_client.post("/api/v1/accounting/transaction/add", json={})
    assert response.status_code == 500
    assert "Generic Error" in response.json()["detail"]

def test_update_transaction(test_client, mock_accounting_helper):
    transaction_data = {
        "acc_entry_id": 1,
        "acc_category_id": 1,
        "acc_entry_amount": 150,
        "acc_entry_date": date.today().isoformat(),
        "acc_entry_description": "updated test",
        "txn_by": 1,
        "paid_by": 1,
        "received_by": 1,
        "received_for_booking_id": 1,
        "payment_type": "card"
    }
    mock_accounting_helper.updateTransaction.return_value = transaction_data
    response = test_client.post("/api/v1/accounting/transaction/update", json=transaction_data)
    assert response.status_code == 200
    assert response.json()["status"] == status.HTTP_201_CREATED

def test_update_transaction_exception(test_client, mock_accounting_helper):
    mock_accounting_helper.updateTransaction.side_effect = Exception("Generic Error")
    response = test_client.post("/api/v1/accounting/transaction/update", json={})
    assert response.status_code == 500
    assert "Generic Error" in response.json()["detail"]

def test_delete_transaction(test_client, mock_accounting_helper):
    mock_accounting_helper.deleteTransaction.return_value = {"id": 1}
    response = test_client.post("/api/v1/accounting/transaction/deleteById/1")
    assert response.status_code == 200
    assert response.json()["status"] == status.HTTP_201_CREATED

def test_delete_transaction_exception(test_client, mock_accounting_helper):
    mock_accounting_helper.deleteTransaction.side_effect = Exception("Generic Error")
    response = test_client.post("/api/v1/accounting/transaction/deleteById/1")
    assert response.status_code == 500
    assert "Generic Error" in response.json()["detail"]

def test_list_entries_default(test_client, mock_accounting_helper):
    mock_accounting_helper.getTransactionsSince.return_value = [{"id": 1}]
    response = test_client.get("/api/v1/accounting/transactions")
    assert response.status_code == 200

def test_list_entries_default_exception(test_client, mock_accounting_helper):
    mock_accounting_helper.getTransactionsSince.side_effect = Exception("Generic Error")
    response = test_client.get("/api/v1/accounting/transactions")
    assert response.status_code == 500
    assert "Generic Error" in response.json()["detail"]

def test_list_entries_with_date(test_client, mock_accounting_helper):
    test_date = date.today().isoformat()
    mock_accounting_helper.getTransactionsSince.return_value = [{"id": 1, "date": test_date}]
    response = test_client.get(f"/api/v1/accounting/transactions/{test_date}")
    assert response.status_code == 200

def test_list_entries_with_date_exception(test_client, mock_accounting_helper):
    test_date = date.today().isoformat()
    mock_accounting_helper.getTransactionsSince.side_effect = Exception("Generic Error")
    response = test_client.get(f"/api/v1/accounting/transactions/{test_date}")
    assert response.status_code == 500
    assert "Generic Error" in response.json()["detail"]

def test_list_payments_for_booking(test_client, mock_accounting_helper):
    mock_accounting_helper.getPaymentsForBooking.return_value = [{"id": 1}]
    response = test_client.get("/api/v1/accounting/payment/forBookingID/1")
    assert response.status_code == 200

def test_list_payments_for_booking_exception(test_client, mock_accounting_helper):
    mock_accounting_helper.getPaymentsForBooking.side_effect = Exception("Generic Error")
    response = test_client.get("/api/v1/accounting/payment/forBookingID/1")
    assert response.status_code == 500
    assert "Generic Error" in response.json()["detail"]

def test_search_transactions(test_client, mock_accounting_helper):
    mock_accounting_helper.searchTransactions.return_value = [{"id": 1}]
    response = test_client.post("/api/v1/accounting/transactions/search", json={})
    assert response.status_code == 200

def test_search_transactions_exception(test_client, mock_accounting_helper):
    mock_accounting_helper.searchTransactions.side_effect = Exception("Generic Error")
    response = test_client.post("/api/v1/accounting/transactions/search", json={})
    assert response.status_code == 500
    assert "Generic Error" in response.json()["detail"]

def test_search_expenses(test_client, mock_accounting_helper):
    mock_accounting_helper.searchTransactions.return_value = [{"id": 1}]
    response = test_client.post("/api/v1/accounting/expenses/search", json={})
    assert response.status_code == 200

def test_search_expenses_exception(test_client, mock_accounting_helper):
    mock_accounting_helper.searchTransactions.side_effect = Exception("Generic Error")
    response = test_client.post("/api/v1/accounting/expenses/search", json={})
    assert response.status_code == 500
    assert "Generic Error" in response.json()["detail"]

def test_search_consolidated(test_client, mock_accounting_helper):
    mock_accounting_helper.fetchConsolidatedTransactions.return_value = [{"id": 1}]
    response = test_client.post("/api/v1/accounting/consolidated/search", json={})
    assert response.status_code == 200

def test_search_consolidated_exception(test_client, mock_accounting_helper):
    mock_accounting_helper.fetchConsolidatedTransactions.side_effect = Exception("Generic Error")
    response = test_client.post("/api/v1/accounting/consolidated/search", json={})
    assert response.status_code == 500
    assert "Generic Error" in response.json()["detail"]

def test_add_commission_payout(test_client, mock_accounting_helper):
    mock_accounting_helper.addCommissionPayout.return_value = [{"id": 1}]
    response = test_client.post("/api/v1/accounting/commission-payouts/add", json={"selected_bookings": [1, 2]})
    assert response.status_code == 200

def test_add_commission_payout_exception(test_client, mock_accounting_helper):
    mock_accounting_helper.addCommissionPayout.side_effect = Exception("Unable to add the commission payout")
    response = test_client.post("/api/v1/accounting/commission-payouts/add", json={"selected_bookings": [1, 2]})
    assert response.status_code == 500
    assert "Unable to add the commission payout" in response.json()["detail"]
