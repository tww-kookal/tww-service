import pytest
from unittest.mock import patch, MagicMock, ANY
from datetime import date
from app.data import accountingDB as data

@patch('app.data.database.get_connection')
def test_listAllAccountingCategories(mock_get_connection):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [{"id": 1, "name": "Category 1"}]

    result = data.listAllAccountingCategories()

    assert result is not None
    mock_cursor.execute.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.data.database.get_connection')
def test_createCommissionPayout(mock_get_connection):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    data.createCommissionPayout({"selected_bookings": [1, 2]})

    mock_cursor.execute.assert_called_once()
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.data.database.get_connection')
def test_insertTransaction(mock_get_connection):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.lastrowid = 1

    transaction = {
        "acc_category_id": 1,
        "acc_entry_amount": 100,
        "acc_entry_date": date.today(),
        "acc_entry_description": "test",
        "created_by": 1,
        "txn_by": 1,
        "paid_by": 1,
        "received_by": 1,
        "received_for_booking_id": 1,
        "payment_type": "cash"
    }
    result = data.insertTransaction(transaction)

    assert result["acc_entry_id"] == 1
    mock_cursor.execute.assert_called_once()
    mock_conn.commit.assert_called_once()

@patch('app.data.database.get_connection')
def test_queryTransactionsSince(mock_get_connection):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [{"id": 1}]

    result = data.queryTransactionsSince(date.today())

    assert result is not None
    mock_cursor.execute.assert_called_once()

@patch('app.data.database.get_connection')
def test_queryPaymentsForBooking(mock_get_connection):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [{"id": 1}]

    result = data.queryPaymentsForBooking(1)

    assert result is not None
    mock_cursor.execute.assert_called_once_with(ANY, (1,))

@patch('app.data.database.get_connection')
def test_updateTransaction(mock_get_connection):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    transaction = {
        "acc_entry_id": 1,
        "acc_category_id": 1,
        "acc_entry_amount": 100,
        "acc_entry_date": date.today(),
        "acc_entry_description": "test",
        "created_by": 1,
        "txn_by": 1,
        "paid_by": 1,
        "received_by": 1,
        "received_for_booking_id": 1,
        "payment_type": "cash"
    }
    data.updateTransaction(transaction)

    mock_cursor.execute.assert_called_once()
    mock_conn.commit.assert_called_once()

@patch('app.data.database.get_connection')
def test_deleteTransaction(mock_get_connection):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    data.deleteTransaction(1)

    mock_cursor.execute.assert_called_once_with(ANY, (1,))
    mock_conn.commit.assert_called_once()

@patch('app.data.database.get_connection')
def test_searchTransactions(mock_get_connection):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [{"id": 1}]

    criteria = {"acc_category_type": "debit"}
    result = data.searchTransactions(criteria)

    assert result is not None
    assert "ac_cat.acc_category_type = 'debit'" in mock_cursor.execute.call_args[0][0]


@patch('app.data.database.get_connection')
def test_listAllAccountingCategories_exception(mock_get_connection):
    mock_get_connection.side_effect = Exception("DB Error")
    with pytest.raises(Exception, match="DB Error"):
        data.listAllAccountingCategories()

@patch('app.data.database.get_connection')
def test_createCommissionPayout_exception(mock_get_connection):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.execute.side_effect = Exception("DB Error")

    with pytest.raises(Exception, match="DB Error"):
        data.createCommissionPayout({"selected_bookings": [1, 2]})
    
    mock_conn.rollback.assert_called_once()

@patch('app.data.database.get_connection')
def test_insertTransaction_exception(mock_get_connection):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.execute.side_effect = Exception("DB Error")

    transaction = {
        "acc_category_id": 1, "acc_entry_amount": 100, "acc_entry_date": date.today(),
        "acc_entry_description": "test", "created_by": 1, "txn_by": 1, "paid_by": 1,
        "received_by": 1, "received_for_booking_id": 1, "payment_type": "cash"
    }
    with pytest.raises(Exception, match="DB Error"):
        data.insertTransaction(transaction)
    
    mock_conn.rollback.assert_called_once()

