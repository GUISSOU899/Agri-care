'use client';

import { useEffect, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';

export default function AdminGuard({ children }: { children: React.ReactNode }) {
    const router = useRouter();
    const pathname = usePathname();
    const [authorized, setAuthorized] = useState(false);

    useEffect(() => {
        // If we are on the login page, no need to check
        if (pathname === '/admin/login' || pathname === '/admin/forgot-password') {
            setAuthorized(true);
            return;
        }

        const token = localStorage.getItem('token') || sessionStorage.getItem('token');
        const role = localStorage.getItem('role') || sessionStorage.getItem('role');

        if (!token || role !== 'admin') {
            // Not authenticated or not admin, redirect to login
            router.push('/admin/login');
        } else {
            setAuthorized(true);
        }
    }, [router, pathname]);

    // Optionally show a loader while checking
    if (!authorized && pathname !== '/admin/login' && pathname !== '/admin/forgot-password') {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-100">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
            </div>
        );
    }

    return <>{children}</>;
}
