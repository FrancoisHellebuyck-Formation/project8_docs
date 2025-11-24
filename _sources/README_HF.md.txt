---
title: Lung Cancer Prediction
emoji: 🫁
colorFrom: green
colorTo: red
sdk: docker
app_port: 7860
pinned: false
license: mit
---

# 🫁 Lung Cancer Prediction - MLOps Project

Application de prédiction de cancer du poumon avec interface Gradio et API FastAPI.

## 🎯 Fonctionnalités

- **🎨 Interface Gradio** : Interface utilisateur intuitive avec barre de progression colorée
- **📊 API REST FastAPI** : Endpoints `/predict`, `/predict_proba`, `/health`, `/logs`
- **🤖 Modèle ML LightGBM** : Modèle optimisé avec feature engineering automatique
- **📈 Feature Engineering** : 15 features d'entrée → 29 features totales (14 dérivées)
- **📝 Logs Redis** : Système de logging persistant avec Redis in-memory (256MB)

## 🚀 Utilisation

### Interface Gradio (Port 7860)

L'interface Gradio est accessible directement sur le port principal. Elle permet de :
- Saisir les informations du patient (âge, genre, symptômes)
- Obtenir une prédiction visuelle avec barre de probabilité
- Visualiser le risque : FAIBLE 🟢 / MODÉRÉ 🟠 / ÉLEVÉ 🔴

### API REST

L'API FastAPI tourne en arrière-plan. Vous pouvez l'utiliser de **deux façons** :

#### Méthode 1 : Via l'API Gradio (Recommandée pour HF Spaces)

**Compatible Hugging Face Spaces** - Utilise l'API native de Gradio :

```python
from gradio_client import Client

client = Client("https://francoisformation-oc-project8.hf.space")

# Health check
health = client.predict(api_name="/health")

# Prédiction
payload = {"AGE": 65, "GENDER": 1, "SMOKING": 1, ...}
result = client.predict(payload, api_name="/predict_api")

# Prédiction avec probabilités
result_proba = client.predict(payload, api_name="/predict_proba_api")

# Récupérer les logs (limite: 10)
logs = client.predict(10, api_name="/logs_api")
```

**Endpoints disponibles :**
- `/api/health` : État de santé de l'API
- `/api/predict_api` : Prédiction binaire (0 ou 1)
- `/api/predict_proba_api` : Prédiction avec probabilités
- `/api/logs_api` : Récupérer les logs

#### Méthode 2 : Accès direct FastAPI (Développement local uniquement)

**Non disponible sur HF Spaces** - L'API FastAPI tourne sur le port 8000 en local :

```bash
# Endpoints FastAPI (localhost uniquement)
curl http://localhost:8000/health
curl -X POST http://localhost:8000/predict -H "Content-Type: application/json" -d '{...}'
```

**Exemple complet avec Python :**

```python
from gradio_client import Client

# Connexion au Space
client = Client("https://francoisformation-oc-project8.hf.space")

# Prédiction
result = client.predict(
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
        "CHEST PAIN": 1,
        "CHRONIC DISEASE": 0
    },
    api_name="/predict_proba_api"
)

print(f"Prédiction: {result['prediction']}")
print(f"Probabilité: {result['probability']:.2%}")
print(f"Message: {result['message']}")
```

### 🧪 Tests automatisés

Un script de test complet est fourni pour valider tous les endpoints :

```bash
# Test en local (nécessite API + Gradio lancés)
make test-gradio-api-local

# Test sur HuggingFace Spaces (Space PUBLIC uniquement)
make test-gradio-api-hf

# Ou directement avec Python
python test_gradio_api.py  # Local par défaut
GRADIO_URL=https://francoisformation-oc-project8.hf.space python test_gradio_api.py
```

**⚠️ Important : Spaces privés vs publics**

Les endpoints Gradio API sont accessibles **uniquement si le Space HuggingFace est PUBLIC**.

