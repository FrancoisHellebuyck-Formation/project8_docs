# Accès HTTP Direct à l'API sur HuggingFace Spaces

Ce document explique comment accéder directement à l'API ML via des requêtes HTTP standard (curl, Postman, etc.) lorsque l'application est déployée sur HuggingFace Spaces.

## 📋 Sommaire

1. [Architecture](#architecture)
2. [Endpoints Disponibles](#endpoints-disponibles)
3. [Exemples curl](#exemples-curl)
4. [Intégration dans votre code](#intégration-dans-votre-code)
5. [Déploiement](#déploiement)

## 🏗️ Architecture

L'application utilise une architecture **FastAPI + Gradio** où:

- **FastAPI** sert les endpoints REST API (`/api/*`)
- **Gradio** est monté sur la racine (`/`) pour l'interface utilisateur
- Tout est accessible via le même port (7860)

```
┌─────────────────────────────────────────┐
│   HuggingFace Space (Port 7860)         │
├─────────────────────────────────────────┤
│                                         │
│  FastAPI (app principale)               │
│  ├── /api/health                        │
│  ├── /api/info                          │
│  ├── /api/predict                       │
│  ├── /api/predict_proba                 │
│  ├── /api/logs                          │
│  └── /api/logs (DELETE)                 │
│                                         │
│  Gradio UI (montée sur /)               │
│  └── Interface utilisateur interactive  │
│                                         │
└─────────────────────────────────────────┘
```

## 🔌 Endpoints Disponibles

### 1. Health Check
```http
GET /api/health
```
Vérifie l'état de santé de l'API et ses dépendances.

**Réponse**:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "redis_connected": false,
  "version": "1.0.0"
}
```

### 2. Informations API
```http
GET /api/info
```
Récupère les informations générales de l'API.

**Réponse**:
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

### 3. Prédiction
```http
POST /api/predict
Content-Type: application/json
```
Effectue une prédiction de cancer du poumon.

**Corps de la requête** (14 features obligatoires):
```json
{
  "AGE": 50,
  "GENDER": 1,
  "SMOKING": 1,
  "ALCOHOL CONSUMING": 0,
  "PEER_PRESSURE": 0,
  "YELLOW_FINGERS": 1,
  "ANXIETY": 0,
  "FATIGUE": 1,
  "ALLERGY": 0,
  "WHEEZING": 1,
  "COUGHING": 1,
  "SHORTNESS OF BREATH": 1,
  "SWALLOWING DIFFICULTY": 0,
  "CHEST PAIN": 1,
  "CHRONIC DISEASE": 0
}
```

**Réponse**:
```json
{
  "prediction": 1,
  "probability": 0.8659778675097131,
  "message": "Prédiction positive"
}
```

### 4. Probabilités Détaillées
```http
POST /api/predict_proba
Content-Type: application/json
```
Récupère les probabilités pour chaque classe.

**Corps**: Identique à `/api/predict`

**Réponse**:
```json
{
  "probabilities": {
    "class_0": 0.1340221324902869,
    "class_1": 0.8659778675097131
  },
  "prediction": 1
}
```

### 5. Récupérer les Logs
```http
GET /api/logs?limit=100&offset=0
```
Récupère les logs de l'API depuis Redis.

**Paramètres**:
- `limit` (int, optionnel): Nombre de logs à récupérer (défaut: 100, max: 1000)
- `offset` (int, optionnel): Pagination (défaut: 0)

**Réponse**:
```json
{
  "logs": [
    "[transaction_id] POST /predict - 200 - 123ms - {...} - {...}",
    "..."
  ],
  "total": 245,
  "limit": 100,
  "offset": 0
}
```

### 6. Vider les Logs
```http
DELETE /api/logs
```
Vide complètement le cache Redis des logs.

**Réponse**:
```json
{
  "message": "Logs Redis vidés avec succès",
  "deleted": 245
}
```

## 🔧 Exemples curl

### Exemple 1: Health Check
```bash
curl https://francoisformation-oc-project8.hf.space/api/health
```

**Sortie**:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "redis_connected": false,
  "version": "1.0.0"
}
```

### Exemple 2: Prédiction Complète
```bash
curl -X POST https://francoisformation-oc-project8.hf.space/api/predict \
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
    "CHEST PAIN": 1,
    "CHRONIC DISEASE": 0
  }'
```

**Sortie**:
```json
{
  "prediction": 1,
  "probability": 0.9234567890123456,
  "message": "Prédiction positive"
}
```

### Exemple 3: Probabilités Détaillées
```bash
curl -X POST https://francoisformation-oc-project8.hf.space/api/predict_proba \
  -H "Content-Type: application/json" \
  -d @patient_data.json
```

Avec `patient_data.json`:
```json
{
  "AGE": 45,
  "GENDER": 2,
  "SMOKING": 0,
  "ALCOHOL CONSUMING": 0,
  "PEER_PRESSURE": 0,
  "YELLOW_FINGERS": 0,
  "ANXIETY": 0,
  "FATIGUE": 0,
  "ALLERGY": 1,
  "WHEEZING": 0,
  "COUGHING": 0,
  "SHORTNESS OF BREATH": 0,
  "SWALLOWING DIFFICULTY": 0,
  "CHEST PAIN": 0,
  "CHRONIC DISEASE": 0
}
```

### Exemple 4: Récupérer les 10 Derniers Logs
```bash
curl "https://francoisformation-oc-project8.hf.space/api/logs?limit=10&offset=0"
```

### Exemple 5: Vider les Logs (Nécessite Authentification)
```bash
curl -X DELETE https://francoisformation-oc-project8.hf.space/api/logs
```

## 💻 Intégration dans votre Code

### Python avec `requests`
```python
import requests

# Configuration
API_URL = "https://francoisformation-oc-project8.hf.space"

# Health check
response = requests.get(f"{API_URL}/api/health")
print(response.json())

# Prédiction
patient_data = {
    "AGE": 50,
    "GENDER": 1,
    "SMOKING": 1,
    "ALCOHOL CONSUMING": 0,
    "PEER_PRESSURE": 0,
    "YELLOW_FINGERS": 1,
    "ANXIETY": 0,
    "FATIGUE": 1,
    "ALLERGY": 0,
    "WHEEZING": 1,
    "COUGHING": 1,
    "SHORTNESS OF BREATH": 1,
    "SWALLOWING DIFFICULTY": 0,
    "CHEST PAIN": 1,
    "CHRONIC DISEASE": 0
}

response = requests.post(f"{API_URL}/api/predict", json=patient_data)
prediction = response.json()
print(f"Prédiction: {prediction['prediction']}")
print(f"Probabilité: {prediction['probability']:.2%}")
```

### JavaScript/Node.js avec `fetch`
```javascript
const API_URL = "https://francoisformation-oc-project8.hf.space";

// Health check
fetch(`${API_URL}/api/health`)
  .then(response => response.json())
  .then(data => console.log(data));

// Prédiction
const patientData = {
  AGE: 50,
  GENDER: 1,
  SMOKING: 1,
  "ALCOHOL CONSUMING": 0,
  PEER_PRESSURE: 0,
  YELLOW_FINGERS: 1,
  ANXIETY: 0,
  FATIGUE: 1,
  ALLERGY: 0,
  WHEEZING: 1,
  COUGHING: 1,
  "SHORTNESS OF BREATH": 1,
  "SWALLOWING DIFFICULTY": 0,
  "CHEST PAIN": 1,
  "CHRONIC DISEASE": 0
};

fetch(`${API_URL}/api/predict`, {
  method: "POST",
  headers: {
    "Content-Type": "application/json"
  },
  body: JSON.stringify(patientData)
})
  .then(response => response.json())
  .then(data => console.log(`Prédiction: ${data.prediction}, Probabilité: ${data.probability}`));
```

### R avec `httr`
```r
library(httr)
library(jsonlite)

API_URL <- "https://francoisformation-oc-project8.hf.space"

# Health check
response <- GET(paste0(API_URL, "/api/health"))
content(response, "parsed")

# Prédiction
patient_data <- list(
  AGE = 50,
  GENDER = 1,
  SMOKING = 1,
  `ALCOHOL CONSUMING` = 0,
  PEER_PRESSURE = 0,
  YELLOW_FINGERS = 1,
  ANXIETY = 0,
  FATIGUE = 1,
  ALLERGY = 0,
  WHEEZING = 1,
  COUGHING = 1,
  `SHORTNESS OF BREATH` = 1,
  `SWALLOWING DIFFICULTY` = 0,
  `CHEST PAIN` = 1,
  `CHRONIC DISEASE` = 0
)

response <- POST(
  paste0(API_URL, "/api/predict"),
  body = toJSON(patient_data, auto_unbox = TRUE),
  content_type_json()
)

result <- content(response, "parsed")
cat(sprintf("Prédiction: %d, Probabilité: %.2f%%\n",
            result$prediction, result$probability * 100))
```

## 🚀 Déploiement

### Étape 1: Mise à Jour du Dockerfile

Le `docker/Dockerfile.hf` a été modifié pour utiliser le nouveau module `fastapi_app`:

```dockerfile
# Démarrer l'UI avec FastAPI+Gradio
echo "🎨 Démarrage de l'UI avec FastAPI+Gradio sur le port 7860..."
python -m src.ui.fastapi_app
```

### Étape 2: Push vers HuggingFace

Une fois déployé sur HuggingFace Spaces, les endpoints seront accessibles via:

```
https://YOUR-SPACE-NAME.hf.space/api/health
https://YOUR-SPACE-NAME.hf.space/api/predict
...
```

### Étape 3: Test du Déploiement

```bash
# Remplacez par votre URL HF Space
export HF_SPACE_URL="https://francoisformation-oc-project8.hf.space"

# Test health check
curl $HF_SPACE_URL/api/health

# Test prédiction
curl -X POST $HF_SPACE_URL/api/predict \
  -H "Content-Type: application/json" \
  -d '{"AGE": 50, "GENDER": 1, "SMOKING": 1, ...}'
```

## 📊 Codes de Statut HTTP

| Code | Signification | Description |
|------|---------------|-------------|
| 200 | OK | Requête réussie |
| 400 | Bad Request | Données invalides (features manquantes) |
| 500 | Internal Server Error | Erreur serveur (modèle non chargé, etc.) |
| 503 | Service Unavailable | API backend inaccessible |

## 🔒 Sécurité

- ✅ Les endpoints sont **en lecture seule** (sauf DELETE /logs)
- ✅ Pas de données sensibles dans les réponses
- ⚠️ Considérer l'ajout d'authentification pour la production
- ⚠️ Rate limiting recommandé pour éviter les abus

## 🐛 Dépannage

### Erreur: "Connection refused"
```bash
# Vérifier que le Space est démarré
curl https://YOUR-SPACE.hf.space/
```

### Erreur: "404 Not Found"
Vérifiez que vous utilisez bien `/api/` (avec le slash):
```bash
# ✅ Correct
curl https://YOUR-SPACE.hf.space/api/health

# ❌ Incorrect
curl https://YOUR-SPACE.hf.space/health
```

### Erreur: "Service Unavailable"
L'API backend (port 8000) n'est pas accessible. Vérifiez les logs HF.

## 📚 Ressources

- [Documentation FastAPI](https://fastapi.tiangolo.com/)
- [Documentation Gradio](https://www.gradio.app/docs/)
- [HuggingFace Spaces](https://huggingface.co/docs/hub/spaces)
- [Code Source](https://github.com/...)

---

**Dernière mise à jour**: 2025-11-21
**Version**: 1.0.0
