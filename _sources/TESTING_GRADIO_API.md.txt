# Tests des Endpoints via Gradio API

Ce document explique comment tester les endpoints de l'API via l'interface Gradio, que ce soit en local ou sur Hugging Face Spaces.

## Vue d'ensemble

Le projet dispose d'un script de test complet ([test_gradio_api.py](../test_gradio_api.py)) qui permet de tester tous les endpoints de l'API via l'API native de Gradio. Cette approche fonctionne aussi bien en local que sur Hugging Face Spaces.

## Endpoints testés

Le script teste les 4 endpoints suivants :

1. **Health Check** (`/health`) : Vérifie l'état de l'API et du modèle
2. **Predict** (`/predict_api`) : Fait une prédiction simple
3. **Predict Proba** (`/predict_proba_api`) : Fait une prédiction avec probabilités
4. **Logs** (`/logs_api`) : Récupère les logs de l'API

## Utilisation

### Via Makefile (Recommandé)

#### Test en local

```bash
# Assurez-vous que l'API et Gradio tournent
make run-api    # Terminal 1
make run-ui     # Terminal 2

# Lancez les tests
make test-gradio-api-local
```

#### Test sur Hugging Face Spaces

```bash
# Test sur le Space public ou privé avec token
make test-gradio-api-hf
```

**Note :** Si le Space est privé, le token HuggingFace sera automatiquement chargé depuis le fichier `.env` (variable `HF_TOKEN`).

### Via Python directement

#### Test en local

```bash
# URL par défaut : http://localhost:7860
uv run python3 test_gradio_api.py

# Ou avec URL explicite
GRADIO_URL=http://localhost:7860 uv run python3 test_gradio_api.py
```

#### Test sur Hugging Face Spaces

```bash
# Space public
GRADIO_URL=https://francoisformation-oc-project8.hf.space \
    uv run python3 test_gradio_api.py

# Space privé avec token
HF_TOKEN=your_token_here \
GRADIO_URL=https://francoisformation-oc-project8.hf.space \
    uv run python3 test_gradio_api.py
```

## Configuration

### Variables d'environnement

- **`GRADIO_URL`** : URL de l'interface Gradio
  - Par défaut : `http://localhost:7860`
  - HF Spaces : `https://francoisformation-oc-project8.hf.space`

- **`HF_TOKEN`** : Token d'accès Hugging Face (optionnel)
  - Requis uniquement pour les Spaces privés
  - Peut être défini dans le fichier `.env`

### Fichier .env

Pour tester automatiquement sur HF Spaces avec un token :

```bash
# Ajoutez cette ligne à votre fichier .env
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Le Makefile chargera automatiquement ce token lors de l'exécution de `make test-gradio-api-hf`.

## Format de sortie

Le script affiche pour chaque test :

```
============================================================
TEST: Gradio API - Health Check
============================================================
Loaded as API: https://francoisformation-oc-project8.hf.space/ ✔
Status: ✅ SUCCESS
Response: {
  "status": "healthy",
  "model_loaded": true,
  "redis_connected": true,
  "version": "1.0.0"
}
```

Et un résumé final :

```
============================================================
RÉSUMÉ DES TESTS
============================================================
Health               : ✅ PASS
Predict              : ✅ PASS
Predict Proba        : ✅ PASS
Logs                 : ✅ PASS

Résultat: 4/4 tests réussis

🎉 Tous les tests ont réussi !
```

## Payload de test

Le script utilise un patient de test avec les caractéristiques suivantes :

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
  "CHEST PAIN": 1,
  "CHRONIC DISEASE": 0
}
```

Ce profil correspond à un patient à risque modéré-élevé.

## Dépannage

### Erreur de connexion en local

**Symptôme :** `Connection refused` ou `Could not connect to Gradio`

**Solution :**
1. Vérifiez que l'API tourne : `curl http://localhost:8000/health`
2. Vérifiez que Gradio tourne : `curl http://localhost:7860`
3. Redémarrez les services :
   ```bash
   make run-api
   make run-ui
   ```

### Erreur de token sur HF Spaces

**Symptôme :** `401 Unauthorized` ou `Space is private`

**Solution :**
1. Vérifiez que `HF_TOKEN` est défini dans `.env`
2. Vérifiez que le token est valide sur [Hugging Face Settings](https://huggingface.co/settings/tokens)
3. Vérifiez que le token a les permissions nécessaires (`read` minimum)

### Timeout lors des tests

**Symptôme :** `TimeoutError` ou `Request timed out`

**Solution :**
1. Le Space HF est peut-être en cours de démarrage (cold start)
2. Attendez quelques secondes et réessayez
3. Vérifiez que le Space est actif sur [HF Spaces Dashboard](https://huggingface.co/spaces/francoisformation/oc-project8)

## Comparaison avec les tests unitaires

| Aspect | Tests unitaires (pytest) | Tests Gradio API |
|--------|-------------------------|------------------|
| **Scope** | Teste le code Python directement | Teste l'API via HTTP |
| **Environnement** | Mock du modèle et de Redis | Vrai modèle et vrai Redis |
| **Vitesse** | Très rapide (~0.3s) | Plus lent (~5-10s) |
| **Usage** | CI/CD, développement | Validation end-to-end |
| **HF Spaces** | Non applicable | ✅ Fonctionne |

## Intégration CI/CD

Les tests Gradio API peuvent être intégrés dans une pipeline CI/CD :

```yaml
# Exemple GitHub Actions
- name: Test Gradio API on HF Spaces
  env:
    HF_TOKEN: ${{ secrets.HF_TOKEN }}
  run: make test-gradio-api-hf
```

## Références

- [Script de test](../test_gradio_api.py)
- [Makefile](../Makefile) (commandes `test-gradio-api-local` et `test-gradio-api-hf`)
- [Documentation Gradio Client](https://www.gradio.app/guides/gradio-client)
- [HF Spaces](https://huggingface.co/spaces/francoisformation/oc-project8)
