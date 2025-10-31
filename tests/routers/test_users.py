import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from app.routers.users import router
from app.biz import usersHelper as helper
from app import auth
from app.biz.BizExceptions import DuplicateUserException, UserNotAvailableException

@pytest.fixture
def test_client():
    """Provides a test client with an admin user."""
    app = FastAPI()

    def override_authorized_user():
        return {'user_name': 'testadmin', 'roles': ['admin'], 'is_authorized': True}

    app.include_router(router)

    for route in app.routes:
        if hasattr(route, "dependant") and route.dependant:
            for dep in route.dependant.dependencies:
                if dep.call.__qualname__.startswith("authorizedUser"):
                    app.dependency_overrides[dep.call] = override_authorized_user
    
    with TestClient(app) as client:
        yield client

def test_google_signup_success(test_client, monkeypatch):
    monkeypatch.setattr("app.routers.users.auth.getUserDetailsFromAccessToken", lambda token: {"username": "newuser", "first_name": "Test", "last_name": "User"})
    monkeypatch.setattr("app.routers.users.helper.createUser", lambda userInfo: {"user_id": 1, "username": "newuser"})
    response = test_client.post("/api/v1/users/googleAuth/signup", json={"token": "validtoken"})
    assert response.status_code == 200
    assert response.json()["status"] == status.HTTP_201_CREATED
    assert response.json()["message"] == "User created successfully"
    assert response.json()["user"]["username"] == "newuser"

def test_google_signup_duplicate(test_client, monkeypatch):
    monkeypatch.setattr("app.routers.users.auth.getUserDetailsFromAccessToken", lambda token: {"username": "newuser", "first_name": "Test", "last_name": "User"})
    monkeypatch.setattr("app.routers.users.helper.createUser", lambda userInfo: (_ for _ in ()).throw(DuplicateUserException("User exists")))
    response = test_client.post("/api/v1/users/googleAuth/signup", json={"token": "validtoken"})
    assert response.status_code == status.HTTP_409_CONFLICT
    assert "User exists" in response.json()["detail"]

def test_google_login_success(test_client, monkeypatch):
    monkeypatch.setattr("app.routers.users.auth.getUserDetailsFromAccessToken", lambda token: {"username": "newuser", "first_name": "Test", "last_name": "User"})
    monkeypatch.setattr("app.routers.users.helper.getUserByUserName", lambda username: {"user_id": 1, "username": username, "email": "test@example.com"})
    monkeypatch.setattr("app.routers.users.helper.getRolesForUser", lambda username: ["admin"])
    response = test_client.post("/api/v1/users/googleAuth/login", json={"token": "validtoken"})
    assert response.status_code == 200
    assert response.json()["user"]["username"] == "newuser"
    assert "roles" in response.json()["user"]

def test_google_login_user_not_found(test_client, monkeypatch):
    monkeypatch.setattr("app.routers.users.auth.getUserDetailsFromAccessToken", lambda token: {"username": "nouser", "first_name": "Test", "last_name": "User"})
    monkeypatch.setattr("app.routers.users.helper.getUserByUserName", lambda username: (_ for _ in ()).throw(UserNotAvailableException("Not found")))
    response = test_client.post("/api/v1/users/googleAuth/login", json={"token": "validtoken"})
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Not found" in response.json()["detail"]

def test_list_users_success(test_client, monkeypatch):
    monkeypatch.setattr("app.routers.users.queryAllUsersDB", lambda: [{"user_id": 1, "username": "admin"}])
    response = test_client.get("/api/v1/users/")
    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["users"][0]["username"] == "admin"

def test_create_user_success(test_client, monkeypatch):
    monkeypatch.setattr("app.routers.users.helper.createUser", lambda user_dict: {"user_id": 2, "username": "newuser"})
    user_data = {
        "username": "newuser",
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "phone": "1234567890",
        "booking_commission": 10,
        "password": "password123",
        "user_type": "CUSTOMER"
    }
    response = test_client.post("/api/v1/users/create", json=user_data)
    assert response.status_code == 200
    assert response.json()["status"] == status.HTTP_201_CREATED
    assert response.json()["user"]["username"] == "newuser"

def test_create_user_duplicate(test_client, monkeypatch):
    monkeypatch.setattr("app.routers.users.helper.createUser", lambda user_dict: (_ for _ in ()).throw(DuplicateUserException("User exists")))
    user_data = {
        "username": "newuser",
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "phone": "1234567890",
        "booking_commission": 10,
        "password": "password123",
        "user_type": "CUSTOMER"
    }
    response = test_client.post("/api/v1/users/create", json=user_data)
    assert response.status_code == status.HTTP_409_CONFLICT
    assert "User exists" in response.json()["detail"]

def test_update_user_success(test_client, monkeypatch):
    monkeypatch.setattr("app.routers.users.helper.updateUserDetail", lambda user_dict: {"user_id": 2, "username": "newuser"})
    user_detail = {
        "user_id": 2,
        "username": "newuser",
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "phone": "1234567890",
        "booking_commission": 10,
        "user_type": "CUSTOMER"
    }
    response = test_client.post("/api/v1/users/update", json=user_detail)
    assert response.status_code == 200
    assert response.json()["user"]["username"] == "newuser"