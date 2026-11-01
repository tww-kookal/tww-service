import pytest
from unittest.mock import patch, MagicMock
from datetime import date
from app.biz import accounting as helper

@patch('app.biz.accounting.data.listAllAccountingCategories')
def test_getAllAccountingCategories(mock_listAllAccountingCategories):
    mock_listAllAccountingCategories.return_value = [{"id": 1, "name": "Category 1"}]
    result = helper.getAllAccountingCategories()
    assert result is not None
    mock_listAllAccountingCategories.assert_called_once()

@patch('app.biz.accounting.data.listAllAccountingCategories')
def test_getAllAccountingCategories_exception(mock_listAllAccountingCategories):
    mock_listAllAccountingCategories.side_effect = Exception("DB Error")
    with pytest.raises(Exception):
        helper.getAllAccountingCategories()

@patch('app.biz.accounting.userHelper.queryUser')
@patch('app.biz.accounting.data.insertTransaction')
def test_createTransaction(mock_insertTransaction, mock_queryUser):
    mock_queryUser.return_value = {"user_id": 1}
    mock_insertTransaction.return_value = {"id": 1}
    transaction = {"created_by": "testuser", "paid_by": "testpaid"}
    result = helper.createTransaction(transaction)
    assert result is not None
    mock_queryUser.assert_called_once_with("testuser")
    mock_insertTransaction.assert_called_once()

@patch('app.biz.accounting.userHelper.queryUser')
@patch('app.biz.accounting.data.insertTransaction')
def test_createTransaction_with_txn_by(mock_insertTransaction, mock_queryUser):
    mock_queryUser.return_value = {"user_id": 1}
    mock_insertTransaction.return_value = {"id": 1}
    transaction = {"created_by": "testuser", "paid_by": "testpaid", "txn_by": "testtxn"}
    result = helper.createTransaction(transaction)
    assert result is not None
    assert transaction['txn_by'] == "testtxn"

@patch('app.biz.accounting.data.queryTransactionsSince')
def test_getTransactionsSince(mock_queryTransactionsSince):
    mock_queryTransactionsSince.return_value = [{"id": 1, "amount": 100}]
    result = helper.getTransactionsSince()
    assert result is not None
    mock_queryTransactionsSince.assert_called_once()

@patch('app.biz.accounting.data.queryPaymentsForBooking')
def test_getPaymentsForBooking(mock_queryPaymentsForBooking):
    mock_queryPaymentsForBooking.return_value = [{"id": 1, "amount": 100}]
    result = helper.getPaymentsForBooking(1)
    assert result is not None
    mock_queryPaymentsForBooking.assert_called_once_with(1)

@patch('app.biz.accounting.data.deleteTransaction')
def test_deleteTransaction(mock_deleteTransaction):
    mock_deleteTransaction.return_value = None
    helper.deleteTransaction(1)
    mock_deleteTransaction.assert_called_once_with(1)

@patch('app.biz.accounting.data.searchTransactions')
def test_searchTransactions(mock_searchTransactions):
    mock_searchTransactions.return_value = [{"id": 1, "amount": 100}]
    result = helper.searchTransactions({})
    assert result is not None
    mock_searchTransactions.assert_called_once_with({})

@patch('app.biz.accounting.data.searchTransactions')
def test_fetchConsolidatedTransactions(mock_searchTransactions):
    transactions = [
        {"acc_category_type": "debit", "acc_entry_amount": 100},
        {"acc_category_type": "credit", "acc_entry_amount": 200}
    ]
    mock_searchTransactions.return_value = transactions
    result = helper.fetchConsolidatedTransactions({})
    assert result["expenses"] == 100
    assert result["sales"] == 200
    assert result["revenue"] == 100

@patch('app.biz.accounting.data.createCommissionPayout')
@patch('app.biz.accounting.data.insertTransaction')
def test_addCommissionPayout(mock_insertTransaction, mock_createCommissionPayout):
    commission_payout = {
        "selected_bookings": [1, 2],
        "acc_category_id": 1,
        "acc_entry_amount": 100,
        "acc_entry_date": date.today(),
        "acc_entry_description": "test",
        "created_by": "testuser",
        "txn_by": "testtxn",
        "paid_by": "testpaid",
        "received_by": "testreceived",
        "payment_type": "cash"
    }
    helper.addCommissionPayout(commission_payout)
    mock_createCommissionPayout.assert_called_once()
    mock_insertTransaction.assert_called_once()

