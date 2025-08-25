import pytest
from fastapi.testclient import TestClient
from app.routers.login import router
from app.biz import usersHelper as userHelper
from app import utils
from app.config import config
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm

client = TestClient(router)

def test_login_success(monkeypatch):
    monkeypatch.setattr(userHelper, "queryUser", lambda username: {"username": username})
    monkeypatch.setattr(userHelper, "validateUser", lambda user, pwd: True)
    monkeypatch.setattr(utils, "create_access_token", lambda data, expires_delta: "token123")
    response = client.post("/api/v1/login", data={"username": "testuser", "password": "testpass"})
    assert response.status_code == 200
    assert response.json()["access_token"] == "token123"
    assert response.json()["token_type"] == "bearer"

def test_login_invalid_credentials(monkeypatch):
    monkeypatch.setattr(userHelper, "queryUser", lambda username: {"username": username})
    monkeypatch.setattr(userHelper, "validateUser", lambda user, pwd: False)
    response = client.post("/api/v1/login", data={"username": "testuser", "password": "wrongpass"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid credentials"