"use client";

import { useState, useEffect } from 'react';
import axios from 'axios';
import { Crop } from '@/types';
import { Plus, Trash2, Sprout } from 'lucide-react';

export default function AdminCrops() {
    const [crops, setCrops] = useState<Crop[]>([]);
    const [formData, setFormData] = useState({ name: '', code: '', description: '' });
    const [loading, setLoading] = useState(false);
    const [msg, setMsg] = useState('');

    const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';

    const fetchCrops = async () => {
        try {
            const res = await axios.get(`${API_BASE_URL}/crops/`);
            setCrops(res.data);
        } catch (err) {
            console.error(err);
        }
    };

    useEffect(() => {
        fetchCrops();
    }, [API_BASE_URL]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        try {
            await axios.post(`${API_BASE_URL}/crops/`, formData);
            setMsg('Crop created successfully!');
            setFormData({ name: '', code: '', description: '' });
            fetchCrops();
        } catch (err) {
            console.error(err);
            setMsg('Error creating crop.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div>
            <h1 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-2">
                <Sprout /> Manage Crops
            </h1>

            {/* Create Form */}
            <div className="bg-gray-50 p-6 rounded-lg mb-8 border border-gray-200">
                <h3 className="font-semibold mb-4 text-gray-700">Add New Crop</h3>
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div className="flex flex-col md:flex-row gap-4">
                        <div className="flex-1">
                            <label className="block text-sm font-medium mb-1">Name</label>
                            <input
                                type="text" required
                                className="w-full p-2 border rounded"
                                value={formData.name}
                                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                placeholder="Wheat"
                            />
                        </div>
                        <div className="flex-1">
                            <label className="block text-sm font-medium mb-1">Code</label>
                            <input
                                type="text" required
                                className="w-full p-2 border rounded"
                                value={formData.code}
                                onChange={(e) => setFormData({ ...formData, code: e.target.value })}
                                placeholder="wheat"
                            />
                        </div>
                    </div>
                    <div>
                        <label className="block text-sm font-medium mb-1">Description</label>
                        <input
                            type="text"
                            className="w-full p-2 border rounded"
                            value={formData.description}
                            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                            placeholder="Optional description"
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 flex items-center gap-2"
                    >
                        <Plus size={18} /> {loading ? 'Saving...' : 'Add Crop'}
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
                            <th className="py-3 px-4 text-left text-xs font-medium text-gray-500 uppercase">Code</th>
                            <th className="py-3 px-4 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                        {crops.map((c) => (
                            <tr key={c.id}>
                                <td className="py-3 px-4 text-sm text-gray-900">#{c.id}</td>
                                <td className="py-3 px-4 text-sm font-medium text-gray-900">{c.name}</td>
                                <td className="py-3 px-4 text-sm text-gray-500">{c.code}</td>
                                <td className="py-3 px-4 text-sm">
                                    <button className="text-red-500 hover:text-red-700 opacity-50 cursor-not-allowed">
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
