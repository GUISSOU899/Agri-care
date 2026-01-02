from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

def test_read_forecasts(client: TestClient, db: Session):
    response = client.get("/api/v1/forecast/?region_id=1&crop_id=1")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "temperature_c" in data[0]
        assert "rainfall_mm" in data[0]
