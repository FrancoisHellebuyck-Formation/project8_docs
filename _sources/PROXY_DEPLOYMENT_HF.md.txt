# Déploiement du Package Proxy sur HuggingFace Spaces

## ✅ Vérification du déploiement

### 1. Le package proxy sera-t-il déployé sur HF ?

**OUI**, le package `src/proxy/` sera bien déployé sur HuggingFace Spaces.

#### Preuve dans le workflow CI/CD

Le fichier `.github/workflows/cicd.yml` (lignes 134-138) supprime uniquement :
- `docs/` (documentation)
- `tests/` (tests unitaires)
- `sql/` (fichiers SQL)
- `docker/` (Dockerfiles locaux)
- `docker-compose.yml`

**Le dossier `src/` est conservé intégralement**, incluant `src/proxy/`.

#### Preuve dans le Dockerfile HF

Le `docker/Dockerfile.hf` (ligne 35) copie explicitement :
```dockerfile
COPY src/ ./src/
```

Cela inclut :
- `src/api/` ✅
- `src/model/` ✅
- `src/ui/` ✅
- **`src/proxy/` ✅** ← Package proxy inclus
- `src/config.py` ✅
- `src/logs_pipeline/` ✅
- `src/simulator/` ✅

### 2. Dépendances du package proxy

Toutes les dépendances nécessaires sont déjà dans `pyproject.toml` :

| Dépendance | Version | Statut | Usage |
|------------|---------|--------|-------|
| gradio | ≥5.0.0 | ✅ Présente | Interface Gradio |
| requests | ≥2.31.0 | ✅ Présente | Client HTTP |
| python-dotenv | ≥1.0.0 | ✅ Présente | Configuration |

**Aucune dépendance supplémentaire requise**.

### 3. Structure déployée sur HF

```
/app/
├── src/
│   ├── api/              ✅ Déployé
│   ├── model/            ✅ Déployé
│   ├── ui/               ✅ Déployé
│   ├── proxy/            ✅ Déployé (nouveau)
│   │   ├── __init__.py
│   │   ├── client.py
│   │   └── gradio_app.py
│   ├── logs_pipeline/    ✅ Déployé
│   ├── simulator/        ✅ Déployé
│   └── config.py         ✅ Déployé
├── model/
│   └── model.pkl         ✅ Déployé (via Git LFS)
└── .env                  ✅ Déployé (copie de .env.example)
```

### 4. Tests d'import

```bash
# Test local avec uv
uv run python3 -c "from src.proxy import APIProxyClient; print('✅ OK')"
# Résultat: ✅ Import du package proxy: OK
```

---

## 🔧 Utilisation du package proxy sur HF

### Option 1 : Utiliser l'UI Gradio existante (déployée)

L'interface Gradio déployée (`src/ui/app.py`) utilise **automatiquement** le package proxy sur HuggingFace Spaces :

**Détection automatique** :
- ✅ Sur HuggingFace (détecté via `SPACE_ID`) → Utilise `APIProxyClient`
- ✅ En local → Utilise les fonctions proxy simples (requests direct)

**Fonctions proxy disponibles** :
- `api_health_proxy()` → `proxy_client.get_health()` (sur HF)
- `api_predict_proxy()` → `proxy_client.post_predict()` (sur HF)
- `api_predict_proba_proxy()` → `proxy_client.post_predict_proba()` (sur HF)
- `api_logs_proxy()` → `proxy_client.get_logs()` (sur HF)
- `api_clear_logs_proxy()` → `proxy_client.delete_logs()` (sur HF)

**Cette interface est celle qui sera accessible sur HF Spaces** à l'URL :
```
https://francoisformation-oc-project8.hf.space
```

**Avantages du package proxy sur HF** :
- ✅ Gestion d'erreurs unifiée et robuste
- ✅ Timeouts configurables
- ✅ Logging amélioré
- ✅ Code maintenu et testé

### Option 2 : Utiliser le client proxy programmatiquement

Si vous avez accès au backend HF ou pour des scripts de test :

```python
from src.proxy import APIProxyClient

# Créer un client pointant vers l'API HF
client = APIProxyClient(
    api_url="http://localhost:8000"  # API interne au conteneur HF
)

# Utiliser le client
response, status = client.get_health()
print(response)
```

### Option 3 : Lancer l'interface proxy standalone (développement local)

**Pour le développement local uniquement**, pas sur HF Spaces :

```bash
# Terminal 1 : API
make run-api

# Terminal 2 : Interface proxy complète
make run-proxy

# Accès : http://localhost:7860
```

---

## 📊 Comparaison des interfaces

### Interface principale (`src/ui/app.py`) - Déployée sur HF

**Usage** : Interface utilisateur pour les prédictions
**Endpoints exposés** :
- ✅ Health check
- ✅ Prédiction ML
- ✅ Probabilités
- ✅ Logs (consultation + suppression)

