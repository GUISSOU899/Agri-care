"use client";

import { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import axios from 'axios';
import { Region, Crop, Forecast, IrrigationRecommendation } from '@/types';
import IrrigationTable from '@/components/IrrigationTable';
import AlertsPanel from '@/components/AlertsPanel';
import { Sprout, Droplets, Map as MapIcon, Calendar } from 'lucide-react';

// Dynamic import for MapView to avoid SSR issues with Leaflet
const MapView = dynamic(() => import('@/components/MapView'), { ssr: false });
const ForecastChart = dynamic(() => import('@/components/ForecastChart'), { ssr: false });

export default function Dashboard() {
    const [regions, setRegions] = useState<Region[]>([]);
    const [crops, setCrops] = useState<Crop[]>([]);
    const [selectedRegionId, setSelectedRegionId] = useState<number | undefined>(undefined);
    const [selectedCropId, setSelectedCropId] = useState<number | undefined>(undefined);
    const [forecasts, setForecasts] = useState<Forecast[]>([]);
    const [loading, setLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);

    // Mock irrigation data generation based on forecast (since backend doesn't provide it yet)
    const [irrigationData, setIrrigationData] = useState<IrrigationRecommendation[]>([]);

    const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';

    // Fetch initial data
    useEffect(() => {
        const fetchData = async () => {
            try {
                const [regionsRes, cropsRes] = await Promise.all([
                    axios.get(`${API_BASE_URL}/regions/`),
                    axios.get(`${API_BASE_URL}/crops/`)
                ]);
                setRegions(regionsRes.data);
                setCrops(cropsRes.data);

                // Select first region/crop by default if available
                if (regionsRes.data.length > 0) setSelectedRegionId(regionsRes.data[0].id);
                if (cropsRes.data.length > 0) setSelectedCropId(cropsRes.data[0].id);
            } catch (err) {
                console.error("Failed to load initial data", err);
                setError("Failed to load regions or crops. Please check backend connection.");
            }
        };
        fetchData();
    }, [API_BASE_URL]);

    const handleLoadForecast = async () => {
        if (!selectedRegionId || !selectedCropId) return;

        setLoading(true);
        setError(null);
        try {
            const res = await axios.get(`${API_BASE_URL}/forecast/`, {
                params: {
                    region_id: selectedRegionId,
                    crop_id: selectedCropId
                }
            });

            const forecastData: Forecast[] = res.data;
            setForecasts(forecastData);

            // Generate mock irrigation recommendations derived from forecast/date
            // In a real scenario, this would come from an endpoint like /api/v1/irrigation
            const mockIrrigation: IrrigationRecommendation[] = forecastData.map(f => ({
                date: f.date,
                irrigation_mm: Math.round(Math.random() * 10), // Random 0-10mm
                comment: Math.random() > 0.7 ? "High heat expected, irrigate heavily." : "Standard irrigation."
            }));
            setIrrigationData(mockIrrigation);

        } catch (err) {
            console.error("Failed to load forecast", err);
            setError("Failed to load forecast data.");
            setForecasts([]);
            setIrrigationData([]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex flex-col font-sans text-gray-900">
            <main className="container mx-auto px-4 py-8 flex-grow space-y-6">

                {/* Stats / Intro */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center gap-4">
                        <div className="p-3 bg-blue-100 text-blue-600 rounded-full">
                            <MapIcon size={24} />
                        </div>
                        <div>
                            <p className="text-sm text-gray-500 font-medium">Regions</p>
                            <p className="text-2xl font-bold">{regions.length}</p>
                        </div>
                    </div>
                    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center gap-4">
                        <div className="p-3 bg-amber-100 text-amber-600 rounded-full">
                            <Sprout size={24} />
                        </div>
                        <div>
                            <p className="text-sm text-gray-500 font-medium">Crops</p>
                            <p className="text-2xl font-bold">{crops.length}</p>
                        </div>
                    </div>
                    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center gap-4">
                        <div className="p-3 bg-green-100 text-green-600 rounded-full">
                            <Calendar size={24} />
                        </div>
                        <div>
                            <p className="text-sm text-gray-500 font-medium">Forecast Horizon</p>
                            <p className="text-2xl font-bold">30 Days</p>
                        </div>
                    </div>
                </div>

                {/* Main Content Area */}
                <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">

                    {/* Controls & Map Column */}
                    <div className="lg:col-span-1 space-y-6">
                        {/* Controls */}
                        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                            <h2 className="text-lg font-semibold mb-4 text-gray-800 flex items-center gap-2">
                                <Droplets size={20} className="text-blue-500" />
                                Configuration
                            </h2>

                            <div className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Region</label>
                                    <select
                                        className="w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 p-2 border"
                                        value={selectedRegionId || ''}
                                        onChange={(e) => setSelectedRegionId(Number(e.target.value))}
                                    >
                                        <option value="">Select Region</option>
                                        {regions.map(r => (
                                            <option key={r.id} value={r.id}>{r.name}</option>
                                        ))}
                                    </select>
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Crop</label>
                                    <select
                                        className="w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 p-2 border"
                                        value={selectedCropId || ''}
                                        onChange={(e) => setSelectedCropId(Number(e.target.value))}
                                    >
                                        <option value="">Select Crop</option>
                                        {crops.map(c => (
                                            <option key={c.id} value={c.id}>{c.name}</option>
                                        ))}
                                    </select>
                                </div>

                                <button
                                    onClick={handleLoadForecast}
                                    disabled={loading || !selectedRegionId || !selectedCropId}
                                    className={`w-full py-2 px-4 rounded-md text-white font-medium transition-colors ${loading || !selectedRegionId || !selectedCropId
                                            ? 'bg-gray-400 cursor-not-allowed'
                                            : 'bg-green-600 hover:bg-green-700'
                                        }`}
                                >
                                    {loading ? 'Loading...' : 'Load Forecast'}
                                </button>

                                {error && (
                                    <div className="p-3 bg-red-50 text-red-700 text-sm rounded-md border border-red-200">
                                        {error}
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* Map Preview */}
                        <div className="bg-white p-2 rounded-xl shadow-sm border border-gray-200">
                            <MapView
                                regions={regions}
                                selectedRegionId={selectedRegionId}
                                onSelectRegion={setSelectedRegionId}
                            />
                        </div>
                    </div>

                    {/* Charts & Data Column */}
                    <div className="lg:col-span-3 space-y-6">

                        {/* Forecast Chart */}
                        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 h-[400px]">
                            <ForecastChart data={forecasts} />
                        </div>

                        {/* Alerts and Irrigation Grid */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div className="h-full">
                                <AlertsPanel regionId={selectedRegionId} cropId={selectedCropId} />
                            </div>
                            <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden h-full">
                                <IrrigationTable data={irrigationData} />
                            </div>
                        </div>

                    </div>
                </div>
            </main>
        </div>
    );
}
