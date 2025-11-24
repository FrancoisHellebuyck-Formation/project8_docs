# Pipeline d'Intégration des Logs

## Vue d'ensemble

Ce document décrit l'architecture complète du pipeline d'intégration des logs, permettant la collecte, le filtrage et l'indexation des logs de l'API ML dans Elasticsearch pour analyse et monitoring.

## Table des matières

- [Architecture Globale](#architecture-globale)
- [Composants du Pipeline](#composants-du-pipeline)
- [Flux de Données](#flux-de-données)
- [Sources de Logs](#sources-de-logs)
- [Indexation Multiple](#indexation-multiple)
- [Configuration](#configuration)
- [Utilisation](#utilisation)
- [Monitoring](#monitoring)

## Architecture Globale

```
┌─────────────────────────────────────────────────────────────────┐
│                    SOURCES DE LOGS                              │
├────────────────────────┬────────────────────────────────────────┤
│    Redis (API logs)    │  Gradio (/logs_api endpoint)          │
│    Port 6379           │  HuggingFace Spaces                    │
└────────────────────────┴────────────────────────────────────────┘
                              ↓
                    ┌─────────────────┐
                    │   COLLECTOR     │
                    │  collector.py   │
                    │                 │
                    │  - Connexion    │
                    │  - Récupération │
                    │  - Déduplication│
                    │  - Parsing JSON │
                    └─────────────────┘
                              ↓
                    ┌─────────────────┐
                    │     FILTER      │
                    │    filter.py    │
                    │                 │
                    │  - Pattern match│
                    │  - HTTP method  │
                    │  - Validation   │
                    └─────────────────┘
                              ↓
                    ┌─────────────────────────────────────┐
                    │           INDEXER                   │
                    │          indexer.py                 │
                    │                                     │
                    │  ┌───────────────────────────────┐ │
                    │  │  ALL_DOCUMENTS (non filtrés)  │ │
                    │  └───────────────────────────────┘ │
                    │              ↓                      │
                    │  ┌───────────────────────────────┐ │
                    │  │    ml-api-logs (TOUS)         │ │
                    │  └───────────────────────────────┘ │
                    │                                     │
                    │  ┌───────────────────────────────┐ │
                    │  │ FILTERED_DOCUMENTS (filtrés)  │ │
                    │  └───────────────────────────────┘ │
                    │         ↓              ↓            │
                    │  ┌─────────────┐ ┌──────────────┐ │
                    │  │ml-api-message│ │ml-api-perfs │ │
                    │  │             │ │              │ │
                    │  │ml-api-top-  │ │              │ │
                    │  │   func      │ │              │ │
                    │  └─────────────┘ └──────────────┘ │
                    └─────────────────────────────────────┘
                              ↓
                    ┌─────────────────┐
                    │  ELASTICSEARCH  │
                    │  Port 9200      │
                    │  4 index créés  │
                    └─────────────────┘
                              ↓
                    ┌─────────────────┐
                    │    KIBANA       │
                    │  Port 5601      │
                    │  Visualisation  │
                    └─────────────────┘
```

## Composants du Pipeline

### 1. Collector (`src/logs_pipeline/collector.py`)

**Responsabilités** :
- Connexion aux sources de logs (Redis ou Gradio)
- Récupération des logs bruts
- Déduplication basée sur le timestamp
- Parsing JSON et validation

**Classe principale** :
```python
class LogCollector:
    def __init__(self, source: str = "redis"):
        """
        Args:
            source: "redis" ou "gradio"
        """

    def fetch_logs(self, limit: int = 100) -> List[Dict]:
        """Récupère les logs depuis la source."""

    def parse_log_entry(self, log_entry: str) -> Optional[Dict]:
        """Parse une entrée de log JSON."""
```

**Sources supportées** :

| Source | Description | Configuration |
|--------|-------------|---------------|
| `redis` | Cache Redis local | `REDIS_HOST`, `REDIS_PORT` |
| `gradio` | API Gradio HF Spaces | `GRADIO_URL` |

**Exemple d'utilisation** :
```python
# Mode Redis
collector = LogCollector(source="redis")
logs = collector.fetch_logs(limit=100)

# Mode Gradio
collector = LogCollector(source="gradio")
logs = collector.fetch_logs(limit=100)
```

### 2. Filter (`src/logs_pipeline/filter.py`)

**Responsabilités** :
- Filtrage par pattern (regex)
- Filtrage par méthode HTTP
- Extraction des données structurées
- Validation des champs requis

**Classe principale** :
```python
class LogFilter:
    def __init__(self, pattern: str = "API Call - POST /predict"):
        """
        Args:
            pattern: Pattern regex pour filtrer les logs
        """

    def filter_logs(self, logs: List[Dict]) -> List[Dict]:
        """Filtre les logs selon le pattern."""

    def extract_performance_metrics(self, log: Dict) -> Optional[Dict]:
        """Extrait les métriques de performance."""
```

**Patterns de filtrage** :

| Pattern | Description |
|---------|-------------|
| `API Call - POST /predict` | Logs de prédiction |
| `API Call - POST /predict_proba` | Logs de probabilités |
| `Performance metrics` | Métriques uniquement |

**Exemple d'utilisation** :
```python
log_filter = LogFilter(pattern="API Call - POST /predict")
filtered_logs = log_filter.filter_logs(raw_logs)
```

### 3. Indexer (`src/logs_pipeline/indexer.py`)

**Responsabilités** :
- Connexion à Elasticsearch
- Création et gestion des index
- Indexation en batch (bulk)
- Gestion des erreurs d'indexation

**Classe principale** :
```python
class ElasticsearchIndexer:
    def __init__(self, host: str = "localhost", port: int = 9200):
        """
        Args:
            host: Host Elasticsearch
            port: Port Elasticsearch
        """

    def create_index(self, index_name: str, mapping: Dict):
        """Crée un index avec mapping."""

    def index_logs(self, index_name: str, logs: List[Dict]) -> Dict:
        """Indexe les logs en batch."""

    def get_index_stats(self, index_name: str) -> Dict:
        """Récupère les statistiques d'un index."""
```

**Index créés** :

| Index | Description | Documents |
|-------|-------------|-----------|
| `ml-api-logs` | Tous les logs bruts | ALL |
| `ml-api-message` | Logs avec données de prédiction | FILTERED |
| `ml-api-perfs` | Logs avec métriques de performance | FILTERED |
| `ml-api-top-func` | Top fonctions coûteuses | FILTERED |

**Exemple d'utilisation** :
```python
indexer = ElasticsearchIndexer(host="localhost", port=9200)

# Indexer tous les logs
indexer.index_logs("ml-api-logs", all_logs)

# Indexer les logs filtrés
indexer.index_logs("ml-api-message", filtered_logs)
indexer.index_logs("ml-api-perfs", filtered_logs)
```

### 4. Pipeline Orchestrator (`src/logs_pipeline/pipeline.py`)

**Responsabilités** :
- Orchestration du pipeline complet
- Gestion des erreurs
- Logging du processus
- Statistiques d'exécution

**Classe principale** :
```python
class LogPipeline:
    def __init__(
        self,
        source: str = "redis",
        es_host: str = "localhost",
        es_port: int = 9200,
        batch_size: int = 100
    ):
        """Initialise le pipeline."""

    def run_once(self) -> Dict:
        """Exécute le pipeline une seule fois."""

    def run_continuous(self, interval: int = 10):
        """Exécute le pipeline en continu."""
```

**Exemple d'utilisation** :
```python
# Exécution unique
pipeline = LogPipeline(source="redis")
stats = pipeline.run_once()

# Exécution continue (toutes les 10 secondes)
pipeline.run_continuous(interval=10)
```

## Flux de Données

### Flux 1 : Pipeline Complet (Mode Normal)

```
┌──────────────┐
│  API Request │
└──────┬───────┘
       │ 1. Génération log
       ↓
┌──────────────┐
│ Redis Cache  │
│ (api_logs)   │
└──────┬───────┘
       │ 2. Collecte (poll)
       ↓
┌──────────────┐
│  Collector   │
│  - Fetch     │
│  - Parse     │
│  - Dedupe    │
└──────┬───────┘
       │ 3. Documents bruts
       ↓
┌──────────────┐
│   Filter     │
│  - Pattern   │
│  - Extract   │
└──────┬───────┘
       │ 4. Documents filtrés + tous
       ↓
┌──────────────────────────┐
│      Indexer             │
│                          │
│  all_docs → ml-api-logs  │
│                          │
│  filtered_docs →         │
│    ml-api-message        │
│    ml-api-perfs          │
│    ml-api-top-func       │
└──────┬───────────────────┘
       │ 5. Bulk insert
       ↓
┌──────────────┐
│Elasticsearch │
└──────────────┘
```

### Flux 2 : Mode Gradio (HuggingFace Spaces)

```
┌──────────────────┐
│  Gradio Space    │
│  (Port 7860)     │
│                  │
│  /logs_api       │
│  endpoint        │
└──────┬───────────┘
       │ 1. HTTP GET request
       ↓
┌──────────────┐
│  Collector   │
│  (gradio)    │
└──────┬───────┘
       │ 2. JSON logs
       ↓
┌──────────────┐
│   Filter     │
└──────┬───────┘
       │ 3. Filtered docs
       ↓
┌──────────────┐
│   Indexer    │
└──────┬───────┘
       │ 4. Bulk insert
       ↓
┌──────────────┐
│Elasticsearch │
└──────────────┘
```

### Flux 3 : Déduplication

```
┌─────────────────────────────────────┐
│          Collector                  │
│                                     │
│  seen_timestamps = set()            │
│                                     │
│  for log in raw_logs:               │
│    timestamp = log["timestamp"]     │
│                                     │
│    if timestamp in seen_timestamps: │
│      skip  # ❌ Doublon             │
│    else:                            │
│      seen_timestamps.add(timestamp) │
│      process  # ✅ Nouveau          │
└─────────────────────────────────────┘
```

## Sources de Logs

### Source 1 : Redis (Mode Local/Docker)

**Configuration** :
```bash
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_LOGS_KEY=api_logs
```

**Avantages** :
- Latence faible
- Accès direct local
- Pas de dépendance réseau

**Inconvénients** :
- Nécessite Redis actif
- Logs volatils (max 1000)

**Structure des logs Redis** :
```json
{
  "timestamp": "2025-11-22T10:30:45.123456",
  "level": "INFO",
  "message": "[uuid] POST /predict - 200 - 45ms - input - result",
  "data": {
    "transaction_id": "550e8400-e29b-41d4-a716-446655440000",
    "input_data": {
      "AGE": 65,
      "GENDER": 1,
      "SMOKING": 1,
      ...
    },
    "result": {
      "prediction": 1,
      "probability": 0.85,
      "message": "YES - High probability"
    },
    "performance_metrics": {
      "inference_time_ms": 12.5,
      "cpu_time_ms": 8.3,
      "memory_mb": 245.6,
      ...
    }
  }
}
```

### Source 2 : Gradio (Mode HuggingFace Spaces)

**Configuration** :
```bash
GRADIO_URL=https://francoisformation-oc-project8.hf.space
```

**Avantages** :
- Accès à distance
- Pas de Redis nécessaire
- Logs persistants

**Inconvénients** :
- Latence réseau
- Dépendance HF Spaces
- Rate limiting possible

**Endpoint** :
```
GET {GRADIO_URL}/logs_api?limit=100&offset=0
```

**Réponse** :
```json
{
  "logs": [
    {
      "timestamp": "...",
      "level": "INFO",
      "message": "...",
      "data": {...}
    }
  ],
  "total": 523,
  "limit": 100,
  "offset": 0
}
```

## Indexation Multiple

### Index 1 : ml-api-logs (Tous les logs)

**Objectif** : Conservation de TOUS les logs sans filtrage

**Mapping** :
```json
{
  "mappings": {
    "properties": {
      "timestamp": {"type": "date"},
      "level": {"type": "keyword"},
      "message": {"type": "text"},
      "data": {"type": "object", "enabled": true}
    }
  }
}
```

**Cas d'usage** :
- Débogage complet
- Audit
- Recherche full-text
- Analyse des erreurs

### Index 2 : ml-api-message (Prédictions)

**Objectif** : Logs filtrés contenant les données de prédiction

**Champs extraits** :
```python
{
  "timestamp": "2025-11-22T10:30:45.123456",
  "transaction_id": "uuid",
  "input_data": {
    "AGE": 65,
    "GENDER": 1,
    "SMOKING": 1,
    # ... 14 features
  },
  "result": {
    "prediction": 1,
    "probability": 0.85,
    "message": "YES - High probability"
  }
}
```

**Cas d'usage** :
- Analyse du drift de données
- Distribution des prédictions
- Analyse des patterns de patients

### Index 3 : ml-api-perfs (Métriques de Performance)

**Objectif** : Logs filtrés contenant les métriques de performance

**Champs extraits** :
```python
{
  "timestamp": "2025-11-22T10:30:45.123456",
  "transaction_id": "uuid",
  "inference_time_ms": 12.5,
  "cpu_time_ms": 8.3,
  "memory_mb": 245.6,
  "memory_delta_mb": 2.3,
  "function_calls": 42,
  "latency_ms": 45.2
}
```

**Cas d'usage** :
- Optimisation du modèle
- Détection de dégradation
- Alerting sur latence
- Analyse de throughput

### Index 4 : ml-api-top-func (Profiling Fonctions)

**Objectif** : Top fonctions coûteuses par transaction

**Champs extraits** :
```python
{
  "timestamp": "2025-11-22T10:30:45.123456",
  "transaction_id": "uuid",
  "function_name": "predict",
  "cumulative_time": 8.5,
  "calls": 1,
  "filename": "predictor.py",
  "line_number": 42
}
```

**Cas d'usage** :
- Profiling détaillé
- Optimisation du code
- Détection de bottlenecks
- Code review

## Configuration

### Variables d'Environnement

```bash
# Source des logs
PIPELINE_SOURCE=redis  # ou "gradio"

# Configuration Redis (si source=redis)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_LOGS_KEY=api_logs

# Configuration Gradio (si source=gradio)
GRADIO_URL=https://francoisformation-oc-project8.hf.space

# Configuration Elasticsearch
ELASTICSEARCH_HOST=localhost
ELASTICSEARCH_PORT=9200
ELASTICSEARCH_INDEX=ml-api-logs  # Index de base

# Configuration Pipeline
PIPELINE_BATCH_SIZE=100
PIPELINE_POLL_INTERVAL=10
PIPELINE_FILTER_PATTERN=API Call - POST /predict
```

### Fichier de Configuration

Fichier : `.env`

```bash
# Pipeline de logs
PIPELINE_BATCH_SIZE=100
PIPELINE_POLL_INTERVAL=10
PIPELINE_FILTER_PATTERN=API Call - POST /predict

# Elasticsearch
ELASTICSEARCH_HOST=localhost
ELASTICSEARCH_PORT=9200
ELASTICSEARCH_INDEX=ml-api-logs

# Gradio (optionnel)
GRADIO_URL=https://francoisformation-oc-project8.hf.space
```

## Utilisation

### Mode 1 : Exécution Unique

```bash
# Depuis Redis
make pipeline-once

# Équivalent à :
uv run python -m src.logs_pipeline.pipeline --source redis --once
```

**Sortie** :
```
📊 Pipeline de logs - Exécution unique
===========================================
Source: redis
Elasticsearch: localhost:9200
Batch size: 100
-------------------------------------------
✅ Collecte: 42 logs récupérés
✅ Filtrage: 38 logs filtrés
✅ Indexation:
   - ml-api-logs: 42 documents
   - ml-api-message: 38 documents
   - ml-api-perfs: 38 documents
   - ml-api-top-func: 152 documents (4 par transaction)
===========================================
Durée totale: 1.23s
```

### Mode 2 : Exécution Continue

```bash
# Mode continu (toutes les 10 secondes)
make pipeline-continuous

# Équivalent à :
uv run python -m src.logs_pipeline.pipeline --source redis --continuous --interval 10
```

**Sortie** :
```
🔄 Pipeline de logs - Mode continu (interval: 10s)
===========================================
[2025-11-22 10:30:00] ✅ Batch #1: 42 logs indexés
[2025-11-22 10:30:10] ✅ Batch #2: 15 logs indexés
[2025-11-22 10:30:20] ✅ Batch #3: 0 logs (aucun nouveau)
[2025-11-22 10:30:30] ✅ Batch #4: 23 logs indexés
...
```

### Mode 3 : Avec Docker Compose

```bash
# Lancer Elasticsearch + Kibana
make pipeline-elasticsearch-up

# Attendre le démarrage (30s)
sleep 30

# Lancer le pipeline
make pipeline-continuous
```

### Mode 4 : Depuis Gradio

```bash
# Mode Gradio (HuggingFace Spaces)
uv run python -m src.logs_pipeline.pipeline --source gradio --once

# Avec URL personnalisée
GRADIO_URL=https://custom-space.hf.space uv run python -m src.logs_pipeline.pipeline --source gradio --once
```

## Monitoring

### Commandes Makefile

```bash
# Vider tous les index
make pipeline-clear-indexes

# Statistiques Elasticsearch
curl http://localhost:9200/_cat/indices?v

# Compter les documents
curl http://localhost:9200/ml-api-logs/_count
curl http://localhost:9200/ml-api-message/_count
curl http://localhost:9200/ml-api-perfs/_count
curl http://localhost:9200/ml-api-top-func/_count
```

### Kibana Dashboards

**Accès** : http://localhost:5601

**Index Patterns à créer** :
1. `ml-api-logs*` - Tous les logs
2. `ml-api-message*` - Logs de prédictions
3. `ml-api-perfs*` - Métriques de performance
4. `ml-api-top-func*` - Profiling fonctions

**Visualisations recommandées** :

| Dashboard | Visualisations |
|-----------|----------------|
| **Vue d'ensemble** | Nombre de logs par heure, Distribution des niveaux (INFO/ERROR), Top 10 endpoints |
| **Prédictions ML** | Distribution YES/NO, Features moyennes, Probabilités (histogram), Drift de données |
| **Performance** | Latence (p50, p95, p99), CPU usage, Mémoire utilisée, Top fonctions coûteuses |
| **Erreurs** | Taux d'erreur, Types d'erreurs, Timeline des erreurs |

### Alertes Recommandées

| Métrique | Seuil Warning | Seuil Critical | Action |
|----------|---------------|----------------|--------|
| Latence moyenne | > 100ms | > 200ms | Vérifier le pool |
| Taux d'erreur | > 5% | > 10% | Vérifier les logs |
| CPU usage | > 80% | > 95% | Scaler horizontalement |
| Mémoire | > 1GB | > 2GB | Optimiser le pool |

## Troubleshooting

### Problème 1 : Pas de logs collectés

**Diagnostic** :
```bash
# Vérifier Redis
redis-cli -h localhost -p 6379 LLEN api_logs

# Vérifier Gradio
curl https://francoisformation-oc-project8.hf.space/logs_api?limit=10
```

**Solutions** :
- Vérifier que l'API génère des logs
- Vérifier la connexion Redis/Gradio
- Vérifier les variables d'environnement

### Problème 2 : Erreurs d'indexation

**Diagnostic** :
```bash
# Vérifier Elasticsearch
curl http://localhost:9200/_cluster/health

# Vérifier les index
curl http://localhost:9200/_cat/indices?v
```

**Solutions** :
- Vérifier qu'Elasticsearch est démarré
- Vérifier le mapping des index
- Augmenter la taille du batch

### Problème 3 : Doublons dans Elasticsearch

**Diagnostic** :
```bash
# Compter les documents
curl http://localhost:9200/ml-api-logs/_count
```

**Solutions** :
- Vérifier la déduplication dans le collector
- Ajouter un champ `_id` unique (transaction_id)
- Nettoyer les index et réindexer

## Migration et Backup

### Export complet

```bash
python scripts/migrate_elasticsearch.py export --output ./backup
```

### Import complet

```bash
python scripts/migrate_elasticsearch.py import --input ./backup/backup_YYYYMMDD_HHMMSS
```

Documentation complète : [ELASTIC.md](ELASTIC.md)

## Références

- [Architecture globale](ARCHITECTURE.md)
- [Documentation API](API_DOCUMENTATION.md)
- [Métriques de performance](PERFORMANCE_METRICS.md)
- [Migration Elasticsearch](ELASTIC.md)
- [Code source pipeline](../src/logs_pipeline/README.md)

---

**Version** : 1.0.0
**Dernière mise à jour** : 22 novembre 2025
**Projet** : OpenClassrooms MLOps - Projet 8
