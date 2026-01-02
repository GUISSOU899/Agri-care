from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

def test_create_read_crop(client: TestClient, db: Session):
    crop_data = {
        "name": "Test Crop", 
        "type": "Cereal",
        "water_need": 4.0,
        "temp_low": 5.0,
        "temp_high": 35.0,
        "rain_threshold": 20.0,
        "variety": "Test Variety"
    }
    
    # Create
    response = client.post("/api/v1/crops/", json=crop_data)
    assert response.status_code == 201
    content = response.json()
    assert content["name"] == crop_data["name"]
    assert content["type"] == crop_data["type"]
    
    # Read
    response = client.get("/api/v1/crops/")
    assert response.status_code == 200
    assert len(response.json()) > 0
