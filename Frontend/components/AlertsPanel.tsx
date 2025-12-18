"use client";

import { useState, useEffect } from 'react';
import axios from 'axios';
import { AlertCircle, AlertTriangle, Info, CheckCircle } from 'lucide-react';
import { Alert, Region, Crop } from '@/types';

interface AlertsPanelProps {
    regionId?: number;
    cropId?: number;
}

export default function AlertsPanel({ regionId, cropId }: AlertsPanelProps) {
    const [alerts, setAlerts] = useState<Alert[]>([]);
    const [loading, setLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);

    const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';

    const fetchAlerts = async () => {
        // Only fetch if we have at least a region, or fetch all if nothing selected?
        // Requirement says: "Si regionId et cropId sont définis, le composant doit appeler..."
        // Let's allow fetching global alerts if nothing selected, or just return empty for now to match spec strictness.
        // Spec: "Si regionId et cropId sont définis..." -> let's fetch.

        if (!regionId && !cropId) {
            setAlerts([]);
            return;
        }

        setLoading(true);
        try {
            const params: any = {};
            if (regionId) params.region_id = regionId;
            if (cropId) params.crop_id = cropId;

            const res = await axios.get(`${API_BASE_URL}/alerts/`, { params });
            setAlerts(res.data);
            setError(null);
        } catch (err) {
            console.error("Failed to load alerts", err);
            // "erreur silencieuse (log en console)" -> maybe don't set user visible error?
            // But debugging is nice. Let's keep it simple.
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchAlerts();
    }, [regionId, cropId, API_BASE_URL]);

    const handleRunAnalysis = async () => {
        if (!regionId) return;
        setLoading(true);
        try {
            const params: any = { region_id: regionId };
            if (cropId) params.crop_id = cropId;

            await axios.post(`${API_BASE_URL}/alerts/generate`, null, {
                params: params
            });
            // Refresh list
            await fetchAlerts();
        } catch (err) {
            console.error("Analysis failed", err);
        } finally {
            setLoading(false);
        }
    };

    const getSeverityIcon = (severity: string) => {
        switch (severity) {
            case 'critical': return <AlertCircle className="text-red-600" size={20} />;
            case 'warning': return <AlertTriangle className="text-amber-600" size={20} />;
            case 'info': return <Info className="text-blue-600" size={20} />;
            default: return <Info className="text-gray-600" size={20} />;
        }
    };

    const getSeverityClass = (severity: string) => {
        switch (severity) {
            case 'critical': return 'bg-red-50 border-red-100 text-red-900';
            case 'warning': return 'bg-amber-50 border-amber-100 text-amber-900';
            case 'info': return 'bg-blue-50 border-blue-100 text-blue-900';
            default: return 'bg-gray-50 border-gray-100 text-gray-900';
        }
    };

    if (!regionId && !cropId) {
        return (
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                <h2 className="text-lg font-semibold mb-4 text-gray-800 flex items-center gap-2">
                    <AlertCircle size={20} className="text-orange-500" />
                    Alerts
                </h2>
                <div className="text-gray-500 text-sm italic">
                    Select a Region/Crop to view alerts.
                </div>
            </div>
        );
    }

    return (
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 h-full flex flex-col">
            <div className="flex justify-between items-center mb-4">
                <h2 className="text-lg font-semibold text-gray-800 flex items-center gap-2">
                    <AlertCircle size={20} className="text-orange-500" />
                    Active Alerts
                </h2>
                {regionId && (
                    <button
                        onClick={handleRunAnalysis}
                        disabled={loading}
                        className="text-xs bg-indigo-50 text-indigo-600 px-3 py-1 rounded hover:bg-indigo-100 disabled:opacity-50"
                    >
                        {loading ? 'Analyzing...' : 'Run Analysis'}
                    </button>
                )}
            </div>

            {alerts.length === 0 && !loading ? (
                <div className="flex flex-col items-center justify-center p-6 text-gray-400">
                    <CheckCircle size={32} className="mb-2 text-green-100" />
                    <p className="text-sm">No active alerts for this selection.</p>
                </div>
            ) : (
                <div className="space-y-3 max-h-[300px] overflow-y-auto pr-2">
                    {alerts.map(alert => (
                        <div key={alert.id} className={`p-3 rounded-lg border flex gap-3 ${getSeverityClass(alert.severity)}`}>
                            <div className="mt-0.5 flex-shrink-0">
                                {getSeverityIcon(alert.severity)}
                            </div>
                            <div>
                                <h4 className="font-medium text-sm">{alert.alert_type}</h4>
                                <p className="text-xs opacity-90 mt-1">{alert.message}</p>
                                <div className="text-[10px] opacity-70 mt-2 text-right">
                                    {new Date(alert.created_at).toLocaleDateString()}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
