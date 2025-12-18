"use client";

import { useState, useEffect } from 'react';
import axios from 'axios';
import { Region } from '@/types';
import { Plus, Trash2, MapPin } from 'lucide-react';

export default function AdminRegions() {
    const [regions, setRegions] = useState<Region[]>([]);
    const [formData, setFormData] = useState({ name: '', latitude: '', longitude: '' });
    const [loading, setLoading] = useState(false);
    const [msg, setMsg] = useState('');

    const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';

    const fetchRegions = async () => {
        try {
            const res = await axios.get(`${API_BASE_URL}/regions/`);
            setRegions(res.data);
        } catch (err) {
            console.error(err);
        }
    };

    useEffect(() => {
        fetchRegions();
    }, [API_BASE_URL]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        try {
            await axios.post(`${API_BASE_URL}/regions/`, {
                name: formData.name,
                latitude: parseFloat(formData.latitude),
                longitude: parseFloat(formData.longitude)
            });
            setMsg('Region created successfully!');
            setFormData({ name: '', latitude: '', longitude: '' });
            fetchRegions();
        } catch (err) {
            console.error(err);
            setMsg('Error creating region.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div>
            <h1 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-2">
                <MapPin /> Manage Regions
            </h1>

            {/* Create Form */}
            <div className="bg-gray-50 p-6 rounded-lg mb-8 border border-gray-200">
                <h3 className="font-semibold mb-4 text-gray-700">Add New Region</h3>
                <form onSubmit={handleSubmit} className="flex flex-col md:flex-row gap-4 items-end">
                    <div className="flex-1 w-full">
                        <label className="block text-sm font-medium mb-1">Name</label>
                        <input
                            type="text"
                            required
                            className="w-full p-2 border rounded"
                            value={formData.name}
                            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                        />
                    </div>
                    <div className="w-full md:w-32">
                        <label className="block text-sm font-medium mb-1">Lat</label>
                        <input
                            type="number" step="any" required
                            className="w-full p-2 border rounded"
                            value={formData.latitude}
                            onChange={(e) => setFormData({ ...formData, latitude: e.target.value })}
                        />
                    </div>
                    <div className="w-full md:w-32">
                        <label className="block text-sm font-medium mb-1">Lon</label>
                        <input
                            type="number" step="any" required
                            className="w-full p-2 border rounded"
                            value={formData.longitude}
                            onChange={(e) => setFormData({ ...formData, longitude: e.target.value })}
                        />
                    </div>
                    <button
                        type="submit"
                        disabled={loading}
                        className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 flex items-center gap-2"
                    >
                        <Plus size={18} /> {loading ? 'Saving...' : 'Add'}
                    </button>
                </form>
                {msg && <p className="mt-2 text-sm text-blue-600">{msg}</p>}
            </div>

            {/* List */}
            <div className="overflow-x-auto">
                <table className="min-w-full bg-white border border-gray-200">
                    <thead className="bg-gray-50">
                        <tr>
                            <th className="py-3 px-4 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
                            <th className="py-3 px-4 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                            <th className="py-3 px-4 text-left text-xs font-medium text-gray-500 uppercase">Location</th>
                            <th className="py-3 px-4 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                        {regions.map((r) => (
                            <tr key={r.id}>
                                <td className="py-3 px-4 text-sm text-gray-900">#{r.id}</td>
                                <td className="py-3 px-4 text-sm font-medium text-gray-900">{r.name}</td>
                                <td className="py-3 px-4 text-sm text-gray-500">{r.latitude}, {r.longitude}</td>
                                <td className="py-3 px-4 text-sm">
                                    <button className="text-red-500 hover:text-red-700 opacity-50 cursor-not-allowed" title="Delete not implemented">
                                        <Trash2 size={18} />
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
