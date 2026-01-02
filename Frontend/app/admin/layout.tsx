'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import AdminGuard from '../../components/AdminGuard';
import {
    LayoutDashboard,
    Map,
    Sprout,
    Bell,
    Workflow,
    BrainCircuit,
    Users,
    Settings,
    LogOut,
    Menu,
    X
} from 'lucide-react';

export default function AdminLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    const pathname = usePathname();
    const router = useRouter();
    const [sidebarOpen, setSidebarOpen] = React.useState(false);

    // If on login page, don't show layout elements
    if (pathname === '/admin/login' || pathname === '/admin/forgot-password') {
        return <AdminGuard>{children}</AdminGuard>;
    }

    const handleLogout = () => {
        if (confirm('Êtes-vous sûr de vouloir vous déconnecter ?')) {
            localStorage.removeItem('token');
            localStorage.removeItem('role');
            sessionStorage.removeItem('token');
            sessionStorage.removeItem('role');
            // Keep email if remembered
            router.push('/admin/login');
        }
    };

    const navItems = [
        { name: 'Dashboard', href: '/admin', icon: LayoutDashboard },
        { name: 'Régions (CSV)', href: '/admin/regions', icon: Map },
        { name: 'Cultures (CSV)', href: '/admin/crops', icon: Sprout },
        { name: 'Alertes (CSV)', href: '/admin/alerts', icon: Bell },
        { name: 'ETL Jobs', href: '/admin/etl', icon: Workflow },
        { name: 'IA Training', href: '/admin/ml', icon: BrainCircuit },
        { name: 'Utilisateurs', href: '/admin/users', icon: Users },
        { name: 'Système', href: '/admin/system', icon: Settings },
    ];

    return (
        <AdminGuard>
            <div className="flex h-screen bg-gray-100 font-sans">
                {/* Mobile Sidebar Overlay */}
                {sidebarOpen && (
                    <div
                        className="fixed inset-0 bg-black bg-opacity-50 z-20 md:hidden"
                        onClick={() => setSidebarOpen(false)}
                    />
                )}

                {/* Sidebar */}
                <aside className={`
                    fixed inset-y-0 left-0 z-30 w-64 bg-white shadow-xl transform transition-transform duration-300 ease-in-out
                    md:relative md:translate-x-0
                    ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
                `}>
                    <div className="h-16 flex items-center justify-center border-b bg-green-600">
                        <h1 className="text-xl font-bold text-white tracking-wide">Agri-Care Admin</h1>
                    </div>

                    <nav className="p-4 space-y-1 overflow-y-auto h-[calc(100vh-64px)]">
                        <div className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2 px-4 mt-2">
                            Menu Principal
                        </div>
                        {navItems.map((item) => {
                            const isActive = pathname === item.href;
                            return (
                                <Link
                                    key={item.href}
                                    href={item.href}
                                    onClick={() => setSidebarOpen(false)}
                                    className={`
                                        flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors
                                        ${isActive
                                            ? 'bg-green-50 text-green-700'
                                            : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'}
                                    `}
                                >
                                    <item.icon className={`mr-3 h-5 w-5 ${isActive ? 'text-green-600' : 'text-gray-400'}`} />
                                    {item.name}
                                </Link>
                            );
                        })}

                        <div className="border-t my-4 pt-4">
                            <button
                                onClick={handleLogout}
                                className="w-full flex items-center px-4 py-3 text-sm font-medium text-red-600 rounded-lg hover:bg-red-50 transition-colors"
                            >
                                <LogOut className="mr-3 h-5 w-5" />
                                Déconnexion
                            </button>
                        </div>
                    </nav>
                </aside>

                {/* Main Content */}
                <div className="flex-1 flex flex-col overflow-hidden">
                    {/* Header */}
                    <header className="bg-white shadow-sm h-16 flex items-center justify-between px-6 z-10">
                        <button
                            className="md:hidden text-gray-500 hover:text-gray-700"
                            onClick={() => setSidebarOpen(true)}
                        >
                            <Menu className="h-6 w-6" />
                        </button>

                        <div className="flex-1 px-4">
                            {/* Breadcrumbs or search could go here */}
                        </div>

                        <div className="flex items-center space-x-4">
                            <div className="relative">
                                {/* Profile Dropdown placeholder */}
                                <div className="h-8 w-8 rounded-full bg-green-100 flex items-center justify-center text-green-700 font-bold border border-green-200">
                                    A
                                </div>
                            </div>
                        </div>
                    </header>

                    {/* Page Content */}
                    <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-50 p-6">
                        {children}
                    </main>
                </div>
            </div>
        </AdminGuard>
    );
}
