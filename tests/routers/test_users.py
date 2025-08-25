import pytest
from fastapi.testclient import TestClient
from app.routers.users import router
from app.biz import usersHelper as helper
from app import auth
from app.data.usersDB import queryAllUsersDB, queryUserByIdDB
from app.config.config import settings
from fastapi import status

client = TestClient(router)

@pytest.fixture
def mock_authorized_user(monkeypatch):
    def mock_auth(*args, **kwargs):
        return lambda: {"user_name": "admin", "is_authorized": True}
    monkeypatch.setattr(auth, "authorizedUser", mock_auth)

def test_google_signup_success(monkeypatch):
    monkeypatch.setattr(auth, "getUserDetailsFromAccessToken", lambda token: {"username": "newuser", "first_name": "Test", "last_name": "User"})
    monkeypatch.setattr(helper, "createUser", lambda userInfo: {"user_id": 1, "username": "newuser"})
    response = client.post("/api/v1/users/googleAuth/signup", json={"token": "validtoken"})
    assert response.status_code == 201
    assert response.json()["message"] == "User created successfully"
    assert response.json()["user"]["username"] == "newuser"

def test_google_signup_duplicate(monkeypatch):
    monkeypatch.setattr(auth, "getUserDetailsFromAccessToken", lambda token: {"username": "newuser", "first_name": "Test", "last_name": "User"})
    class DuplicateUserException(Exception):
        def __init__(self, message):
            self.message = message
    monkeypatch.setattr(helper, "createUser", lambda userInfo: (_ for _ in ()).throw(DuplicateUserException("User exists")))
    response = client.post("/api/v1/users/googleAuth/signup", json={"token": "validtoken"})
    assert response.status_code == 409
    assert "User exists" in response.json()["detail"]

def test_google_login_success(monkeypatch):
    monkeypatch.setattr(auth, "getUserDetailsFromAccessToken", lambda token: {"username": "newuser", "first_name": "Test", "last_name": "User"})
    monkeypatch.setattr(helper, "getUserByUserName", lambda username: {"user_id": 1, "username": username, "email": "test@example.com"})
    monkeypatch.setattr(helper, "getRolesForUser", lambda username: ["admin"])
    response = client.post("/api/v1/users/googleAuth/login", json={"token": "validtoken"})
    assert response.status_code == 200
    assert response.json()["user"]["username"] == "newuser"
    assert "roles" in response.json()["user"]

def test_google_login_user_not_found(monkeypatch):
    monkeypatch.setattr(auth, "getUserDetailsFromAccessToken", lambda token: {"username": "nouser", "first_name": "Test", "last_name": "User"})
    class UserNotAvailableException(Exception):
        def __init__(self, message):
            self.message = message
    monkeypatch.setattr(helper, "getUserByUserName", lambda username: (_ for _ in ()).throw(UserNotAvailableException("Not found")))
    response = client.post("/api/v1/users/googleAuth/login", json={"token": "validtoken"})
    assert response.status_code == 404
    assert "Not found" in response.json()["detail"]

def test_list_users_success(mock_authorized_user, monkeypatch):
    monkeypatch.setattr(queryAllUsersDB, "__call__", lambda: [{"user_id": 1, "username": "admin"}])
    response = client.get("/api/v1/users/")
    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["users"][0]["username"] == "admin"

def test_create_user_success(mock_authorized_user, monkeypatch):
    monkeypatch.setattr(helper, "createUser", lambda user_dict: {"user_id": 2, "username": "newuser"})
    user_data = {
        "username": "newuser",
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "phone": "1234567890",
        "booking_commission": 10,
        "password": "password123"
    }
    response = client.post("/api/v1/users/create", json=user_data)
    assert response.status_code == 201
    assert response.json()["user"]["username"] == "newuser"

def test_create_user_duplicate(mock_authorized_user, monkeypatch):
    class DuplicateUserException(Exception):
        def __init__(self, message):
            self.message = message
    monkeypatch.setattr(helper, "createUser", lambda user_dict: (_ for _ in ()).throw(DuplicateUserException("User exists")))
    user_data = {
        "username": "newuser",
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "phone": "1234567890",
        "booking_commission": 10,
        "password": "password123"
    }
    response = client.post("/api/v1/users/create", json=user_data)
    assert response.status_code == 409
    assert "User exists" in response.json()["detail"]

def test_update_user_success(mock_authorized_user, monkeypatch):
    monkeypatch.setattr(helper, "updateUserDetail", lambda user_dict: {"user_id": 2, "username": "newuser"})
    user_detail = {
        "user_id": 2,
        "username": "newuser",
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "phone": "1234567890",
        "booking_commission": 10
    }
    response = client.post("/api/v1/users/update", json=user_detail)
    assert response.status_code == 200
    assert response.json()["user"]["username"] == "newuser"