# Métriques de Performance de l'API ML

Ce document détaille les métriques de performance collectées et loggées par l'API lors de chaque prédiction.

## Vue d'ensemble

L'API collecte automatiquement des métriques de performance détaillées pour chaque appel aux endpoints `/predict` et `/predict_proba`. Ces métriques permettent de :

- **Optimiser les performances** du modèle ML
- **Identifier les goulots d'étranglement** dans le code
- **Monitorer la latence** de l'API en production
- **Analyser l'utilisation des ressources** (CPU, mémoire)

## Activation/Désactivation

Les métriques de performance sont contrôlées par la variable d'environnement `ENABLE_PERFORMANCE_MONITORING`.

### Configuration

```bash
# Dans .env
ENABLE_PERFORMANCE_MONITORING=true   # Activer (par défaut)
ENABLE_PERFORMANCE_MONITORING=false  # Désactiver
```

### Impact sur les performances

⚠️ **Important** : Le monitoring de performance utilise `cProfile` qui ajoute un léger overhead (~5-10ms par requête). En production, évaluez si cet overhead est acceptable pour votre cas d'usage.

## Structure des métriques

### Format JSON

Les métriques sont loggées au format JSON structuré :

```json
{
  "performance_metrics": {
    "transaction_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "inference_time_ms": 25.34,
    "cpu_time_ms": 18.12,
    "memory_mb": 245.6,
    "memory_delta_mb": 2.3,
    "function_calls": 1523,
    "latency_ms": 28.45,
    "top_functions": [
      {
        "function": "predict",
        "file": "src/model/predictor.py",
        "line": 45,
        "cumulative_time_ms": 15.23,
        "total_time_ms": 12.45,
        "calls": 1
      },
      {
        "function": "engineer_features",
        "file": "src/model/feature_engineering.py",
        "line": 78,
        "cumulative_time_ms": 8.12,
        "total_time_ms": 7.89,
        "calls": 1
      }
    ]
  }
}
```

## Métriques collectées

### 1. `transaction_id` (string)

**Description** : Identifiant unique (UUID) de la transaction.

**Utilité** : Permet de corréler les métriques de performance avec les logs de prédiction dans Elasticsearch.

**Exemple** : `"a1b2c3d4-e5f6-7890-abcd-ef1234567890"`

**Disponibilité** : ✅ Toujours présent

---

### 2. `inference_time_ms` (float)

**Description** : Temps total d'inférence du modèle ML en millisecondes.

**Mesure** : Temps écoulé depuis le début du profiling jusqu'à la fin, incluant :
- Feature engineering
- Prédiction du modèle
- Post-traitement

**Plage typique** : 10-50 ms (dépend de la complexité du modèle)

**Utilité** :
- Indicateur principal de performance du modèle
- Permet de détecter les dégradations de performance
- Utile pour définir des SLA (Service Level Agreement)

**Exemple** : `25.34` (ms)

**Alerte recommandée** : > 100 ms

---

### 3. `cpu_time_ms` (float)

**Description** : Temps CPU utilisé par le processus en millisecondes.

**Mesure** : Temps réel passé sur le CPU (peut être inférieur à `inference_time_ms` si le processus attend des I/O).

**Plage typique** : 15-40 ms

**Utilité** :
- Identifier les opérations CPU-intensives
- Optimiser l'utilisation des ressources
- Dimensionner les instances en production

**Exemple** : `18.12` (ms)

**Formule** : `cpu_time_ms ≤ inference_time_ms`

---

### 4. `memory_mb` (float)

**Description** : Mémoire totale utilisée par le processus en mégaoctets.

**Mesure** : RSS (Resident Set Size) du processus au moment de la mesure.

**Plage typique** : 200-500 MB (dépend de la taille du modèle)

**Utilité** :
- Surveiller les fuites mémoire
- Dimensionner les conteneurs Docker
- Optimiser le chargement du modèle

**Exemple** : `245.6` (MB)

**Alerte recommandée** : Augmentation constante sur plusieurs requêtes

---

### 5. `memory_delta_mb` (float)

**Description** : Variation de mémoire entre le début et la fin de la requête en mégaoctets.

**Mesure** : `memory_after - memory_before`

**Plage typique** : -5 à +10 MB

**Valeur positive** : Allocation mémoire (normale)
**Valeur négative** : Libération mémoire par le garbage collector

