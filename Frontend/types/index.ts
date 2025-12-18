export interface Region {
    id: number;
    name: string;
    latitude: number;
    longitude: number;
}

export interface Crop {
    id: number;
    name: string;
    code: string;
    description?: string;
}

export interface Forecast {
    id: number;
    region_id: number;
    crop_id: number;
    date: string;
    horizon_days: number;
    yield_index: number;
    created_at: string;
}

export interface Alert {
    id: number;
    region_id: number;
    crop_id?: number;
    alert_type: string;
    message: string;
    severity: "info" | "warning" | "critical";
    created_at: string;
    resolved_at?: string;
}

// Mocking irrigation recommendation structure for now as it wasn't explicitly in backend yet
// But we need it for the table. We can derive it or add it to forecast endpoint later.
// For now, let's assume valid forecast data includes irrigation info or we fetch it separately.
// The user request mentioned "daily irrigation recommendation". 
// Since backend doesn't have a specific irrigation endpoint yet (only weather/forecast/alert),
// we might simulate it based on weather or just use a placeholder field if using real backend.
// Re-reading task: "Create an IrrigationTable component that displays... daily irrigation recommendation... Columns: date, irrigation_mm..."
// If backend doesn't provide it, I might need to mock it on frontend or assume it comes with forecast.
// Let's define a type for it.
export interface IrrigationRecommendation {
    date: string;
    irrigation_mm: number;
    comment?: string;
}
