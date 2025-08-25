import pytest
from unittest.mock import patch, MagicMock
from datetime import date
from app.data import paymentDB

@pytest.fixture
def mock_db_connection():
    with patch('app.data.database.get_connection') as mock_conn:
        mock_cursor = MagicMock()
        mock_conn.return_value.cursor.return_value = mock_cursor
        yield mock_conn, mock_cursor

def test_query_payments_for_booking(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchall.return_value = [
        {
            'booking_payments_id': 1,
            'booking_id': 100,
            'payment_amount': 1000.0,
            'payment_date': date(2024, 1, 1),
            'payment_to': 'vendor',
            'payment_for': 'deposit',
            'remarks': 'Initial payment',
            'payment_type': 'cash'
        }
    ]

    result = paymentDB.queryPaymentsForBooking(100)

    mock_cursor.execute.assert_called_once()
    assert len(result) == 1
    assert result[0]['booking_id'] == 100
    assert result[0]['payment_amount'] == 1000.0
    
    mock_cursor.close.assert_called_once()
    mock_conn.return_value.close.assert_called_once()

def test_persist_payment(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.lastrowid = 1

    payment = {
        'booking_id': 100,
        'payment_amount': 1000.0,
        'payment_date': date(2024, 1, 1),
        'payment_to': 'vendor',
        'payment_type': 'CASH',
        'payment_for': 'DEPOSIT',
        'remarks': 'Initial payment',
        'payment_added_by': 'admin'
    }

    result = paymentDB.persistPaymentDB(payment)

    mock_cursor.execute.assert_called_once()
    mock_conn.return_value.commit.assert_called_once()
    assert result['booking_payments_id'] == 1
    assert result['payment_type'].lower() == 'cash'
    assert result['payment_for'].lower() == 'deposit'

    mock_cursor.close.assert_called_once()
    mock_conn.return_value.close.assert_called_once()

def test_update_payment(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection

    payment = {
        'booking_payments_id': 1,
        'booking_id': 100,
        'payment_amount': 1500.0,
        'payment_date': date(2024, 1, 2),
        'payment_to': 'vendor',
        'payment_type': 'BANK',
        'payment_for': 'FINAL',
        'remarks': 'Final payment',
        'payment_added_by': 'admin'
    }

    result = paymentDB.updatePaymentDB(payment)

    mock_cursor.execute.assert_called_once()
    mock_conn.return_value.commit.assert_called_once()
    assert result['payment_amount'] == 1500.0
    assert result['payment_type'].lower() == 'bank'
    assert result['payment_for'].lower() == 'final'

    mock_cursor.close.assert_called_once()
    mock_conn.return_value.close.assert_called_once()

def test_delete_payment(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection

    result = paymentDB.deletePaymentDB(1)

    mock_cursor.execute.assert_called_once()
    mock_conn.return_value.commit.assert_called_once()
    assert result is True

    mock_cursor.close.assert_called_once()
    mock_conn.return_value.close.assert_called_once()

def test_query_payments_handles_empty_result(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchall.return_value = []

    result = paymentDB.queryPaymentsForBooking(100)

    assert len(result) == 0
    mock_cursor.close.assert_called_once()
    mock_conn.return_value.close.assert_called_once()

def test_persist_payment_handles_error(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.execute.side_effect = Exception('Database error')

    payment = {
        'booking_id': 100,
        'payment_amount': 1000.0,
        'payment_date': date(2024, 1, 1),
        'payment_to': 'vendor',
        'payment_type': 'CASH',
        'payment_for': 'DEPOSIT',
        'remarks': 'Initial payment',
        'payment_added_by': 'admin'
    }

    with pytest.raises(Exception):
        paymentDB.persistPaymentDB(payment)

    mock_cursor.close.assert_called_once()
    mock_conn.return_value.close.assert_called_once()
    mock_conn.return_value.commit.assert_not_called()