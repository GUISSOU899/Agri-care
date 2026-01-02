"use client";

import { useState, useEffect } from 'react';
import axios from 'axios';
import { Crop } from '@/types';
import { Upload, FileText, Play, Save, CheckCircle, AlertTriangle, Sprout, Download } from 'lucide-react';

export default function AdminCrops() {
    const [crops, setCrops] = useState<Crop[]>([]);
    const [file, setFile] = useState<File | null>(null);
    const [previewData, setPreviewData] = useState<any[]>([]);
    const [uploading, setUploading] = useState(false);
    const [etlStatus, setEtlStatus] = useState<string | null>(null);

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
    }, []);

    const downloadTemplate = () => {
        const csvContent = "data:text/csv;charset=utf-8,name,code,description\nBlé,wheat,Culture céréalière\nMaïs,corn,Culture d'été";
        const encodedUri = encodeURI(csvContent);
        const link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", "template_crops.csv");
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            const f = e.target.files[0];
            setFile(f);

            const reader = new FileReader();
            reader.onload = (evt) => {
                const text = evt.target?.result as string;
                const lines = text.split('\n');
                if (lines.length > 0) {
                    const headers = lines[0].split(',');
                    const data = lines.slice(1, 6).map(line => {
                        if (!line.trim()) return null;
                        const values = line.split(',');
                        return headers.reduce((obj, header, index) => {
                            if (header) obj[header.trim()] = values[index]?.trim();
                            return obj;
                        }, {} as any);
                    }).filter(Boolean);
                    setPreviewData(data);
                }
            };
            reader.readAsText(f);
        }
    };

    const handleUpload = async () => {
        if (!file) return;
        setUploading(true);
        const formData = new FormData();
        formData.append('file', file);

        try {
            const token = localStorage.getItem('token') || sessionStorage.getItem('token');
            await axios.post(`${API_BASE_URL}/admin/upload/crops-csv`, formData, {
                headers: { 'Content-Type': 'multipart/form-data', Authorization: `Bearer ${token}` }
            });
            alert('Fichier uploadé avec succès !');
        } catch (err) {
            console.error(err);
            alert('Erreur lors de l\'upload.');
        } finally {
            setUploading(false);
        }
    };

    const runEtl = async () => {
        setEtlStatus('running');
        try {
            const token = localStorage.getItem('token') || sessionStorage.getItem('token');
            await axios.post(`${API_BASE_URL}/admin/etl/run`, { type: 'crops' }, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setEtlStatus('success');
            fetchCrops();
        } catch (err) {
            console.error(err);
            setEtlStatus('error');
        }
    };

    return (
        <div>
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
                    <Sprout /> Gestion des Cultures (CSV)
                </h1>
                <button
                    onClick={downloadTemplate}
                    className="flex items-center gap-2 text-sm text-green-600 hover:text-green-800 border border-green-200 px-3 py-1.5 rounded-lg bg-green-50"
                >
                    <Download size={16} /> Modèle CSV
                </button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
                {/* Upload Section */}
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                    <h3 className="font-semibold text-lg mb-4 flex items-center gap-2">
                        1. Upload CSV
                    </h3>
                    <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-green-500 transition-colors relative">
                        <input type="file" accept=".csv" onChange={handleFileChange} className="absolute inset-0 w-full h-full opacity-0 cursor-pointer" />
                        <div className="flex flex-col items-center gap-2 pointer-events-none">
                            <Upload className="h-10 w-10 text-gray-400" />
                            <span className="text-sm text-gray-600 font-medium">Choisir un fichier crops.csv</span>
                        </div>
                    </div>
                    {file && <p className="mt-2 text-sm text-center text-green-600 font-semibold">{file.name}</p>}

                    {file && previewData.length > 0 && (
                        <div className="mt-4">
                            <h4 className="text-sm font-semibold mb-2 text-gray-500">Aperçu</h4>
                            <div className="bg-gray-50 p-2 rounded text-xs overflow-x-auto">
                                <table className="min-w-full">
                                    <thead>
                                        <tr>
                                            {Object.keys(previewData[0]).map(h => <th key={h} className="text-left p-1 border-b font-medium">{h}</th>)}
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {previewData.map((row, i) => (
                                            <tr key={i}>{Object.values(row).map((v: any, j) => <td key={j} className="p-1 border-b">{v}</td>)}</tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                            <button onClick={handleUpload} disabled={uploading} className="mt-4 w-full bg-blue-600 text-white py-2 rounded flex items-center justify-center gap-2 hover:bg-blue-700">
                                <Save size={18} /> {uploading ? 'Envoi...' : 'Enregistrer'}
                            </button>
                        </div>
                    )}
                </div>

                {/* ETL Status */}
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 flex flex-col justify-between">
                    <div>
                        <h3 className="font-semibold text-lg mb-4">2. Traitement ETL</h3>
                        <p className="text-gray-600 text-sm mb-6">Met à jour la liste des cultures.</p>
                        {etlStatus === 'running' && <div className="bg-blue-50 text-blue-800 p-4 rounded-lg flex items-center gap-3 mb-4"><div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-800"></div>Traitement...</div>}
                        {etlStatus === 'success' && <div className="bg-green-50 text-green-800 p-4 rounded-lg flex items-center gap-3 mb-4"><CheckCircle className="h-5 w-5" />Succès.</div>}
                        {etlStatus === 'error' && <div className="bg-red-50 text-red-800 p-4 rounded-lg flex items-center gap-3 mb-4"><AlertTriangle className="h-5 w-5" />Erreur.</div>}
                    </div>
                    <button onClick={runEtl} disabled={etlStatus === 'running'} className="w-full bg-green-600 text-white py-3 rounded-lg font-bold flex items-center justify-center gap-2 hover:bg-green-700 disabled:opacity-50">
                        <Play size={24} /> Lancer ETL Crops
                    </button>
                </div>
            </div>

            {/* List */}
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                <div className="flex justify-between items-center mb-4">
                    <h3 className="font-semibold text-lg">Données en base ({crops.length})</h3>
                    <button onClick={fetchCrops} className="text-sm text-gray-500 hover:text-green-600">Actualiser</button>
                </div>
                <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                            <tr>
                                <th className="py-3 px-4 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
                                <th className="py-3 px-4 text-left text-xs font-medium text-gray-500 uppercase">Use Name</th>
                                <th className="py-3 px-4 text-left text-xs font-medium text-gray-500 uppercase">Code</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200">
                            {crops.map((c) => (
                                <tr key={c.id}>
                                    <td className="py-3 px-4 text-sm text-gray-900">#{c.id}</td>
                                    <td className="py-3 px-4 text-sm font-medium text-gray-900">{c.name}</td>
                                    <td className="py-3 px-4 text-sm text-gray-500">{c.code}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
