# Makefile pour le projet ML API
# Commandes pour faciliter le développement, les tests et le déploiement

.PHONY: help install install-dev clean lint format test test-coverage test-api test-model test-gradio-api test-gradio-api-local test-gradio-api-hf run-api run-ui run-ui-fastapi run-api-ui stop-api-ui run-redis stop-redis docker-build docker-up docker-down docker-logs logs clear-logs logs-gradio-local logs-gradio-hf health predict-test pipeline-check pipeline-once pipeline-continuous pipeline-elasticsearch-up pipeline-elasticsearch-down simulate simulate-quick simulate-load simulate-drift simulate-drift-progressive simulate-gradio-local simulate-gradio-hf simulate-gradio-drift-local simulate-gradio-drift-hf simulate-gradio-drift-progressive-hf drift-analyze docs docs-clean docs-open

# Variables
PYTHON := python
VENV := .venv
VENV_BIN := $(VENV)/bin
UV := uv
API_HOST := 0.0.0.0
API_PORT := 8000
GRADIO_HOST := 0.0.0.0
GRADIO_PORT := 7860
GRADIO_LOCAL_URL := http://localhost:7860
GRADIO_HF_URL := https://francoisformation-oc-project8.hf.space
REDIS_PORT := 6379

# Couleurs pour l'affichage
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

## help: Affiche ce message d'aide
help:
	@echo "$(BLUE)Commandes disponibles:$(NC)"
	@echo ""
	@echo "$(GREEN)Installation et configuration:$(NC)"
	@echo "  make install          - Installe les dépendances de production"
	@echo "  make install-dev      - Installe toutes les dépendances (dev inclus)"
	@echo "  make clean            - Nettoie les fichiers temporaires"
	@echo ""
	@echo "$(GREEN)Qualité du code:$(NC)"
	@echo "  make lint             - Vérifie le code avec flake8"
	@echo "  make format           - Formate le code (placeholder)"
	@echo "  make test             - Lance tous les tests"
	@echo "  make test-coverage    - Lance les tests avec couverture (≥80%)"
	@echo "  make test-api         - Lance les tests de l'API uniquement"
	@echo "  make test-api-coverage - Vérifie la couverture API (≥80%)"
	@echo "  make test-model       - Lance les tests du modèle uniquement"
	@echo "  make test-proxy       - Lance les tests du package proxy"
	@echo "  make test-performance - Test le monitoring de performance"
	@echo "  make test-gradio-api-local  - Test l'API Gradio (local)"
	@echo "  make test-gradio-api-hf     - Test l'API Gradio (HuggingFace)"
	@echo ""
	@echo "$(GREEN)Développement:$(NC)"
	@echo "  make run-api          - Lance l'API FastAPI (port 8000)"
	@echo "  make run-ui           - Lance l'interface Gradio simple (port 7860)"
	@echo "  make run-ui-fastapi   - Lance FastAPI+Gradio hybride (port 7860, avec /api/*)"
	@echo "  make run-api-ui       - Lance API + UI en background"
	@echo "  make stop-api-ui      - Arrête API + UI lancés en background"
	@echo "  make run-proxy        - Lance l'interface proxy (tous endpoints)"
	@echo "  make run-redis        - Lance Redis avec Docker"
	@echo "  make stop-redis       - Arrête le conteneur Redis"
	@echo ""
	@echo "$(GREEN)Docker:$(NC)"
	@echo "  make docker-build     - Construit les images Docker"
	@echo "  make docker-up        - Lance tous les conteneurs"
	@echo "  make docker-down      - Arrête tous les conteneurs"
	@echo "  make docker-logs      - Affiche les logs des conteneurs"
	@echo ""
	@echo "$(GREEN)Utilitaires:$(NC)"
	@echo "  make logs             - Affiche les logs de l'API via endpoint"
	@echo "  make clear-logs       - Vide le cache des logs Redis"
	@echo "  make logs-gradio-local - Affiche les logs via Gradio local"
	@echo "  make logs-gradio-hf   - Affiche les logs via Gradio HF Spaces"
	@echo "  make health           - Vérifie la santé de l'API"
	@echo "  make predict-test     - Test une prédiction"
	@echo ""
	@echo "$(GREEN)Pipeline Elasticsearch:$(NC)"
	@echo "  make pipeline-elasticsearch-up - Lance Elasticsearch et Kibana"
	@echo "  make pipeline-elasticsearch-down - Arrête Elasticsearch et Kibana"
	@echo "  make pipeline-check   - Vérifie les pré-requis du pipeline"
	@echo "  make pipeline-once    - Exécute le pipeline une fois"
	@echo "  make pipeline-continuous - Exécute le pipeline en continu"
	@echo "  make pipeline-clear-indexes - Vide les index Elasticsearch"
	@echo "  make pipeline-deduplicate - Dédoublonne l'index ml-api-message"
	@echo "  make pipeline-export-parquet - Exporte vers Parquet"
	@echo "  make pipeline-analyze-drift - Analyse le drift de données"
	@echo "  make pipeline-test-parsing - Test le parsing des logs"
	@echo ""
	@echo "$(GREEN)Simulation FastAPI:$(NC)"
	@echo "  make simulate         - Simule des requêtes (config depuis .env)"
	@echo "  make simulate-quick   - Simule 20 requêtes avec 5 utilisateurs"
	@echo "  make simulate-load    - Test de charge (500 requêtes, 50 users)"
	@echo "  make simulate-drift   - Simule avec data drift immédiat (75 ans)"
	@echo "  make simulate-drift-progressive - Drift progressif (50%-100%)"
	@echo ""
	@echo "$(GREEN)Simulation Gradio:$(NC)"
	@echo "  make simulate-gradio-local - Simule via Gradio API (local)"
	@echo "  make simulate-gradio-hf - Simule via Gradio API (HF Spaces)"
	@echo "  make simulate-gradio-drift-local - Drift Gradio local (75 ans)"
	@echo "  make simulate-gradio-drift-hf - Drift Gradio HF (75 ans)"
	@echo "  make simulate-gradio-drift-progressive-hf - Drift progressif HF (50%-100%)"
	@echo ""
	@echo "$(GREEN)Analyse:$(NC)"
	@echo "  make drift-analyze    - Analyse le data drift"
	@echo ""
	@echo "$(GREEN)Migration ONNX:$(NC)"
	@echo "  make convert-onnx     - Convertit le modèle en ONNX (avec validation)"
	@echo "  make convert-onnx-quick - Conversion ONNX rapide (sans validation)"
	@echo ""
	@echo "$(GREEN)Documentation:$(NC)"
	@echo "  make docs             - Génère la documentation Sphinx"
	@echo "  make docs-clean       - Nettoie et régénère la documentation"
	@echo "  make docs-open        - Génère et ouvre la documentation"
	@echo ""

