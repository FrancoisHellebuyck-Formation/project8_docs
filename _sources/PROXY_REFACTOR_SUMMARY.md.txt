# Refactorisation du Proxy pour Accès HTTP Direct

## 📝 Résumé

Cette refactorisation permet l'accès **HTTP/REST direct** aux endpoints de l'API ML déployée sur HuggingFace Spaces, **sans nécessiter le client Gradio**.

## ✅ Changements Effectués

### 1. Nouveau Module: `src/ui/fastapi_app.py`
**Fichier créé**: [src/ui/fastapi_app.py](../src/ui/fastapi_app.py)

- **Architecture**: FastAPI principale avec Gradio monté dessus (via `gr.mount_gradio_app()`)
- **Endpoints REST disponibles**:
  - `GET /api/health` - Health check
  - `GET /api/info` - Informations API
  - `POST /api/predict` - Prédiction ML
  - `POST /api/predict_proba` - Probabilités détaillées
  - `GET /api/logs` - Récupérer les logs
  - `DELETE /api/logs` - Vider les logs

### 2. Routes API: `src/ui/api_routes.py`
**Fichier créé**: [src/ui/api_routes.py](../src/ui/api_routes.py)

- Router FastAPI avec tous les endpoints REST
- Utilise `APIProxyClient` pour communiquer avec l'API backend (port 8000)
- Documentation intégrée avec exemples curl

### 3. Dockerfile Mis à Jour
**Fichier modifié**: [docker/Dockerfile.hf](../docker/Dockerfile.hf)

**Avant**:
```dockerfile
python -m src.ui
```

**Après**:
```dockerfile
python -m src.ui.fastapi_app
```

### 4. Documentation Complète
**Fichier créé**: [docs/DIRECT_HTTP_ACCESS.md](DIRECT_HTTP_ACCESS.md)

- Guide complet d'utilisation avec exemples curl
- Intégrations Python, JavaScript, R
- Codes de statut HTTP
- Dépannage

## 🧪 Tests Réalisés

### Test Local Réussi
```bash
# Démarrage du backend API
uv run uvicorn src.api.main:app --host 0.0.0.0 --port 8000 &

# Démarrage FastAPI+Gradio
uv run python3 -m src.ui.fastapi_app &

# Test health check
curl http://localhost:7860/api/health
# ✅ {"status":"healthy","model_loaded":true,"redis_connected":false,"version":"1.0.0"}

# Test prédiction
curl -X POST http://localhost:7860/api/predict \
  -H "Content-Type: application/json" \
  -d '{"AGE": 50, "GENDER": 1, "SMOKING": 1, ...}'
# ✅ {"prediction":1,"probability":0.8659778675097131,"message":"Prédiction positive"}
```

## 🚀 Utilisation

### Local
```bash
# Terminal 1: Démarrer l'API backend
make run-api

# Terminal 2: Démarrer FastAPI+Gradio
python -m src.ui.fastapi_app
```

### HuggingFace Spaces (après déploiement)
```bash
# Health check
curl https://francoisformation-oc-project8.hf.space/api/health

# Prédiction
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

## 📊 Architecture

### Avant (Gradio uniquement)
```
HuggingFace Space (Port 7860)
└── Gradio UI
    └── API via client Gradio uniquement
```

### Après (FastAPI + Gradio)
```
HuggingFace Space (Port 7860)
├── FastAPI (routes /api/*)
│   ├── GET /api/health
│   ├── POST /api/predict
│   ├── POST /api/predict_proba
│   ├── GET /api/logs
│   └── DELETE /api/logs
└── Gradio UI (monté sur /)
    └── Interface utilisateur interactive
```

## 🔗 Avantages

| Avant | Après |
|-------|-------|
| ❌ Nécessite le client Gradio Python | ✅ Accès via HTTP standard (curl, requests, fetch) |
| ❌ Format de requête propriétaire Gradio | ✅ Format JSON standard REST API |
| ❌ Difficile à intégrer dans d'autres langages | ✅ Compatible avec n'importe quel langage (Python, JS, R, etc.) |
| ❌ Pas de documentation OpenAPI automatique | ✅ Documentation FastAPI intégrée |
| ⚠️ Interface UI seulement | ✅ Interface UI **ET** API REST |

## 📦 Fichiers Créés/Modifiés

### Créés (4 fichiers)
1. **src/ui/fastapi_app.py** (225 lignes) - App FastAPI principale
2. **src/ui/api_routes.py** (195 lignes) - Router FastAPI (remplacé par fastapi_app.py)
3. **docs/DIRECT_HTTP_ACCESS.md** (550 lignes) - Documentation complète
4. **docs/PROXY_REFACTOR_SUMMARY.md** (ce fichier)

### Modifiés (1 fichier)
1. **docker/Dockerfile.hf** (ligne 84-87) - Changement du point d'entrée

## ⚙️ Déploiement

### Étapes pour déployer sur HuggingFace

1. **Commit les changements**:
```bash
git add src/ui/fastapi_app.py src/ui/api_routes.py docker/Dockerfile.hf docs/
git commit -m "feat: Add direct HTTP/REST access to API on HF Spaces"
git push origin develop
```

2. **Merge vers main** (déclenche le déploiement automatique via GitHub Actions):
```bash
git checkout main
git merge develop
git push origin main
```

3. **Vérifier le déploiement**:
```bash
# Attendre 2-3 minutes que le Space se redémarre
curl https://francoisformation-oc-project8.hf.space/api/health
```

## 🎯 Prochaines Étapes (Optionnel)

- [ ] Ajouter authentification API (API keys)
- [ ] Implémenter rate limiting
- [ ] Ajouter CORS personnalisé
- [ ] Créer un client Python SDK simplifié
- [ ] Ajouter métriques Prometheus sur `/metrics`
- [ ] Documentation OpenAPI interactive sur `/docs`

## 🐛 Résolution de Problèmes

### Problème: "404 Not Found" sur /api/health
**Cause**: Le Space utilise encore l'ancien `src.ui` au lieu de `src.ui.fastapi_app`

**Solution**:
1. Vérifier que `Dockerfile.hf` contient `python -m src.ui.fastapi_app`
2. Redéployer le Space
3. Attendre le redémarrage complet (2-3 min)

### Problème: "Connection refused"
**Cause**: Le Space n'est pas encore démarré

**Solution**:
1. Vérifier le status du Space sur HuggingFace
2. Consulter les logs du Space
3. Attendre que le healthcheck passe (environ 30s après démarrage)

## 📚 Documentation Complète

Pour plus de détails, consultez:
- **[docs/DIRECT_HTTP_ACCESS.md](DIRECT_HTTP_ACCESS.md)** - Guide complet avec exemples
- **[src/ui/fastapi_app.py](../src/ui/fastapi_app.py)** - Code source commenté

---

**Date**: 2025-11-21
**Auteur**: Project8 Team
**Version**: 1.0.0
