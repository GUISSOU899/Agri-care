import requests

def check_openapi():
    try:
        url = "http://localhost:8000/api/v1/openapi.json"
        resp = requests.get(url)
        data = resp.json()
        
        paths = data.get("paths", {})
        gen_path = "/api/v1/alerts/generate"
        
        print(f"Checking for {gen_path}...")
        if gen_path in paths:
            print("FOUND! Endpoint exists in OpenAPI spec.")
        else:
            print("MISSING! Endpoint NOT found in spec.")
            print("Available paths starting with /api/v1/alerts:")
            for p in paths.keys():
                if "/alerts" in p:
                    print(f" - {p}")
                    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_openapi()
