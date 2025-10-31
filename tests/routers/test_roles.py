import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from app.routers.roles import router
from app.data import rolesDB
from app import auth


@pytest.fixture
def test_client():
    """Provides a test client with an admin user."""
    app = FastAPI()

    def override_authorized_user():
        return {'user_name': 'testadmin', 'roles': ['admin']}

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


def test_create_role_success(test_client, monkeypatch):
    monkeypatch.setattr(rolesDB, "persistRoleDB", lambda role_name: None)
    response = test_client.post("/api/v1/roles/create", json={"role_name": "manager"})
    assert response.status_code == 200
    assert response.json()["status"] == status.HTTP_201_CREATED
    assert response.json()["message"] == "Role created successfully"


def test_create_role_error(test_client, monkeypatch):
    def raise_exception(role_name):
        raise Exception("Role already exists")
    monkeypatch.setattr(rolesDB, "persistRoleDB", raise_exception)
    response = test_client.post("/api/v1/roles/create", json={"role_name": "manager"})
    assert response.status_code == status.HTTP_412_PRECONDITION_FAILED
    assert "Role already exists" in response.json()["detail"]


def test_list_roles_success(test_client, monkeypatch):
    monkeypatch.setattr(rolesDB, "queryRolesDB", lambda: ["admin", "manager"])
    response = test_client.get("/api/v1/roles/")
    assert response.status_code == 200
    assert "roles" in response.json()
    assert response.json()["status"] == status.HTTP_200_OK
    assert "admin" in response.json()["roles"]