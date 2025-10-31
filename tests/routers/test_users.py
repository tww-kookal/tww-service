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


def test_update_user_not_found(test_client, monkeypatch):
    monkeypatch.setattr("app.routers.users.helper.updateUserDetail", lambda user_dict: (_ for _ in ()).throw(UserNotAvailableException("User not found")))
    user_detail = {
        "user_id": 99,
        "username": "nonexistent",
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "phone": "1234567890",
        "booking_commission": 10,
        "user_type": "CUSTOMER"
    }
    response = test_client.post("/api/v1/users/update", json=user_detail)
    assert response.status_code == status.HTTP_409_CONFLICT
    assert "User not found" in response.json()["detail"]

def test_get_by_id_success(test_client, monkeypatch):
    monkeypatch.setattr("app.routers.users.queryUserByIdDB", lambda user_id: {"user_id": 1, "username": "testuser"})
    response = test_client.get("/api/v1/users/getById/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["user"]["username"] == "testuser"

def test_get_by_id_not_found(test_client, monkeypatch):
    monkeypatch.setattr("app.routers.users.queryUserByIdDB", lambda user_id: None)
    response = test_client.get("/api/v1/users/getById/99")
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_get_by_username_success(test_client, monkeypatch):
    monkeypatch.setattr("app.routers.users.queryUserDB", lambda username: {"user_id": 1, "username": "testuser"})
    response = test_client.get("/api/v1/users/getByUsername/testuser")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["user"]["username"] == "testuser"

def test_get_by_username_not_found(test_client, monkeypatch):
    monkeypatch.setattr("app.routers.users.queryUserDB", lambda username: None)
    response = test_client.get("/api/v1/users/getByUsername/nonexistent")
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_assign_roles_to_user_success(test_client, monkeypatch):
    monkeypatch.setattr("app.routers.users.assignRolesToUserDB", lambda username, roles: None)
    response = test_client.post("/api/v1/users/assignRolesToUser?username=testuser", json=["manager"])
    assert response.status_code == status.HTTP_200_OK
    assert "Roles assigned" in response.json()["message"]

def test_assign_roles_to_user_exception(test_client, monkeypatch):
    monkeypatch.setattr("app.routers.users.assignRolesToUserDB", lambda username, roles: (_ for _ in ()).throw(Exception("DB error")))
    response = test_client.post("/api/v1/users/assignRolesToUser?username=testuser", json=["manager"])
    assert response.status_code == status.HTTP_412_PRECONDITION_FAILED

def test_user_roles_success(test_client, monkeypatch):
    monkeypatch.setattr("app.routers.users.helper.getRolesForUser", lambda username: ["customer"])
    response = test_client.get("/api/v1/users/userRoles?username=testuser")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["user"]["roles"] == ["customer"]

def test_list_my_roles_success(test_client):
    response = test_client.get("/api/v1/users/listMyRoles")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["user"]["username"] == "testadmin"
    assert "admin" in response.json()["user"]["roles"]

def test_list_booking_sources_success(test_client, monkeypatch):
    monkeypatch.setattr("app.routers.users.helper.getBookingSources", lambda: [{"id": 1, "name": "source1"}])
    response = test_client.get("/api/v1/users/bookingSource")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["users"]) == 1

def test_list_employees_success(test_client, monkeypatch):
    monkeypatch.setattr("app.routers.users.helper.getEmployees", lambda: [{"id": 1, "name": "emp1"}])
    response = test_client.get("/api/v1/users/employees")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["users"]) == 1

def test_list_vendors_success(test_client, monkeypatch):
    monkeypatch.setattr("app.routers.users.helper.getVendors", lambda: [{"id": 1, "name": "vendor1"}])
    response = test_client.get("/api/v1/users/vendors")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["users"]) == 1

def test_list_non_customers_success(test_client, monkeypatch):
    monkeypatch.setattr("app.routers.users.helper.getNonCustomers", lambda: [{"id": 1, "name": "noncust1"}])
    response = test_client.get("/api/v1/users/non-customers")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["users"]) == 1

def test_auth_google_success(test_client, monkeypatch):
    monkeypatch.setattr("app.routers.users.id_token.verify_oauth2_token", lambda token, req, client_id: {"sub": "123", "email": "test@google.com", "name": "Test User"})
    response = test_client.post("/api/v1/users/auth/google", json={"token": "validgoogletoken"})
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["email"] == "test@google.com"

def test_auth_google_failure(test_client, monkeypatch):
    monkeypatch.setattr("app.routers.users.id_token.verify_oauth2_token", lambda token, req, client_id: (_ for _ in ()).throw(Exception("Invalid token")))
    response = test_client.post("/api/v1/users/auth/google", json={"token": "invalidgoogletoken"})
    assert response.status_code == status.HTTP_400_BAD_REQUEST    