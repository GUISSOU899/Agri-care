import requests

API_URL = "http://localhost:8000/api/v1"

def trigger_gen():
    print("Triggering Generation for Region 1, Crop 3...")
    # POST /alerts/generate?region_id=1&crop_id=3
    url = f"{API_URL}/alerts/generate"
    try:
        resp = requests.post(url, params={"region_id": 1, "crop_id": 3})
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text}")
    except Exception as e:
        print(f"Error: {e}")

def check_alerts():
    print("Checking Alerts for Region 1, Crop 3...")
    url = f"{API_URL}/alerts/"
    try:
        resp = requests.get(url, params={"region_id": 1, "crop_id": 3})
        print(f"Status: {resp.status_code}")
        alerts = resp.json()
        print(f"Alerts count: {len(alerts)}")
        for a in alerts:
            print(f"- {a['alert_type']}: {a['message']}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    trigger_gen()
    check_alerts()