## install: Installe les dépendances de production
install:
	@echo "$(BLUE)Installation des dépendances...$(NC)"
	@test -d $(VENV) || python -m venv $(VENV)
	@$(VENV_BIN)/pip install --upgrade pip
	@$(VENV_BIN)/pip install uv
	@$(VENV_BIN)/uv pip install -e .
	@echo "$(GREEN)✓ Dépendances installées$(NC)"

## install-dev: Installe toutes les dépendances (dev inclus)
install-dev:
	@echo "$(BLUE)Installation des dépendances de développement...$(NC)"
	@test -d $(VENV) || python -m venv $(VENV)
	@$(VENV_BIN)/pip install --upgrade pip
	@$(VENV_BIN)/pip install uv
	@$(VENV_BIN)/uv pip install -e ".[dev]"
	@echo "$(GREEN)✓ Dépendances de développement installées$(NC)"

## clean: Nettoie les fichiers temporaires
clean:
	@echo "$(BLUE)Nettoyage des fichiers temporaires...$(NC)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".coverage" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name ".coverage" -delete 2>/dev/null || true
	@find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)✓ Nettoyage terminé$(NC)"

## lint: Vérifie le code avec flake8
lint:
	@echo "$(BLUE)Vérification du code avec flake8...$(NC)"
	@$(VENV_BIN)/flake8 src/ tests/ || \
		(echo "$(RED)✗ Erreurs de linting détectées$(NC)" && exit 1)
	@echo "$(GREEN)✓ Code conforme aux standards$(NC)"

## format: Formate le code
format:
	@echo "$(YELLOW)⚠ Formatage non implémenté (TODO: black/ruff)$(NC)"

## test: Lance les tests
test:
	@echo "$(BLUE)Lancement des tests...$(NC)"
	@$(UV) run pytest tests/ -v || \
		(echo "$(RED)✗ Tests échoués$(NC)" && exit 1)
	@echo "$(GREEN)✓ Tous les tests passent$(NC)"

## test-coverage: Lance les tests avec couverture (seuil global: 80%)
test-coverage:
	@echo "$(BLUE)Lancement des tests avec couverture...$(NC)"
	@$(UV) run pytest tests/ --cov=src --cov-report=html \
		--cov-report=term-missing --cov-report=xml \
		--cov-fail-under=80 || \
		(echo "$(RED)✗ Tests échoués ou couverture < 80%$(NC)" && exit 1)
	@echo "$(GREEN)✓ Rapport de couverture généré dans htmlcov/ et coverage.xml$(NC)"

## test-api: Lance les tests de l'API uniquement
test-api:
	@echo "$(BLUE)Lancement des tests API...$(NC)"
	@$(UV) run pytest tests/api/ -v || \
		(echo "$(RED)✗ Tests API échoués$(NC)" && exit 1)
	@echo "$(GREEN)✓ Tests API passent$(NC)"

