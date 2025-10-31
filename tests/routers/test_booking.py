import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.routers import booking
from app.biz import bookingHelper
from datetime import date, timedelta
from fastapi.routing import APIRoute


@pytest.fixture
def test_client():
    app = FastAPI()
    app.include_router(booking.router)

    def override_authorized_user():
        return {"user_name": "agent1", "roles": ["agent", "manager", "admin", "employee", "owner"]}

    for route in app.routes:
        if isinstance(route, APIRoute):
            for dep in route.dependant.dependencies:
                if dep.name == "authorized_user":
                    app.dependency_overrides[dep.call] = override_authorized_user

    return TestClient(app)


@pytest.fixture
def sample_booking_data():
    def convert_dates_to_str(d):
        for k, v in d.items():
            if isinstance(v, date):
                d[k] = v.isoformat()
        return d

    booking = {
        "booked_by_id": 1,
        "booking_id": 1,
        "room_id": 101,
        "customer_id": 1,
        "booking_date": date.today(),
        "check_in": date.today() + timedelta(days=1),
        "check_out": date.today() + timedelta(days=3),
        "number_of_people": 2,
        "number_of_nights": 2,
        "status": "CONFIRMED",
        "source_of_booking_id": 1,
        "room_price": 200.0,
        "food_price": 50.0,
        "service_price": 20.0,
        "tax_percent": 10.0,
        "tax_price": 27.0,
        "discount_price": 0.0,
        "total_price": 297.0,
        "commission_percent": 5.0,
        "commission": 14.85,
        "is_commission_settled": False,
        "remarks": "Test booking",
    }
    return convert_dates_to_str(booking)


def test_check_room_availability_success(test_client):
    with patch.object(bookingHelper, "getAvailableRooms") as mock_get_rooms:
        mock_get_rooms.return_value = [
            {"room_id": 101, "room_name": "Deluxe Room", "capacity": 2}
        ]

        response = test_client.get(
            "/api/v1/booking/checkRoomAvailability",
            params={
                "check_in_date": "2024-01-15",
                "check_out_date": "2024-01-20",
                "number_of_people": 2,
            },
        )

        print(response.json())
        assert response.status_code == 200
        assert len(response.json()["available_rooms"]) == 1
        assert response.json()["available_rooms"][0]["room_name"] == "Deluxe Room"


def test_check_room_availability_no_rooms(test_client):
    with patch.object(bookingHelper, "getAvailableRooms") as mock_get_rooms:
        mock_get_rooms.return_value = []

        response = test_client.get(
            "/api/v1/booking/checkRoomAvailability",
            params={
                "check_in_date": "2024-01-15",
                "check_out_date": "2024-01-20",
                "number_of_people": 2,
            },
        )

        assert response.status_code == 200
        assert len(response.json()["available_rooms"]) == 0


def test_create_booking_success(test_client, sample_booking_data):
    with patch.object(bookingHelper, "bookRoom") as mock_book_room:
        mock_book_room.return_value = sample_booking_data
        response = test_client.post("/api/v1/booking/createBooking", json=sample_booking_data)
        assert response.status_code == 200
        assert response.json()["message"] == "Room booked successfully"
        assert response.json()["booking"] == sample_booking_data


def test_create_booking_room_not_available(test_client, sample_booking_data):
    with patch.object(bookingHelper, "bookRoom", side_effect=bookingHelper.RoomNotAvailableException("No rooms available")):
        response = test_client.post("/api/v1/booking/createBooking", json=sample_booking_data)
        assert response.status_code == 400
        assert response.json()["detail"] == "Room Not Available"


def test_update_booking_success(test_client, sample_booking_data):
    with patch.object(bookingHelper, "bookRoom") as mock_book_room:
        mock_book_room.return_value = sample_booking_data
        response = test_client.post("/api/v1/booking/updateBooking", json=sample_booking_data)
        assert response.status_code == 200
        assert response.json()["message"] == "Booking updated successfully"
        assert response.json()["booking"] == sample_booking_data


def test_get_booking_by_id_success(test_client, sample_booking_data):
    with patch.object(bookingHelper, "getBookingByID") as mock_get_booking:
        mock_get_booking.return_value = sample_booking_data
        response = test_client.get("/api/v1/booking/byID/1")
        assert response.status_code == 200
        assert response.json()["booking"] == sample_booking_data


def test_get_booking_by_id_not_found(test_client):
    with patch.object(bookingHelper, "getBookingByID", side_effect=bookingHelper.BookingNotFoundException("Booking not found")):
        response = test_client.get("/api/v1/booking/byID/999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Booking Not Found"


def test_list_all_bookings_success(test_client, sample_booking_data):
    with patch.object(bookingHelper, "listBookingsSince") as mock_list_bookings:
        mock_list_bookings.return_value = [sample_booking_data]
        response = test_client.get("/api/v1/booking/listAllBookings")
        assert response.status_code == 200
        assert response.json()["bookings"] == [sample_booking_data]


def test_list_bookings_by_check_in_date_success(test_client, sample_booking_data):
    check_in_date = (date.today()).isoformat()
    with patch.object(bookingHelper, "listBookingsSince") as mock_list_bookings:
        mock_list_bookings.return_value = [sample_booking_data]
        response = test_client.get(f"/api/v1/booking/listBookingsByCheckInDate/{check_in_date}")
        assert response.status_code == 200
        assert response.json()["bookings"] == [sample_booking_data]


def test_search_bookings_success(test_client, sample_booking_data):
    search_criteria = {"guest_name": "Test"}
    with patch.object(bookingHelper, "search_bookings") as mock_search:
        mock_search.return_value = [sample_booking_data]
        response = test_client.post("/api/v1/booking/search", json=search_criteria)
        assert response.status_code == 200
        assert response.json()["bookings"] == [sample_booking_data]


def test_guests_for_day_success(test_client):
    for_date = date.today().isoformat()
    with patch.object(bookingHelper, "guestsForDay") as mock_guests:
        mock_guests.return_value = {"guest_count": 5}
        response = test_client.get(f"/api/v1/booking/guestsForDay/{for_date}")
        assert response.status_code == 200
        assert response.json() == {"guest_count": 5}