# Documentation de l'Interface Gradio

## 📋 Vue d'ensemble

L'interface Gradio fournit une interface utilisateur web intuitive pour interagir avec le modèle de prédiction de cancer du poumon. Elle communique avec l'API FastAPI pour obtenir les prédictions.

## 🎨 Interface utilisateur

### Sections de l'interface

L'interface est organisée en plusieurs sections logiques :

#### 1. Informations générales
- **Âge** : Slider de 0 à 120 ans
- **Genre** : Liste déroulante (Féminin / Masculin)

#### 2. Facteurs de risque comportementaux
- **Fumeur** : Case à cocher
- **Consommation d'alcool** : Case à cocher
- **Pression des pairs** : Case à cocher

#### 3. Signes physiques
- **Doigts jaunes** : Case à cocher
- **Anxiété** : Case à cocher
- **Fatigue chronique** : Case à cocher
- **Allergies** : Case à cocher

#### 4. Symptômes respiratoires
- **Respiration sifflante** : Case à cocher
- **Toux persistante** : Case à cocher
- **Essoufflement** : Case à cocher

#### 5. Autres symptômes
- **Difficulté à avaler** : Case à cocher
- **Douleur thoracique** : Case à cocher

#### 6. Résultat
- **Bouton "Obtenir la prédiction"** : Lance la prédiction
- **Niveau de risque** : Affiche le niveau de risque (🟢 FAIBLE, 🔴 ÉLEVÉ, ⚫ ERREUR)
- **Message détaillé** : Affiche le message de prédiction et la probabilité

## 🚀 Utilisation

### Lancement de l'interface

```bash
# Avec Make
make run-ui

# Directement avec Python
python -m src.ui.app

# Avec le module
python -c "from src.ui import launch_ui; launch_ui()"
```

L'interface sera accessible sur : **http://localhost:7860**

### Configuration

L'interface utilise les variables d'environnement suivantes (définies dans `.env`) :

```env
# Configuration Gradio
GRADIO_HOST=0.0.0.0
GRADIO_PORT=7860
API_URL=http://localhost:8000
```

### Workflow d'utilisation

1. **Remplir les informations du patient**
   - Ajuster l'âge avec le slider
   - Sélectionner le genre dans la liste déroulante
   - Cocher les cases correspondant aux symptômes et caractéristiques du patient
   - Les cases non cochées correspondent à "Non" (0)

2. **Obtenir la prédiction**
   - Cliquer sur le bouton "Obtenir la prédiction"
   - Le système envoie automatiquement les données à l'API
   - Les features dérivées sont calculées automatiquement par l'API

3. **Interpréter les résultats**
   - **Niveau de risque** : Indique si le risque est faible ou élevé
   - **Message détaillé** : Fournit des informations supplémentaires
   - **Probabilité** : Affiche la probabilité de la prédiction

## 📊 Exemples de cas d'utilisation

### Cas 1 : Patient à risque élevé

```
Âge: 65 ans
Genre: Masculin
Fumeur: ✓
Consommation d'alcool: ✓
Doigts jaunes: ✓
Fatigue chronique: ✓
Respiration sifflante: ✓
Toux persistante: ✓
Essoufflement: ✓
Douleur thoracique: ✓

Résultat: 🔴 RISQUE ÉLEVÉ
Probabilité: ~85%
```

### Cas 2 : Patient à risque faible

```
Âge: 30 ans
Genre: Féminin
Tous les symptômes: Non

Résultat: 🟢 RISQUE FAIBLE
Probabilité: ~95%
```

## 🔧 Architecture technique

### Communication avec l'API

L'interface communique avec l'API via des requêtes HTTP POST :

```python
# Endpoint utilisé
POST http://localhost:8000/predict

# Format du payload
{
  "AGE": 65,
  "GENDER": 1,
  "SMOKING": 1,
  "ALCOHOL CONSUMING": 1,
  ...
}
```

### Endpoints API Proxy

Gradio expose maintenant des **endpoints API proxy** qui redirigent vers l'API FastAPI. Cela permet d'accéder à l'API via le port Gradio (7860) au lieu du port FastAPI (8000).

**Endpoints disponibles :**

#### 1. Health Check
```bash
GET http://localhost:7860/api/health
```

**Exemple :**
```bash
curl http://localhost:7860/api/health
```

**Réponse :**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "redis_connected": true
}
```

#### 2. Prédiction binaire
```bash
POST http://localhost:7860/api/predict
```

**Exemple :**
```bash
curl -X POST http://localhost:7860/api/predict \
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

**Réponse :**
```json
{
  "prediction": 1,
  "message": "Risque élevé de cancer du poumon"
}
```

#### 3. Prédiction avec probabilités
```bash
POST http://localhost:7860/api/predict_proba
```

**Exemple :**
```bash
curl -X POST http://localhost:7860/api/predict_proba \
  -H "Content-Type: application/json" \
  -d '{...}'  # Même payload que /predict
```

**Réponse :**
```json
{
  "prediction": 1,
  "probability": 0.87,
  "message": "Risque élevé de cancer du poumon (probabilité: 87.0%)"
}
```

#### 4. Récupération des logs
```bash
GET http://localhost:7860/api/logs?limit=100
```

**Exemple :**
```bash
curl "http://localhost:7860/api/logs?limit=10"
```

**Réponse :**
```json
{
  "logs": [
    "2025-01-14 10:30:15 - INFO - Prediction received",
    "2025-01-14 10:30:16 - INFO - Model prediction: 1"
  ],
  "count": 2
}
```

