# Documentation de l'API

Cette documentation décrit l'utilisation de l'API FastAPI pour le modèle de prédiction ML.

## Démarrage de l'API

### Prérequis

1. **Redis** doit être en cours d'exécution :
   ```bash
   # Avec Docker
   docker run -d -p 6379:6379 redis:latest

   # Ou avec redis-server
   redis-server
   ```

2. **Variables d'environnement** configurées dans `.env` :
   ```env
   MODEL_PATH=./model/model.pkl
   API_HOST=0.0.0.0
   API_PORT=8000
   REDIS_HOST=localhost
   REDIS_PORT=6379
   REDIS_DB=0
   ```

### Lancer l'API

```bash
# Méthode 1 : Avec uvicorn directement
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

# Méthode 2 : Avec Python
python -m src.api.main

# Méthode 3 : Via le module uvicorn
python -m uvicorn src.api.main:app --reload
```

L'API sera accessible sur `http://localhost:8000`

### Documentation interactive

- **Swagger UI** : `http://localhost:8000/docs`
- **ReDoc** : `http://localhost:8000/redoc`

## Endpoints

### 1. Root - `/`

**Méthode** : `GET`

Retourne les informations de base de l'API.

**Réponse** :
```json
{
  "message": "API de Prédiction ML",
  "version": "1.0.0",
  "endpoints": {
    "health": "/health",
    "predict": "/predict",
    "predict_proba": "/predict_proba",
    "logs": "/logs"
  }
}
```

### 2. Health Check - `/health`

**Méthode** : `GET`

Vérifie l'état de santé de l'API.

**Réponse** :
```json
{
  "status": "healthy",
  "model_loaded": true,
  "redis_connected": true,
  "version": "1.0.0"
}
```

**Exemple cURL** :
```bash
curl http://localhost:8000/health
```

### 3. Prédiction - `/predict`

**Méthode** : `POST`

Effectue une prédiction pour un patient.

**Corps de la requête** :
```json
{
  "AGE": 65,
  "GENDER": 1,
  "SMOKING": 1,
  "ALCOHOL CONSUMING": 1,
  "PEER_PRESSURE": 0,
  "YELLOW_FINGERS": 1,
  "ANXIETY": 0,
  "FATIGUE": 1,
  "ALLERGY": 0,
  "WHEEZING": 1,
  "COUGHING": 1,
  "SHORTNESS OF BREATH": 1,
  "SWALLOWING DIFFICULTY": 0,
  "CHEST PAIN": 1
}
```

**Réponse** :
```json
{
  "prediction": 1,
  "probability": 0.85,
  "message": "Prédiction positive"
}
```

**Exemple cURL** :
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "AGE": 65,
    "GENDER": 1,
    "SMOKING": 1,
    "ALCOHOL CONSUMING": 1,
    "PEER_PRESSURE": 0,
    "YELLOW_FINGERS": 1,
    "ANXIETY": 0,
    "FATIGUE": 1,
    "ALLERGY": 0,
    "WHEEZING": 1,
    "COUGHING": 1,
    "SHORTNESS OF BREATH": 1,
    "SWALLOWING DIFFICULTY": 0,
    "CHEST PAIN": 1
  }'
```

**Exemple Python** :
```python
import requests

data = {
    "AGE": 65,
    "GENDER": 1,
    "SMOKING": 1,
    "ALCOHOL CONSUMING": 1,
    "PEER_PRESSURE": 0,
    "YELLOW_FINGERS": 1,
    "ANXIETY": 0,
    "FATIGUE": 1,
    "ALLERGY": 0,
    "WHEEZING": 1,
    "COUGHING": 1,
    "SHORTNESS OF BREATH": 1,
    "SWALLOWING DIFFICULTY": 0,
    "CHEST PAIN": 1
}

response = requests.post("http://localhost:8000/predict", json=data)
print(response.json())
```

### 4. Prédiction avec probabilités - `/predict_proba`

**Méthode** : `POST`

Effectue une prédiction avec les probabilités pour chaque classe.

**Corps de la requête** : Identique à `/predict`

**Réponse** :
```json
{
  "prediction": 1,
  "probabilities": [0.15, 0.85],
  "message": "Prédiction positive"
}
```

### 5. Récupérer les logs - `/logs`

**Méthode** : `GET`

Récupère les logs de l'API stockés dans Redis avec pagination.

**Paramètres de requête** :
- `limit` (optionnel) : Nombre de logs à récupérer (défaut: 100, max: 1000)
- `offset` (optionnel) : Nombre de logs à sauter pour la pagination (défaut: 0)

**Réponse** :
```json
{
  "total": 25,
  "logs": [
    {
      "timestamp": "2024-11-10T10:30:45.123456",
      "level": "INFO",
      "message": "Prédiction effectuée : 1",
      "data": {
        "prediction": 1,
        "probability": 0.85,
        "age": 65
      }
    }
  ]
}
```

**Exemples cURL** :
```bash
# Récupérer les 50 premiers logs
curl "http://localhost:8000/logs?limit=50"