**Utilité** :
- Détecter les allocations mémoire importantes
- Identifier les fuites mémoire potentielles
- Optimiser les structures de données

**Exemple** : `2.3` (MB)

**Alerte recommandée** : > 50 MB (allocation excessive)

---

### 6. `function_calls` (integer)

**Description** : Nombre total d'appels de fonctions durant l'exécution.

**Mesure** : Compteur de tous les appels de fonctions interceptés par cProfile.

**Plage typique** : 1000-5000 appels

**Utilité** :
- Identifier les chemins d'exécution complexes
- Détecter les boucles récursives excessives
- Comparer la complexité entre différentes versions

**Exemple** : `1523`

**Alerte recommandée** : > 10,000 (code potentiellement inefficace)

---

### 7. `latency_ms` (float)

**Description** : Latence totale de la requête HTTP en millisecondes (temps wall-clock).

**Mesure** : Temps écoulé du début à la fin de la requête HTTP, incluant :
- Parsing de la requête
- Validation Pydantic
- Inférence du modèle
- Sérialisation de la réponse

**Plage typique** : 20-60 ms

**Utilité** :
- Mesure de l'expérience utilisateur réelle
- Inclut tous les overheads (réseau, middleware, etc.)
- Métrique principale pour les SLA

**Exemple** : `28.45` (ms)

**Formule** : `latency_ms ≥ inference_time_ms`

**Alerte recommandée** : > 200 ms (mauvaise expérience utilisateur)

---

### 8. `top_functions` (array)

**Description** : Liste des 5 fonctions les plus coûteuses en temps d'exécution.

**Structure** : Tableau d'objets contenant :
- `function` : Nom de la fonction
- `file` : Chemin du fichier source
- `line` : Numéro de ligne dans le fichier
- `cumulative_time_ms` : Temps cumulatif (incluant les sous-appels)
- `total_time_ms` : Temps passé dans la fonction elle-même
- `calls` : Nombre d'appels à cette fonction

**Utilité** :
- Identifier précisément les goulots d'étranglement
- Prioriser les optimisations
- Comprendre le comportement du code en production

**Exemple** :

```json
{
  "function": "predict",
  "file": "src/model/predictor.py",
  "line": 45,
  "cumulative_time_ms": 15.23,
  "total_time_ms": 12.45,
  "calls": 1
}
```

**Interprétation** :
- `cumulative_time_ms` élevé : La fonction et ses sous-fonctions sont coûteuses
- `total_time_ms` élevé : La fonction elle-même est coûteuse
- `calls` élevé : La fonction est appelée fréquemment

---

## Flux de collecte

```
1. Requête HTTP POST /predict
        ↓
2. Middleware ajoute transaction_id
        ↓
3. PerformanceMonitor.start()
   - Capture memory_before
   - Démarre cProfile
        ↓
4. Exécution de la prédiction
   - Feature engineering
   - Inférence du modèle
        ↓
5. PerformanceMonitor.stop()
   - Capture memory_after
   - Arrête cProfile
   - Calcule les métriques
        ↓
6. PerformanceMonitor.log_metrics()
   - Formate en JSON
   - Logge avec transaction_id
        ↓
7. Logs envoyés à Redis
        ↓
8. Pipeline Elasticsearch collecte
        ↓
9. Indexation dans ml-api-perfs
```

## Accès aux métriques

### 1. Via les logs Redis (temps réel)

```bash
# Récupérer les derniers logs incluant les métriques
curl "http://localhost:8000/logs?limit=50" | jq '.logs[] | select(.message | contains("performance_metrics"))'
```

### 2. Via Elasticsearch (historique)

```bash
# Requête Elasticsearch pour les métriques
curl -X GET "http://localhost:9200/ml-api-perfs/_search?pretty" \
  -H 'Content-Type: application/json' \
  -d '{
    "size": 10,
    "sort": [{"@timestamp": "desc"}],
    "query": {
      "range": {
        "inference_time_ms": {
          "gte": 50
        }
      }
    }
  }'
```

### 3. Via Kibana (visualisation)

1. Ouvrir Kibana : http://localhost:5601
2. Créer un index pattern : `ml-api-perfs*`
3. Créer des visualisations :
   - Graphique de latence moyenne au fil du temps
   - Distribution des temps d'inférence
   - Top fonctions par temps cumulatif
   - Utilisation mémoire par requête