### Avantages des endpoints proxy

1. **Un seul port à exposer** : En production (HuggingFace Spaces), seul le port 7860 (Gradio) est exposé
2. **Simplification du déploiement** : Pas besoin d'exposer le port FastAPI (8000) publiquement
3. **Accès unifié** : Toute l'application accessible via une seule URL
4. **Sécurité renforcée** : L'API FastAPI reste en backend (localhost uniquement)

### Tester les endpoints proxy

Un script de test est fourni :

```bash
# Lancer l'API et Gradio
make run-api &
make run-ui &

# Tester les endpoints proxy
python test_gradio_endpoints.py
```

### Gestion des erreurs

L'interface gère automatiquement plusieurs types d'erreurs :

1. **Erreur de connexion** : L'API n'est pas accessible
2. **Timeout** : L'API ne répond pas dans le délai imparti (10s)
3. **Erreur HTTP** : L'API retourne une erreur (4xx, 5xx)
4. **Erreur inattendue** : Toute autre erreur

Chaque type d'erreur affiche un message approprié à l'utilisateur.

## 🎨 Personnalisation

### Modifier le thème

Le thème de l'interface peut être modifié dans `src/ui/app.py` :

```python
interface = gr.Blocks(
    title="Prédiction Cancer du Poumon",
    theme=gr.themes.Soft()  # Changer ici: Soft, Base, Monochrome, etc.
)
```

### Modifier les valeurs par défaut

Les valeurs par défaut peuvent être ajustées :

```python
age_input = gr.Slider(
    minimum=0,
    maximum=120,
    value=50,  # Valeur par défaut
    step=1,
    label="Âge"
)
```

### Activer le partage public

Pour créer un lien public partageable (utile pour les démos) :

```python
launch_ui(share=True)
```

Ou via la ligne de commande :

```bash
python -c "from src.ui import launch_ui; launch_ui(share=True)"
```

## 🔒 Sécurité

### Bonnes pratiques

1. **Ne jamais exposer l'interface publiquement en production** sans authentification
2. **Utiliser HTTPS** en production avec un reverse proxy
3. **Limiter l'accès** via firewall ou réseau privé
4. **Valider les données** côté API (déjà implémenté avec Pydantic)

### Mode développement vs production

```bash
# Développement (localhost uniquement)
GRADIO_HOST=127.0.0.1
GRADIO_PORT=7860

# Production (accessible depuis le réseau)
GRADIO_HOST=0.0.0.0
GRADIO_PORT=7860
```

## 🐳 Docker

L'interface Gradio sera déployée dans un conteneur Docker séparé (Docker 2) :

```yaml
# À venir : docker-compose pour l'UI
services:
  ui:
    build: ./docker-ui
    ports:
      - "7860:7860"
    environment:
      - API_URL=http://api:8000
    depends_on:
      - api
```

## 🧪 Tests

### Test manuel

1. Lancer l'API : `make run-api`
2. Lancer l'interface : `make run-ui`
3. Ouvrir http://localhost:7860
4. Tester différentes combinaisons de paramètres

### Test de connexion

Vérifier que l'API est accessible :

```bash
curl http://localhost:8000/health
```

## 📝 Notes importantes

### Avertissement médical

L'interface affiche un avertissement clair :

> **Note**: Cette application est à but éducatif uniquement et ne remplace pas un diagnostic médical professionnel.

### Feature engineering automatique

L'utilisateur ne saisit que **14 features** (les features d'entrée). Les **14 features dérivées** sont calculées automatiquement par l'API :

**Features saisies** (14) :
- AGE, GENDER, SMOKING, ALCOHOL CONSUMING, PEER_PRESSURE
- YELLOW_FINGERS, ANXIETY, FATIGUE, ALLERGY
- WHEEZING, COUGHING, SHORTNESS OF BREATH
- SWALLOWING DIFFICULTY, CHEST PAIN

**Features calculées automatiquement** (14) :
- SMOKING_x_AGE, SMOKING_x_ALCOHOL, RESPIRATORY_SYMPTOMS
- TOTAL_SYMPTOMS, BEHAVIORAL_RISK_SCORE, etc.

Voir [FEATURE_ENGINEERING.md](FEATURE_ENGINEERING.md) pour plus de détails.

## 🔗 Liens utiles

- [Documentation API](API_DOCUMENTATION.md)
- [Feature Engineering](FEATURE_ENGINEERING.md)
- [Documentation Gradio](https://www.gradio.app/docs/)
- [Variables d'environnement](ENV_VARIABLES.md)

## 🆘 Dépannage

### Problème : Interface inaccessible

```bash
# Vérifier que le port n'est pas déjà utilisé
lsof -i :7860

# Vérifier les logs
tail -f logs/gradio.log
```

### Problème : Erreur de connexion à l'API

```bash
# Vérifier que l'API est lancée
curl http://localhost:8000/health

# Vérifier la configuration
cat .env | grep API_URL
```

### Problème : Prédictions incorrectes

Vérifier que :
1. L'API utilise le bon modèle (`MODEL_PATH` correct)
2. Le feature engineering est activé
3. Les données sont correctement formatées

## 📊 Améliorations futures

- [ ] Ajouter l'authentification utilisateur
- [ ] Historique des prédictions
- [ ] Graphiques de visualisation des features
- [ ] Export des résultats en PDF
- [ ] Multi-langue (FR/EN)
- [ ] Dark mode
- [ ] Batch predictions (plusieurs patients)
