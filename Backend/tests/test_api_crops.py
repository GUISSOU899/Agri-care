from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

def test_create_read_crop(client: TestClient, db: Session):
    crop_data = {"name": "Test Crop", "code": "TST001", "description": "A test crop"}
    
    # Create
    response = client.post("/api/v1/crops/", json=crop_data)
    assert response.status_code == 201
    content = response.json()
    assert content["name"] == crop_data["name"]
    assert content["code"] == crop_data["code"]
    
    # Read
    response = client.get("/api/v1/crops/")
    assert response.status_code == 200
    assert len(response.json()) > 0