## Dashboards Kibana recommandés

### Dashboard 1 : Vue d'ensemble des performances

**Visualisations** :
1. **Latence moyenne** (Line chart)
   - Axe X : @timestamp
   - Axe Y : Moyenne de latency_ms

2. **Distribution des temps d'inférence** (Histogram)
   - Buckets : inference_time_ms (0-20ms, 20-50ms, 50-100ms, >100ms)

3. **Utilisation mémoire** (Area chart)
   - Axe X : @timestamp
   - Axe Y : memory_mb

4. **Top 10 fonctions coûteuses** (Data table)
   - Colonnes : function, file, avg(cumulative_time_ms)

### Dashboard 2 : Analyse détaillée

**Visualisations** :
1. **Corrélation CPU vs Latence** (Scatter plot)
   - Axe X : cpu_time_ms
   - Axe Y : latency_ms

2. **Évolution de la mémoire** (Line chart)
   - memory_delta_mb par requête

3. **Nombre d'appels de fonctions** (Metric)
   - Moyenne de function_calls

4. **Percentiles de latence** (Line chart)
   - P50, P95, P99 de latency_ms

## Analyse et optimisation

### 1. Identifier les requêtes lentes

**Requête Elasticsearch** :

```json
{
  "query": {
    "range": {
      "latency_ms": {"gte": 100}
    }
  },
  "sort": [{"latency_ms": "desc"}],
  "size": 20
}
```

**Actions** :
- Analyser les `top_functions` des requêtes lentes
- Vérifier si memory_delta_mb est anormalement élevé
- Comparer avec des requêtes rapides du même endpoint

### 2. Détecter les fuites mémoire

**Critères** :
- `memory_delta_mb` positif constant sur plusieurs requêtes
- `memory_mb` augmente linéairement dans le temps

**Requête Elasticsearch** :

```json
{
  "aggs": {
    "memory_trend": {
      "date_histogram": {
        "field": "@timestamp",
        "interval": "1h"
      },
      "aggs": {
        "avg_memory": {"avg": {"field": "memory_mb"}},
        "avg_delta": {"avg": {"field": "memory_delta_mb"}}
      }
    }
  }
}
```

### 3. Optimiser le feature engineering

Si `engineer_features` apparaît souvent dans `top_functions` :

**Optimisations possibles** :
- Vectoriser les opérations avec NumPy
- Éviter les boucles Python
- Utiliser des opérations Pandas optimisées
- Cacher les résultats si les features sont identiques

### 4. Optimiser la prédiction

Si `predict` ou `predict_proba` est lent :

**Vérifications** :
- Utiliser un modèle plus léger (pruning, quantization)
- Vérifier la taille des features (28 features actuellement)
- Considérer ONNX Runtime pour l'inférence
- Évaluer l'utilisation de batch predictions

## Alertes recommandées

### Alertes critiques

| Métrique | Seuil | Action |
|----------|-------|--------|
| `latency_ms` | > 500 ms | Investigation immédiate |
| `memory_mb` | > 1000 MB | Risque de OOM |
| `memory_delta_mb` | > 100 MB | Fuite mémoire probable |

### Alertes warning

| Métrique | Seuil | Action |
|----------|-------|--------|
| `latency_ms` | > 200 ms | Analyse de performance |
| `inference_time_ms` | > 100 ms | Optimisation du modèle |
| `cpu_time_ms` | > 50 ms | Optimisation du code |
| `function_calls` | > 10,000 | Refactoring recommandé |

### Configuration Prometheus (exemple)

```yaml
groups:
  - name: ml-api-performance
    rules:
      - alert: HighLatency
        expr: avg(ml_api_latency_ms) > 200
        for: 5m
        annotations:
          summary: "Latence API élevée"
          description: "Latence moyenne > 200ms sur 5 minutes"

      - alert: MemoryLeak
        expr: increase(ml_api_memory_mb[1h]) > 100
        annotations:
          summary: "Fuite mémoire détectée"
          description: "Augmentation de +100MB en 1 heure"
```

## Exemples d'analyse

### Exemple 1 : Requête lente identifiée

**Métriques observées** :
```json
{
  "inference_time_ms": 125.45,
  "cpu_time_ms": 98.32,
  "latency_ms": 132.67,
  "top_functions": [
    {
      "function": "engineer_features",
      "cumulative_time_ms": 85.12,
      "total_time_ms": 78.45,
      "calls": 1
    }
  ]
}
```