## test-api-coverage: Lance les tests API avec vérification de couverture (seuil: 80%)
test-api-coverage:
	@echo "$(BLUE)Lancement des tests API avec couverture...$(NC)"
	@echo "$(YELLOW)Seuil minimum requis: 80%$(NC)"
	@$(UV) run pytest tests/api/ -v \
		--cov=src/api \
		--cov-report=term-missing \
		--cov-report=html:htmlcov-api \
		--cov-report=json:coverage-api.json \
		--cov-fail-under=80 || \
		(echo "$(RED)✗ Tests API échoués ou couverture < 80%$(NC)" && exit 1)
	@echo ""
	@echo "$(GREEN)✓ Tests API passent avec couverture >= 80%$(NC)"
	@echo "$(YELLOW)📊 Rapport détaillé: htmlcov-api/index.html$(NC)"
	@if [ -f coverage-api.json ]; then \
		echo ""; \
		echo "================================================="; \
		echo "📈 Résumé de la couverture de l'API"; \
		echo "================================================="; \
		python3 -c "\
import json; \
data = json.load(open('coverage-api.json')); \
total = data['totals']['percent_covered']; \
print(f'Couverture totale API: {total:.2f}%'); \
print(''); \
print('Détail par fichier:'); \
[print(f\"  {file.replace('src/api/', '')}: {stats['summary']['percent_covered']:.2f}%\") \
 for file, stats in data['files'].items() if 'src/api' in file]"; \
		echo "================================================="; \
	fi

## test-model: Lance les tests du modèle uniquement
test-model:
	@echo "$(BLUE)Lancement des tests du modèle...$(NC)"
	@$(UV) run pytest tests/model/ -v || \
		(echo "$(RED)✗ Tests modèle échoués$(NC)" && exit 1)
	@echo "$(GREEN)✓ Tests modèle passent$(NC)"

## test-performance: Test le monitoring de performance
test-performance:
	@echo "$(BLUE)Test du monitoring de performance...$(NC)"
	@$(UV) run python scripts/test_performance_monitoring.py || \
		(echo "$(RED)✗ Tests de performance échoués$(NC)" && exit 1)
	@echo "$(GREEN)✓ Tests de performance passent$(NC)"

## test-gradio-api-local: Test l'API Gradio en local
test-gradio-api-local:
	@echo "$(BLUE)Test de l'API Gradio (local)...$(NC)"
	@echo "$(YELLOW)URL: $(GRADIO_LOCAL_URL)$(NC)"
	@echo "$(YELLOW)Assurez-vous que l'API et Gradio tournent localement$(NC)"
	@GRADIO_URL=$(GRADIO_LOCAL_URL) $(UV) run python3 test_gradio_api.py || \
		(echo "$(RED)✗ Tests Gradio API échoués$(NC)" && exit 1)
	@echo "$(GREEN)✓ Tests Gradio API passent$(NC)"

## test-gradio-api-hf: Test l'API Gradio sur HuggingFace Spaces
test-gradio-api-hf:
	@echo "$(BLUE)Test de l'API Gradio (HuggingFace Spaces)...$(NC)"
	@echo "$(YELLOW)URL: $(GRADIO_HF_URL)$(NC)"
	@if [ -f .env ]; then \
		echo "$(YELLOW)Chargement de HF_TOKEN depuis .env...$(NC)"; \
		export $$(cat .env | grep -v '^#' | grep HF_TOKEN | xargs) && \
		GRADIO_URL=$(GRADIO_HF_URL) $(UV) run python3 test_gradio_api.py || \
		(echo "$(RED)✗ Tests Gradio API échoués$(NC)" && exit 1); \
	else \
		echo "$(YELLOW)⚠️  Fichier .env non trouvé, test sans token$(NC)"; \
		GRADIO_URL=$(GRADIO_HF_URL) $(UV) run python3 test_gradio_api.py || \
		(echo "$(RED)✗ Tests Gradio API échoués$(NC)" && exit 1); \
	fi
	@echo "$(GREEN)✓ Tests Gradio API passent$(NC)"

## run-api: Lance l'API FastAPI
run-api:
	@echo "$(BLUE)Démarrage de l'API FastAPI...$(NC)"
	@echo "$(YELLOW)API disponible sur http://$(API_HOST):$(API_PORT)$(NC)"
	@echo "$(YELLOW)Documentation sur http://$(API_HOST):$(API_PORT)/docs$(NC)"
	@$(VENV_BIN)/uvicorn src.api.main:app \
		--host $(API_HOST) \
		--port $(API_PORT) \
		--reload

## run-proxy: Lance l'interface proxy Gradio (tous les endpoints)
run-proxy:
	@echo "$(BLUE)Démarrage du proxy Gradio...$(NC)"
	@echo "$(YELLOW)Proxy disponible sur http://0.0.0.0:7860$(NC)"
	@echo "$(YELLOW)Expose tous les endpoints de l'API FastAPI$(NC)"
	@python3 run_proxy.py

