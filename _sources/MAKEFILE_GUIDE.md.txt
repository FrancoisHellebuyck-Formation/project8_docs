# Guide d'utilisation du Makefile

Ce guide explique comment utiliser les commandes du Makefile pour faciliter le développement.

## Afficher l'aide

```bash
make help
```

Affiche toutes les commandes disponibles avec leurs descriptions.

---

## Installation et configuration

### Installation des dépendances de production

```bash
make install
```

- Crée l'environnement virtuel si nécessaire
- Installe pip et uv
- Installe uniquement les dépendances de production

### Installation complète (développement)

```bash
make install-dev
```

- Installe toutes les dépendances (production + développement)
- Nécessaire pour lancer les tests et le linting

### Configuration initiale du projet

```bash
make setup
```

- Installe les dépendances de développement
- Crée le fichier `.env` depuis `.env.example`
- Configure l'environnement de base

### Environnement de développement complet

```bash
make dev
```

- Exécute `make setup`
- Lance Redis avec Docker
- Prépare l'environnement complet pour le développement

**Ensuite**, dans un autre terminal :
```bash
make run-api
```

### Nettoyage

```bash
make clean
```

Supprime tous les fichiers temporaires :
- `__pycache__`
- `*.pyc`, `*.pyo`
- `.pytest_cache`
- `.coverage`
- `htmlcov/`
- `*.egg-info`

---

## Qualité du code

### Vérification avec flake8

```bash
make lint
```

- Vérifie la conformité du code avec flake8
- Utilise la configuration de `.flake8`
- Retourne une erreur si le code n'est pas conforme

### Tests

```bash
make test
```

- Lance tous les tests avec pytest
- Affiche les résultats de manière verbose

### Tests avec couverture

```bash
make test-coverage
```

- Lance les tests avec mesure de la couverture
- Génère un rapport HTML dans `htmlcov/`
- Affiche un résumé dans le terminal

```bash
# Ouvrir le rapport de couverture
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### CI/CD

```bash
make ci
```

- Exécute `make lint` et `make test`
- Utilisé pour les pipelines CI/CD
- Échoue si le linting ou les tests échouent

---

## Développement

### Lancer l'API FastAPI

```bash
make run-api
```

- Démarre l'API avec uvicorn
- Mode reload activé (rechargement automatique)
- Accessible sur `http://0.0.0.0:8000`
- Documentation sur `http://0.0.0.0:8000/docs`

**Variables personnalisables** :
```bash
# Dans le Makefile, modifier :
API_HOST := 0.0.0.0
API_PORT := 8000
```

### Lancer le proxy Gradio

```bash
make run-proxy
```

- Démarre l'interface proxy Gradio complète
- Expose tous les endpoints de l'API FastAPI
- Accessible sur `http://0.0.0.0:7860`
- Interface interactive avec 6 sections :
  - Vérification de connexion
  - Informations API
  - Health check
  - Prédiction ML
  - Probabilités détaillées
  - Gestion des logs
- Voir [PROXY_DOCUMENTATION.md](PROXY_DOCUMENTATION.md) pour plus de détails

### Lancer Redis

```bash
make run-redis
```

- Lance un conteneur Docker Redis
- Port : 6379
- Nom du conteneur : `redis-ml-api`
- Si le conteneur existe déjà, il est redémarré

### Arrêter Redis

```bash
make stop-redis
```

- Arrête le conteneur Redis
- Ne supprime pas le conteneur (données conservées)

---

## Docker

### Construire les images

```bash
make docker-build
```

- Construit toutes les images Docker définies dans `docker-compose.yml`
- À exécuter après modification des Dockerfiles

### Lancer tous les conteneurs

```bash
make docker-up
```

- Démarre tous les services définis dans `docker-compose.yml`
- Mode détaché (-d)
- Affiche l'URL de l'API

### Arrêter tous les conteneurs

```bash
make docker-down
```

- Arrête tous les conteneurs
- Nettoie les ressources

### Afficher les logs

```bash
make docker-logs
```

- Affiche les logs de tous les conteneurs
- Mode suivi (-f) pour voir les logs en temps réel
- `Ctrl+C` pour quitter

---

## Utilitaires

### Vérifier la santé de l'API

```bash
make health
```

- Appelle l'endpoint `/health`
- Affiche le statut de l'API, du modèle et de Redis
- Format JSON lisible

**Exemple de réponse** :
```json
{
  "status": "healthy",
  "model_loaded": true,
  "redis_connected": true,
  "version": "1.0.0"
}
```

### Afficher les logs

```bash
make logs
```

- Appelle l'endpoint `/logs`
- Affiche les 50 derniers logs
- Format JSON lisible

