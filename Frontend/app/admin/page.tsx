'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import {
    Activity,
    Map,
    Sprout,
    Bell,
    Users,
    Database,
    Server,
    Cpu
} from 'lucide-react';
import Link from 'next/link';

export default function AdminDashboard() {
    const [stats, setStats] = useState({
        regions: 0,
        crops: 0,
        alerts: 0,
        users: 0,
        etlLastRun: 'N/A', // Placeholder
        etlStatus: 'Unknown' // Placeholder
    });
    const [health, setHealth] = useState({
        status: 'checking...',
        db: 'checking...',
        redis: 'checking...'
    });
    const [loading, setLoading] = useState(true);

    const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';

    useEffect(() => {
        const fetchData = async () => {
            try {
                const token = localStorage.getItem('token') || sessionStorage.getItem('token');
                const headers = { Authorization: `Bearer ${token}` };

                // Parallel fetches
                const [regionsRes, cropsRes, alertsRes, healthRes, usersRes] = await Promise.allSettled([
                    axios.get(`${API_BASE_URL}/regions/`),
                    axios.get(`${API_BASE_URL}/crops/`),
                    axios.get(`${API_BASE_URL}/alerts/`),
                    axios.get(`${API_BASE_URL}/health/`),
                    axios.get(`${API_BASE_URL}/auth/users/`, { headers }) // Might fail if unauthorized
                ]);

                setStats(prev => ({
                    ...prev,
                    regions: regionsRes.status === 'fulfilled' ? regionsRes.value.data.length : 0,
                    crops: cropsRes.status === 'fulfilled' ? cropsRes.value.data.length : 0,
                    alerts: alertsRes.status === 'fulfilled' ? alertsRes.value.data.length : 0,
                    users: usersRes.status === 'fulfilled' ? usersRes.value.data.length : 0,
                }));

                if (healthRes.status === 'fulfilled') {
                    setHealth(healthRes.value.data);
                } else {
                    setHealth({ status: 'error', db: 'unreachable', redis: 'unreachable' });
                }

            } catch (err) {
                console.error("Error loading dashboard data", err);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    const StatCard = ({ title, value, icon: Icon, color, link }: any) => (
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100 flex items-center justify-between">
            <div>
                <p className="text-gray-500 text-sm font-medium mb-1">{title}</p>
                <h3 className="text-3xl font-bold text-gray-800">{loading ? '-' : value}</h3>
                {link && (
                    <Link href={link} className="text-xs font-semibold text-green-600 hover:text-green-800 mt-2 inline-block">
                        Voir détails &rarr;
                    </Link>
                )}
            </div>
            <div className={`p-4 rounded-full bg-${color}-50 text-${color}-600`}>
                <Icon size={24} />
            </div>
        </div>
    );

    return (
        <div>
            <h1 className="text-2xl font-bold text-gray-800 mb-6">Dashboard Admin</h1>

            {/* KPIs */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                <StatCard title="Régions" value={stats.regions} icon={Map} color="blue" link="/admin/regions" />
                <StatCard title="Cultures" value={stats.crops} icon={Sprout} color="green" link="/admin/crops" />
                <StatCard title="Alertes Actives" value={stats.alerts} icon={Bell} color="red" link="/admin/alerts" />
                <StatCard title="Utilisateurs" value={stats.users} icon={Users} color="purple" link="/admin/users" />
            </div>

            {/* System Health */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
                    <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
                        <Activity className="text-green-600" /> État du Système
                    </h3>
                    <div className="space-y-4">
                        <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                            <div className="flex items-center gap-3">
                                <Server className="text-gray-500" size={20} />
                                <span className="font-medium text-gray-700">API Gateway</span>
                            </div>
                            <span className="px-3 py-1 rounded-full text-xs font-bold bg-green-100 text-green-800">
                                ONLINE
                            </span>
                        </div>
                        <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                            <div className="flex items-center gap-3">
                                <Database className="text-gray-500" size={20} />
                                <span className="font-medium text-gray-700">Database (PostgreSQL)</span>
                            </div>
                            <span className={`px-3 py-1 rounded-full text-xs font-bold ${health.db === 'connected' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                                }`}>
                                {health.db?.toUpperCase()}
                            </span>
                        </div>
                        <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                            <div className="flex items-center gap-3">
                                <Cpu className="text-gray-500" size={20} />
                                <span className="font-medium text-gray-700">Redis Cache</span>
                            </div>
                            <span className={`px-3 py-1 rounded-full text-xs font-bold ${health.redis === 'connected' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                                }`}>
                                {health.redis?.toUpperCase()}
                            </span>
                        </div>
                    </div>
                </div>

                {/* ETL Status (Mocked or Minimal) */}
                <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
                    <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
                        <Activity className="text-blue-600" /> Pipeline ETL
                    </h3>
                    <p className="text-gray-500 mb-6 text-sm">
                        Dernière exécution enregistrée du pipeline de données.
                    </p>
                    <div className="flex items-center justify-between mb-4">
                        <span className="text-gray-600 font-medium">Statut global</span>
                        {/* Placeholder status */}
                        <span className="px-3 py-1 rounded-full text-xs font-bold bg-gray-100 text-gray-600">
                            EN ATTENTE
                        </span>
                    </div>
                    <Link
                        href="/admin/etl"
                        className="w-full block text-center bg-gray-50 text-gray-700 font-semibold py-2 rounded-lg hover:bg-gray-100 border border-gray-200"
                    >
                        Gérer les Jobs ETL
                    </Link>
                </div>
            </div>
        </div>
    );
}
