import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from app.routers.rooms import router
from app import auth


@pytest.fixture
def test_client():
    """Provides a test client with an admin user."""
    app = FastAPI()

    def override_authorized_user():
        return {'user_name': 'testadmin', 'roles': ['admin'], 'is_authorized': True}

    # Include the router first to inspect its routes
    app.include_router(router)

    # Find the dependency from the routes and override it
    for route in app.routes:
        if hasattr(route, "dependant") and route.dependant:
            for dep in route.dependant.dependencies:
                if dep.call.__qualname__.startswith("authorizedUser"):
                    app.dependency_overrides[dep.call] = override_authorized_user
    
    with TestClient(app) as client:
        yield client


def test_list_rooms_success(test_client, monkeypatch):
    monkeypatch.setattr("app.routers.rooms.helper.getAllRooms", lambda: [{"room_id": 1, "room_name": "Deluxe"}])
    response = test_client.get("/api/v1/rooms/")
    assert response.status_code == 200
    assert "rooms" in response.json()
    assert response.json()["rooms"][0]["room_name"] == "Deluxe"


def test_get_room_by_name_success(test_client, monkeypatch):
    monkeypatch.setattr("app.routers.rooms.helper.getRoomByName", lambda name: {"room_id": 1, "room_name": name})
    response = test_client.get("/api/v1/rooms/byName/Deluxe")
    assert response.status_code == 200
    assert response.json()["room"]["room_name"] == "Deluxe"


def test_get_room_by_name_not_found(test_client, monkeypatch):
    monkeypatch.setattr("app.routers.rooms.helper.getRoomByName", lambda name: None)
    response = test_client.get("/api/v1/rooms/byName/Unknown")
    assert response.status_code == 404
    assert response.json()["detail"] == "Room not found"


def test_create_room_success(test_client, monkeypatch):
    def mock_create_room(room_dict):
        return {**room_dict, "room_id": 2}
    monkeypatch.setattr("app.routers.rooms.helper.createRoom", mock_create_room)
    room_data = {
        "room_id": 2,
        "room_name": "Suite",
        "min_capacity": 1,
        "max_capacity": 4,
        "number_of_beds": 2,
        "number_of_bathrooms": 1
    }
    response = test_client.post("/api/v1/rooms/create", json=room_data)
    assert response.status_code == 200
    assert response.json()["message"] == "Room created successfully"
    assert response.json()["room"]["room_name"] == "Suite"


def test_create_room_error(test_client, monkeypatch):
    def raise_exception(room_dict):
        raise Exception("Room creation failed")
    monkeypatch.setattr("app.routers.rooms.helper.createRoom", raise_exception)
    room_data = {
        "room_id": 3,
        "room_name": "ErrorRoom",
        "min_capacity": 1,
        "max_capacity": 2,
        "number_of_beds": 1,
        "number_of_bathrooms": 1
    }
    response = test_client.post("/api/v1/rooms/create", json=room_data)
    assert response.status_code == 500
    assert response.json()["detail"] == "Not able to create the room"