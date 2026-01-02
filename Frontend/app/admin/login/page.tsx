'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import axios from 'axios';
import Link from 'next/link';

export default function AdminLogin() {
    const router = useRouter();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [rememberMe, setRememberMe] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [showPassword, setShowPassword] = useState(false);

    // Check for saved email on mount
    useEffect(() => {
        const savedEmail = localStorage.getItem('admin_email');
        if (savedEmail) {
            setEmail(savedEmail);
            setRememberMe(true);
        }
    }, []);

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';
            const res = await axios.post(`${API_BASE_URL}/auth/login`, {
                email,
                password,
            });

            const { access_token, role, email: returnedEmail } = res.data;

            if (role !== 'admin') {
                setError('Accès refusé. Rôle administrateur requis.');
                setLoading(false);
                return;
            }

            // Save token
            // Using localStorage for simplicity as per plan "Session par défaut... si remember me -> localStorage"
            // Wait, user said: "Session par défaut (plus safe) ... si Se souvenir de moi coché -> localStorage"
            // In a SPA/client-side, "Session" usually implies sessionStorage or memory.

            const storage = rememberMe ? localStorage : sessionStorage;
            storage.setItem('token', access_token);
            storage.setItem('role', role);

            // Handle "Remember Email"
            if (rememberMe) {
                localStorage.setItem('admin_email', email);
            } else {
                localStorage.removeItem('admin_email');
            }

            router.push('/admin');
        } catch (err: any) {
            console.error(err);
            if (err.response?.status === 400 || err.response?.status === 401) {
                setError('Email ou mot de passe incorrect.');
            } else {
                setError('Une erreur est survenue. Veuillez réessayer.');
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
            <div className="bg-white p-8 rounded-xl shadow-lg max-w-md w-full border border-gray-200">
                <div className="text-center mb-8">
                    <h1 className="text-3xl font-bold text-gray-800">Agri-Care Admin</h1>
                    <p className="text-gray-500 mt-2">Connectez-vous pour gérer la plateforme</p>
                </div>

                {error && (
                    <div className="bg-red-50 text-red-600 p-3 rounded-md mb-6 text-sm border border-red-200">
                        {error}
                    </div>
                )}

                <form onSubmit={handleLogin} className="space-y-6">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                        <input
                            type="email"
                            required
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 outline-none transition-all"
                            placeholder="admin@example.com"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            autoComplete="email"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Mot de passe</label>
                        <div className="relative">
                            <input
                                type={showPassword ? "text" : "password"}
                                required
                                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 outline-none transition-all"
                                placeholder="••••••••"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                autoComplete="current-password"
                            />
                            <button
                                type="button"
                                onClick={() => setShowPassword(!showPassword)}
                                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 text-sm"
                            >
                                {showPassword ? "Masquer" : "Afficher"}
                            </button>
                        </div>
                    </div>

                    <div className="flex items-center justify-between">
                        <label className="flex items-center space-x-2 cursor-pointer">
                            <input
                                type="checkbox"
                                checked={rememberMe}
                                onChange={(e) => setRememberMe(e.target.checked)}
                                className="w-4 h-4 text-green-600 rounded border-gray-300 focus:ring-green-500"
                            />
                            <span className="text-sm text-gray-600">Se souvenir de moi</span>
                        </label>
                        <Link href="/admin/forgot-password" className="text-sm text-green-600 hover:text-green-700 font-medium">
                            Mot de passe oublié ?
                        </Link>
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full bg-green-600 text-white py-2.5 rounded-lg font-semibold hover:bg-green-700 transition-colors shadow-md disabled:opacity-70 disabled:cursor-not-allowed"
                    >
                        {loading ? 'Connexion en cours...' : 'Se connecter'}
                    </button>
                </form>
            </div>
        </div>
    );
}
