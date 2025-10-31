import pytest
from unittest.mock import patch, MagicMock
from app.data import bookingDB
from datetime import date

@patch('app.data.bookingDB.database.get_connection')
def test_queryAvailableRoomsDB_success(mock_get_conn):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_conn.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [{'room_id': 1}]
    result = bookingDB.queryAvailableRoomsDB('2023-01-01', '2023-01-02', 2, None)
    assert result == [{'room_id': 1}]
    mock_cursor.close.assert_called()
    mock_conn.close.assert_called()

@patch('app.data.bookingDB.database.get_connection')
def test_queryAvailableRoomsDB_with_room_id(mock_get_conn):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_conn.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [{'room_id': 2}]
    result = bookingDB.queryAvailableRoomsDB('2023-01-01', '2023-01-02', 2, 2)
    assert result == [{'room_id': 2}]
    mock_cursor.close.assert_called()
    mock_conn.close.assert_called()

@patch('app.data.bookingDB.database.get_connection')
def test_listBookingsSinceDB_check_in(mock_get_conn):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_conn.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [{'booking_id': 1}]
    result = bookingDB.listBookingsSinceDB(date(2023,1,1), True)
    assert result == [{'booking_id': 1}]
    mock_cursor.close.assert_called()
    mock_conn.close.assert_called()

@patch('app.data.bookingDB.database.get_connection')
def test_listBookingsSinceDB_booking_date(mock_get_conn):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_conn.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [{'booking_id': 2}]
    result = bookingDB.listBookingsSinceDB(date(2023,1,1), False)
    assert result == [{'booking_id': 2}]
    mock_cursor.close.assert_called()
    mock_conn.close.assert_called()

@patch('app.data.bookingDB.database.get_connection')
def test_guestsForDay_success(mock_get_conn):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_conn.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = {'number_of_guests': 5}
    result = bookingDB.guestsForDay(date(2023,1,1))
    assert result == {'number_of_guests': 5}
    mock_cursor.close.assert_called()
    mock_conn.close.assert_called()

@patch('app.data.bookingDB.database.get_connection')
def test_getBookingById_success(mock_get_conn):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_conn.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = {'booking_id': 1}
    result = bookingDB.getBookingById(1)
    assert result == {'booking_id': 1}
    mock_cursor.close.assert_called()
    mock_conn.close.assert_called()

@patch('app.data.bookingDB.database.get_connection')
def test_updateBookingDB_success(mock_get_conn):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_conn.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    booking = {
        "customer_id": 1, "room_id": 1, "number_of_people": 2, "check_in": "2023-01-01", "check_out": "2023-01-02",
        "status": "CONFIRMED", "booking_date": "2023-01-01", "booked_by_id": 1, "source_of_booking_id": 1,
        "room_price": 100, "food_price": 20, "service_price": 10, "tax_percent": 5, "tax_price": 5,
        "discount_price": 0, "total_price": 135, "commission_percent": 10, "commission": 13.5,
        "is_commission_settled": False, "remarks": "", "booking_id": 1
    }
    result = bookingDB.updateBookingDB(booking)
    assert result == booking
    mock_cursor.close.assert_called()
    mock_conn.close.assert_called()

@patch('app.data.bookingDB.database.get_connection')
def test_persistBookingDB_success(mock_get_conn):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_conn.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.lastrowid = 99
    booking = {
        "customer_id": 1, "room_id": 1, "number_of_people": 2, "check_in": "2023-01-01", "check_out": "2023-01-02",
        "status": "CONFIRMED", "booking_date": "2023-01-01", "booked_by_id": 1, "source_of_booking_id": 1,
        "room_price": 100, "food_price": 20, "service_price": 10, "tax_percent": 5, "tax_price": 5,
        "discount_price": 0, "total_price": 135, "commission_percent": 10, "commission": 13.5,
        "is_commission_settled": False, "remarks": ""
    }
    result = bookingDB.persistBookingDB(booking)
    assert result["booking_id"] == 99
    mock_cursor.close.assert_called()
    mock_conn.close.assert_called()

@patch('app.data.bookingDB.database.get_connection')
def test_search_bookings_by_date_range(mock_get_conn):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_conn.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [{'booking_id': 1}]
    
    search_criteria = {'from_date': '2023-01-01', 'to_date': '2023-01-10'}
    result = bookingDB.search_bookings(search_criteria)
    
    assert result == [{'booking_id': 1}]
    mock_cursor.execute.assert_called()
    args, _ = mock_cursor.execute.call_args
    assert "b.check_in BETWEEN %s AND %s" in args[0]
    assert args[1] == ('2023-01-01', '2023-01-10', '2023-01-01', '2023-01-10')
    mock_cursor.close.assert_called()
    mock_conn.close.assert_called()

