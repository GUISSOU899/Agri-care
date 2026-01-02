from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

from app.core.config import settings

def test_health_check():
    response = client.get(f"{settings.API_V1_STR}/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
