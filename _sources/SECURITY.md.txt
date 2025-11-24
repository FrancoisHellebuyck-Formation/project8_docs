# Sécurité du Projet

Ce document décrit les mesures de sécurité et les justifications des choix techniques pour le projet MLOps.

## Analyse de Sécurité

Le projet utilise **Bandit** et **Safety** pour l'analyse de sécurité automatique lors du CI/CD.

### Bandit - Analyse statique du code

Bandit est un outil d'analyse statique qui détecte les problèmes de sécurité courants dans le code Python.

### Safety - Analyse des vulnérabilités des dépendances

Safety vérifie les dépendances installées contre une base de données de vulnérabilités connues (CVE).

## Utilisation de Pickle pour les Modèles ML

### Contexte

Le projet utilise `pickle` pour charger les modèles de machine learning dans les fichiers suivants:
- [src/model/model_loader.py](../src/model/model_loader.py)
- [src/model/model_pool.py](../src/model/model_pool.py)

### Risques identifiés par Bandit

```
B403/B301: Pickle and modules that wrap it can be unsafe when used to
deserialize untrusted data, possible security issue.
```

### Pourquoi c'est acceptable dans notre cas

#### 1. Source de confiance

Les fichiers `.pkl` proviennent **exclusivement** de notre pipeline d'entraînement interne:

```python
# Le modèle est créé par notre propre code d'entraînement
# et stocké dans ./model/model.pkl
MODEL_PATH = "./model/model.pkl"
```

**Mesures de sécurité:**
- Le fichier `model.pkl` est versionné dans Git LFS
- Aucun téléchargement de modèles depuis des sources externes
- Le modèle n'est chargé qu'au démarrage de l'API (pas d'upload dynamique)
- Pas d'endpoint permettant de charger un modèle arbitraire

#### 2. Standard de l'industrie ML

Pickle est le format standard pour la sérialisation de modèles scikit-learn:

- **scikit-learn** recommande pickle/joblib pour la persistance
- **MLflow** utilise pickle en interne pour le tracking des modèles
- Alternatives (ONNX, PMML) nécessitent une conversion et perdent certaines fonctionnalités

#### 3. Isolation au niveau infrastructure

```
┌─────────────────────────────────────────┐
│  Container Docker (API)                 │
│  ┌───────────────────────────────────┐  │
│  │  ./model/model.pkl (Read-only)    │  │
│  │  Bind mount depuis l'hôte         │  │
│  └───────────────────────────────────┘  │
│                                         │
│  Pas d'accès réseau au système de      │
│  fichiers hôte                          │
└─────────────────────────────────────────┘
```

**Mesures d'isolation:**
- Le conteneur Docker n'a pas de privilèges élevés
- Utilisateur non-root dans le conteneur
- Le modèle est en lecture seule (bind mount)
- Pas d'accès SSH ou shell dans le conteneur en production

#### 4. Validation au chargement

```python
# src/model/model_pool.py
try:
    with open(model_path, "rb") as f:
        base_model = pickle.load(f)

    # Vérification que c'est bien un modèle scikit-learn
    if not hasattr(base_model, 'predict'):
        raise ValueError("Invalid model: missing predict method")

except Exception as e:
    logger.error(f"Failed to load model: {e}")
    raise
```

### Alternatives considérées

| Format | Avantages | Inconvénients | Décision |
|--------|-----------|---------------|----------|
| **Pickle** | ✅ Standard scikit-learn<br>✅ Préserve tous les attributs<br>✅ Compatible MLflow | ⚠️ Sécurité si source non fiable | **✅ RETENU** (source fiable) |
| **ONNX** | ✅ Format ouvert<br>✅ Interopérable | ❌ Conversion complexe<br>❌ Perte de métadonnées | ❌ Rejeté |
| **PMML** | ✅ Format XML standard | ❌ Support limité<br>❌ Conversion manuelle | ❌ Rejeté |
| **Joblib** | ✅ Plus rapide que pickle<br>✅ Compression | ⚠️ Mêmes risques que pickle | ⚠️ Alternative acceptable |

### Recommandations pour la production

1. **Validation du hash**:
   ```bash
   # Générer le hash du modèle
   sha256sum model/model.pkl > model/model.pkl.sha256

   # Vérifier avant chargement
   sha256sum -c model/model.pkl.sha256
   ```

2. **Contrôle d'accès**:
   - Restreindre l'accès en écriture au répertoire `model/` aux seuls administrateurs
   - Utiliser des permissions 440 (read-only) pour `model.pkl` en production

3. **Audit**:
   - Logger toutes les tentatives de chargement de modèle
   - Alerter si le hash du modèle change de manière inattendue

4. **CI/CD**:
   - Scanner le modèle avec des outils de détection de malware
   - Vérifier la signature du modèle avant déploiement

## Bind à toutes les interfaces (0.0.0.0)

### Risques identifiés par Bandit

```
B104: Possible binding to all interfaces (0.0.0.0)
```

### Justification

#### 1. Requis pour Docker

Les conteneurs Docker doivent écouter sur `0.0.0.0` pour accepter les connexions:

```python
# src/config.py
API_HOST = os.getenv("API_HOST", "0.0.0.0")  # Requis pour Docker
```

Si on utilisait `127.0.0.1`, le conteneur ne serait accessible que depuis l'intérieur du conteneur.

#### 2. Sécurité réseau assurée par l'infrastructure

```
Internet
   ↓
[Nginx Reverse Proxy]  ← Authentification, rate limiting, SSL/TLS
   ↓
[Docker Network]       ← Isolation réseau
   ↓
[API Container:8000]   ← Bind 0.0.0.0 (nécessaire)
```