## test-proxy: Lance les tests du package proxy
test-proxy:
	@echo "$(BLUE)Lancement des tests du proxy...$(NC)"
	@$(UV) run pytest tests/test_proxy.py -v || \
		(echo "$(RED)✗ Tests proxy échoués$(NC)" && exit 1)
	@echo "$(GREEN)✓ Tests proxy passent$(NC)"

## run-ui: Lance l'interface Gradio simple
run-ui:
	@echo "$(BLUE)Démarrage de l'interface Gradio simple...$(NC)"
	@echo "$(YELLOW)Interface disponible sur http://$(GRADIO_HOST):$(GRADIO_PORT)$(NC)"
	@$(VENV_BIN)/python -m src.ui.app

## run-ui-fastapi: Lance FastAPI+Gradio hybride (avec endpoints REST /api/*)
run-ui-fastapi:
	@echo "$(BLUE)Démarrage de FastAPI+Gradio hybride...$(NC)"
	@echo "$(YELLOW)Interface UI: http://$(GRADIO_HOST):$(GRADIO_PORT)/$(NC)"
	@echo "$(YELLOW)API REST:     http://$(GRADIO_HOST):$(GRADIO_PORT)/api/*$(NC)"
	@echo "$(GREEN)Endpoints disponibles:$(NC)"
	@echo "  - GET  /api/health"
	@echo "  - POST /api/predict"
	@echo "  - POST /api/predict_proba"
	@echo "  - GET  /api/logs"
	@echo "  - DELETE /api/logs"
	@$(VENV_BIN)/python -m src.ui.fastapi_app

## run-api-ui: Lance l'API et l'UI en background
run-api-ui:
	@echo "$(BLUE)Démarrage de l'API et l'UI en background...$(NC)"
	@echo "$(YELLOW)Lancement de l'API FastAPI sur le port $(API_PORT)...$(NC)"
	@$(UV) run uvicorn src.api.main:app --host $(API_HOST) --port $(API_PORT) \
		> /tmp/ml-api.log 2>&1 & echo $$! > /tmp/ml-api.pid
	@sleep 3
	@if curl -s http://localhost:$(API_PORT)/health > /dev/null; then \
		echo "$(GREEN)✓ API démarrée avec succès (PID: $$(cat /tmp/ml-api.pid))$(NC)"; \
	else \
		echo "$(RED)✗ Échec du démarrage de l'API$(NC)"; \
		exit 1; \
	fi
	@echo "$(YELLOW)Lancement de l'UI Gradio sur le port $(GRADIO_PORT)...$(NC)"
	@$(UV) run python -m src.ui.fastapi_app \
		> /tmp/ml-ui.log 2>&1 & echo $$! > /tmp/ml-ui.pid
	@sleep 3
	@echo "$(GREEN)✓ UI démarrée avec succès (PID: $$(cat /tmp/ml-ui.pid))$(NC)"
	@echo ""
	@echo "$(GREEN)Services démarrés:$(NC)"
	@echo "  $(YELLOW)API:$(NC)  http://$(API_HOST):$(API_PORT) (PID: $$(cat /tmp/ml-api.pid))"
	@echo "  $(YELLOW)Docs:$(NC) http://$(API_HOST):$(API_PORT)/docs"
	@echo "  $(YELLOW)UI:$(NC)   http://$(GRADIO_HOST):$(GRADIO_PORT) (PID: $$(cat /tmp/ml-ui.pid))"
	@echo ""
	@echo "$(YELLOW)Logs disponibles:$(NC)"
	@echo "  API: tail -f /tmp/ml-api.log"
	@echo "  UI:  tail -f /tmp/ml-ui.log"
	@echo ""
	@echo "$(YELLOW)Pour arrêter:$(NC) make stop-api-ui"

## stop-api-ui: Arrête l'API et l'UI lancés en background
stop-api-ui:
	@echo "$(BLUE)Arrêt de l'API et l'UI...$(NC)"
	@if [ -f /tmp/ml-api.pid ]; then \
		echo "$(YELLOW)Arrêt de l'API (PID: $$(cat /tmp/ml-api.pid))...$(NC)"; \
		kill $$(cat /tmp/ml-api.pid) 2>/dev/null || true; \
		rm /tmp/ml-api.pid; \
		echo "$(GREEN)✓ API arrêtée$(NC)"; \
	else \
		echo "$(YELLOW)⚠ Pas de PID trouvé pour l'API$(NC)"; \
	fi
	@if [ -f /tmp/ml-ui.pid ]; then \
		echo "$(YELLOW)Arrêt de l'UI (PID: $$(cat /tmp/ml-ui.pid))...$(NC)"; \
		kill $$(cat /tmp/ml-ui.pid) 2>/dev/null || true; \
		rm /tmp/ml-ui.pid; \
		echo "$(GREEN)✓ UI arrêtée$(NC)"; \
	else \
		echo "$(YELLOW)⚠ Pas de PID trouvé pour l'UI$(NC)"; \
	fi
	@echo "$(GREEN)✓ Services arrêtés$(NC)"

