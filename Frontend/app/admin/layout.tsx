import Link from 'next/link';

export default function AdminLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    // A simple sidebar layout
    return (
        <div className="flex min-h-[calc(100vh-64px)] bg-gray-100">
            {/* Sidebar */}
            <aside className="w-64 bg-white shadow-md flex-shrink-0 hidden md:block">
                <div className="p-6 border-b">
                    <h2 className="text-xl font-bold text-gray-800">Admin Panel</h2>
                </div>
                <nav className="p-4 space-y-1">
                    <Link href="/admin" className="block px-4 py-2 text-gray-700 hover:bg-gray-50 hover:text-green-600 rounded-md font-medium">
                        Overview
                    </Link>
                    <Link href="/admin/regions" className="block px-4 py-2 text-gray-700 hover:bg-gray-50 hover:text-green-600 rounded-md font-medium">
                        Regions
                    </Link>
                    <Link href="/admin/crops" className="block px-4 py-2 text-gray-700 hover:bg-gray-50 hover:text-green-600 rounded-md font-medium">
                        Crops
                    </Link>
                    <Link href="/admin/alerts" className="block px-4 py-2 text-gray-700 hover:bg-gray-50 hover:text-green-600 rounded-md font-medium">
                        Alerts
                    </Link>
                </nav>
            </aside>

            {/* Main Content */}
            <main className="flex-1 p-8">
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 min-h-full">
                    {children}
                </div>
            </main>
        </div>
    );
}
