from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/docs")
    assert response.status_code == 200

def test_root_path_404():
    response = client.get("/")
    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}

def test_cors_headers_allowed():
    response = client.options(
        "/",
        headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "GET"}
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"

def test_cors_headers_github_allowed():
    response = client.options(
        "/",
        headers={"Origin": "https://tww-kookal.github.io", "Access-Control-Request-Method": "GET"}
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "https://tww-kookal.github.io"
