from sqlalchemy.orm import Session
from datetime import date
from app.models import Forecast, Alert

def generate_alerts_from_forecasts(db: Session, region_id: int, crop_id: int = None):
    """
    Scans forecasts for a given region (and optional crop) and generates alerts.
    """
    query = db.query(Forecast).filter(
        Forecast.region_id == region_id,
        Forecast.date >= date.today()
    )
    
    if crop_id:
        query = query.filter(Forecast.crop_id == crop_id)
        
    # Cleanup old auto-generated alerts for this context to avoid stale/duplicate alerts
    # We only delete alerts that are likely auto-generated (based on type) and not resolved?
    # Or just wipe all active auto-alerts for this region/crop view? Using a flag or just by type is safer.
    auto_types = ["Heat Wave", "High Heat", "Frost Risk", "Heavy Rain"]
    
    cleanup_query = db.query(Alert).filter(
        Alert.region_id == region_id,
        Alert.alert_type.in_(auto_types),
        Alert.resolved_at == None
    )
    if crop_id:
        cleanup_query = cleanup_query.filter(Alert.crop_id == crop_id)
        
    cleanup_query.delete(synchronize_session=False)

    forecasts = query.all()
    
    new_alerts = []
    
    for f in forecasts:
        # Determine values to check (fallback to temperature_c if new cols missing)
        tmax = f.tmax_c if f.tmax_c is not None else f.temperature_c
        tmin = f.tmin_c if f.tmin_c is not None else f.temperature_c
        rain = f.rainfall_mm

        # High Heat
        if tmax and tmax > 40:
            new_alerts.append(Alert(
                region_id=region_id,
                crop_id=f.crop_id,
                alert_type="Heat Wave",
                message=f"Extreme temperature ({tmax}°C) expected on {f.date}",
                severity="critical"
            ))
        elif tmax and tmax > 35:
            new_alerts.append(Alert(
                region_id=region_id,
                crop_id=f.crop_id,
                alert_type="High Heat",
                message=f"High temperature ({tmax}°C) expected on {f.date}",
                severity="warning"
            ))
            
        # Frost
        if tmin and tmin < 2:
            new_alerts.append(Alert(
                region_id=region_id,
                crop_id=f.crop_id,
                alert_type="Frost Risk",
                message=f"Low temperature ({tmin}°C) expected on {f.date}",
                severity="warning"
            ))
            
        # Rain
        if rain and rain > 30:
             new_alerts.append(Alert(
                region_id=region_id,
                crop_id=f.crop_id,
                alert_type="Heavy Rain",
                message=f"Heavy rainfall ({rain}mm) expected on {f.date}",
                severity="warning"
            ))

    # Bulk insert? Or loop add?
    count = 0
    for alert in new_alerts:
        # Check if similar alert exists to prevent spam
        exists = db.query(Alert).filter(
            Alert.region_id == alert.region_id,
            Alert.crop_id == alert.crop_id,
            Alert.alert_type == alert.alert_type,
            Alert.message == alert.message
        ).first()
        
        if not exists:
            db.add(alert)
            count += 1
            
    db.commit()
    return count
