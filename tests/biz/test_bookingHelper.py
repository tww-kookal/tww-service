import pytest
from unittest.mock import patch
from app.biz import bookingHelper
from app.biz.BizExceptions import CustomerNotAvailableException, RoomNotAvailableException, BookingNotFoundException
from datetime import date

# getAvailableRooms
@patch('app.biz.bookingHelper.bookingDB.queryAvailableRoomsDB')
def test_getAvailableRooms_success(mock_query):
    mock_query.return_value = ['room1', 'room2']
    assert bookingHelper.getAvailableRooms('2023-01-01', '2023-01-02', 2, 1) == ['room1', 'room2']

@patch('app.biz.bookingHelper.bookingDB.queryAvailableRoomsDB')
def test_getAvailableRooms_exception(mock_query):
    mock_query.side_effect = Exception('DB error')
    assert bookingHelper.getAvailableRooms('2023-01-01', '2023-01-02', 2, 1) == []

# getCustomerByID
@patch('app.biz.bookingHelper.customerHelper.getCustomerByID')
def test_getCustomerByID_found(mock_get):
    mock_get.return_value = {'customer_id': 1}
    assert bookingHelper.getCustomerByID(1) == {'customer_id': 1}

@patch('app.biz.bookingHelper.customerHelper.getCustomerByID')
def test_getCustomerByID_not_found(mock_get):
    mock_get.return_value = None
    with pytest.raises(CustomerNotAvailableException):
        bookingHelper.getCustomerByID(1)

# none_if_zero
@pytest.mark.parametrize('value,expected', [(0, None), ('', None), (5, 5)])
def test_none_if_zero(value, expected):
    assert bookingHelper.none_if_zero(value) == expected

# bookRoom (new booking)
@patch('app.biz.bookingHelper.userHelper.getUserByUserName')
@patch('app.biz.bookingHelper.userHelper.getFullNameOfUserByID')
@patch('app.biz.bookingHelper.getSelectedRoom')
@patch('app.biz.bookingHelper.bookingDB.persistBookingDB')
@patch('app.biz.bookingHelper.getCustomerByID')
@patch('app.biz.bookingHelper.roomHelper.getRoomById')
def test_bookRoom_success(mock_room, mock_customer, mock_persist, mock_selected, mock_full_name, mock_user):
    mock_user.return_value = {'user_id': 10}
    mock_full_name.return_value = 'Karthik Ravikumar'
    mock_selected.return_value = {'room_id': 1}
    mock_persist.return_value = {'booked_by_id': 10, 'customer_id': 1, 'room_id': 1}
    mock_customer.return_value = {'customer_name': 'Alice', 'phone': '123'}
    mock_room.return_value = {'room_name': 'Deluxe'}
    booking = {'booked_by': 'user', 'source_of_booking_id': 0, 'check_in': '2023-01-01', 'check_out': '2023-01-02', 'number_of_people': 2, 'room_id': 1, 'customer_id': 1}
    result = bookingHelper.bookRoom(booking)
    assert result['booked_by'] == 'Karthik Ravikumar'
    assert result['customer_name'] == 'Alice'
    assert result['customer_phone'] == '123'
    assert result['room_name'] == 'Deluxe'

@patch('app.biz.bookingHelper.userHelper.getUserByUserName')
@patch('app.biz.bookingHelper.getSelectedRoom')
def test_bookRoom_room_not_available(mock_selected, mock_user):
    mock_user.return_value = {'user_id': 10}
    mock_selected.return_value = None
    booking = {'booked_by': 'user', 'source_of_booking_id': 0, 'check_in': '2023-01-01', 'check_out': '2023-01-02', 'number_of_people': 2, 'room_id': 1}
    with pytest.raises(RoomNotAvailableException):
        bookingHelper.bookRoom(booking)

