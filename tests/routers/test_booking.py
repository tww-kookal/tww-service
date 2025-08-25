import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from datetime import date
from app.routers.booking import router
from app.biz import BizExceptions, bookingHelper

@pytest.fixture
def test_client():
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)

@pytest.fixture
def mock_authorized_user():
    return {
        'user_name': 'agent1',
        'roles': ['agent']
    }

@pytest.fixture
def sample_booking():
    return {
        'booked_by_id': 1,
        'booking_id': 1,
        'room_id': 101,
        'customer_id': 201,
        'booking_date': date(2024, 1, 1),
        'check_in': date(2024, 1, 15),
        'check_out': date(2024, 1, 20),
        'number_of_people': 2,
        'number_of_nights': 5,
        'status': 'confirmed',
        'source_of_booking_id': 1,
        'room_price': 1000.0,
        'food_price': 200.0,
        'service_price': 100.0,
        'tax_percent': 10.0,
        'tax_price': 130.0,
        'discount_price': 0.0,
        'total_price': 1430.0,
        'commission_percent': 5.0,
        'commission': 71.5,
        'is_commission_settled': False,
        'remarks': 'Test booking'
    }

def test_check_room_availability_success(test_client):
    with patch('app.auth.authorizedUser', return_value=lambda: {'user_name': 'agent1', 'roles': ['agent']}):
        with patch('app.biz.bookingHelper.getAvailableRooms') as mock_get_rooms:
            mock_get_rooms.return_value = [
                {'room_id': 101, 'room_name': 'Deluxe Room', 'capacity': 2}
            ]
            response = test_client.get(
                '/api/v1/booking/checkRoomAvailability',
                params={
                    'check_in_date': '2024-01-15',
                    'check_out_date': '2024-01-20',
                    'number_of_people': 2
                }
            )
            
            assert response.status_code == 200
            assert len(response.json()['available_rooms']) == 1

def test_check_room_availability_unauthorized(test_client):
    with patch('app.auth.authorizedUser', side_effect=Exception('Unauthorized')):
        response = test_client.get(
            '/api/v1/booking/checkRoomAvailability',
            params={
                'check_in_date': '2024-01-15',
                'check_out_date': '2024-01-20',
                'number_of_people': 2
            }
        )
        assert response.status_code == 401

def test_create_booking_success(test_client, sample_booking):
    with patch('app.auth.authorizedUser', return_value=lambda: {'user_name': 'agent1', 'roles': ['agent']}):
        with patch('app.biz.bookingHelper.bookRoom', return_value=sample_booking) as mock_book:
            response = test_client.post(
                '/api/v1/booking/createBooking',
                json=sample_booking
            )
            
            assert response.status_code == 200
            assert response.json()['message'] == 'Room booked successfully'
            mock_book.assert_called_once()

def test_create_booking_room_not_available(test_client, sample_booking):
    with patch('app.auth.authorizedUser', return_value=lambda: {'user_name': 'agent1', 'roles': ['agent']}):
        with patch('app.biz.bookingHelper.bookRoom', side_effect=bookingHelper.RoomNotAvailableException()):
            with patch('app.routers.booking.logger') as mock_logger:
                response = test_client.post(
                    '/api/v1/booking/createBooking',
                    json=sample_booking
                )
                
                assert response.status_code == 400
                assert response.json()['detail'] == 'Room Not Available'
                mock_logger.error.assert_called_once()

def test_update_booking_success(test_client, sample_booking):
    with patch('app.auth.authorizedUser', return_value=lambda: {'user_name': 'agent1', 'roles': ['agent']}):
        with patch('app.biz.bookingHelper.bookRoom', return_value=sample_booking) as mock_update:
            response = test_client.post(
                '/api/v1/booking/updateBooking',
                json=sample_booking
            )
            
            assert response.status_code == 200
            assert response.json()['message'] == 'Booking updated successfully'
            mock_update.assert_called_once()

def test_list_bookings_by_check_in_date(test_client):
    with patch('app.auth.authorizedUser', return_value=lambda: {'user_name': 'manager1', 'roles': ['manager']}):
        with patch('app.biz.bookingHelper.listBookingsSince') as mock_list:
            mock_list.return_value = [{'booking_id': 1}]
            response = test_client.get('/api/v1/booking/listBookingsByCheckInDate/2024-01-15')
            
            assert response.status_code == 200
            assert len(response.json()['bookings']) == 1

def test_list_all_bookings(test_client):
    with patch('app.auth.authorizedUser', return_value=lambda: {'user_name': 'manager1', 'roles': ['manager']}):
        with patch('app.biz.bookingHelper.listBookingsSince') as mock_list:
            mock_list.return_value = [{'booking_id': 1}, {'booking_id': 2}]
            response = test_client.get('/api/v1/booking/listAllBookings')
            
            assert response.status_code == 200
            assert len(response.json()['bookings']) == 2

def test_get_booking_by_id_success(test_client, sample_booking):
    with patch('app.auth.authorizedUser', return_value=lambda: {'user_name': 'manager1', 'roles': ['manager']}):
        with patch('app.biz.bookingHelper.getBookingByID', return_value=sample_booking) as mock_get:
            response = test_client.get('/api/v1/booking/byID/1')
            
            assert response.status_code == 200
            assert response.json()['booking']['booking_id'] == 1

def test_get_booking_by_id_not_found(test_client):
    with patch('app.auth.authorizedUser', return_value=lambda: {'user_name': 'manager1', 'roles': ['manager']}):
        with patch('app.biz.bookingHelper.getBookingByID', side_effect=bookingHelper.BookingNotFoundException()):
            with patch('app.routers.booking.logger') as mock_logger:
                response = test_client.get('/api/v1/booking/byID/999')
                
                assert response.status_code == 404
                assert response.json()['detail'] == 'Booking Not Found'
                mock_logger.error.assert_called_once()

def test_guests_for_day(test_client):
    with patch('app.auth.authorizedUser', return_value=lambda: {'user_name': 'manager1', 'roles': ['manager']}):
        with patch('app.biz.bookingHelper.guestsForDay') as mock_guests:
            mock_guests.return_value = {'total_guests': 10, 'bookings': []}
            response = test_client.get('/api/v1/booking/guestsForDay/2024-01-15')
            
            assert response.status_code == 200
            assert response.json()['total_guests'] == 10