@patch('app.data.database.get_connection')
def test_insertTransaction_booking_id_edge_cases(mock_get_connection):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.lastrowid = 1

    transaction = {
        "acc_category_id": 1, "acc_entry_amount": 100, "acc_entry_date": date.today(),
        "acc_entry_description": "test", "created_by": 1, "txn_by": 1, "paid_by": 1,
        "received_by": 1, "payment_type": "cash"
    }

    # Test with received_for_booking_id = 0
    transaction["received_for_booking_id"] = 0
    data.insertTransaction(transaction)
    args, _ = mock_cursor.execute.call_args
    assert args[1][8] is None  # received_for_booking_id should be None

@patch('app.data.database.get_connection')
def test_queryTransactionsSince_exception(mock_get_connection):
    mock_get_connection.side_effect = Exception("DB Error")
    with pytest.raises(Exception, match="DB Error"):
        data.queryTransactionsSince(date.today())

@patch('app.data.database.get_connection')
def test_queryPaymentsForBooking_exception(mock_get_connection):
    mock_get_connection.side_effect = Exception("DB Error")
    with pytest.raises(Exception, match="DB Error"):
        data.queryPaymentsForBooking(1)

@patch('app.data.database.get_connection')
def test_updateTransaction_exception(mock_get_connection):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.execute.side_effect = Exception("DB Error")

    transaction = {
        "acc_entry_id": 1, "acc_category_id": 1, "acc_entry_amount": 100,
        "acc_entry_date": date.today(), "acc_entry_description": "test", "created_by": 1,
        "txn_by": 1, "paid_by": 1, "received_by": 1, "received_for_booking_id": 1,
        "payment_type": "cash"
    }
    with pytest.raises(Exception, match="DB Error"):
        data.updateTransaction(transaction)
    
    mock_conn.rollback.assert_called_once()

@patch('app.data.database.get_connection')
def test_deleteTransaction_exception(mock_get_connection):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.execute.side_effect = Exception("DB Error")

    with pytest.raises(Exception, match="DB Error"):
        data.deleteTransaction(1)
    
    mock_conn.rollback.assert_called_once()

@patch('app.data.database.get_connection')
def test_searchTransactions_multiple_criteria(mock_get_connection):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    criteria = {
        "acc_category_type": "credit",
        "transaction_date": "2023-01-01",
        "transaction_end_date": "2023-01-31",
        "paid_by": 1,
        "txn_by": 2,
        "acc_category_id": 3,
        "received_by": 4,
        "booking_id": 5
    }
    data.searchTransactions(criteria)
    
    args, _ = mock_cursor.execute.call_args
    query = args[0]
    params = args[1]

    assert "ac_cat.acc_category_type = 'credit'" in query
    assert "acc_entry_date >= %s" in query
    assert "acc_entry_date <= %s" in query
    assert "paid_by = %s" in query
    assert "txn_by = %s" in query
    assert "a.acc_category_id = %s" in query
    assert "received_by = %s" in query
    assert "received_for_booking_id = %s" in query
    assert params == ("2023-01-01", "2023-01-31", 1, 2, 3, 4, 5)

@patch('app.data.database.get_connection')
def test_searchTransactions_type_transaction(mock_get_connection):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    criteria = {"acc_category_type": "transaction"}
    data.searchTransactions(criteria)
    
    args, _ = mock_cursor.execute.call_args
    assert "ac_cat.acc_category_type like '%'" in args[0]

@patch('app.data.database.get_connection')
def test_searchTransactions_exception(mock_get_connection):
    mock_get_connection.side_effect = Exception("DB Error")
    with pytest.raises(Exception, match="DB Error"):
        data.searchTransactions({"acc_category_type": "debit"})    
