from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

def test_read_alerts(client: TestClient, db: Session):
    response = client.get("/api/v1/alerts/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
