# Documentation du Package Proxy

## 📋 Table des matières

- [Vue d'ensemble](#vue-densemble)
- [Architecture](#architecture)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [API Client](#api-client)
- [Interface Gradio](#interface-gradio)
- [Tests](#tests)
- [Exemples](#exemples)
- [Dépannage](#dépannage)

---

## 🎯 Vue d'ensemble

Le package `proxy` permet de créer une passerelle entre Gradio (port 7860) et FastAPI (port 8000). Il expose tous les endpoints de l'API FastAPI via une interface Gradio interactive et conviviale.

### Deux modes de déploiement

#### Mode 1: Proxy Gradio standalone (développement local)
Architecture classique avec Gradio qui communique avec l'API FastAPI sur des ports séparés.

#### Mode 2: FastAPI+Gradio hybride (HuggingFace Spaces) 🆕
Architecture innovante où FastAPI et Gradio sont montés dans la même application, permettant **l'accès HTTP/REST direct sans client Gradio**.

### Fonctionnalités principales

✅ **Client proxy complet** : Accès à tous les endpoints de l'API FastAPI
✅ **Interface Gradio interactive** : UI complète pour tous les endpoints
✅ **🆕 Architecture hybride** : FastAPI + Gradio dans une seule app (HF Spaces)
✅ **🆕 Accès HTTP direct** : Endpoints REST accessibles via curl/HTTP (HF Spaces)
✅ **Gestion des erreurs** : Gestion uniforme des erreurs et timeouts
✅ **Support batch** : Prédictions en batch pour plusieurs patients
✅ **Tests unitaires** : Suite de tests complète avec mocks
✅ **Type hints** : Annotations de type pour une meilleure maintenabilité

---

## 🏗️ Architecture

### Structure du package

```
src/proxy/
├── __init__.py          # Exports du package
├── client.py            # Client proxy API (APIProxyClient)
└── gradio_app.py        # Interface Gradio standalone

src/ui/
├── __init__.py          # Exports UI
├── app.py               # Interface Gradio classique
├── fastapi_app.py       # 🆕 App FastAPI+Gradio hybride (HF Spaces)
└── api_routes.py        # 🆕 Routes REST API (référence)

tests/
├── test_proxy.py        # Tests unitaires proxy
└── test_ui.py           # Tests unitaires UI
```

### Diagramme de flux - Mode 1: Standalone

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│                 │         │                 │         │                 │
│  Utilisateur    │────────▶│  Gradio Proxy   │────────▶│   FastAPI       │
│                 │         │   (port 7860)   │         │   (port 8000)   │
│                 │◀────────│                 │◀────────│                 │
└─────────────────┘         └─────────────────┘         └─────────────────┘
                                    │
                                    │ utilise
                                    ▼
                            ┌──────────────────┐
                            │  APIProxyClient  │
                            │                  │
                            │ - get_health()   │
                            │ - post_predict() │
                            │ - get_logs()     │
                            │ - etc.           │
                            └──────────────────┘
```

### Diagramme de flux - Mode 2: Hybride (HF Spaces) 🆕

```
┌─────────────────────────────────────────────────────────────────────┐
│                   HuggingFace Space (Port 7860)                     │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │              FastAPI App (src/ui/fastapi_app.py)              │ │
│  │                                                                │ │
│  │  ┌─────────────────────┐      ┌──────────────────────────┐  │ │
│  │  │   Gradio Interface  │      │    REST API Endpoints    │  │ │
│  │  │    (Monté sur /)    │      │      (Montés sur /api)   │  │ │
│  │  │                     │      │                          │  │ │
│  │  │  • Formulaire UI    │      │  • GET  /api/health      │  │ │
│  │  │  • Prédictions      │      │  • POST /api/predict     │  │ │
│  │  │  • Résultats        │      │  • POST /api/predict_proba│ │ │
│  │  │                     │      │  • GET  /api/logs        │  │ │
│  │  └──────────┬──────────┘      │  • DELETE /api/logs      │  │ │
│  │             │                 └────────┬─────────────────┘  │ │
│  │             │                          │                     │ │
│  │             └──────────┬───────────────┘                     │ │
│  │                        │                                     │ │
│  │                        ▼                                     │ │
│  │              ┌──────────────────┐                           │ │
│  │              │  APIProxyClient  │                           │ │
│  │              │  (HTTP Requests) │                           │ │
│  │              └────────┬─────────┘                           │ │
│  └───────────────────────┼─────────────────────────────────────┘ │
│                          │                                       │
└──────────────────────────┼───────────────────────────────────────┘
                           │
                           │ HTTP (localhost:8000)
                           ▼
              ┌────────────────────────────┐
              │   API FastAPI (Port 8000)  │
              │   (src/api/main.py)        │
              │                            │
              │  • Model Pool              │
              │  • Feature Engineering     │
              │  • Redis Logging           │
              │  • Performance Monitoring  │
              └────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                          Flux des requêtes                          │
└─────────────────────────────────────────────────────────────────────┘

1️⃣  Accès via Interface Gradio (Navigateur)
    ┌──────────┐
    │Utilisateur│  →  http://localhost:7860/
    └──────────┘           │
                           ▼
                  ┌─────────────────┐
                  │  Gradio UI (/)  │
                  └────────┬────────┘
                           │ APIProxyClient
                           ▼
                  ┌─────────────────┐
                  │ API (port 8000) │
                  └─────────────────┘

2️⃣  Accès direct via REST API (curl/HTTP)
    ┌──────────┐
    │  Client  │  →  http://localhost:7860/api/predict
    └──────────┘           │
                           ▼
                  ┌──────────────────┐
                  │  REST API (/api) │
                  └────────┬─────────┘
                           │ APIProxyClient
                           ▼
                  ┌─────────────────┐
                  │ API (port 8000) │
                  └─────────────────┘

🔑 Points clés:
   • Une seule application FastAPI (port 7860)
   • Gradio monté sur "/" avec gr.mount_gradio_app()
   • API REST montée sur "/api/*" avec app.mount()
   • Les deux utilisent APIProxyClient pour appeler l'API FastAPI (port 8000)
   • Double accès: Interface UI + HTTP direct
```

---

## 📦 Installation

### Prérequis

- Python 3.13+
- FastAPI API en cours d'exécution (port 8000)
- Dépendances : `gradio`, `requests`

### Installation automatique

Les dépendances sont déjà incluses dans `pyproject.toml` :

```bash
# Installation avec uv
uv sync

# Ou avec pip
pip install -e .
```

---

## 🚀 Utilisation

### 1. Lancer l'interface proxy

#### Méthode 1 : Script Python

```python
from src.proxy import launch_proxy

# Lancer avec les paramètres par défaut
launch_proxy()

# Ou avec des paramètres personnalisés
launch_proxy(
    api_url="http://localhost:8000",
    server_port=7860,
    share=False
)
```

#### Méthode 2 : Ligne de commande

```bash
# Depuis le répertoire racine
python -m src.proxy.gradio_app

# Avec des variables d'environnement
API_URL=http://localhost:8000 python -m src.proxy.gradio_app
```

#### Méthode 3 : Makefile (à ajouter)

```bash
# Ajouter au Makefile
make run-proxy
```

### 2. Accéder à l'interface

Une fois lancé, l'interface est accessible à :

- **Local** : http://localhost:7860
- **Réseau local** : http://0.0.0.0:7860
- **Public** (si share=True) : URL Gradio temporaire

### 3. Mode hybride FastAPI+Gradio (HuggingFace Spaces) 🆕

#### Lancer l'application hybride localement

```bash
# Méthode 1: Makefile
make run-ui-fastapi

# Méthode 2: Python
python -m src.ui.fastapi_app

# Méthode 3: Script Python
from src.ui.fastapi_app import app
import uvicorn
uvicorn.run(app, host="0.0.0.0", port=7860)
```

#### Accès dual (Interface + API REST)

Une fois lancé, vous avez accès à:

**Interface Gradio** : http://localhost:7860/
```bash
# Ouvrir dans le navigateur
open http://localhost:7860/
```

**API REST** : http://localhost:7860/api/*
```bash
# Health check
curl http://localhost:7860/api/health

# Prédiction
curl -X POST http://localhost:7860/api/predict \
  -H "Content-Type: application/json" \
  -d '{"AGE": 65, "GENDER": 1, "SMOKING": 1, ...}'
```

#### Déploiement sur HuggingFace Spaces

Le mode hybride est automatiquement utilisé lors du déploiement sur HuggingFace Spaces:

```bash
# Le Dockerfile.hf utilise automatiquement fastapi_app
python -m src.ui.fastapi_app
```

**URL du Space** : https://francoisformation-oc-project8.hf.space

**Accès direct via HTTP** :
```bash
# Health check
curl https://francoisformation-oc-project8.hf.space/api/health

# Prédiction
curl -X POST https://francoisformation-oc-project8.hf.space/api/predict \
  -H "Content-Type: application/json" \
  -d @patient_data.json
```

Documentation complète:
- [DIRECT_HTTP_ACCESS.md](DIRECT_HTTP_ACCESS.md) - Guide complet HTTP
- [QUICK_START_HTTP_ACCESS.md](QUICK_START_HTTP_ACCESS.md) - Quick start (5 min)
- [PROXY_REFACTOR_SUMMARY.md](PROXY_REFACTOR_SUMMARY.md) - Résumé technique

---

## 🔌 API Client

### Classe `APIProxyClient`

Client Python pour interagir avec l'API FastAPI de manière programmatique.

#### Initialisation

```python
from src.proxy import APIProxyClient

# Avec l'URL par défaut (depuis config)
client = APIProxyClient()

# Avec une URL personnalisée
client = APIProxyClient(api_url="http://localhost:8000")
```

#### Méthodes disponibles

##### 1. Informations API

```python
# GET /
response, status_code = client.get_root()
print(response)  # {"message": "API de Prédiction ML", ...}

# Alias pour get_root()
response, status_code = client.get_api_info()
```

##### 2. Health Check

```python
# GET /health
response, status_code = client.get_health()
print(response)
# {
#   "status": "healthy",
#   "model_loaded": true,
#   "redis_connected": true
# }
```

##### 3. Prédictions

```python
# POST /predict
patient_data = {
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
    "CHRONIC DISEASE": 1
}

response, status_code = client.post_predict(patient_data)
print(response)
# {
#   "prediction": 1,
#   "probability": 0.85,
#   "message": "Prédiction positive"
# }
```

##### 4. Probabilités détaillées

```python
# POST /predict_proba
response, status_code = client.post_predict_proba(patient_data)
print(response)
# {
#   "probabilities": [0.15, 0.85],
#   "prediction": 1
# }
```

##### 5. Gestion des logs

```python
# GET /logs
response, status_code = client.get_logs(limit=50, offset=0)
print(response)
# {
#   "total": 25,
#   "logs": [...]
# }

# DELETE /logs
response, status_code = client.delete_logs()
print(response)
# {"message": "Logs supprimés avec succès"}
```

##### 6. Batch predictions

```python
# Prédictions multiples
patients = [
    {"AGE": 50, "GENDER": 1, ...},
    {"AGE": 60, "GENDER": 2, ...},
    {"AGE": 70, "GENDER": 1, ...}
]

results = client.batch_predict(patients)
for response, status_code in results:
    print(f"Status: {status_code}, Prediction: {response}")
```

##### 7. Vérification de connexion

```python
# Vérifier si l'API est accessible
is_connected = client.check_connection()
if is_connected:
    print("✅ API accessible")
else:
    print("❌ API inaccessible")
```

#### Gestion des erreurs

Le client gère automatiquement les erreurs :

```python
response, status_code = client.get_health()

if status_code == 200:
    print("Succès:", response)
elif status_code == 503:
    print("Erreur de connexion:", response["error"])
elif status_code == 504:
    print("Timeout:", response["error"])
else:
    print("Erreur:", response)
```

Codes de statut retournés :
- `200` : Succès
- `503` : Erreur de connexion (API inaccessible)
- `504` : Timeout (API ne répond pas à temps)
- `500` : Erreur inattendue
- Autres codes : Codes HTTP de l'API FastAPI

---

## 🎨 Interface Gradio

### Fonctionnalités de l'interface

L'interface Gradio expose 6 sections principales :

#### 1. 🔌 Vérification de connexion

Vérifie que l'API FastAPI est accessible.

**Sortie** :
```json
{
  "connected": true,
  "api_url": "http://localhost:8000",
  "message": "✅ Connecté"
}
```

#### 2. ℹ️ Informations de l'API

Affiche les informations générales de l'API (version, endpoints disponibles).

#### 3. 💚 Health Check

Vérifie l'état de santé de l'API, du modèle ML et de Redis.

#### 4. 🔮 Prédiction ML

Interface complète pour effectuer une prédiction :

**Inputs** :
- Âge (slider 18-100)
- Genre (dropdown Homme/Femme)
- 13 checkboxes pour les symptômes et facteurs de risque

**Output** :
```json
{
  "status_code": 200,
  "response": {
    "prediction": 1,
    "probability": 0.85,
    "message": "Prédiction positive"
  }
}
```

#### 5. 📊 Probabilités de prédiction

Identique à la section Prédiction, mais appelle `/predict_proba` pour obtenir les probabilités détaillées.

#### 6. 📋 Gestion des logs

Deux fonctionnalités :

**GET /logs** :
- Slider pour le nombre de logs (1-1000)
- Slider pour l'offset (pagination)
- Bouton pour récupérer les logs

**DELETE /logs** :
- Bouton pour vider le cache Redis
- ⚠️ Confirmation visuelle avec couleur rouge

### Personnalisation de l'interface

```python
from src.proxy import create_proxy_interface

# Créer l'interface
interface = create_proxy_interface(
    api_url="http://localhost:8000",
    share=False
)

# Personnaliser et lancer
interface.launch(
    server_name="0.0.0.0",
    server_port=7860,
    share=False,
    debug=True
)
```

---

## 🧪 Tests

### Lancer les tests

```bash
# Tous les tests du proxy
uv run pytest tests/test_proxy.py -v

# Avec couverture
uv run pytest tests/test_proxy.py --cov=src/proxy --cov-report=term-missing

# Test spécifique
uv run pytest tests/test_proxy.py::TestAPIProxyClient::test_get_health_success -v
```

### Tests disponibles

Les tests couvrent :

✅ Initialisation du client
✅ Tous les endpoints (GET, POST, DELETE)
✅ Gestion des erreurs (timeout, connexion, JSON invalide)
✅ Batch predictions
✅ Vérification de connexion

**Couverture actuelle** : ~95%

### Exemple de test

```python
@patch('src.proxy.client.requests.get')
def test_get_health_success(self, mock_get, client):
    """Test GET /health avec succès."""
    mock_response = Mock()
    mock_response.json.return_value = {
        "status": "healthy",
        "model_loaded": True
    }
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    result, status = client.get_health()

    assert result["status"] == "healthy"
    assert result["model_loaded"] is True
    assert status == 200
```

---

## 💡 Exemples

### Exemple 1 : Script de monitoring

```python
"""Script de monitoring de l'API."""

import time
from src.proxy import APIProxyClient

def monitor_api(interval=60):
    """Vérifie la santé de l'API à intervalles réguliers."""
    client = APIProxyClient()

    while True:
        if client.check_connection():
            response, status = client.get_health()
            print(f"✅ API OK - {response}")
        else:
            print("❌ API inaccessible")

        time.sleep(interval)

if __name__ == "__main__":
    monitor_api(interval=30)  # Toutes les 30 secondes
```

### Exemple 2 : Prédictions en masse

```python
"""Script de prédictions en batch."""

import pandas as pd
from src.proxy import APIProxyClient

def batch_predict_from_csv(csv_path):
    """Effectue des prédictions pour tous les patients d'un CSV."""
    client = APIProxyClient()

    # Charger les données
    df = pd.read_csv(csv_path)

    # Convertir en liste de dicts
    patients = df.to_dict('records')

    # Prédictions en batch
    results = client.batch_predict(patients)

    # Ajouter les résultats au DataFrame
    predictions = [r[0].get('prediction', None) for r in results]
    probabilities = [r[0].get('probability', None) for r in results]

    df['prediction'] = predictions
    df['probability'] = probabilities

    # Sauvegarder
    df.to_csv('results.csv', index=False)
    print(f"✅ {len(results)} prédictions effectuées")

if __name__ == "__main__":
    batch_predict_from_csv('patients.csv')
```

### Exemple 3 : Intégration dans un notebook

```python
# Notebook Jupyter
from src.proxy import APIProxyClient
import matplotlib.pyplot as plt

client = APIProxyClient()

# Récupérer les logs
logs_response, _ = client.get_logs(limit=100)
logs = logs_response.get('logs', [])

# Extraire les probabilités
probabilities = [log.get('probability', 0) for log in logs]

# Visualiser
plt.hist(probabilities, bins=20)
plt.xlabel('Probabilité')
plt.ylabel('Nombre de prédictions')
plt.title('Distribution des probabilités de prédiction')
plt.show()
```

### Exemple 4 : CLI personnalisé

```python
"""CLI personnalisé pour le proxy."""

import click
from src.proxy import APIProxyClient

@click.group()
def cli():
    """CLI pour interagir avec l'API via le proxy."""
    pass

@cli.command()
def health():
    """Vérifie la santé de l'API."""
    client = APIProxyClient()
    response, status = client.get_health()
    click.echo(f"Status: {status}")
    click.echo(f"Response: {response}")

@cli.command()
@click.option('--limit', default=10, help='Nombre de logs')
def logs(limit):
    """Affiche les logs."""
    client = APIProxyClient()
    response, _ = client.get_logs(limit=limit)
    for log in response.get('logs', []):
        click.echo(f"- {log}")

@cli.command()
def clear_logs():
    """Vide les logs Redis."""
    client = APIProxyClient()
    if click.confirm('Voulez-vous vraiment vider les logs ?'):
        response, _ = client.delete_logs()
        click.echo(f"✅ {response.get('message')}")

if __name__ == '__main__':
    cli()
```

Utilisation :
```bash
python cli.py health
python cli.py logs --limit 20
python cli.py clear-logs
```

---

## 🔧 Dépannage

### Problème : API inaccessible

**Symptôme** : `{"error": "Erreur de connexion", "status_code": 503}`

**Solutions** :
1. Vérifier que l'API FastAPI est en cours d'exécution :
   ```bash
   curl http://localhost:8000/health
   ```

2. Vérifier l'URL de l'API dans la config :
   ```python
   from src.config import config
   print(config.API_URL)  # Doit être http://localhost:8000
   ```

3. Vérifier les ports :
   ```bash
   lsof -i :8000  # Port FastAPI
   lsof -i :7860  # Port Gradio
   ```

### Problème : Timeout

**Symptôme** : `{"error": "Timeout: L'API ne répond pas", "status_code": 504}`

**Solutions** :
1. Augmenter le timeout du client :
   ```python
   client = APIProxyClient()
   client.timeout = 60  # 60 secondes
   ```

2. Vérifier les performances de l'API :
   ```bash
   time curl http://localhost:8000/health
   ```

### Problème : Interface Gradio ne démarre pas

**Symptôme** : Erreur lors du lancement de l'interface

**Solutions** :
1. Vérifier que Gradio est installé :
   ```bash
   uv pip list | grep gradio
   ```

2. Vérifier les logs :
   ```bash
   python -m src.proxy.gradio_app 2>&1 | tee gradio.log
   ```

3. Port déjà utilisé :
   ```bash
   # Utiliser un autre port
   python -m src.proxy.gradio_app --server-port 7861
   ```

### Problème : Erreurs dans les tests

**Symptôme** : Tests qui échouent

**Solutions** :
1. Vérifier les dépendances de test :
   ```bash
   uv sync --dev
   ```

2. Lancer les tests en mode verbeux :
   ```bash
   uv run pytest tests/test_proxy.py -v -s
   ```

3. Vérifier les mocks :
   ```bash
   # S'assurer que pytest-mock est installé
   uv pip list | grep pytest-mock
   ```

---

## 📚 Ressources supplémentaires

### Documentation associée

#### Proxy et déploiement
- [DIRECT_HTTP_ACCESS.md](DIRECT_HTTP_ACCESS.md) - 🆕 Accès HTTP direct (HF Spaces)
- [QUICK_START_HTTP_ACCESS.md](QUICK_START_HTTP_ACCESS.md) - 🆕 Quick start HTTP (5 min)
- [PROXY_REFACTOR_SUMMARY.md](PROXY_REFACTOR_SUMMARY.md) - 🆕 Résumé technique

#### Architecture
- [ARCHITECTURE.md](ARCHITECTURE.md) - Architecture technique complète
- [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - Documentation complète de l'API
- [MAKEFILE_GUIDE.md](MAKEFILE_GUIDE.md) - Guide du Makefile

### Liens utiles

- **Gradio** : https://gradio.app/docs/
- **Requests** : https://requests.readthedocs.io/
- **FastAPI** : https://fastapi.tiangolo.com/
- **HuggingFace Spaces** : https://huggingface.co/docs/hub/spaces

---

## 🔄 Évolutions

### Version 2.0.0 (2025-01-21) - Implémenté ✅

- ✅ **Architecture hybride FastAPI+Gradio** : Application unique pour HuggingFace Spaces
- ✅ **Accès HTTP/REST direct** : Endpoints `/api/*` accessibles via curl/HTTP
- ✅ **Documentation complète** : 3 guides (complet, quick start, résumé technique)
- ✅ **Déploiement HF Spaces** : Compatible avec limitations HF (pas d'accès direct port 8000)
- ✅ **Mode dual** : Interface UI + API REST dans la même application

### Version 1.0.0 (2024-11-20) - Implémenté ✅

- ✅ Client proxy complet (`APIProxyClient`)
- ✅ Interface Gradio interactive
- ✅ Gestion des erreurs et timeouts
- ✅ Support batch predictions
- ✅ Tests unitaires (~95% couverture)
- ✅ Type hints complets

### Évolutions futures planifiées

Fonctionnalités à venir :

- [ ] Support WebSocket pour les logs en temps réel
- [ ] Authentification et tokens JWT pour les endpoints `/api/*`
- [ ] Cache côté client pour les réponses fréquentes
- [ ] Support multi-API (plusieurs backends FastAPI)
- [ ] Interface CLI intégrée avec commandes dédiées
- [ ] Métriques et observabilité (Prometheus/Grafana)
- [ ] Support de requêtes asynchrones (aiohttp pour meilleures performances)
- [ ] Rate limiting pour éviter les abus sur HF Spaces
- [ ] OpenAPI/Swagger UI intégré sur `/docs`

---

## 📝 Licence

Ce package fait partie du Projet 8 - MLOps (OpenClassrooms).

---

## 👥 Contribution

Pour contribuer :

1. Créer une branche : `git checkout -b feature/proxy-improvement`
2. Implémenter les changements
3. Ajouter/mettre à jour les tests
4. Vérifier le linting : `make lint`
5. Lancer les tests : `make test`
6. Créer une Pull Request

---

## 📚 Documentation associée

### Architecture et déploiement
- [ARCHITECTURE.md](ARCHITECTURE.md) - Architecture technique complète
- [DIRECT_HTTP_ACCESS.md](DIRECT_HTTP_ACCESS.md) - Accès HTTP sur HuggingFace Spaces (guide complet)
- [QUICK_START_HTTP_ACCESS.md](QUICK_START_HTTP_ACCESS.md) - Quick start HTTP (5 minutes)
- [PROXY_REFACTOR_SUMMARY.md](PROXY_REFACTOR_SUMMARY.md) - Résumé technique du refactoring

### API et tests
- [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - Documentation complète de l'API
- [MAKEFILE_GUIDE.md](MAKEFILE_GUIDE.md) - Guide des commandes Makefile

---

**Version** : 2.0.0
**Dernière mise à jour** : 21 janvier 2025
**Projet** : OpenClassrooms MLOps - Projet 8

### Changelog

**Version 2.0.0** (21 janvier 2025):
- ✅ Architecture hybride FastAPI+Gradio pour HuggingFace Spaces
- ✅ Accès HTTP/REST direct sans client Gradio (`/api/*`)
- ✅ Documentation complète en 3 niveaux
- ✅ Mise à jour diagrammes d'architecture
- ✅ Ajout commande `make run-ui-fastapi`

**Version 1.0.0** (20 novembre 2024):
- Client proxy initial (`APIProxyClient`)
- Interface Gradio standalone
- Tests unitaires complets
