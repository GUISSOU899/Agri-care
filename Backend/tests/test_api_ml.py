from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_predict_endpoint():
    payload = {
        "region_id": 1,
        "crop_id": 1,
        "rainfall_mm": 20.0,
        "temperature_c": 25.0,
        "pesticide_tonnes": 0.5,
        "avg_temp": 25.0
    }
    response = client.post("/api/v1/ml/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "yield_prediction" in data
    assert isinstance(data["yield_prediction"], float)

def test_explain_endpoint():
    response = client.get("/api/v1/ml/explain")
    assert response.status_code == 200
    data = response.json()
    assert "feature_importance" in data
    assert "temperature_c" in data["feature_importance"]