- **Space PUBLIC** : Accessible sans authentification via `gradio_client`
- **Space PRIVÉ** : Nécessite un token HuggingFace

**Configuration du token pour Space privé :**

1. Créer un token sur https://huggingface.co/settings/tokens
2. Ajouter le token dans votre fichier `.env` :
   ```bash
   HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxx
   ```
3. Lancer les tests (le Makefile charge automatiquement le token depuis .env) :
   ```bash
   make test-gradio-api-hf
   ```

**Ou manuellement avec variable d'environnement :**
```bash
HF_TOKEN=your_hf_token GRADIO_URL=https://francoisformation-oc-project8.hf.space python test_gradio_api.py
```

**Pour rendre votre Space public :** Settings → Visibility → Public

## 📋 Features du modèle

**15 features d'entrée :**
- AGE, GENDER, SMOKING, ALCOHOL CONSUMING, PEER_PRESSURE
- YELLOW_FINGERS, ANXIETY, FATIGUE, ALLERGY
- WHEEZING, COUGHING, SHORTNESS OF BREATH
- SWALLOWING DIFFICULTY, CHEST PAIN, CHRONIC DISEASE

**14 features dérivées (automatiques) :**
- HIGH_RISK_PROFILE, AGE_SQUARED, TOTAL_SYMPTOMS
- RESPIRATORY_SYMPTOMS, CANCER_TRIAD, SMOKER_WITH_RESP_SYMPTOMS
- ADVANCED_SYMPTOMS, SYMPTOMS_PER_AGE, AGE_RISK_INTERACTION
- MALE_SMOKER, SYMPTOM_INTENSITY, RESPIRATORY_DISTRESS
- CHRONIC_SMOKER_SYMPTOMS, SYMPTOM_DIVERSITY

## ⚙️ Architecture

```
┌────────────────────────────────────────┐
│   Hugging Face Space Container         │
│                                        │
│  ┌──────────────────────────────┐     │
│  │   Gradio UI (Port 7860)      │◄────┼─── Interface publique
│  │   (Frontend)                 │     │
│  └────────────┬─────────────────┘     │
│               │ localhost HTTP        │
│               ↓                        │
│  ┌──────────────────────────────┐     │
│  │   FastAPI (Port 8000)        │     │
│  │   (Backend)                  │     │
│  └────────────┬─────────────────┘     │
│               │                        │
│               ↓                        │
│  ┌──────────────────────────────┐     │
│  │   Redis (Port 6379)          │     │
│  │   (In-Memory Logs)           │     │
│  └──────────────────────────────┘     │
│               ↑                        │
│  ┌────────────┴─────────────────┐     │
│  │   LightGBM Model             │     │
│  │   (ML Engine)                │     │
│  └──────────────────────────────┘     │
└────────────────────────────────────────┘
```

## 🏗️ Technologies

- **Python 3.13+** : Langage principal
- **FastAPI** : Framework API REST
- **Gradio** : Interface utilisateur interactive
- **LightGBM** : Algorithme de machine learning
- **Redis** : Base de données in-memory pour les logs
- **Pydantic v2** : Validation des données
- **Scikit-learn** : Pipeline ML
- **Docker** : Containerisation
- **pytest** : Tests unitaires (83% coverage)

## 📚 Documentation

- **Documentation API** : Disponible via `/docs` (Swagger UI)
- **Tests** : 126 tests unitaires avec 83% de couverture
- **CI/CD** : GitHub Actions avec tests automatiques
- **Code Quality** : Flake8 compliant (88 char max)

## ⚠️ Avertissement

Cette application est à **but éducatif uniquement** et ne remplace pas un diagnostic médical professionnel. Les prédictions doivent être interprétées par un professionnel de santé qualifié.

## 📄 Licence

MIT License - Projet OpenClassrooms MLOps (Partie 2/2)

---

**Développé avec ❤️ dans le cadre du parcours MLOps OpenClassrooms**
