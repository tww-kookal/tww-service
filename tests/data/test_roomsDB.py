import pytest
from unittest.mock import patch, MagicMock
from app.data import roomsDB

@pytest.fixture
def mock_db_connection():
    with patch('app.data.database.get_connection') as mock_conn:
        mock_cursor = MagicMock()
        mock_conn.return_value.cursor.return_value = mock_cursor
        yield mock_conn, mock_cursor

def test_query_all_rooms(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchall.return_value = [
        {'room_id': 1, 'room_name': 'Deluxe', 'min_capacity': 1, 'max_capacity': 2, 'number_of_beds': 1, 'number_of_bathrooms': 1},
        {'room_id': 2, 'room_name': 'Suite', 'min_capacity': 2, 'max_capacity': 4, 'number_of_beds': 2, 'number_of_bathrooms': 2}
    ]
    result = roomsDB.queryAllRoomsDB()
    mock_cursor.execute.assert_called_once_with("SELECT * FROM rooms")
    assert isinstance(result, list)
    assert result[0]['room_name'] == 'Deluxe'
    mock_cursor.close.assert_called_once()
    mock_conn.return_value.close.assert_called_once()

def test_create_room_success(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    with patch('app.data.roomsDB.queryRoomByNameDB', return_value=None):
        mock_cursor.lastrowid = 10
        room = {
            'room_name': 'Premium',
            'min_capacity': 2,
            'max_capacity': 4,
            'number_of_beds': 2,
            'number_of_bathrooms': 2
        }
        result = roomsDB.createRoomDB(room)
        mock_cursor.execute.assert_called_once_with(
            "INSERT INTO rooms (room_name, min_capacity, max_capacity, number_of_beds, number_of_bathrooms) VALUES (%s, %s, %s, %s, %s)",
            ('Premium', 2, 4, 2, 2)
        )
        mock_conn.return_value.commit.assert_called_once()
        assert result['room_id'] == 10
        mock_cursor.close.assert_called_once()
        mock_conn.return_value.close.assert_called_once()

def test_create_room_duplicate(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    with patch('app.data.roomsDB.queryRoomByNameDB', return_value={'room_id': 1}):
        room = {
            'room_name': 'Deluxe',
            'min_capacity': 1,
            'max_capacity': 2,
            'number_of_beds': 1,
            'number_of_bathrooms': 1
        }
        with pytest.raises(Exception) as exc:
            roomsDB.createRoomDB(room)
        mock_cursor.execute.assert_not_called()
        mock_conn.return_value.commit.assert_not_called()
        #assert str(exc.value) == 'Room Already Exists'
        #mock_cursor.close.assert_called_once()
        #mock_conn.return_value.close.assert_called_once()

def test_create_room_error_logging(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    with patch('app.data.roomsDB.queryRoomByNameDB', return_value=None):
        mock_cursor.execute.side_effect = Exception('DB Error')
        room = {
            'room_name': 'Premium',
            'min_capacity': 2,
            'max_capacity': 4,
            'number_of_beds': 2,
            'number_of_bathrooms': 2
        }
        with patch('app.data.roomsDB.logger') as mock_logger:
            with pytest.raises(Exception):
                roomsDB.createRoomDB(room)
            mock_logger.error.assert_called()
        mock_cursor.close.assert_called_once()
        mock_conn.return_value.close.assert_called_once()

def test_query_room_by_name_found(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchone.return_value = {'room_id': 2, 'room_name': 'Suite'}
    result = roomsDB.queryRoomByNameDB('Suite')
    mock_cursor.execute.assert_called_once_with("SELECT * FROM rooms WHERE room_name = %s", ('Suite',))
    assert result['room_id'] == 2
    mock_cursor.close.assert_called_once()
    mock_conn.return_value.close.assert_called_once()

def test_query_room_by_name_not_found(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchone.return_value = None
    result = roomsDB.queryRoomByNameDB('Unknown')
    mock_cursor.execute.assert_called_once_with("SELECT * FROM rooms WHERE room_name = %s", ('Unknown',))
    assert result is None
    mock_cursor.close.assert_called_once()
    mock_conn.return_value.close.assert_called_once()

def test_query_room_by_id_found(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchone.return_value = {'room_id': 1, 'room_name': 'Deluxe'}
    result = roomsDB.queryRoomById(1)
    mock_cursor.execute.assert_called_once_with("SELECT * FROM rooms WHERE room_id = %s", (1,))
    assert result['room_name'] == 'Deluxe'
    mock_cursor.close.assert_called_once()
    mock_conn.return_value.close.assert_called_once()

def test_query_room_by_id_not_found(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchone.return_value = None
    result = roomsDB.queryRoomById(99)
    mock_cursor.execute.assert_called_once_with("SELECT * FROM rooms WHERE room_id = %s", (99,))
    assert result is None
    mock_cursor.close.assert_called_once()
    mock_conn.return_value.close.assert_called_once()

def test_query_roles_db(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchall.return_value = [
        {'role_id': 1, 'role_name': 'admin'},
        {'role_id': 2, 'role_name': 'user'}
    ]
    result = roomsDB.queryRolesDB()
    mock_cursor.execute.assert_called_once_with("SELECT role_id, role_name FROM roles")
    assert isinstance(result, list)
    assert result[0]['role_name'] == 'admin'
    assert result[1]['role_id'] == 2
    mock_cursor.close.assert_called_once()
    mock_conn.return_value.close.assert_called_once()