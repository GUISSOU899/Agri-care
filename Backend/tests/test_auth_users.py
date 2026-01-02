import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_users():
    response = client.get("/api/v1/auth/users/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # At least one user should be present (admin)
    assert any(user.get("email") == "admin@agri-care.local" for user in data)