def test_addCommissionPayout_no_bookings():
    with pytest.raises(Exception, match="No bookings selected for commission payout"):
        helper.addCommissionPayout({"selected_bookings": []})

@patch('app.biz.accounting.userHelper.queryUser')
@patch('app.biz.accounting.data.updateTransaction')
def test_updateTransaction(mock_updateTransaction, mock_queryUser):
    mock_queryUser.return_value = {"user_id": 1}
    mock_updateTransaction.return_value = {"id": 1}
    transaction = {"created_by": "testuser", "paid_by": "testpaid"}
    result = helper.updateTransaction(transaction)
    assert result is not None
    mock_queryUser.assert_called_once_with("testuser")
    mock_updateTransaction.assert_called_once()

@patch('app.biz.accounting.userHelper.queryUser')
def test_createTransaction_exception(mock_queryUser):
    mock_queryUser.side_effect = Exception("User not found")
    with pytest.raises(Exception):
        helper.createTransaction({"created_by": "testuser", "paid_by": "testpaid"})

@patch('app.biz.accounting.userHelper.queryUser')
@patch('app.biz.accounting.data.updateTransaction')
def test_updateTransaction_with_txn_by(mock_updateTransaction, mock_queryUser):
    mock_queryUser.return_value = {"user_id": 1}
    mock_updateTransaction.return_value = {"id": 1}
    transaction = {"created_by": "testuser", "paid_by": "testpaid", "txn_by": "testtxn"}
    result = helper.updateTransaction(transaction)
    assert result is not None
    assert transaction['txn_by'] == "testtxn"

@patch('app.biz.accounting.userHelper.queryUser')
def test_updateTransaction_exception(mock_queryUser):
    mock_queryUser.side_effect = Exception("User not found")
    with pytest.raises(Exception):
        helper.updateTransaction({"created_by": "testuser", "paid_by": "testpaid"})

@patch('app.biz.accounting.data.queryTransactionsSince')
def test_getTransactionsSince_exception(mock_queryTransactionsSince):
    mock_queryTransactionsSince.side_effect = Exception("DB Error")
    with pytest.raises(Exception):
        helper.getTransactionsSince()

@patch('app.biz.accounting.data.queryPaymentsForBooking')
def test_getPaymentsForBooking_exception(mock_queryPaymentsForBooking):
    mock_queryPaymentsForBooking.side_effect = Exception("DB Error")
    with pytest.raises(Exception):
        helper.getPaymentsForBooking(1)

@patch('app.biz.accounting.data.deleteTransaction')
def test_deleteTransaction_exception(mock_deleteTransaction):
    mock_deleteTransaction.side_effect = Exception("DB Error")
    with pytest.raises(Exception):
        helper.deleteTransaction(1)

@patch('app.biz.accounting.data.searchTransactions')
def test_searchTransactions_exception(mock_searchTransactions):
    mock_searchTransactions.side_effect = Exception("DB Error")
    with pytest.raises(Exception):
        helper.searchTransactions({})

@patch('app.biz.accounting.data.searchTransactions')
def test_fetchConsolidatedTransactions_exception(mock_searchTransactions):
    mock_searchTransactions.side_effect = Exception("DB Error")
    with pytest.raises(Exception):
        helper.fetchConsolidatedTransactions({})

@patch('app.biz.accounting.data.createCommissionPayout')
def test_addCommissionPayout_exception(mock_createCommissionPayout):
    mock_createCommissionPayout.side_effect = Exception("DB Error")
    commission_payout = {
        "selected_bookings": [1, 2],
        "acc_category_id": 1,
        "acc_entry_amount": 100,
        "acc_entry_date": date.today(),
        "acc_entry_description": "test",
        "created_by": "testuser",
        "txn_by": "testtxn",
        "paid_by": "testpaid",
        "received_by": "testreceived",
        "payment_type": "cash"
    }
    with pytest.raises(Exception):
        helper.addCommissionPayout(commission_payout)
