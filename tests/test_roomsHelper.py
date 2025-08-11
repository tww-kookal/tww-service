import pytest
from unittest.mock import patch, MagicMock
from datetime import date
from app.biz import roomsHelper

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
        "check_in": date(2023, 1, 1),
        "check_out": date(2023, 1, 5),
        "number_of_people": 2,
        "customer_name": "Test Customer",
        "booking_date": date(2022, 12, 1),
        "booked_by": "testuser",
        "status": "confirmed",
        "room_price": 100.0,
        "discount_price": 0.0,
        "service_price": 10.0,
        "camp_fire": False,
        "barbeque": False,
        "breakfast": True
    }

@patch('app.biz.roomsHelper.roomsDB')
class TestRoomsHelper:
    
    def test_getAllRooms_success(self, mock_roomsDB):
        # Arrange
        expected_rooms = [mock_room()]
        mock_roomsDB.queryAllRoomsDB.return_value = expected_rooms
        
        # Act
        result = roomsHelper.getAllRooms()
        
        # Assert
        assert result == expected_rooms
        mock_roomsDB.queryAllRoomsDB.assert_called_once()
    
    def test_getAllRooms_exception(self, mock_roomsDB):
        # Arrange
        mock_roomsDB.queryAllRoomsDB.side_effect = Exception("Database error")
        
        # Act
        result = roomsHelper.getAllRooms()
        
        # Assert
        assert result == []
    
    def test_createRoom_success(self, mock_roomsDB, mock_room):
        # Arrange
        mock_roomsDB.createRoomDB.return_value = None
        
        # Act
        result = roomsHelper.createRoom(mock_room)
        
        # Assert
        assert result == []
        mock_roomsDB.createRoomDB.assert_called_once_with(mock_room)
    
    def test_createRoom_exception(self, mock_roomsDB, mock_room):
        # Arrange
        mock_roomsDB.createRoomDB.side_effect = Exception("Database error")
        
        # Act & Assert
        with pytest.raises(Exception, match="Not able to create the room"):
            roomsHelper.createRoom(mock_room)
    
    def test_getRoomByName_success(self, mock_roomsDB, mock_room):
        # Arrange
        mock_roomsDB.queryRoomByNameDB.return_value = mock_room
        
        # Act
        result = roomsHelper.getRoomByName("Test Room")
        
        # Assert
        assert result == mock_room
        mock_roomsDB.queryRoomByNameDB.assert_called_once_with("Test Room")
    
    def test_getRoomByName_exception(self, mock_roomsDB):
        # Arrange
        mock_roomsDB.queryRoomByNameDB.side_effect = Exception("Database error")
        
        # Act
        result = roomsHelper.getRoomByName("Test Room")
        
        # Assert
        assert result is None
    
    def test_getAvailableRooms_success(self, mock_roomsDB, mock_room):
        # Arrange
        expected_rooms = [mock_room]
        mock_roomsDB.queryAvailableRoomsDB.return_value = expected_rooms
        check_in = date(2023, 1, 1)
        check_out = date(2023, 1, 5)
        number_of_people = 2
        
        # Act
        result = roomsHelper.getAvailableRooms(check_in, check_out, number_of_people)
        
        # Assert
        assert result == expected_rooms
        mock_roomsDB.queryAvailableRoomsDB.assert_called_once_with(check_in, check_out, number_of_people)
    
    def test_getAvailableRooms_exception(self, mock_roomsDB):
        # Arrange
        mock_roomsDB.queryAvailableRoomsDB.side_effect = Exception("Database error")
        check_in = date(2023, 1, 1)
        check_out = date(2023, 1, 5)
        number_of_people = 2
        
        # Act
        result = roomsHelper.getAvailableRooms(check_in, check_out, number_of_people)
        
        # Assert
        assert result == []