# bookRoom (update booking)
@patch('app.biz.bookingHelper.userHelper.getUserByUserName')
@patch('app.biz.bookingHelper.bookingDB.getBookingById')
@patch('app.biz.bookingHelper.getSelectedRoom')
@patch('app.biz.bookingHelper.bookingDB.updateBookingDB')
@patch('app.biz.bookingHelper.getCustomerByID')
@patch('app.biz.bookingHelper.roomHelper.getRoomById')
def test_bookRoom_update_success(mock_room, mock_customer, mock_update, mock_selected, mock_get, mock_user):
    mock_user.return_value = {'user_id': 10}
    mock_get.return_value = {'booking_id': 1, 'room_id': 1, 'check_in': '2023-01-01', 'check_out': '2023-01-02'}
    mock_selected.return_value = {'room_id': 1}
    mock_update.return_value = {'booked_by_id': 10, 'customer_id': 20, 'room_id': 1}
    mock_customer.return_value = {'customer_name': 'Bob', 'phone': '456'}
    mock_room.return_value = {'room_name': 'Suite'}
    booking = {'booked_by': 'user', 'source_of_booking_id': 0, 'check_in': '2023-01-01', 'check_out': '2023-01-02', 'number_of_people': 2, 'room_id': 1, 'booking_id': 1, 'customer_id': 20, 'status': 'CONFIRMED'}
    result = bookingHelper.bookRoom(booking, is_update=True)
    assert result['customer_name'] == 'Bob'
    assert result['customer_phone'] == '456'
    assert result['room_name'] == 'Suite'

@patch('app.biz.bookingHelper.bookingDB.search_bookings')
def test_search_bookings_success(mock_search):
    mock_search.return_value = [{'booking_id': 1, 'customer_name': 'Test Customer'}]
    
    search_criteria = {'customer_name': 'Test'}
    result = bookingHelper.search_bookings(search_criteria)
    
    assert len(result) == 1
    assert result[0]['customer_name'] == 'Test Customer'
    mock_search.assert_called_once_with(search_criteria)

@patch('app.biz.bookingHelper.bookingDB.search_bookings', side_effect=Exception("DB Error"))
def test_search_bookings_exception(mock_search):
    search_criteria = {'customer_name': 'Test'}
    result = bookingHelper.search_bookings(search_criteria)
    
    assert result == []
    mock_search.assert_called_once_with(search_criteria)

# listBookingsSince
@patch('app.biz.bookingHelper.bookingDB.listBookingsSinceDB')
def test_listBookingsSince_success(mock_list):
    mock_list.return_value = ['booking1', 'booking2']
    assert bookingHelper.listBookingsSince(date(2023,1,1)) == ['booking1', 'booking2']

@patch('app.biz.bookingHelper.bookingDB.listBookingsSinceDB')
def test_listBookingsSince_exception(mock_list):
    mock_list.side_effect = Exception('DB error')
    assert bookingHelper.listBookingsSince(date(2023,1,1)) == []

# guestsForDay
@patch('app.biz.bookingHelper.bookingDB.guestsForDay')
def test_guestsForDay_success(mock_guests):
    mock_guests.return_value = [5]
    assert bookingHelper.guestsForDay(date(2023,1,1)) == 5

@patch('app.biz.bookingHelper.bookingDB.guestsForDay')
def test_guestsForDay_exception(mock_guests):
    mock_guests.side_effect = Exception('DB error')
    with pytest.raises(Exception):
        bookingHelper.guestsForDay(date(2023,1,1))

# getSelectedRoom
@patch('app.biz.bookingHelper.bookingDB.queryAvailableRoomsDB')
def test_getSelectedRoom_success(mock_query):
    mock_query.return_value = [{'room_id': 1}]
    assert bookingHelper.getSelectedRoom(date(2023,1,1), date(2023,1,2), 2, 1) == {'room_id': 1}

@patch('app.biz.bookingHelper.bookingDB.queryAvailableRoomsDB')
def test_getSelectedRoom_no_rooms(mock_query):
    mock_query.return_value = []
    with pytest.raises(RoomNotAvailableException):
        bookingHelper.getSelectedRoom(date(2023,1,1), date(2023,1,2), 2, 1)

@patch('app.biz.bookingHelper.bookingDB.queryAvailableRoomsDB')
def test_getSelectedRoom_multiple_rooms(mock_query):
    mock_query.return_value = [{'room_id': 1}, {'room_id': 2}]
    with pytest.raises(RoomNotAvailableException):
        bookingHelper.getSelectedRoom(date(2023,1,1), date(2023,1,2), 2, 1)

# getBookingByID
@patch('app.biz.bookingHelper.bookingDB.getBookingById')
@patch('app.biz.bookingHelper.paymentHelper.getPaymentsForBooking')
def test_getBookingByID_success(mock_payments, mock_get):
    mock_get.return_value = {'booking_id': 1}
    mock_payments.return_value = ['payment1']
    result = bookingHelper.getBookingByID(1)
    assert result['payments'] == ['payment1']

@patch('app.biz.bookingHelper.bookingDB.getBookingById')
def test_getBookingByID_not_found(mock_get):
    mock_get.return_value = None
    with pytest.raises(BookingNotFoundException):
        bookingHelper.getBookingByID(1)