## run-redis: Lance Redis avec Docker
run-redis:
	@echo "$(BLUE)Démarrage de Redis...$(NC)"
	@docker run -d \
		--name redis-ml-api \
		-p $(REDIS_PORT):6379 \
		redis:latest \
		2>/dev/null || \
		(docker start redis-ml-api 2>/dev/null || true)
	@sleep 2
	@echo "$(GREEN)✓ Redis en cours d'exécution sur le port $(REDIS_PORT)$(NC)"

## stop-redis: Arrête le conteneur Redis
stop-redis:
	@echo "$(BLUE)Arrêt de Redis...$(NC)"
	@docker stop redis-ml-api 2>/dev/null || true
	@echo "$(GREEN)✓ Redis arrêté$(NC)"

## docker-build: Construit les images Docker
docker-build:
	@echo "$(BLUE)Construction des images Docker...$(NC)"
	@cd docker && docker-compose build
	@echo "$(GREEN)✓ Images construites$(NC)"

## docker-up: Lance tous les conteneurs
docker-up:
	@echo "$(BLUE)Démarrage des conteneurs Docker...$(NC)"
	@cd docker && docker-compose up -d
	@echo "$(GREEN)✓ Conteneurs démarrés$(NC)"
	@echo "$(YELLOW)API: http://localhost:$(API_PORT)$(NC)"
	@echo "$(YELLOW)Redis: localhost:6379$(NC)"
	@echo "$(YELLOW)Logs: http://localhost:$(API_PORT)/logs$(NC)"

## docker-down: Arrête tous les conteneurs
docker-down:
	@echo "$(BLUE)Arrêt des conteneurs Docker...$(NC)"
	@cd docker && docker-compose down
	@echo "$(GREEN)✓ Conteneurs arrêtés$(NC)"

## docker-down-volumes: Arrête les conteneurs et supprime les volumes
docker-down-volumes:
	@echo "$(BLUE)Arrêt des conteneurs et suppression des volumes...$(NC)"
	@cd docker && docker-compose down -v
	@echo "$(GREEN)✓ Conteneurs et volumes supprimés$(NC)"

## docker-logs: Affiche les logs des conteneurs
docker-logs:
	@cd docker && docker-compose logs -f

## docker-logs-api: Affiche les logs de l'API uniquement
docker-logs-api:
	@cd docker && docker-compose logs -f api

## docker-logs-redis: Affiche les logs de Redis uniquement
docker-logs-redis:
	@cd docker && docker-compose logs -f redis

## docker-restart: Redémarre tous les conteneurs
docker-restart: docker-down docker-up

## logs: Affiche les logs de l'API via endpoint
logs:
	@echo "$(BLUE)Récupération des logs de l'API...$(NC)"
	@curl -s http://localhost:$(API_PORT)/logs?limit=50 | \
		$(PYTHON) -m json.tool || \
		echo "$(RED)✗ Impossible de récupérer les logs$(NC)"

## clear-logs: Vide le cache des logs Redis (API locale)
clear-logs:
	@echo "$(BLUE)Suppression des logs du cache Redis...$(NC)"
	@curl -X DELETE -s http://localhost:$(API_PORT)/logs | \
		$(PYTHON) -m json.tool && \
		echo "$(GREEN)✓ Logs supprimés avec succès$(NC)" || \
		echo "$(RED)✗ Échec de la suppression des logs$(NC)"

## clear-logs-gradio-local: Vide le cache Redis via Gradio local
clear-logs-gradio-local:
	@echo "$(BLUE)Suppression des logs via Gradio local...$(NC)"
	@GRADIO_URL=http://localhost:7860 $(UV) run python3 clear_logs_gradio.py

## clear-logs-gradio-hf: Vide le cache Redis via Gradio HF Spaces
clear-logs-gradio-hf:
	@echo "$(BLUE)Suppression des logs via Gradio HF Spaces...$(NC)"
	@if [ -f .env ]; then \
		echo "$(YELLOW)Chargement de HF_TOKEN depuis .env...$(NC)"; \
		export $$(cat .env | grep -v '^#' | grep HF_TOKEN | xargs) && \
		GRADIO_URL=$(GRADIO_HF_URL) $(UV) run python3 clear_logs_gradio.py; \
	else \
		echo "$(YELLOW)⚠️  Fichier .env non trouvé, test sans token$(NC)"; \
		GRADIO_URL=$(GRADIO_HF_URL) $(UV) run python3 clear_logs_gradio.py; \
	fi