### Vider le cache des logs Redis

#### API locale

```bash
make clear-logs
```

- Appelle l'endpoint `DELETE /logs` de l'API locale
- Supprime tous les logs du cache Redis
- Utile après des tests de charge ou pour maintenance
- **Note** : Ne supprime pas les logs déjà indexés dans Elasticsearch

**Exemple de réponse** :
```json
{
  "message": "Logs supprimés avec succès"
}
```

#### Via Gradio local

```bash
make clear-logs-gradio-local
```

- Vide les logs via l'interface Gradio locale (port 7860)
- Utilise le client Gradio pour appeler l'endpoint `/api_clear_logs_proxy`
- Utile quand l'API n'est pas directement accessible

#### Via Gradio HuggingFace Spaces

```bash
make clear-logs-gradio-hf
```

- Vide les logs via Gradio déployé sur HuggingFace Spaces
- Charge automatiquement `HF_TOKEN` depuis `.env` si disponible
- URL configurée : `https://francoisformation-oc-project8.hf.space`
- **Note** : Nécessite le token HF pour les Spaces privés

**Documentation complète** : [CLEAR_LOGS_ENDPOINT.md](CLEAR_LOGS_ENDPOINT.md)

### Tester une prédiction

```bash
make predict-test
```

- Envoie une requête POST à `/predict`
- Utilise des données de test prédéfinies
- Affiche la réponse au format JSON

**Exemple de réponse** :
```json
{
  "prediction": 1,
  "probability": 0.85,
  "message": "Prédiction positive"
}
```

---

## Workflows courants

### Premier démarrage

```bash
# 1. Configuration initiale
make setup

# 2. Lancer Redis
make run-redis

# 3. Dans un autre terminal, lancer l'API
make run-api

# 4. Dans un troisième terminal, tester
make health
make predict-test
```

### Développement quotidien

```bash
# 1. Lancer l'environnement
make dev

# 2. Dans un autre terminal
make run-api

# 3. Développer...

# 4. Vérifier le code
make lint

# 5. Tester
make test
```

### Avant un commit

```bash
# 1. Nettoyer
make clean

# 2. Vérifier le code
make lint

# 3. Lancer les tests
make test-coverage

# 4. Si tout passe, commiter
git add .
git commit -m "message"
```

### Déploiement avec Docker

```bash
# 1. Construire les images
make docker-build

# 2. Lancer les conteneurs
make docker-up

# 3. Vérifier les logs
make docker-logs

# 4. Tester
make health
make predict-test

# 5. Arrêter si nécessaire
make docker-down
```

---

## Personnalisation

### Variables

Vous pouvez personnaliser les variables dans le Makefile :

```makefile
API_HOST := 0.0.0.0      # Adresse de l'API
API_PORT := 8000          # Port de l'API
REDIS_PORT := 6379        # Port Redis
```

### Ajouter des commandes

Pour ajouter une nouvelle commande :

```makefile
## ma-commande: Description de ma commande
ma-commande:
	@echo "$(BLUE)Exécution de ma commande...$(NC)"
	# Commandes ici
	@echo "$(GREEN)✓ Terminé$(NC)"
```

### Couleurs disponibles

```makefile
BLUE := \033[0;34m      # Bleu (informations)
GREEN := \033[0;32m     # Vert (succès)
YELLOW := \033[0;33m    # Jaune (avertissements)
RED := \033[0;31m       # Rouge (erreurs)
NC := \033[0m           # Pas de couleur
```

---

## Dépannage

### "make: command not found"

Installez make :
```bash
# macOS
xcode-select --install

# Ubuntu/Debian
sudo apt-get install build-essential

# Fedora
sudo dnf install make
```

### "No rule to make target"

Vérifiez que vous êtes dans le bon répertoire :
```bash
pwd  # Doit afficher le chemin du projet
ls Makefile  # Doit afficher "Makefile"
```

### "Permission denied"

Assurez-vous que le Makefile est exécutable :
```bash
chmod +x Makefile
```

### Redis ne démarre pas

Vérifiez que Docker est en cours d'exécution :
```bash
docker ps
```

### L'API ne démarre pas

Vérifiez que :
1. L'environnement virtuel est activé
2. Les dépendances sont installées (`make install-dev`)
3. Le fichier `.env` existe
4. Le modèle existe dans `./model/model.pkl`

---

## Aide supplémentaire

Pour toute question, consultez :
- [GEMINI.md](../GEMINI.md) - Règles de développement
- [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - Documentation de l'API
- [FEATURE_ENGINEERING.md](FEATURE_ENGINEERING.md) - Feature engineering
- [ENV_VARIABLES.md](ENV_VARIABLES.md) - Variables d'environnement
