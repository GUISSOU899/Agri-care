from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.api.routers.regions import read_regions

def test_read_regions(client: TestClient, db: Session):
    response = client.get("/api/v1/regions/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
