'use client';

import React from 'react';
import AdminUsers from '@/components/AdminUsers';

export default function AdminUsersPage() {
    return (
        <div className="min-h-screen bg-gray-100 p-8">
            <div className="max-w-6xl mx-auto">
                <h1 className="text-3xl font-bold text-gray-800 mb-6">User Management</h1>
                <div className="bg-white rounded-xl shadow-lg p-6">
                    <AdminUsers />
                </div>
            </div>
        </div>
    );
}
