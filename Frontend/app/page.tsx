import Link from 'next/link';

export default function Home() {
    return (
        <div className="flex flex-col items-center justify-center min-h-[calc(100vh-140px)] bg-gray-50 text-center px-4">
            <h1 className="text-4xl md:text-5xl font-extrabold text-green-800 mb-6 drop-shadow-sm">
                Bienvenue sur Agri-Care
            </h1>
            <p className="text-lg md:text-xl text-gray-600 mb-8 max-w-2xl">
                La plateforme de prévision agricole intelligente pour optimiser vos rendements et votre irrigation grâce à l&apos;analyse de données climatiques.
            </p>

            <div className="flex flex-col md:flex-row gap-6 mb-12">
                <div className="p-6 bg-white rounded-lg shadow-sm border border-gray-200 max-w-sm">
                    <h3 className="text-xl font-bold text-blue-600 mb-2">1. Données Météo</h3>
                    <p className="text-gray-500">Collecte automatique de données via NASA POWER API.</p>
                </div>
                <div className="p-6 bg-white rounded-lg shadow-sm border border-gray-200 max-w-sm">
                    <h3 className="text-xl font-bold text-amber-600 mb-2">2. Modèles IA</h3>
                    <p className="text-gray-500">Prédiction de rendement et besoins en eau sur 30 jours.</p>
                </div>
                <div className="p-6 bg-white rounded-lg shadow-sm border border-gray-200 max-w-sm">
                    <h3 className="text-xl font-bold text-green-600 mb-2">3. Visualisation</h3>
                    <p className="text-gray-500">Tableau de bord interactif avec cartes et graphiques.</p>
                </div>
            </div>

            <Link
                href="/dashboard"
                className="px-8 py-3 bg-green-600 text-white text-lg font-semibold rounded-full hover:bg-green-700 transition shadow-lg hover:shadow-xl"
            >
                Accéder au Tableau de Bord
            </Link>
        </div>
    );
}
