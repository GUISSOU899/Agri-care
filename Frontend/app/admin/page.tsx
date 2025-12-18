export default function AdminHome() {
    return (
        <div>
            <h1 className="text-2xl font-bold text-gray-800 mb-4">Administration Agri-Care</h1>
            <p className="text-gray-600">
                Bienvenue dans l&apos;espace d&apos;administration. Utilisez le menu latéral pour gérer les données de la plateforme.
            </p>
            <ul className="mt-8 list-disc list-inside space-y-2 text-gray-700">
                <li><strong>Regions:</strong> Ajouter et gérer les zones géographiques.</li>
                <li><strong>Crops:</strong> Définir les cultures supportées.</li>
                <li><strong>Alerts:</strong> Créer des alertes manuelles pour les agriculteurs.</li>
            </ul>
        </div>
    );
}