## logs-gradio-local: Affiche les logs via Gradio local
logs-gradio-local:
	@echo "$(BLUE)Récupération des logs via Gradio local...$(NC)"
	@$(UV) run python scripts/get_logs_gradio.py \
		--gradio-url $(GRADIO_LOCAL_URL) \
		--limit 50

## logs-gradio-hf: Affiche les logs via Gradio HF Spaces
logs-gradio-hf:
	@echo "$(BLUE)Récupération des logs via Gradio HF Spaces...$(NC)"
	@if [ -f .env ]; then \
		echo "$(YELLOW)Chargement de HF_TOKEN depuis .env...$(NC)"; \
		export $$(cat .env | grep -v '^#' | grep HF_TOKEN | xargs) && \
		$(UV) run python scripts/get_logs_gradio.py \
			--gradio-url $(GRADIO_HF_URL) \
			--hf-token $$HF_TOKEN \
			--limit 50; \
	else \
		echo "$(YELLOW)⚠️  Fichier .env non trouvé, test sans token$(NC)"; \
		$(UV) run python scripts/get_logs_gradio.py \
			--gradio-url $(GRADIO_HF_URL) \
			--limit 50; \
	fi

## health: Vérifie la santé de l'API
health:
	@echo "$(BLUE)Vérification de la santé de l'API...$(NC)"
	@curl -s http://localhost:$(API_PORT)/health | \
		$(PYTHON) -m json.tool || \
		echo "$(RED)✗ API non disponible$(NC)"

## predict-test: Test une prédiction
predict-test:
	@echo "$(BLUE)Test d'une prédiction...$(NC)"
	@curl -X POST http://localhost:$(API_PORT)/predict \
		-H "Content-Type: application/json" \
		-d '{ \
			"AGE": 65, \
			"GENDER": 1, \
			"SMOKING": 1, \
			"ALCOHOL CONSUMING": 1, \
			"PEER_PRESSURE": 0, \
			"YELLOW_FINGERS": 1, \
			"ANXIETY": 0, \
			"FATIGUE": 1, \
			"ALLERGY": 0, \
			"WHEEZING": 1, \
			"COUGHING": 1, \
			"SHORTNESS OF BREATH": 1, \
			"SWALLOWING DIFFICULTY": 0, \
			"CHEST PAIN": 1, \
			"CHRONIC DISEASE": 0 \
		}' | python3 -m json.tool

## simulate: Simule des requêtes (utilise la config du .env)
simulate:
	@echo "$(BLUE)Simulation d'utilisateurs...$(NC)"
	@$(UV) run python -m src.simulator

## simulate-quick: Simule 20 requêtes avec 5 utilisateurs (override .env)
simulate-quick:
	@echo "$(BLUE)Simulation rapide...$(NC)"
	@$(UV) run python -m src.simulator -r 20 -u 5 -v

## simulate-load: Test de charge avec 500 requêtes et 50 utilisateurs (override .env)
simulate-load:
	@echo "$(BLUE)Test de charge...$(NC)"
	@$(UV) run python -m src.simulator -r 500 -u 50

## simulate-drift: Simule avec data drift immédiat sur l'âge (vers 75 ans)
simulate-drift:
	@echo "$(BLUE)Simulation avec data drift immédiat...$(NC)"
	@echo "$(YELLOW)⚠️  Drift vers 75 ans sur toute la simulation$(NC)"
	@$(UV) run python -m src.simulator -r 200 -u 10 --enable-age-drift \
		--age-drift-target 75

## simulate-drift-progressive: Drift progressif (50% à 100% de la simulation)
simulate-drift-progressive:
	@echo "$(BLUE)Simulation avec data drift progressif...$(NC)"
	@echo "$(YELLOW)⚠️  Drift vers 80 ans entre 50% et 100%$(NC)"
	@$(UV) run python -m src.simulator -r 300 -u 15 --enable-age-drift \
		--age-drift-target 80 --age-drift-start 50 --age-drift-end 100

## simulate-gradio-drift-local: Drift via Gradio local (vers 75 ans)
simulate-gradio-drift-local:
	@echo "$(BLUE)Simulation Gradio avec data drift (local)...$(NC)"
	@echo "$(YELLOW)⚠️  Drift vers 75 ans sur toute la simulation$(NC)"
	@$(UV) run python -m src.simulator --use-gradio --gradio-url $(GRADIO_LOCAL_URL) \
		-r 200 -u 10 --enable-age-drift --age-drift-target 75 -v

