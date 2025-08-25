import pytest
from unittest.mock import patch, MagicMock
from app.biz import roomsHelper

class TestRoomsHelperBiz:
    @patch('app.biz.roomsHelper.roomsDB.queryAllRoomsDB')
    def test_getAllRooms_success(self, mock_query):
        mock_query.return_value = [{"room_id": 1, "room_name": "RoomA"}]
        result = roomsHelper.getAllRooms()
        assert result == [{"room_id": 1, "room_name": "RoomA"}]
        mock_query.assert_called_once()

    @patch('app.biz.roomsHelper.roomsDB.queryAllRoomsDB')
    def test_getAllRooms_exception(self, mock_query):
        mock_query.side_effect = Exception("DB error")
        result = roomsHelper.getAllRooms()
        assert result == []
        mock_query.assert_called_once()

    @patch('app.biz.roomsHelper.roomsDB.createRoomDB')
    def test_createRoom_success(self, mock_create):
        mock_create.return_value = {"room_id": 2, "room_name": "RoomB"}
        room = {"room_name": "RoomB"}
        result = roomsHelper.createRoom(room)
        assert result["room_id"] == 2
        mock_create.assert_called_once_with(room)

    @patch('app.biz.roomsHelper.roomsDB.createRoomDB')
    def test_createRoom_exception(self, mock_create):
        mock_create.side_effect = Exception("Not able to create the room")
        room = {"room_name": "RoomC"}
        with pytest.raises(Exception) as exc_info:
            roomsHelper.createRoom(room)
        assert "Not able to create the room" in str(exc_info.value)
        mock_create.assert_called_once_with(room)

    @patch('app.biz.roomsHelper.roomsDB.queryRoomByNameDB')
    def test_getRoomByName_success(self, mock_query):
        mock_query.return_value = {"room_id": 3, "room_name": "RoomD"}
        result = roomsHelper.getRoomByName("RoomD")
        assert result["room_name"] == "RoomD"
        mock_query.assert_called_once_with("RoomD")

    @patch('app.biz.roomsHelper.roomsDB.queryRoomByNameDB')
    def test_getRoomByName_exception(self, mock_query):
        mock_query.side_effect = Exception("DB error")
        result = roomsHelper.getRoomByName("RoomE")
        assert result is None
        mock_query.assert_called_once_with("RoomE")

    @patch('app.biz.roomsHelper.roomsDB.queryRoomById')
    def test_getRoomById_success(self, mock_query):
        mock_query.return_value = {"room_id": 4, "room_name": "RoomF"}
        result = roomsHelper.getRoomById("4")
        assert result["room_name"] == "RoomF"
        mock_query.assert_called_once_with("4")

    @patch('app.biz.roomsHelper.roomsDB.queryRoomById')
    def test_getRoomById_exception(self, mock_query):
        mock_query.side_effect = Exception("DB error")
        result = roomsHelper.getRoomById("5")
        assert result is None
        mock_query.assert_called_once_with("5")