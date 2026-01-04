'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import { BrainCircuit, Play, BarChart2, Activity } from 'lucide-react';

export default function AdminML() {
    const [training, setTraining] = useState(false);
    const [runs, setRuns] = useState<any[]>([]);
    const [progress, setProgress] = useState(0);

    const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';

    const fetchRuns = async () => {
        try {
            const token = localStorage.getItem('token') || sessionStorage.getItem('token');
            const res = await axios.get(`${API_BASE_URL}/admin/ml/runs`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setRuns(res.data);
        } catch (err) {
            console.error("Error fetching runs:", err);
            setRuns([]);
        }
    };

    const startTraining = async () => {
        setTraining(true);
        setProgress(0);

        // Mock progress
        const interval = setInterval(() => {
            setProgress(p => {
                if (p >= 90) return p;
                return p + 10;
            });
        }, 500);

        try {
            const token = localStorage.getItem('token') || sessionStorage.getItem('token');
            await axios.post(`${API_BASE_URL}/admin/ml/train`, {}, {
                headers: { Authorization: `Bearer ${token}` }
            });
            clearInterval(interval);
            setProgress(100);
            setTimeout(() => {
                setTraining(false);
                fetchRuns();
            }, 3000);
        } catch (err) {
            clearInterval(interval);
            setTraining(false);
            console.error(err);
            alert("Erreur lors de l'entraînement");
        }
    };

    useEffect(() => {
        fetchRuns();
    }, []);

    return (
        <div>
            <h1 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-2">
                <BrainCircuit /> Intelligence Artificielle (ML)
            </h1>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
                {/* Training Panel */}
                <div className="lg:col-span-1 bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                    <h3 className="font-semibold text-lg mb-4">Entraîner le Modèle</h3>
                    <p className="text-sm text-gray-600 mb-6">
                        Lance l'entraînement sur les dernières données (regions, crops, forecasts).
                    </p>

                    <div className="space-y-4 mb-6">
                        <div className="flex justify-between text-sm">
                            <span className="text-gray-500">Modèle Actif</span>
                            <span className="font-medium text-gray-800">RandomForest v2.4</span>
                        </div>
                        <div className="flex justify-between text-sm">
                            <span className="text-gray-500">Dernier score (R²)</span>
                            <span className="font-medium text-green-600">0.94</span>
                        </div>
                    </div>

                    {training ? (
                        <div className="space-y-2">
                            <div className="w-full bg-gray-200 rounded-full h-2.5">
                                <div className="bg-purple-600 h-2.5 rounded-full transition-all duration-300" style={{ width: `${progress}%` }}></div>
                            </div>
                            <p className="text-center text-xs text-purple-600 font-medium">Entraînement en cours...</p>
                        </div>
                    ) : (
                        <button
                            onClick={startTraining}
                            className="w-full bg-purple-600 text-white py-3 rounded-lg font-bold flex items-center justify-center gap-2 hover:bg-purple-700 transition-colors shadow-lg shadow-purple-200"
                        >
                            <Play size={20} /> Lancer Entraînement
                        </button>
                    )}
                </div>

                {/* Runs History */}
                <div className="lg:col-span-2 bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                    <h3 className="font-semibold text-lg mb-4 flex items-center gap-2">
                        <Activity className="text-gray-400" size={20} /> Historique des Runs
                    </h3>
                    <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200">
                            <thead className="bg-gray-50">
                                <tr>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Run ID</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Modèle</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Précision</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Statut</th>
                                </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-200">
                                {runs.map((run) => (
                                    <tr key={run.id}>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{run.id}</td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{run.date}</td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{run.model}</td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-bold">{run.accuracy}</td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${run.status === 'Success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                                                }`}>
                                                {run.status}
                                            </span>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            {/* Evaluation (Optional) */}
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 opacity-75">
                <h3 className="font-semibold text-lg mb-2">Evaluation (Coming soon)</h3>
                <p className="text-sm text-gray-500">
                    Des métriques détaillées (MSE, RMSE, MAE) seront disponibles ici après connexion avec MLFlow.
                </p>
            </div>
        </div>
    );
}
