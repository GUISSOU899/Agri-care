import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { ReactNode } from "react";
import Link from "next/link";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
    title: "Agri-Care",
    description: "Plateforme de prévision agricole",
};

export default function RootLayout({
    children,
}: Readonly<{
    children: ReactNode;
}>) {
    return (
        <html lang="fr">
            <body className={inter.className}>
                <div className="flex flex-col min-h-screen">
                    <header className="bg-green-800 text-white p-4 shadow-md sticky top-0 z-50">
                        <div className="container mx-auto flex justify-between items-center">
                            <Link href="/" className="text-2xl font-bold flex items-center gap-2">
                                <span className="bg-white text-green-800 rounded-full w-8 h-8 flex items-center justify-center text-sm">AG</span>
                                Agri-Care
                            </Link>
                            <nav>
                                <ul className="flex space-x-6 font-medium">
                                    <li><Link href="/" className="hover:text-green-200 transition">Accueil</Link></li>
                                    <li><Link href="/dashboard" className="hover:text-green-200 transition">Tableau de Bord</Link></li>
                                    <li><Link href="/admin" className="hover:text-green-200 transition">Admin</Link></li>
                                </ul>
                            </nav>
                        </div>
                    </header>
                    <main className="flex-grow bg-gray-50">
                        {children}
                    </main>
                    <footer className="bg-gray-800 text-white p-4 text-center mt-auto">
                        <p>&copy; 2024 Agri-Care. Tous droits réservés.</p>
                    </footer>
                </div>
            </body>
        </html>
    );
}
