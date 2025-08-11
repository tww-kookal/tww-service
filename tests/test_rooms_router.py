import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from datetime import date
from app.main import app

client = TestClient(app)

@pytest.fixture
def mock_room():
    return {
        "room_id": 1,
        "room_name": "Test Room",
        "min_capacity": 2,
        "max_capacity": 4,
        "number_of_beds": 2,
        "number_of_bathrooms": 1
    }

@pytest.fixture
def mock_booking():
    return {
        "booking_id": 1,
        "room_id": 1,
        "check_in": "2023-01-01",
        "check_out": "2023-01-05",
        "number_of_people": 2,
        "customer_name": "Test Customer",
        "booking_date": "2022-12-01",
        "booked_by": "testuser",
        "status": "confirmed",
        "room_price": 100.0,
        "discount_price": 0.0,
        "service_price": 10.0,
        "camp_fire": False,
        "barbeque": False,
        "breakfast": True
    }

@pytest.fixture
def mock_token():
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0dXNlciIsImV4cCI6MTY5MDAwMDAwMH0.this_is_a_mock_token"

@pytest.fixture
def auth_headers(mock_token):
    return {"Authorization": f"Bearer {mock_token}"}

class TestRoomsRouter:
    
    @patch('app.routers.rooms.get_current_user')
    @patch('app.routers.rooms.utils.isAuthorized')
    @patch('app.routers.rooms.helper.getAllRooms')
    def test_listRooms(self, mock_getAllRooms, mock_isAuthorized, mock_get_current_user, mock_room, auth_headers):
        # Arrange
        mock_get_current_user.return_value = "testuser"
        mock_isAuthorized.return_value = True
        mock_getAllRooms.return_value = [mock_room]
        
        # Act
        response = client.get("/rooms/", headers=auth_headers)
        
        # Assert
        assert response.status_code == 200
        assert response.json() == [mock_room]
        mock_isAuthorized.assert_called_once()
        mock_getAllRooms.assert_called_once()
    
    @patch('app.routers.rooms.get_current_user')
    @patch('app.routers.rooms.utils.isAuthorized')
    def test_listRooms_unauthorized(self, mock_isAuthorized, mock_get_current_user, auth_headers):
        # Arrange
        mock_get_current_user.return_value = "testuser"
        mock_isAuthorized.return_value = False
        
        # Act
        response = client.get("/rooms/", headers=auth_headers)
        
        # Assert
        assert response.status_code == 403
        mock_isAuthorized.assert_called_once()
    
    @patch('app.routers.rooms.get_current_user')
    @patch('app.routers.rooms.utils.isAuthorized')
    @patch('app.routers.rooms.helper.getAvailableRooms')
    def test_getAvailableRooms(self, mock_getAvailableRooms, mock_isAuthorized, mock_get_current_user, mock_room, auth_headers):
        # Arrange
        mock_get_current_user.return_value = "testuser"
        mock_isAuthorized.return_value = True
        mock_getAvailableRooms.return_value = [mock_room]
        
        # Act
        response = client.get("/rooms/available?check_in=2023-01-01&check_out=2023-01-05&number_of_people=2", headers=auth_headers)
        
        # Assert
        assert response.status_code == 200
        assert response.json() == [mock_room]
        mock_isAuthorized.assert_called_once()
        mock_getAvailableRooms.assert_called_once_with(date(2023, 1, 1), date(2023, 1, 5), 2)