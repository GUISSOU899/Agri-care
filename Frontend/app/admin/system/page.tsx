'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import { Settings, ShieldCheck, Database, Cpu, Globe, Server } from 'lucide-react';

export default function AdminSystem() {
    const [health, setHealth] = useState<any>(null);
    const [config, setConfig] = useState<any>({
        version: "v1.2.0",
        environment: "production", // Mock
        csv_path: "/data/uploads/",
        retrain_policy: "auto_after_upload"
    });

    const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';

    useEffect(() => {
        const fetchHealth = async () => {
            try {
                const res = await axios.get(`${API_BASE_URL}/health/`);
                setHealth(res.data);
            } catch (err) {
                setHealth({ status: 'error', db: 'unreachable', redis: 'unreachable' });
            }
        };
        fetchHealth();
    }, []);

    const StatusBadge = ({ status }: { status: string }) => {
        const isOk = status === 'connected' || status === 'ok' || status === 'online';
        return (
            <span className={`px-2 py-1 rounded text-xs font-bold uppercase ${isOk ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                }`}>
                {status || 'Unknown'}
            </span>
        );
    };

    return (
        <div>
            <h1 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-2">
                <Settings /> Système & Configuration
            </h1>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* Health Monitor */}
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                    <h3 className="font-semibold text-lg mb-4 flex items-center gap-2">
                        <ShieldCheck className="text-green-600" /> État des Services
                    </h3>
                    <div className="space-y-4">
                        <div className="flex justify-between items-center p-3 border-b last:border-0">
                            <div className="flex items-center gap-3">
                                <Globe size={18} className="text-gray-400" />
                                <span className="text-gray-700">API Gateway</span>
                            </div>
                            <StatusBadge status="online" />
                        </div>
                        <div className="flex justify-between items-center p-3 border-b last:border-0">
                            <div className="flex items-center gap-3">
                                <Database size={18} className="text-gray-400" />
                                <span className="text-gray-700">MySQL Database</span>
                            </div>
                            <StatusBadge status={health?.db} />
                        </div>
                        <div className="flex justify-between items-center p-3 border-b last:border-0">
                            <div className="flex items-center gap-3">
                                <Cpu size={18} className="text-gray-400" />
                                <span className="text-gray-700">Redis Cache</span>
                            </div>
                            <StatusBadge status={health?.redis} />
                        </div>
                        <div className="flex justify-between items-center p-3 border-b last:border-0">
                            <div className="flex items-center gap-3">
                                <Server size={18} className="text-gray-400" />
                                <span className="text-gray-700">ML Service</span>
                            </div>
                            <StatusBadge status="online" />
                            {/* Mock ML status unless endpoint exists */}
                        </div>
                    </div>
                </div>

                {/* Configuration */}
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                    <h3 className="font-semibold text-lg mb-4 flex items-center gap-2">
                        <Settings className="text-blue-600" /> Paramètres
                    </h3>
                    <div className="space-y-4">
                        <div className="grid grid-cols-2 gap-4 text-sm">
                            <div className="text-gray-500">Version API</div>
                            <div className="font-mono">{config.version}</div>

                            <div className="text-gray-500">Environnement</div>
                            <div className="font-medium capitalize">{config.environment}</div>

                            <div className="text-gray-500">Dossier Uploads</div>
                            <div className="font-mono bg-gray-50 p-1 rounded inline-block">{config.csv_path}</div>

                            <div className="text-gray-500">Politique Retrain</div>
                            <div className="font-medium text-blue-600">{config.retrain_policy}</div>
                        </div>

                        <div className="mt-6 pt-6 border-t border-gray-100">
                            <button className="w-full border border-gray-300 text-gray-700 py-2 rounded hover:bg-gray-50 text-sm font-medium">
                                Modifier la Configuration
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
