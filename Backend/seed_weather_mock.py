from datetime import date, timedelta
import random, math
import argparse

from app.db.session import SessionLocal
from app.models.weather import WeatherDaily

def parse_ymd(s: str) -> date:
    y, m, d = map(int, s.split("-"))
    return date(y, m, d)

def iter_days(a, b):
    d = a
    while d <= b:
        yield d
        d += timedelta(days=1)

def seasonal_tmean(d):
    doy = d.timetuple().tm_yday
    return 18 + 7 * math.sin(2 * math.pi * (doy - 80) / 365.25)

def main(region_id: int, start: date, end: date, seed: int = 42):
    random.seed(seed)
    db = SessionLocal()
    try:
        # delete existing rows in range (avoid duplicates)
        db.query(WeatherDaily).filter(
            WeatherDaily.region_id == region_id,
            WeatherDaily.date >= start,
            WeatherDaily.date <= end
        ).delete(synchronize_session=False)

        rows = []
        for d in iter_days(start, end):
            tmean = seasonal_tmean(d) + random.uniform(-1.0, 1.0)
            tmin  = tmean - (5 + random.uniform(-1.0, 1.0))
            tmax  = tmean + (5 + random.uniform(-1.0, 1.0))

            p = 0.25 if d.month in (11,12,1,2) else (0.15 if d.month in (3,4) else 0.08)
            rain = (random.random() < p) * max(0.0, random.gauss(4.0, 3.0))

            eto = max(0.5, 0.15*tmean + 0.05*(tmax - tmin) + random.uniform(-0.2, 0.2))

            obj = WeatherDaily(
                region_id=region_id,
                date=d,
                tmin_c=round(tmin, 2),
                tmax_c=round(tmax, 2),
                tmean_c=round(tmean, 2),
                rainfall_mm=round(rain, 2),
                evapotranspiration_mm=round(eto, 2),
            )

            if hasattr(obj, "source"):
                obj.source = "mock"

            rows.append(obj)

        db.add_all(rows)
        db.commit()
        print(f"OK: inserted {len(rows)} rows into weather_daily for region={region_id} [{start}..{end}]")

    finally:
        db.close()

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--region_id", type=int, default=1)
    ap.add_argument("--start", type=str, default="2025-11-15")
    ap.add_argument("--end", type=str, default="2026-05-15")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    main(args.region_id, parse_ymd(args.start), parse_ymd(args.end), args.seed)
