import httpx
import asyncio

BASE_URL = "http://localhost:8000/api/v1"

ENDPOINTS = [
    "/health/",
    "/regions/",
    "/crops/",
    "/forecast/?region_id=1&crop_id=1",
    "/ml/explain",
    "/ml/predict",
    "/ml/season/dataset/status",
    "/ml/season/predict?region_id=1&crop_id=1&season_year=2025",
    "/auth/users/",
]

async def check_endpoint(client, path):
    try:
        resp = await client.get(BASE_URL + path, timeout=10.0)
        return path, resp.status_code, resp.text[:200]
    except Exception as e:
        return path, None, str(e)

async def main():
    async with httpx.AsyncClient() as client:
        tasks = [check_endpoint(client, ep) for ep in ENDPOINTS]
        results = await asyncio.gather(*tasks)
        for path, status, info in results:
            print(f"{path} -> {status}")
            if status != 200:
                print(f"  Issue: {info}")

if __name__ == "__main__":
    asyncio.run(main())
