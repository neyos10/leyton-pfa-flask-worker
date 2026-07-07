# Leyton PFA Flask Worker

API Flask locale pour créer, consulter et mettre à jour des tâches en base de données. Le point d'entrée principal lance l'API et le worker ensemble.

## Installation

```bash
cd backend
pip install -r requirements.txt
```

L'application utilise PostgreSQL par défaut avec l'URL suivante :

```text
postgresql://localhost/leyton_pfa
```

Tu peux utiliser une autre base en définissant la variable d'environnement `DATABASE_URL`.

## Lancer le backend

```bash
cd backend
python main.py
```

Cette commande lance l'API Flask sur le port `5000` et démarre le worker dans un thread séparé.

Sur macOS, si `localhost:5000` répond avec `AirTunes` ou `403 Forbidden`, force IPv4 avec `curl -4` ou utilise directement `127.0.0.1`.

Le worker cherche les tâches `pending`, les passe en `in_progress`, télécharge le fichier indiqué par `file_location`, puis les passe en `done`. En cas d'erreur pendant le traitement d'une tâche, il la passe en `failed` et continue avec les suivantes.

## Endpoints

Créer une tâche :

```bash
curl -4 -sS -X POST http://localhost:5000/tasks -H 'Content-Type: application/json' -d '{"file_location":"/tmp/example.pdf","parameters":{"source":"curl"}}'
```

Lister toutes les tâches :

```bash
curl -4 -sS http://localhost:5000/tasks
```

Filtrer les tâches par statut :

```bash
curl -4 -sS 'http://localhost:5000/tasks?status=pending'
```

Récupérer une tâche par id :

```bash
curl -4 -sS http://localhost:5000/tasks/1
```

Mettre à jour le statut d'une tâche :

```bash
curl -4 -sS -X PATCH http://localhost:5000/tasks/1 -H 'Content-Type: application/json' -d '{"status":"in_progress"}'
```

Les statuts autorisés sont `pending`, `in_progress`, `done` et `failed`.

## Tests

```bash
cd backend
pytest
```

Les tests utilisent une base SQLite temporaire et vérifient la création, la lecture, le filtrage, la mise à jour du statut et les erreurs principales de l'API.
