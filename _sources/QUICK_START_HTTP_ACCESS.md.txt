# Quick Start - Accès HTTP Direct

Guide rapide pour utiliser l'API ML via HTTP/curl sur HuggingFace Spaces.

## 🚀 URL du Space

```
https://francoisformation-oc-project8.hf.space
```

## ⚡ Exemples Rapides

### 1. Health Check (5 secondes)
```bash
curl https://francoisformation-oc-project8.hf.space/api/health
```

**Réponse attendue**:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "redis_connected": false,
  "version": "1.0.0"
}
```

### 2. Prédiction Rapide (10 secondes)
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

**Réponse attendue**:
```json
{
  "prediction": 1,
  "probability": 0.92,
  "message": "Prédiction positive"
}
```

### 3. Probabilités Détaillées
```bash
curl -X POST https://francoisformation-oc-project8.hf.space/api/predict_proba \
  -H "Content-Type: application/json" \
  -d '{"AGE": 50, "GENDER": 2, "SMOKING": 0, ...}'
```

### 4. Logs (Derniers 10)
```bash
curl "https://francoisformation-oc-project8.hf.space/api/logs?limit=10"
```

## 📋 Format des Données

### Features Obligatoires (14)
| Feature | Type | Valeurs | Description |
|---------|------|---------|-------------|
| AGE | int | 20-80 | Âge du patient |
| GENDER | int | 1=M, 2=F | Genre |
| SMOKING | int | 0/1 | Fumeur |
| ALCOHOL CONSUMING | int | 0/1 | Consommation d'alcool |
| PEER_PRESSURE | int | 0/1 | Pression des pairs |
| YELLOW_FINGERS | int | 0/1 | Doigts jaunes |
| ANXIETY | int | 0/1 | Anxiété |
| FATIGUE | int | 0/1 | Fatigue |
| ALLERGY | int | 0/1 | Allergies |
| WHEEZING | int | 0/1 | Respiration sifflante |
| COUGHING | int | 0/1 | Toux |
| SHORTNESS OF BREATH | int | 0/1 | Essoufflement |
| SWALLOWING DIFFICULTY | int | 0/1 | Difficulté à avaler |
| CHEST PAIN | int | 0/1 | Douleur thoracique |
| CHRONIC DISEASE | int | 0/1 | Maladie chronique |

## 💻 Intégration dans Votre Code

### Python
```python
import requests

url = "https://francoisformation-oc-project8.hf.space/api/predict"
data = {
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

response = requests.post(url, json=data)
print(f"Prédiction: {response.json()['prediction']}")
print(f"Probabilité: {response.json()['probability']:.2%}")
```

### JavaScript
```javascript
const url = "https://francoisformation-oc-project8.hf.space/api/predict";
const data = {
  AGE: 50,
  GENDER: 1,
  SMOKING: 1,
  "ALCOHOL CONSUMING": 0,
  // ... autres features
};

fetch(url, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(data)
})
  .then(res => res.json())
  .then(data => console.log(data));
```

### cURL avec fichier
```bash
# Créer un fichier patient.json
cat > patient.json << EOF
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
EOF

# Utiliser le fichier
curl -X POST https://francoisformation-oc-project8.hf.space/api/predict \
  -H "Content-Type: application/json" \
  -d @patient.json
```

## 🔍 Endpoints Disponibles

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/health` | GET | État de santé de l'API |
| `/api/info` | GET | Informations API |
| `/api/predict` | POST | Prédiction binaire |
| `/api/predict_proba` | POST | Probabilités détaillées |
| `/api/logs` | GET | Récupérer les logs |
| `/api/logs` | DELETE | Vider les logs Redis |
| `/` | GET | Interface Gradio UI |

## ❌ Gestion des Erreurs

### Erreur 400 - Bad Request
```json
{
  "detail": "Missing required fields: AGE, GENDER"
}
```
**Solution**: Vérifier que toutes les 14 features sont présentes.

### Erreur 500 - Internal Server Error
```json
{
  "error": "Model not loaded"
}
```
**Solution**: Attendre que le Space soit complètement démarré (30s).

### Erreur 503 - Service Unavailable
```json
{
  "error": "API backend not accessible"
}
```
**Solution**: L'API backend (port 8000) n'est pas accessible. Vérifier les logs HF.

## 📊 Codes de Statut

| Code | Signification | Action |
|------|---------------|--------|
| 200 | OK | Requête réussie |
| 400 | Bad Request | Vérifier les données |
| 500 | Internal Error | Contacter le support |
| 503 | Service Unavailable | Réessayer plus tard |

## 🐛 Dépannage

### Le Space retourne 404
❌ **Problème**: `/api/health` retourne 404

✅ **Solution**:
1. Vérifier l'URL (avec `/api/` au début)
2. Attendre 1-2 minutes après le déploiement
3. Tester d'abord la racine: `curl https://francoisformation-oc-project8.hf.space/`

### Timeout après 30s
❌ **Problème**: La requête timeout

✅ **Solution**:
1. Le Space est peut-être en sommeil (HF arrête les Spaces inactifs)
2. Première requête prend 30-60s pour réveiller le Space
3. Réessayer immédiatement après

### Feature manquante
❌ **Problème**: `{"detail": "Missing required field: AGE"}`

✅ **Solution**:
```bash
# Vérifier le JSON avec jq
echo '{"AGE": 50, ...}' | jq .

# Compter les features (devrait être 14)
echo '{"AGE": 50, ...}' | jq 'keys | length'
```

## 📚 Documentation Complète

- **[DIRECT_HTTP_ACCESS.md](DIRECT_HTTP_ACCESS.md)** - Guide complet (550 lignes)
  - Tous les endpoints
  - Intégrations (Python, JS, R)
  - Architecture
  - Exemples avancés

- **[PROXY_REFACTOR_SUMMARY.md](PROXY_REFACTOR_SUMMARY.md)** - Résumé technique
  - Changements effectués
  - Architecture avant/après
  - Tests réalisés

## 🎯 Prochaines Étapes

1. ✅ Tester le health check
2. ✅ Tester une prédiction simple
3. ✅ Intégrer dans votre application
4. 📖 Lire la documentation complète
5. 🚀 Déployer en production

## 💡 Conseils

- **Cache les résultats**: Le modèle ne change pas, cacher les prédictions identiques
- **Batch les requêtes**: Grouper plusieurs prédictions si possible
- **Gérer les timeouts**: Première requête peut prendre 30-60s
- **Valider les données**: Vérifier les 14 features avant l'envoi

---

**Besoin d'aide?** Consultez la [documentation complète](DIRECT_HTTP_ACCESS.md) ou ouvrez une issue sur GitHub.
