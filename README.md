# Agri-Care

Agri-Care est une plateforme de prévision agricole basée sur des données climatiques ouvertes.

## Structure du Projet

- **Backend** : API FastAPI (Python 3.11)
- **Frontend** : Application Next.js (TypeScript, Tailwind CSS)
- **Database** : MySQL 8

## Prérequis

- Docker & Docker Compose
- Python 3.11 (pour le développement local backend)
- Node.js 18+ (pour le développement local frontend)

## Démarrage Rapide (Docker)

La méthode la plus simple pour lancer tout le projet :

```bash
docker-compose up --build
```

- Backend : [http://localhost:8000/health](http://localhost:8000/health)
- Frontend : [http://localhost:3000](http://localhost:3000)

## Développement Local

### Backend

```bash
cd Backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd Frontend
npm install
npm run dev
```
