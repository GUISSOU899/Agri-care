"use client";

import { useState, useEffect } from 'react';
import axios from 'axios';
import { Alert, Region, Crop } from '@/types';
import { Plus, AlertTriangle } from 'lucide-react';

export default function AdminAlerts() {
    const [alerts, setAlerts] = useState<Alert[]>([]);
    const [regions, setRegions] = useState<Region[]>([]);
    const [crops, setCrops] = useState<Crop[]>([]);

    // Form state
    const [formData, setFormData] = useState({
        region_id: '',
        crop_id: '',
        alert_type: 'Manual Alert',
        message: '',
        severity: 'info'
    });

    const [loading, setLoading] = useState(false);
    const [msg, setMsg] = useState('');

    const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';

    const fetchInitialData = async () => {
        try {
            const [alertsRes, regionsRes, cropsRes] = await Promise.all([
                axios.get(`${API_BASE_URL}/alerts/`),
                axios.get(`${API_BASE_URL}/regions/`),
                axios.get(`${API_BASE_URL}/crops/`)
            ]);
            setAlerts(alertsRes.data);
            setRegions(regionsRes.data);
            setCrops(cropsRes.data);
        } catch (err) {
            console.error(err);
        }
    };

    useEffect(() => {
        fetchInitialData();
    }, [API_BASE_URL]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        try {
            await axios.post(`${API_BASE_URL}/alerts/`, {
                region_id: parseInt(formData.region_id),
                crop_id: formData.crop_id ? parseInt(formData.crop_id) : null,
                alert_type: formData.alert_type,
                message: formData.message,
                severity: formData.severity
            });
            setMsg('Alert created successfully!');
            setFormData({ ...formData, message: '', severity: 'info' });

            // Refresh alerts
            const alertsRes = await axios.get(`${API_BASE_URL}/alerts/`);
            setAlerts(alertsRes.data);
        } catch (err) {
            console.error(err);
            setMsg('Error creating alert.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div>
            <h1 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-2">
                <AlertTriangle /> Manage Alerts
            </h1>

            {/* Create Form */}
            <div className="bg-gray-50 p-6 rounded-lg mb-8 border border-gray-200">
                <h3 className="font-semibold mb-4 text-gray-700">Create New Alert</h3>
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium mb-1">Region</label>
                            <select
                                required
                                className="w-full p-2 border rounded"
                                value={formData.region_id}
                                onChange={(e) => setFormData({ ...formData, region_id: e.target.value })}
                            >
                                <option value="">Select Region</option>
                                {regions.map(r => <option key={r.id} value={r.id}>{r.name}</option>)}
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-1">Crop (Optional)</label>
                            <select
                                className="w-full p-2 border rounded"
                                value={formData.crop_id}
                                onChange={(e) => setFormData({ ...formData, crop_id: e.target.value })}
                            >
                                <option value="">Global Alert (All Crops)</option>
                                {crops.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                            </select>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium mb-1">Level</label>
                            <select
                                className="w-full p-2 border rounded"
                                value={formData.severity}
                                onChange={(e) => setFormData({ ...formData, severity: e.target.value })}
                            >
                                <option value="info">Info</option>
                                <option value="warning">Warning</option>
                                <option value="critical">Critical</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-1">Type</label>
                            <input
                                type="text"
                                className="w-full p-2 border rounded"
                                value={formData.alert_type}
                                onChange={(e) => setFormData({ ...formData, alert_type: e.target.value })}
                            />
                        </div>
                    </div>

                    <div>
                        <label className="block text-sm font-medium mb-1">Message</label>
                        <textarea
                            required
                            className="w-full p-2 border rounded"
                            rows={2}
                            value={formData.message}
                            onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 flex items-center gap-2"
                    >
                        <Plus size={18} /> {loading ? 'Saving...' : 'Create Alert'}
                    </button>
                </form>
                {msg && <p className="mt-2 text-sm text-blue-600">{msg}</p>}
            </div>

            {/* List */}
            <div className="space-y-2">
                {alerts.map(alert => (
                    <div key={alert.id} className="bg-white border rounded p-4 flex justify-between items-center">
                        <div>
                            <span className={`inline-block px-2 py-0.5 text-xs rounded uppercase font-bold mr-2 
                                ${alert.severity === 'critical' ? 'bg-red-100 text-red-800' :
                                    alert.severity === 'warning' ? 'bg-amber-100 text-amber-800' : 'bg-blue-100 text-blue-800'}`}>
                                {alert.severity}
                            </span>
                            <span className="font-medium text-gray-800">{alert.alert_type}:</span> {alert.message}
                        </div>
                        <div className="text-xs text-gray-500">
                            {new Date(alert.created_at).toLocaleDateString()}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