**Caractéristiques** :
- Interface orientée utilisateur final
- Formulaire de saisie des symptômes
- Affichage du résultat de prédiction
- Consultation des logs récents

### Interface proxy (`src/proxy/gradio_app.py`) - Pour développement

**Usage** : Outil de développement et test
**Endpoints exposés** :
- ✅ Informations API (GET /)
- ✅ Health check
- ✅ Prédiction ML
- ✅ Probabilités
- ✅ Logs (consultation + suppression)
- ✅ Vérification de connexion

**Caractéristiques** :
- Interface orientée développeur
- Tous les endpoints exposés
- Format de réponse JSON brut
- Tests et debugging

---

## 🎯 Cas d'usage du package proxy

### Sur HuggingFace Spaces

Le package `src/proxy/` sera **disponible mais non utilisé directement** sur HF Spaces.

**Pourquoi déployé alors ?**
1. **Cohérence** : Le code source complet est déployé
2. **Flexibilité** : Possibilité d'utiliser le client dans des scripts
3. **Maintenance** : Facilite les mises à jour futures
4. **Pas de surcoût** : Le package est léger (~700 lignes)

### En développement local

Le package proxy est **essentiel** pour :

1. **Tester tous les endpoints** sans interface utilisateur
2. **Développer des scripts** de monitoring ou de batch
3. **Débugger l'API** avec une interface complète
4. **Automatiser des tâches** via le client Python

---

## 🚀 Workflow de déploiement

### Étapes de déploiement HF

1. **Build** : GitHub Actions construit l'image Docker
2. **Préparation** :
   - Copie `docker/Dockerfile.hf` → `Dockerfile`
   - Copie `docs/README_HF.md` → `README.md`
   - Supprime `docs/`, `tests/`, `sql/`, `docker/`
   - **Conserve `src/` intégralement** (incluant `src/proxy/`)
3. **Push** : Push vers HuggingFace Spaces
4. **Démarrage** : Le conteneur HF :
   - Lance Redis (port 6379)
   - Lance FastAPI (port 8000)
   - Lance Gradio UI (port 7860) ← Interface principale

### Ce qui est accessible sur HF

- ✅ **Interface Gradio principale** : https://francoisformation-oc-project8.hf.space
- ✅ **API FastAPI interne** : http://localhost:8000 (dans le conteneur)
- ✅ **Redis interne** : localhost:6379 (dans le conteneur)
- ❌ **Interface proxy standalone** : Non lancée (car `src/ui/app.py` est lancé)

---

## 📝 Résumé

### ✅ Package proxy déployé sur HF ?

**OUI** - Le code est déployé dans `/app/src/proxy/`

### ✅ Package proxy utilisé sur HF ?

**OUI (automatiquement)** - L'interface `src/ui/app.py` détecte HF et utilise `APIProxyClient`

### ✅ Package proxy utile ?

**OUI** - Utilisé automatiquement sur HF + développement local + scripts

### ✅ Détection automatique ?

**OUI** - Via variable d'environnement `SPACE_ID` (présente uniquement sur HF)

---

## 🔍 Vérification après déploiement

### 1. Vérifier que le package est présent

```bash
# Se connecter au conteneur HF (si accès)
ls /app/src/proxy/

# Devrait afficher:
# __init__.py
# client.py
# gradio_app.py
# README.md
```

### 2. Vérifier l'import

```python
# Depuis un notebook HF ou script
from src.proxy import APIProxyClient

client = APIProxyClient(api_url="http://localhost:8000")
print("✅ Package proxy disponible")
```

### 3. Vérifier l'interface principale

Accéder à : https://francoisformation-oc-project8.hf.space

Devrait afficher l'interface Gradio de prédiction ML.

---

## 🎓 Recommandations

### Pour HuggingFace Spaces

**Utiliser l'interface principale** (`src/ui/app.py`) qui est :
- Optimisée pour les utilisateurs finaux
- Déjà déployée et fonctionnelle
- Intégrée avec l'API et Redis

### Pour le développement local

**Utiliser le package proxy** (`src/proxy/`) pour :
- Tester tous les endpoints API
- Développer des scripts de monitoring
- Débugger l'API complète
- Automatiser des tâches

### Pour l'utilisation programmatique

**Utiliser le client proxy** (`APIProxyClient`) pour :
- Intégrer l'API dans d'autres applications
- Créer des scripts de batch predictions
- Monitorer la santé de l'API
- Gérer les logs programmatiquement

---

**Conclusion** : Le package proxy sera bien déployé sur HuggingFace Spaces et sera **utilisé automatiquement** par l'interface principale via détection de l'environnement HF. En local, ce sont les fonctions proxy simples qui sont utilisées pour plus de légèreté.

**Dernière mise à jour** : 2025-01-21
