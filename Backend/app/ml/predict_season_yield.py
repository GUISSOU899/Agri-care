# Wrapper for script execution of predict_seasonal_yield
import argparse
from app.services.season_yield_service import SeasonYieldService

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--region_id", type=int, required=True)
    parser.add_argument("--crop_id", type=int, required=True)
    parser.add_argument("--season_year", type=int, required=True)
    args = parser.parse_args()
    
    res, err = SeasonYieldService.predict_seasonal_yield(args.region_id, args.crop_id, args.season_year)
    if err:
        print(f"Error: {err}")
    else:
        import json
        print(json.dumps(res, indent=2))