**Diagnostic** :
- Feature engineering consomme 85% du temps total
- La fonction elle-même (vs ses sous-fonctions) prend 78ms
- Optimisation prioritaire : `engineer_features`

**Actions prises** :
1. Profilé le code de `engineer_features`
2. Remplacé les boucles Python par NumPy vectorization
3. Résultat : inference_time_ms réduit à 35ms (-72%)

### Exemple 2 : Fuite mémoire détectée

**Observation sur 100 requêtes** :
```
Requête 1:  memory_mb=245.3, memory_delta_mb=2.1
Requête 50: memory_mb=312.7, memory_delta_mb=1.8
Requête 100: memory_mb=385.2, memory_delta_mb=2.3
```

**Diagnostic** :
- Augmentation de 140 MB sur 100 requêtes
- ~1.4 MB par requête non libéré

**Cause trouvée** :
- Accumulation de logs en mémoire dans une liste globale
- Pas de rotation automatique

**Solution** :
- Implémentation d'un buffer rotatif limité à 1000 entrées
- Résultat : memory_mb stable autour de 250 MB

## Export des métriques

### Export vers Parquet

Le pipeline Elasticsearch peut exporter les métriques vers Parquet :

```bash
# Export des métriques de performance
python scripts/export_perfs_to_parquet.py \
  --output reports/performance_metrics.parquet
```

### Analyse avec Pandas

```python
import pandas as pd

# Charger les métriques
df = pd.read_parquet('reports/performance_metrics.parquet')

# Statistiques descriptives
print(df[['inference_time_ms', 'latency_ms', 'memory_delta_mb']].describe())

# Identifier les outliers
slow_requests = df[df['latency_ms'] > df['latency_ms'].quantile(0.95)]
print(f"Top 5% requêtes lentes:\n{slow_requests}")

# Corrélation entre métriques
corr = df[['inference_time_ms', 'cpu_time_ms', 'memory_mb']].corr()
print(f"\nCorrélations:\n{corr}")
```

## Désactivation en production

Si le monitoring de performance n'est pas nécessaire en production :

```bash
# Dans .env
ENABLE_PERFORMANCE_MONITORING=false
```

**Impact** :
- ✅ Réduction de la latence (~5-10 ms)
- ✅ Réduction de l'overhead CPU
- ❌ Perte de visibilité sur les performances

**Recommandation** : Garder activé en production avec un sampling (ex: 10% des requêtes) pour maintenir la visibilité sans impacter significativement les performances.

## Références

- [src/api/performance_monitor.py](../src/api/performance_monitor.py) - Implémentation du monitoring
- [src/api/PERFORMANCE_MONITORING.md](../src/api/PERFORMANCE_MONITORING.md) - Guide d'utilisation
- [src/logs_pipeline/README.md](../src/logs_pipeline/README.md) - Pipeline Elasticsearch
- [API_DOCUMENTATION.md](../API_DOCUMENTATION.md) - Documentation de l'API

## FAQ

### Q: Les métriques ralentissent-elles l'API ?

**R**: Oui, légèrement (~5-10 ms par requête). Cependant, cet overhead est généralement acceptable par rapport à la valeur des métriques collectées. En production à haute charge, considérez un sampling.

### Q: Puis-je collecter des métriques custom ?

**R**: Oui, modifiez `PerformanceMonitor` dans [src/api/performance_monitor.py](../src/api/performance_monitor.py) pour ajouter vos propres métriques.

### Q: Les métriques sont-elles disponibles en temps réel ?

**R**: Oui, via l'endpoint `/logs`. Pour une analyse historique, utilisez Elasticsearch.

### Q: Comment comparer les performances entre versions ?

**R**: Utilisez le `@timestamp` dans Elasticsearch pour filtrer par période et comparez les moyennes de `inference_time_ms`.

### Q: Que faire si memory_delta_mb est toujours négatif ?

**R**: C'est normal ! Le garbage collector Python libère de la mémoire. Une valeur négative constante indique une bonne gestion mémoire.

### Q: Comment simuler une charge pour tester les métriques ?

**R**: Utilisez le simulateur intégré :
```bash
make simulate-load
# ou
make simulate-quick
```
