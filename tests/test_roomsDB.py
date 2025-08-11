import pytest
from unittest.mock import patch, MagicMock
from datetime import date
from app.data import roomsDB

@pytest.fixture
def mock_connection():
    conn = MagicMock()
    cursor = MagicMock()
    conn.cursor.return_value = cursor
    return conn, cursor

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

class TestRoomsDB:
    
    @patch('app.data.roomsDB.database.get_connection')
    def test_queryAllRoomsDB(self, mock_get_connection, mock_connection, mock_room):
        # Arrange
        conn, cursor = mock_connection
        mock_get_connection.return_value = conn
        cursor.fetchall.return_value = [(1, "Test Room", 2, 4, 2, 1)]
        
        # Act
        result = roomsDB.queryAllRoomsDB()
        
        # Assert
        assert len(result) == 1
        assert result[0]["room_id"] == 1
        assert result[0]["room_name"] == "Test Room"
        cursor.execute.assert_called_once()
        cursor.close.assert_called_once()
        conn.close.assert_called_once()
    
    @patch('app.data.roomsDB.database.get_connection')
    def test_createRoomDB(self, mock_get_connection, mock_connection, mock_room):
        # Arrange
        conn, cursor = mock_connection
        mock_get_connection.return_value = conn
        
        # Act
        roomsDB.createRoomDB(mock_room)
        
        # Assert
        cursor.execute.assert_called_once()
        conn.commit.assert_called_once()
        cursor.close.assert_called_once()
        conn.close.assert_called_once()
    
    @patch('app.data.roomsDB.database.get_connection')
    def test_queryRoomByNameDB(self, mock_get_connection, mock_connection, mock_room):
        # Arrange
        conn, cursor = mock_connection
        mock_get_connection.return_value = conn
        cursor.fetchone.return_value = (1, "Test Room", 2, 4, 2, 1)
        
        # Act
        result = roomsDB.queryRoomByNameDB("Test Room")
        
        # Assert
        assert result["room_id"] == 1
        assert result["room_name"] == "Test Room"
        cursor.execute.assert_called_once_with("SELECT * FROM rooms WHERE room_name = %s", ("Test Room",))
        cursor.close.assert_called_once()
        conn.close.assert_called_once()
    
    @patch('app.data.roomsDB.database.get_connection')
    def test_queryAvailableRoomsDB(self, mock_get_connection, mock_connection):
        # Arrange
        conn, cursor = mock_connection
        mock_get_connection.return_value = conn
        cursor.fetchall.return_value = [(1, "Test Room", 2, 4, 2, 1)]
        check_in = date(2023, 1, 1)
        check_out = date(2023, 1, 5)
        number_of_people = 2
        
        # Act
        result = roomsDB.queryAvailableRoomsDB(check_in, check_out, number_of_people)
        
        # Assert
        assert len(result) == 1
        assert result[0]["room_id"] == 1
        assert result[0]["room_name"] == "Test Room"
        cursor.execute.assert_called_once()
        cursor.close.assert_called_once()
        conn.close.assert_called_once()