# Récupérer 50 logs en sautant les 100 premiers (pagination)
curl "http://localhost:8000/logs?limit=50&offset=100"

# Récupérer tous les logs (jusqu'à 1000)
curl "http://localhost:8000/logs?limit=1000"
```

### 6. Supprimer les logs - `/logs`

**Méthode** : `DELETE`

Vide complètement le cache des logs stockés dans Redis.

⚠️ **Important** : Cet endpoint vide **uniquement** le cache Redis local. Les logs déjà indexés dans Elasticsearch ne sont **pas affectés**.

**Réponse succès** :
```json
{
  "message": "Logs supprimés avec succès"
}
```

**Réponse erreur** :
```json
{
  "detail": "Échec de la suppression des logs"
}
```

**Exemples d'utilisation** :

```bash
# Avec cURL
curl -X DELETE "http://localhost:8000/logs"

# Avec Makefile (recommandé)
make clear-logs

# Avec httpie
http DELETE http://localhost:8000/logs

# Avec Python
import requests
response = requests.delete("http://localhost:8000/logs")
print(response.json())
```

**Cas d'usage** :
- Nettoyage après des tests de charge
- Maintenance périodique du cache Redis
- Reset avant un nouveau test de performance

**Note** : Pour supprimer à la fois le cache Redis ET les index Elasticsearch :
```bash
# 1. Vider le cache Redis
make clear-logs

# 2. Vider les index Elasticsearch
make pipeline-clear-indexes
```

## Validation des données

### Features requises

Les 14 features suivantes sont **obligatoires** :

| Feature | Type | Valeurs | Description |
|---------|------|---------|-------------|
| AGE | int | 0-120 | Âge du patient |
| GENDER | int | 0-1 | Genre (0=F, 1=M) |
| SMOKING | int | 0-1 | Fumeur |
| ALCOHOL CONSUMING | int | 0-1 | Consommation d'alcool |
| PEER_PRESSURE | int | 0-1 | Pression sociale |
| YELLOW_FINGERS | int | 0-1 | Doigts jaunes |
| ANXIETY | int | 0-1 | Anxiété |
| FATIGUE | int | 0-1 | Fatigue |
| ALLERGY | int | 0-1 | Allergie |
| WHEEZING | int | 0-1 | Respiration sifflante |
| COUGHING | int | 0-1 | Toux |
| SHORTNESS OF BREATH | int | 0-1 | Essoufflement |
| SWALLOWING DIFFICULTY | int | 0-1 | Difficulté à avaler |
| CHEST PAIN | int | 0-1 | Douleur thoracique |

### Gestion des erreurs

L'API retourne des codes HTTP appropriés :

- `200` : Succès
- `422` : Erreur de validation (données invalides)
- `500` : Erreur serveur (modèle non chargé, erreur Redis, etc.)

**Exemple d'erreur de validation** :
```json
{
  "detail": [
    {
      "type": "int_parsing",
      "loc": ["body", "AGE"],
      "msg": "Input should be a valid integer",
      "input": "invalid"
    }
  ]
}
```

## Architecture

```
Client
  ↓
FastAPI (src/api/main.py)
  ↓
Predictor (src/model/predictor.py)
  ↓
FeatureEngineer → ModelLoader
  ↓
Modèle ML
  ↓
Prédiction
  ↓
RedisLogger → Redis (logs)
```

## Logs

Tous les événements importants sont loggés dans Redis :

- **INFO** : Prédictions réussies, health checks, démarrage/arrêt
- **ERROR** : Erreurs de prédiction, erreurs de connexion
- **WARNING** : Avertissements divers

Les logs sont stockés avec :
- **timestamp** : Horodatage UTC
- **level** : Niveau du log
- **message** : Message descriptif
- **data** : Données additionnelles (optionnel)

## Sécurité et Performance

### CORS

L'API accepte les requêtes de toutes les origines. Pour la production, configurez :

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://votre-domaine.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

### Singleton Pattern

- Le **modèle ML** est chargé une seule fois au démarrage (pattern Singleton)
- Le **RedisLogger** utilise également le pattern Singleton
- Optimisation de la mémoire et des performances

### Limitations

- Taille maximale des logs : Configurable via `REDIS_LOGS_MAX_SIZE` (défaut: 1000)
- Timeout des requêtes : Par défaut, pas de timeout (configurable dans uvicorn)

## Tests

```bash
# Tester l'API avec pytest
pytest tests/test_api.py -v

# Tester avec httpx
python -c "
import httpx
response = httpx.get('http://localhost:8000/health')
print(response.json())
"
```