## simulate-gradio-drift-hf: Drift via Gradio HF Spaces (vers 75 ans)
simulate-gradio-drift-hf:
	@echo "$(BLUE)Simulation Gradio avec data drift (HF Spaces)...$(NC)"
	@echo "$(YELLOW)⚠️  Drift vers 75 ans sur toute la simulation$(NC)"
	@if [ -f .env ]; then \
		echo "$(YELLOW)Chargement de HF_TOKEN depuis .env...$(NC)"; \
		export $$(cat .env | grep -v '^#' | grep HF_TOKEN | xargs) && \
		$(UV) run python -m src.simulator --use-gradio --gradio-url $(GRADIO_HF_URL) \
			--hf-token $$HF_TOKEN -r 200 -u 10 --enable-age-drift --age-drift-target 75 -v; \
	else \
		echo "$(YELLOW)⚠️  Fichier .env non trouvé, test sans token$(NC)"; \
		$(UV) run python -m src.simulator --use-gradio --gradio-url $(GRADIO_HF_URL) \
			-r 200 -u 10 --enable-age-drift --age-drift-target 75 -v; \
	fi

## simulate-gradio-drift-progressive-hf: Drift progressif via Gradio HF (50%-100%)
simulate-gradio-drift-progressive-hf:
	@echo "$(BLUE)Simulation Gradio avec drift progressif (HF Spaces)...$(NC)"
	@echo "$(YELLOW)⚠️  Drift vers 80 ans entre 50% et 100%$(NC)"
	@if [ -f .env ]; then \
		echo "$(YELLOW)Chargement de HF_TOKEN depuis .env...$(NC)"; \
		export $$(cat .env | grep -v '^#' | grep HF_TOKEN | xargs) && \
		$(UV) run python -m src.simulator --use-gradio --gradio-url $(GRADIO_HF_URL) \
			--hf-token $$HF_TOKEN -r 300 -u 15 --enable-age-drift \
			--age-drift-target 80 --age-drift-start 50 --age-drift-end 100 -v; \
	else \
		echo "$(YELLOW)⚠️  Fichier .env non trouvé, test sans token$(NC)"; \
		$(UV) run python -m src.simulator --use-gradio --gradio-url $(GRADIO_HF_URL) \
			-r 300 -u 15 --enable-age-drift \
			--age-drift-target 80 --age-drift-start 50 --age-drift-end 100 -v; \
	fi

## drift-analyze: Analyse le comportement du data drift
drift-analyze:
	@echo "$(BLUE)Analyse du data drift...$(NC)"
	@$(UV) run python -m src.simulator.drift_analyzer

## simulate-gradio-local: Simule des requêtes via Gradio API local
simulate-gradio-local:
	@echo "$(BLUE)Simulation via Gradio API (local)...$(NC)"
	@$(UV) run python -m src.simulator --use-gradio --gradio-url $(GRADIO_LOCAL_URL) -r 50 -u 5 -v

## simulate-gradio-hf: Simule des requêtes via HuggingFace Spaces
simulate-gradio-hf:
	@echo "$(BLUE)Simulation via Gradio API (HuggingFace Spaces)...$(NC)"
	@if [ -f .env ]; then \
		echo "$(YELLOW)Chargement de HF_TOKEN depuis .env...$(NC)"; \
		export $$(cat .env | grep -v '^#' | grep HF_TOKEN | xargs) && \
		$(UV) run python -m src.simulator --use-gradio --gradio-url $(GRADIO_HF_URL) --hf-token $$HF_TOKEN -r 50 -u 5 -v; \
	else \
		echo "$(YELLOW)⚠️  Fichier .env non trouvé, test sans token$(NC)"; \
		$(UV) run python -m src.simulator --use-gradio --gradio-url $(GRADIO_HF_URL) -r 50 -u 5 -v; \
	fi

## pipeline-elasticsearch-up: Lance Elasticsearch et Kibana
pipeline-elasticsearch-up:
	@echo "$(BLUE)Démarrage d'Elasticsearch et Kibana...$(NC)"
	@cd elasticsearch && docker-compose up -d
	@echo "$(GREEN)✓ Elasticsearch et Kibana démarrés$(NC)"
	@echo "$(YELLOW)Elasticsearch: http://localhost:9200$(NC)"
	@echo "$(YELLOW)Kibana: http://localhost:5601$(NC)"

## pipeline-elasticsearch-down: Arrête Elasticsearch et Kibana
pipeline-elasticsearch-down:
	@echo "$(BLUE)Arrêt d'Elasticsearch et Kibana...$(NC)"
	@cd elasticsearch && docker-compose down
	@echo "$(GREEN)✓ Elasticsearch et Kibana arrêtés$(NC)"

## pipeline-check: Vérifie les pré-requis du pipeline
pipeline-check:
	@if [ -f .env ]; then \
		export $$(cat .env | grep -v '^#' | grep HF_TOKEN | xargs) && \
		$(UV) run python scripts/check_pipeline_prerequisites.py; \
	else \
		$(UV) run python scripts/check_pipeline_prerequisites.py; \
	fi

## pipeline-test-indexes: Teste la création des index Elasticsearch
pipeline-test-indexes:
	@echo "$(BLUE)Test de création des index Elasticsearch...$(NC)"
	@$(UV) run python scripts/test_elasticsearch_indexes.py

