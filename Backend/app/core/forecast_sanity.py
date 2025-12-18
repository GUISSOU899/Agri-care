from datetime import date

def sanitize_forecast(temperature_c: float, rainfall_mm: float, forecast_date: date) -> tuple[float, float]:
    """
    Checks and adjusts forecast values to be within plausible ranges (for Morocco).
    
    Rules:
    - Temp: [-5, 50]
    - Rain: [0, 200]
    - Winter (Dec-Feb): Max Temp < 30. If > 30, cap it or check logic.
    - Summer (Jun-Aug): Max Temp < 50.
    
    Returns:
        tuple (sanitized_temp, sanitized_rain)
    """
    sanitized_temp = temperature_c
    sanitized_rain = rainfall_mm
    
    # Basic bounds
    if sanitized_temp is not None:
        sanitized_temp = max(-5.0, min(50.0, sanitized_temp))
        
    if sanitized_rain is not None:
        sanitized_rain = max(0.0, min(200.0, sanitized_rain))
        
    # Seasonal checks
    month = forecast_date.month
    
    # Winter (Dec, Jan, Feb)
    if month in [12, 1, 2]:
        # Cap extreme heat in winter. 30 is already very generous for winter max.
        if sanitized_temp > 30.0:
            sanitized_temp = 25.0 # Replace outlier with a reasonable warm winter day
            
    # Rain consistency? (Optional)
    
    return round(sanitized_temp, 1), round(sanitized_rain, 1)
