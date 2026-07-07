# Leyton PFA Flask Worker

API Flask locale pour créer et consulter des tâches en base de données. Un worker séparé pourra traiter ces tâches plus tard.

## Installation

```bash
pip install -r requirements.txt
```

Par défaut, l'API utilise SQLite avec `sqlite:///tasks.db`. Tu peux changer la base utilisée avec la variable d'environnement `DATABASE_URL`.

## Lancer l'API

```bash
python run.py
```

L'API démarre en mode debug sur le port `5000`.

Sur macOS, si `localhost:5000` répond avec `AirTunes` ou `403 Forbidden`, force IPv4 avec `curl -4` ou utilise directement `127.0.0.1`.

## Endpoints

Créer une tâche :

```bash
curl -4 -sS -X POST http://localhost:5000/tasks -H 'Content-Type: application/json' -d '{"file_location":"/tmp/example.pdf","parameters":{"source":"curl"}}'
```

Lister les tâches :

```bash
curl -4 -sS http://localhost:5000/tasks
```

Filtrer par statut :

```bash
curl -4 -sS 'http://localhost:5000/tasks?status=pending'
```

Récupérer une tâche :

```bash
curl -4 -sS http://localhost:5000/tasks/1
```

Mettre à jour le statut :

```bash
curl -4 -sS -X PATCH http://localhost:5000/tasks/1 -H 'Content-Type: application/json' -d '{"status":"in_progress"}'
```

Les statuts autorisés sont `pending`, `in_progress`, `done` et `failed`.

## Tests

```bash
python -m pytest
```

Les tests utilisent une base SQLite temporaire et vérifient la création, la lecture, le filtrage, la mise à jour du statut et les erreurs principales de l'API.
