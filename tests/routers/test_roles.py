import pytest
from fastapi.testclient import TestClient
from app.routers.roles import router
from app.data import rolesDB
from app import auth
from fastapi import status

client = TestClient(router)

@pytest.fixture
def mock_authorized_user(monkeypatch):
    def mock_auth(*args, **kwargs):
        return lambda: {"user_name": "admin", "is_authorized": True}
    monkeypatch.setattr(auth, "authorizedUser", mock_auth)

def test_create_role_success(mock_authorized_user, monkeypatch):
    monkeypatch.setattr(rolesDB, "persistRoleDB", lambda role_name: None)
    response = client.post("/api/v1/roles/create", json={"role_name": "manager"})
    assert response.status_code == 201
    assert response.json()["message"] == "Role created successfully"

def test_create_role_error(mock_authorized_user, monkeypatch):
    def raise_exception(role_name):
        raise Exception("Role already exists")
    monkeypatch.setattr(rolesDB, "persistRoleDB", raise_exception)
    response = client.post("/api/v1/roles/create", json={"role_name": "manager"})
    assert response.status_code == 412
    assert "Role already exists" in response.json()["detail"]

def test_list_roles_success(mock_authorized_user, monkeypatch):
    monkeypatch.setattr(rolesDB, "queryRolesDB", lambda: ["admin", "manager"])
    response = client.get("/api/v1/roles/")
    assert response.status_code == 200
    assert "roles" in response.json()
    assert "admin" in response.json()["roles"]