**Couches de sécurité:**
- **Nginx**: Reverse proxy avec SSL/TLS, rate limiting, authentification
- **Docker network**: Isolation réseau entre conteneurs
- **Firewall**: Règles iptables limitant l'accès externe
- **Cloud provider**: Security groups/Network policies

#### 3. Configuration par environnement

```bash
# .env.development
API_HOST=0.0.0.0  # OK pour développement local et Docker

# En production avec Nginx:
# L'API n'est pas exposée directement sur Internet
# Nginx fait le proxy vers http://api:8000
```

### Mesures de sécurité complémentaires

1. **CORS configuré**:
   ```python
   # Limiter les origines autorisées en production
   allowed_origins = ["https://app.example.com"]
   ```

2. **Rate limiting**:
   ```python
   # Via slowapi ou nginx
   @limiter.limit("10/minute")
   async def predict(...)
   ```

3. **Authentification**:
   ```python
   # OAuth2, JWT, ou API keys
   async def verify_token(token: str = Depends(oauth2_scheme))
   ```

## Générateurs pseudo-aléatoires (random)

### Risques identifiés par Bandit

```
B311: Standard pseudo-random generators are not suitable for
security/cryptographic purposes.
```

### Contexte d'utilisation

Le module `random` est utilisé **uniquement** dans le simulateur de charge pour générer des données de test:

```python
# src/simulator/simulator.py
def generate_random_patient():
    return {
        "AGE": random.randint(20, 80),
        "GENDER": random.randint(0, 1),
        # ...
    }
```

### Pourquoi c'est acceptable

1. **Pas d'usage cryptographique**: Les données générées ne sont jamais utilisées pour:
   - Génération de tokens
   - Mots de passe
   - Clés de chiffrement
   - Session IDs

2. **Usage limité aux tests**: Le simulateur est un outil de test de charge, pas un composant de production

3. **Pas d'impact sécurité**: La prédictibilité de `random` n'a aucun impact sur la sécurité de l'application

### Si un usage cryptographique était nécessaire

Utiliser `secrets` au lieu de `random`:

```python
import secrets

# Pour génération de tokens
token = secrets.token_urlsafe(32)

# Pour nombres aléatoires cryptographiquement sûrs
secure_value = secrets.randbelow(100)
```

## Vulnérabilité Gradio (CVE-2024-39236)

### Statut actuel

```
Vulnerability ID: 72086
CVE: CVE-2024-39236
Package: gradio 5.49.1
Severity: DISPUTED
```

### Détails de la vulnérabilité

**Type**: Code injection dans `/gradio/component_meta.py`

**Impact**: Potentielle injection de code via les métadonnées des composants

**Statut**: DISPUTED - Hugging Face conteste la vulnérabilité

### Mesures d'atténuation actuelles

1. **Isolation du composant Gradio**:
   - Gradio tourne dans un conteneur séparé
   - Pas d'accès direct au modèle ou aux données sensibles
   - Communication uniquement via l'API REST

2. **Accès limité**:
   - L'interface Gradio n'est pas exposée directement en production
   - Déployée sur Hugging Face Spaces avec leurs contrôles de sécurité

3. **Pas de données sensibles**:
   - Les données de patients sont synthétiques
   - Pas de stockage de données personnelles identifiables

### Plan de mise à jour

```bash
# Vérifier les nouvelles versions
uv add gradio@latest

# Tester la compatibilité
make test-ui

# Mettre à jour si compatible
git commit -m "chore: Update gradio to fix CVE-2024-39236"
```

**Note**: La mise à jour sera effectuée dès qu'une version corrigée non-disputed sera disponible.

## Surveillance et Monitoring

### Logs de sécurité

Tous les événements de sécurité sont loggés:

```python
# Tentative d'accès non autorisé
logger.warning(f"Unauthorized access attempt: {ip}")

# Erreur de validation
logger.error(f"Invalid input detected: {data}")

# Chargement du modèle
logger.info(f"Model loaded from: {model_path}")
```

### Métriques de sécurité

Via Elasticsearch/Kibana:
- Nombre de requêtes par IP
- Taux d'erreur 4xx/5xx
- Tentatives d'accès à des endpoints non existants
- Temps de réponse anormaux (possible DoS)

### Alertes

Configuration dans Kibana:
- Alerte si > 100 requêtes/minute depuis une même IP
- Alerte si taux d'erreur > 10%
- Alerte si temps de réponse moyen > 5s

## Checklist de sécurité pour la production

- [ ] Activer HTTPS (SSL/TLS) via Nginx
- [ ] Configurer CORS avec les origines spécifiques
- [ ] Implémenter rate limiting
- [ ] Ajouter authentification (OAuth2/JWT)
- [ ] Valider le hash du modèle au démarrage
- [ ] Configurer les logs de sécurité
- [ ] Activer les alertes Kibana
- [ ] Mettre à jour Gradio quand patch disponible
- [ ] Restreindre les permissions du conteneur Docker
- [ ] Configurer le firewall/security groups
- [ ] Activer le monitoring de performance
- [ ] Planifier les audits de sécurité réguliers

## Références

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Bandit Documentation](https://bandit.readthedocs.io/)
- [Safety Documentation](https://docs.safetycli.com/)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [scikit-learn Model Persistence](https://scikit-learn.org/stable/model_persistence.html)

---

**Dernière mise à jour**: 22 novembre 2025
**Responsable sécurité**: Équipe DevSecOps
