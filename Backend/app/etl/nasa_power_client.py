import os
import httpx
from datetime import date
from dateutil import parser
from dateutil.relativedelta import relativedelta
from typing import List, Dict

# Base URL for NASA POWER API, e.g., https://power.larc.nasa.gov/api/temporal/daily
BASE_URL = os.getenv("NASA_POWER_BASE_URL", "https://power.larc.nasa.gov/api/temporal/daily")
API_KEY = os.getenv("NASA_POWER_API_KEY", "")  # optional

def _format_date(d: date) -> str:
    """Format date as YYYYMMDD required by the API."""
    return d.strftime("%Y%m%d")

def fetch_daily_weather(lat: float, lon: float, start_date: date, end_date: date) -> List[Dict]:
    """Fetch daily weather data from NASA POWER.

    Args:
        lat: Latitude of the location.
        lon: Longitude of the location.
        start_date: Start date (inclusive).
        end_date: End date (inclusive).

    Returns:
        A list of dictionaries, each containing date and weather variables.
    """
    params = {
        "latitude": lat,
        "longitude": lon,
        "start": _format_date(start_date),
        "end": _format_date(end_date),
        "parameters": ",".join(["T2M", "T2M_MAX", "T2M_MIN", "PRECTOT"]),
        "community": "AG",
        "format": "JSON",
    }
    if API_KEY:
        params["api_key"] = API_KEY
    # Construct the full endpoint for point data
    url = f"{BASE_URL}/point"
    try:
        response = httpx.get(url, params=params, timeout=30.0)
        response.raise_for_status()
        data = response.json()
        # Extract the daily values
        daily = data.get("properties", {}).get("parameter", {})
        records = []
        dates = daily.get("T2M", {}).keys()
        for d in dates:
            record = {
                "date": parser.parse(d).date(),
                "tavg": daily.get("T2M", {}).get(d),
                "tmax": daily.get("T2M_MAX", {}).get(d),
                "tmin": daily.get("T2M_MIN", {}).get(d),
                "precipitation": daily.get("PRECTOT", {}).get(d),
            }
            records.append(record)
        return records
    except Exception as e:
        # In production you would use proper logging
        raise RuntimeError(f"Failed to fetch NASA POWER data: {e}")