@patch('app.data.bookingDB.database.get_connection')
def test_search_bookings_by_guest_name(mock_get_conn):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_conn.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [{'booking_id': 2}]

    search_criteria = {'guest_name': 'John Doe'}
    result = bookingDB.search_bookings(search_criteria)

    assert result == [{'booking_id': 2}]
    mock_cursor.execute.assert_called()
    args, _ = mock_cursor.execute.call_args
    assert "CONCAT(c.first_name, ' ', c.last_name) LIKE %s" in args[0]
    assert args[1] == ('%John Doe%',)
    mock_cursor.close.assert_called()
    mock_conn.close.assert_called()

@patch('app.data.bookingDB.database.get_connection')
def test_search_bookings_by_source_of_booking(mock_get_conn):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_conn.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [{'booking_id': 3}]

    search_criteria = {'source_of_booking_id': 5}
    result = bookingDB.search_bookings(search_criteria)

    assert result == [{'booking_id': 3}]
    mock_cursor.execute.assert_called()
    args, _ = mock_cursor.execute.call_args
    assert "b.source_of_booking_id = %s" in args[0]
    assert args[1] == (5,)
    mock_cursor.close.assert_called()
    mock_conn.close.assert_called()

@patch('app.data.bookingDB.database.get_connection')
def test_search_bookings_by_guest_phone(mock_get_conn):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_conn.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [{'booking_id': 4}]

    search_criteria = {'guest_phone': '12345'}
    result = bookingDB.search_bookings(search_criteria)

    assert result == [{'booking_id': 4}]
    mock_cursor.execute.assert_called()
    args, _ = mock_cursor.execute.call_args
    assert "c.phone LIKE %s" in args[0]
    assert args[1] == ('%12345%',)
    mock_cursor.close.assert_called()
    mock_conn.close.assert_called()

@patch('app.data.bookingDB.database.get_connection')
def test_search_bookings_by_commission_settled_false(mock_get_conn):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_conn.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [{'booking_id': 5}]

    search_criteria = {'is_commission_settled': False}
    result = bookingDB.search_bookings(search_criteria)

    assert result == [{'booking_id': 5}]
    mock_cursor.execute.assert_called()
    args, _ = mock_cursor.execute.call_args
    assert "b.is_commission_settled = %s" in args[0]
    assert args[1] == (0,)
    mock_cursor.close.assert_called()
    mock_conn.close.assert_called()

@patch('app.data.bookingDB.database.get_connection')
def test_search_bookings_by_commission_settled_true(mock_get_conn):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_conn.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [{'booking_id': 6}]

    search_criteria = {'is_commission_settled': True}
    result = bookingDB.search_bookings(search_criteria)

    assert result == [{'booking_id': 6}]
    mock_cursor.execute.assert_called()
    args, _ = mock_cursor.execute.call_args
    assert "b.is_commission_settled = %s" in args[0]
    assert args[1] == (1,)
    mock_cursor.close.assert_called()
    mock_conn.close.assert_called()

@patch('app.data.bookingDB.database.get_connection')
def test_search_bookings_exception(mock_get_conn):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_conn.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.execute.side_effect = Exception("DB Error")

    with pytest.raises(Exception, match="DB Error"):
        bookingDB.search_bookings({'guest_name': 'John Doe'})
    
    mock_cursor.close.assert_called()
    mock_conn.close.assert_called()

@patch('app.data.bookingDB.database.get_connection')
def test_updateBookingDB_exception(mock_get_conn):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_conn.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.execute.side_effect = Exception("DB Error")
    
    booking = {
        "customer_id": 1, "room_id": 1, "number_of_people": 2, "check_in": "2023-01-01", "check_out": "2023-01-02",
        "status": "CONFIRMED", "booking_date": "2023-01-01", "booked_by_id": 1, "source_of_booking_id": 1,
        "room_price": 100, "food_price": 20, "service_price": 10, "tax_percent": 5, "tax_price": 5,
        "discount_price": 0, "total_price": 135, "commission_percent": 10, "commission": 13.5,
        "is_commission_settled": False, "remarks": "", "booking_id": 1
    }

    with pytest.raises(Exception, match="DB Error"):
        bookingDB.updateBookingDB(booking)
    
    mock_cursor.close.assert_called()
    mock_conn.close.assert_called()

@patch('app.data.bookingDB.database.get_connection')
def test_persistBookingDB_exception(mock_get_conn):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_conn.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.execute.side_effect = Exception("DB Error")
    
    booking = {
        "customer_id": 1, "room_id": 1, "number_of_people": 2, "check_in": "2023-01-01", "check_out": "2023-01-02",
        "status": "CONFIRMED", "booking_date": "2023-01-01", "booked_by_id": 1, "source_of_booking_id": 1,
        "room_price": 100, "food_price": 20, "service_price": 10, "tax_percent": 5, "tax_price": 5,
        "discount_price": 0, "total_price": 135, "commission_percent": 10, "commission": 13.5,
        "is_commission_settled": False, "remarks": ""
    }

    with pytest.raises(Exception, match="DB Error"):
        bookingDB.persistBookingDB(booking)
    
    mock_cursor.close.assert_called()
    mock_conn.close.assert_called()    