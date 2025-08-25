import pytest
from fastapi.testclient import TestClient
from app.routers.rooms import router
from app.biz import roomsHelper as helper
from app import auth
from fastapi import status

client = TestClient(router)

@pytest.fixture
def mock_authorized_user(monkeypatch):
    def mock_auth(*args, **kwargs):
        return lambda: {"user_name": "admin", "is_authorized": True}
    monkeypatch.setattr(auth, "authorizedUser", mock_auth)

def test_list_rooms_success(mock_authorized_user, monkeypatch):
    monkeypatch.setattr(helper, "getAllRooms", lambda: [{"room_id": 1, "room_name": "Deluxe"}])
    response = client.get("/api/v1/rooms/")
    assert response.status_code == 200
    assert "rooms" in response.json()
    assert response.json()["rooms"][0]["room_name"] == "Deluxe"

def test_get_room_by_name_success(mock_authorized_user, monkeypatch):
    monkeypatch.setattr(helper, "getRoomByName", lambda name: {"room_id": 1, "room_name": name})
    response = client.get("/api/v1/rooms/byName/Deluxe")
    assert response.status_code == 200
    assert response.json()["room"]["room_name"] == "Deluxe"

def test_get_room_by_name_not_found(mock_authorized_user, monkeypatch):
    monkeypatch.setattr(helper, "getRoomByName", lambda name: None)
    response = client.get("/api/v1/rooms/byName/Unknown")
    assert response.status_code == 404
    assert response.json()["detail"] == "Room not found"

def test_create_room_success(mock_authorized_user, monkeypatch):
    def mock_create_room(room_dict):
        return {**room_dict, "room_id": 2}
    monkeypatch.setattr(helper, "createRoom", mock_create_room)
    room_data = {
        "room_id": 2,
        "room_name": "Suite",
        "min_capacity": 1,
        "max_capacity": 4,
        "number_of_beds": 2,
        "number_of_bathrooms": 1
    }
    response = client.post("/api/v1/rooms/create", json=room_data)
    assert response.status_code == 200
    assert response.json()["message"] == "Room created successfully"
    assert response.json()["room"]["room_name"] == "Suite"

def test_create_room_error(mock_authorized_user, monkeypatch):
    def raise_exception(room_dict):
        raise Exception("Room creation failed")
    monkeypatch.setattr(helper, "createRoom", raise_exception)
    room_data = {
        "room_id": 3,
        "room_name": "ErrorRoom",
        "min_capacity": 1,
        "max_capacity": 2,
        "number_of_beds": 1,
        "number_of_bathrooms": 1
    }
    response = client.post("/api/v1/rooms/create", json=room_data)
    assert response.status_code == 500
    assert response.json()["detail"] == "Not able to create the room"