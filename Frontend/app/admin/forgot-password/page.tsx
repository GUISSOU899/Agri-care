'use client';

import Link from 'next/link';

export default function ForgotPassword() {
    return (
        <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
            <div className="bg-white p-8 rounded-xl shadow-lg max-w-md w-full text-center border border-gray-200">
                <h1 className="text-2xl font-bold text-gray-800 mb-4">Mot de passe oublié</h1>
                <p className="text-gray-600 mb-6">
                    Cette fonctionnalité sera bientôt disponible. Veuillez contacter l'administrateur système pour réinitialiser votre mot de passe.
                </p>
                <Link href="/admin/login" className="text-blue-600 hover:underline font-medium">
                    Retour à la connexion
                </Link>
            </div>
        </div>
    );
}
