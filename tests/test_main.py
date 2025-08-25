import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_app_initialization():
    assert app.title == "FastAPI"
    assert hasattr(app, "middleware_stack")
    assert hasattr(app, "router")

def test_cors_middleware():
    # Check that CORS middleware is present
    cors_present = any(
        getattr(m, "__class__", None).__name__ == "CORSMiddleware" for m in app.user_middleware
    )
    assert cors_present

def test_metrics_endpoint():
    response = client.get("/metrics")
    assert response.status_code in [200, 404]  # Metrics may be disabled in test

def test_router_inclusion():
    # Check that all routers are included
    expected_prefixes = [
        "/api/v1", "/api/v1/rooms", "/api/v1/users", "/api/v1/roles", "/api/v1/reports", "/api/v1/customers", "/api/v1/booking", "/api/v1/payment"
    ]
    prefixes = [route.path for route in app.routes if hasattr(route, "path")]
    for prefix in expected_prefixes:
        assert any(prefix in p for p in prefixes)