## pipeline-test-parsing: Teste le parsing des logs
pipeline-test-parsing:
	@echo "$(BLUE)Test du parsing des logs...$(NC)"
	@$(UV) run python scripts/test_log_parsing.py

## pipeline-clear-indexes: Vide les index Elasticsearch
pipeline-clear-indexes:
	@echo "$(BLUE)Suppression des index Elasticsearch...$(NC)"
	@$(UV) run python scripts/clear_elasticsearch_indexes.py

## pipeline-deduplicate: Dédoublonne l'index ml-api-message
pipeline-deduplicate:
	@echo "$(BLUE)Déduplication de l'index ml-api-message...$(NC)"
	@$(UV) run python scripts/deduplicate_elasticsearch.py

## pipeline-export-parquet: Exporte ml-api-message vers Parquet
pipeline-export-parquet:
	@echo "$(BLUE)Export de ml-api-message vers Parquet...$(NC)"
	@$(UV) run python scripts/export_elasticsearch_to_parquet.py

## pipeline-analyze-drift: Analyse le drift de données avec Evidently AI
pipeline-analyze-drift:
	@echo "$(BLUE)Analyse du drift de données...$(NC)"
	@$(UV) run python scripts/analyze_data_drift.py

## pipeline-once: Exécute le pipeline une fois
pipeline-once:
	@echo "$(BLUE)Exécution du pipeline (une fois)...$(NC)"
	@if [ -f .env ]; then \
		export $$(cat .env | grep -v '^#' | grep HF_TOKEN | xargs) && \
		$(UV) run python -m src.logs_pipeline --once; \
	else \
		$(UV) run python -m src.logs_pipeline --once; \
	fi

## pipeline-continuous: Exécute le pipeline en continu
pipeline-continuous:
	@echo "$(BLUE)Exécution du pipeline en continu...$(NC)"
	@echo "$(YELLOW)Appuyez sur Ctrl+C pour arrêter$(NC)"
	@if [ -f .env ]; then \
		export $$(cat .env | grep -v '^#' | grep HF_TOKEN | xargs) && \
		$(UV) run python -m src.logs_pipeline --continuous --interval 10; \
	else \
		$(UV) run python -m src.logs_pipeline --continuous --interval 10; \
	fi

## setup: Configuration initiale du projet
setup: install-dev
	@echo "$(BLUE)Configuration initiale du projet...$(NC)"
	@test -f .env || cp .env.example .env
	@echo "$(GREEN)✓ Fichier .env créé$(NC)"
	@echo "$(YELLOW)⚠ Pensez à configurer vos variables d'environnement$(NC)"
	@echo "$(GREEN)✓ Configuration terminée$(NC)"

## dev: Environnement de développement complet
dev: setup run-redis
	@echo "$(GREEN)✓ Environnement de développement prêt$(NC)"
	@echo "$(YELLOW)Lancez 'make run-api' dans un autre terminal$(NC)"
	@echo "$(YELLOW)Lancez 'make run-ui' dans un troisième terminal$(NC)"

## ci: Commandes pour CI/CD
ci: lint test
	@echo "$(GREEN)✓ CI/CD checks passed$(NC)"

## convert-onnx: Convertit le modèle pickle en ONNX
convert-onnx:
	@echo "$(BLUE)Conversion du modèle en ONNX...$(NC)"
	$(PYTHON) scripts/convert_to_onnx.py --validate
	@echo "$(GREEN)✓ Conversion terminée$(NC)"

## convert-onnx-quick: Conversion ONNX sans validation
convert-onnx-quick:
	@echo "$(BLUE)Conversion rapide en ONNX...$(NC)"
	$(PYTHON) scripts/convert_to_onnx.py
	@echo "$(GREEN)✓ Conversion terminée$(NC)"

## docs: Génère la documentation Sphinx
docs:
	@echo "$(BLUE)Génération de la documentation Sphinx...$(NC)"
	@$(UV) run python scripts/generate_docs.py
	@echo "$(GREEN)✓ Documentation générée$(NC)"
	@echo "$(YELLOW)📖 Ouvrir: docs/_build/html/index.html$(NC)"

## docs-clean: Nettoie et régénère la documentation
docs-clean:
	@echo "$(BLUE)Nettoyage et régénération de la documentation...$(NC)"
	@$(UV) run python scripts/generate_docs.py --clean
	@echo "$(GREEN)✓ Documentation nettoyée et régénérée$(NC)"
	@echo "$(YELLOW)📖 Ouvrir: docs/_build/html/index.html$(NC)"

## docs-open: Génère et ouvre la documentation dans le navigateur
docs-open:
	@echo "$(BLUE)Génération de la documentation...$(NC)"
	@$(UV) run python scripts/generate_docs.py --open
	@echo "$(GREEN)✓ Documentation ouverte dans le navigateur$(NC)"

# Cibles par défaut
.DEFAULT_GOAL := help
