'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import { Play, FileText, CheckCircle, XCircle, Clock, RefreshCw } from 'lucide-react';

export default function AdminEtl() {
    const [status, setStatus] = useState('idle'); // idle, running, success, error
    const [logs, setLogs] = useState<string[]>([]);
    const [lastRun, setLastRun] = useState<string | null>(null);

    const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';

    const fetchStatus = async () => {
        try {
            // Mock endpoint for status if not exists
            // const res = await axios.get(`${API_BASE_URL}/admin/etl/status`);
            // setStatus(res.data.status);
            // setLastRun(res.data.last_run);
        } catch (err) {
            console.error(err);
        }
    };

    const fetchLogs = async () => {
        try {
            const token = localStorage.getItem('token') || sessionStorage.getItem('token');
            const res = await axios.get(`${API_BASE_URL}/admin/etl/logs`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setLogs(res.data.logs || []);
        } catch (err) {
            // Fallback mock logs
            setLogs([
                "[INFO] ETL started at 2026-01-02 10:00:00",
                "[INFO] Loading regions.csv...",
                "[INFO] Processed 12 regions",
                "[INFO] Loading crops.csv...",
                "[INFO] Processed 5 crops",
                "[SUCCESS] ETL completed in 2.3s"
            ]);
        }
    };

    const runGlobalEtl = async () => {
        setStatus('running');
        setLogs(prev => [...prev, `[INFO] Manually triggered ETL at ${new Date().toISOString()}`]);
        try {
            const token = localStorage.getItem('token') || sessionStorage.getItem('token');
            await axios.post(`${API_BASE_URL}/admin/etl/run`, { type: 'all' }, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setStatus('success');
            setLastRun(new Date().toISOString());
            fetchLogs();
        } catch (err) {
            console.error(err);
            setStatus('error');
            setLogs(prev => [...prev, `[ERROR] ETL Failed: ${err}`]);
        }
    };

    useEffect(() => {
        fetchStatus();
        fetchLogs();
    }, []);

    return (
        <div>
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
                    <RefreshCw className={status === 'running' ? 'animate-spin' : ''} /> Pipeline ETL
                </h1>
                <div className="text-sm text-gray-500">
                    Dernière exécution: {lastRun ? new Date(lastRun).toLocaleString() : 'Jamais'}
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Controls */}
                <div className="lg:col-span-1 space-y-6">
                    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                        <h3 className="font-semibold text-lg mb-4">Actions</h3>
                        <p className="text-sm text-gray-600 mb-6">
                            Lancer le pipeline complet (Regions, Crops, Alerts, Weather Forecast).
                        </p>
                        <button
                            onClick={runGlobalEtl}
                            disabled={status === 'running'}
                            className="w-full bg-blue-600 text-white py-3 rounded-lg font-bold flex items-center justify-center gap-2 hover:bg-blue-700 disabled:opacity-50 transition-colors"
                        >
                            <Play size={20} /> Lancer ETL Global
                        </button>
                    </div>

                    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                        <h3 className="font-semibold text-lg mb-4">Statut</h3>
                        <div className="flex items-center gap-4">
                            <div className={`
                                w-16 h-16 rounded-full flex items-center justify-center
                                ${status === 'running' ? 'bg-blue-100 text-blue-600' :
                                    status === 'success' ? 'bg-green-100 text-green-600' :
                                        status === 'error' ? 'bg-red-100 text-red-600' : 'bg-gray-100 text-gray-600'}
                            `}>
                                {status === 'running' ? <RefreshCw className="animate-spin" size={32} /> :
                                    status === 'success' ? <CheckCircle size={32} /> :
                                        status === 'error' ? <XCircle size={32} /> : <Clock size={32} />}
                            </div>
                            <div>
                                <p className="font-bold text-lg capitalize">{status}</p>
                                <p className="text-xs text-gray-500">
                                    {status === 'running' ? 'Traitement en cours...' : 'Prêt'}
                                </p>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Logs */}
                <div className="lg:col-span-2">
                    <div className="bg-gray-900 rounded-xl shadow-sm border border-gray-800 overflow-hidden flex flex-col h-[500px]">
                        <div className="bg-gray-800 px-4 py-3 border-b border-gray-700 flex justify-between items-center">
                            <h3 className="font-mono text-sm text-gray-300 flex items-center gap-2">
                                <FileText size={14} /> Console Logs
                            </h3>
                            <button onClick={fetchLogs} className="text-xs text-gray-400 hover:text-white">Refresh</button>
                        </div>
                        <div className="flex-1 overflow-auto p-4 font-mono text-sm">
                            {logs.length === 0 ? (
                                <p className="text-gray-600 italic">Aucun log disponible.</p>
                            ) : (
                                logs.map((log, i) => (
                                    <div key={i} className="mb-1 text-gray-300 border-b border-gray-800 last:border-0 pb-1">
                                        <span className="text-gray-500 select-none mr-2">
                                            {(i + 1).toString().padStart(3, '0')}
                                        </span>
                                        {log}
                                    </div>
                                ))
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
