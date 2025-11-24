# Migration Elasticsearch et Kibana

Guide complet pour migrer vos index Elasticsearch, dataviews et dashboards Kibana.

## 📋 Sommaire

1. [Vue d'ensemble](#vue-densemble)
2. [Installation](#installation)
3. [Utilisation](#utilisation)
4. [Commandes disponibles](#commandes-disponibles)
5. [Format des exports](#format-des-exports)
6. [Exemples d'utilisation](#exemples-dutilisation)
7. [Architecture](#architecture)
8. [Dépannage](#dépannage)

## 🎯 Vue d'ensemble

Le script `scripts/migrate_elasticsearch.py` permet de:

- ✅ **Exporter/Importer les index Elasticsearch**
  - Mappings complets (types, analyseurs, settings)
  - Documents (format NDJSON pour bulk import)
  - Support du Scroll API pour grandes volumétries

- ✅ **Exporter/Importer les dataviews Kibana**
  - Index patterns avec tous les champs
  - Configurations et formatters

- ✅ **Exporter/Importer les dashboards Kibana**
  - Dashboards avec panneaux
  - Visualisations associées
  - Dépendances préservées

- ✅ **Backup/Restore complets**
  - Sauvegarde timestampée
  - Statistiques d'export/import
  - Gestion d'erreurs détaillée

## 📦 Installation

### Prérequis

- Python 3.8+
- Elasticsearch 7.x ou 8.x
- Kibana 7.x ou 8.x

### Dépendances

```bash
# Installation des dépendances
uv pip install elasticsearch requests

# Ou avec pip standard
pip install elasticsearch requests
```

### Vérification

```bash
# Vérifier que le script est exécutable
python scripts/migrate_elasticsearch.py --help
```

## 🚀 Utilisation

### Commande de base

```bash
python scripts/migrate_elasticsearch.py <commande> [options]
```

### Options communes

| Option | Description | Défaut |
|--------|-------------|--------|
| `--es-host` | Hôte Elasticsearch (host:port) | localhost:9200 |
| `--kibana-host` | Hôte Kibana (host:port) | localhost:5601 |
| `--username` | Nom d'utilisateur (optionnel) | None |
| `--password` | Mot de passe (optionnel) | None |

## 📚 Commandes disponibles

### 1. Export complet

Export tous les éléments (index + dataviews + dashboards):

```bash
python scripts/migrate_elasticsearch.py export --output ./backup
```

**Sortie**:
```
📦 Export des index Elasticsearch...
  → Export de l'index: ml-api-logs-predictions
    ✓ Mapping sauvegardé: ./backup/backup_20250121_153000/indexes/ml-api-logs-predictions_mapping.json
    ✓ 1523 documents exportés: ./backup/backup_20250121_153000/indexes/ml-api-logs-predictions_documents.ndjson

📊 Export des dataviews Kibana...
  ✓ Dataview exporté: ml-api-logs-*

📈 Export des dashboards Kibana...
  ✓ Dashboard exporté: ML API - Monitoring Dashboard
  ✓ Visualisation exportée: Predictions per hour

✅ Export complet terminé!
📁 Backup sauvegardé dans: ./backup/backup_20250121_153000
📊 Statistiques: ./backup/backup_20250121_153000/migration_stats.json
```

### 2. Import complet

Import tous les éléments depuis un backup:

```bash
python scripts/migrate_elasticsearch.py import \
  --input ./backup/backup_20250121_153000
```

### 3. Export uniquement les index

Export les index Elasticsearch sans les éléments Kibana:

```bash
python scripts/migrate_elasticsearch.py export-indexes --output ./backup
```

**Filtrage par pattern**:
```bash
# Le script exporte par défaut les index ml-api-*
# Pour personnaliser, modifier le code ligne 106
```

### 4. Import uniquement les index

Import les index depuis un backup:

```bash
python scripts/migrate_elasticsearch.py import-indexes \
  --input ./backup/backup_20250121_153000
```

### 5. Export uniquement les dataviews

Export les dataviews (index patterns) Kibana:

```bash
python scripts/migrate_elasticsearch.py export-dataviews --output ./backup
```

### 6. Import uniquement les dataviews

Import les dataviews depuis un backup:

```bash
python scripts/migrate_elasticsearch.py import-dataviews \
  --input ./backup/backup_20250121_153000
```

### 7. Export uniquement les dashboards

Export les dashboards et visualisations Kibana:

```bash
python scripts/migrate_elasticsearch.py export-dashboards --output ./backup
```

### 8. Import uniquement les dashboards

Import les dashboards depuis un backup:

```bash
python scripts/migrate_elasticsearch.py import-dashboards \
  --input ./backup/backup_20250121_153000
```

## 📂 Format des exports

### Structure du backup

```
backup_20250121_153000/
├── migration_stats.json          # Statistiques globales
├── indexes/                       # Index Elasticsearch
│   ├── ml-api-logs-predictions_mapping.json
│   ├── ml-api-logs-predictions_documents.ndjson
│   ├── ml-api-logs-requests_mapping.json
│   ├── ml-api-logs-requests_documents.ndjson
│   ├── ml-api-logs-errors_mapping.json
│   ├── ml-api-logs-errors_documents.ndjson
│   ├── ml-api-top-func_mapping.json
│   └── ml-api-top-func_documents.ndjson
├── dataviews/                     # Dataviews Kibana
│   ├── ml-api-logs-*.json
│   └── ml-api-errors-*.json
└── dashboards/                    # Dashboards Kibana
    ├── dashboard-1234.json
    ├── dashboard-5678.json
    └── visualizations/            # Visualisations associées
        ├── viz-abc.json
        └── viz-def.json
```

### Format NDJSON pour les documents

Format utilisé: **Newline Delimited JSON** (NDJSON)

```json
{"index":{"_index":"ml-api-logs-predictions","_id":"doc-1"}}
{"timestamp":"2025-01-21T15:30:00Z","prediction":1,"probability":0.85}
{"index":{"_index":"ml-api-logs-predictions","_id":"doc-2"}}
{"timestamp":"2025-01-21T15:31:00Z","prediction":0,"probability":0.23}
```

Ce format est optimisé pour le bulk import Elasticsearch.

### Fichier migration_stats.json

```json
{
  "timestamp": "20250121_153000",
  "backup_dir": "./backup/backup_20250121_153000",
  "indexes": {
    "exported": 4,
    "documents": 15234,
    "errors": []
  },
  "dataviews": {
    "exported": 2,
    "errors": []
  },
  "dashboards": {
    "exported": 8,
    "errors": []
  }
}
```

## 🔧 Exemples d'utilisation

### Exemple 1: Migration complète local → production

```bash
# 1. Export depuis l'environnement local
python scripts/migrate_elasticsearch.py export \
  --output ./backup \
  --es-host localhost:9200 \
  --kibana-host localhost:5601

# 2. Copier le backup vers le serveur de production
scp -r ./backup/backup_20250121_153000 user@production:/tmp/

# 3. Import sur la production
ssh user@production
cd /path/to/project
python scripts/migrate_elasticsearch.py import \
  --input /tmp/backup_20250121_153000 \
  --es-host production:9200 \
  --kibana-host production:5601 \
  --username elastic \
  --password changeme
```

### Exemple 2: Backup quotidien automatisé

Créer un script `backup_daily.sh`:

```bash
#!/bin/bash
# Backup quotidien Elasticsearch + Kibana

BACKUP_DIR="/data/backups/elasticsearch"
RETENTION_DAYS=30

# Export
python scripts/migrate_elasticsearch.py export \
  --output "$BACKUP_DIR" \
  --es-host localhost:9200 \
  --kibana-host localhost:5601

# Nettoyer les anciens backups (>30 jours)
find "$BACKUP_DIR" -type d -name "backup_*" -mtime +$RETENTION_DAYS -exec rm -rf {} \;

echo "✅ Backup terminé: $(date)"
```

Ajouter à crontab:
```bash
# Backup tous les jours à 2h du matin
0 2 * * * /path/to/backup_daily.sh >> /var/log/elasticsearch_backup.log 2>&1
```

### Exemple 3: Migration sélective (seulement les index)

```bash
# Exporter uniquement les index (sans dataviews/dashboards)
python scripts/migrate_elasticsearch.py export-indexes \
  --output ./backup_indexes

# Importer uniquement les index
python scripts/migrate_elasticsearch.py import-indexes \
  --input ./backup_indexes \
  --es-host production:9200
```

### Exemple 4: Restauration après incident

```bash
# 1. Identifier le dernier backup
ls -lt /data/backups/elasticsearch/

# 2. Restauration complète
python scripts/migrate_elasticsearch.py import \
  --input /data/backups/elasticsearch/backup_20250121_020000 \
  --es-host localhost:9200 \
  --kibana-host localhost:5601

# 3. Vérifier l'import
curl http://localhost:9200/_cat/indices?v
```

### Exemple 5: Migration avec authentification

```bash
# Export depuis cluster sécurisé
python scripts/migrate_elasticsearch.py export \
  --output ./backup \
  --es-host cluster.example.com:9200 \
  --kibana-host cluster.example.com:5601 \
  --username admin \
  --password super_secret_password
```

## 🏗️ Architecture

### Classe ElasticsearchMigrator

```python
class ElasticsearchMigrator:
    def __init__(self, es_host, kibana_host, username, password):
        """Initialise les connexions ES et Kibana."""

    def export_indexes(self, output_dir, index_patterns=None):
        """Export index avec Scroll API."""

    def import_indexes(self, input_dir):
        """Import index avec Bulk API."""

    def export_dataviews(self, output_dir):
        """Export dataviews via Kibana API."""

    def import_dataviews(self, input_dir):
        """Import dataviews via Kibana API."""

    def export_dashboards(self, output_dir):
        """Export dashboards + visualizations."""

    def import_dashboards(self, input_dir):
        """Import dashboards + visualizations."""

    def export_all(self, output_dir):
        """Export complet avec timestamp."""

    def import_all(self, input_dir):
        """Import complet."""
```

### APIs utilisées

| Opération | API Elasticsearch/Kibana |
|-----------|-------------------------|
| Récupérer mapping | `GET /{index}` |
| Récupérer documents | `POST /{index}/_search` avec scroll |
| Bulk insert | `POST /_bulk` |
| Liste dataviews | `GET /api/saved_objects/_find?type=index-pattern` |
| Créer dataview | `POST /api/saved_objects/index-pattern/{id}` |
| Liste dashboards | `GET /api/saved_objects/_find?type=dashboard` |
| Créer dashboard | `POST /api/saved_objects/dashboard/{id}` |

### Gestion des grandes volumétries

Le script utilise le **Scroll API** d'Elasticsearch pour paginer les résultats:

```python
# Scroll de 2 minutes, batch de 1000 documents
response = es.search(
    index=index_name,
    scroll='2m',
    size=1000,
    body={"query": {"match_all": {}}}
)

scroll_id = response['_scroll_id']
hits = response['hits']['hits']

while hits:
    # Traiter le batch
    for hit in hits:
        process_document(hit)

    # Récupérer le batch suivant
    response = es.scroll(scroll_id=scroll_id, scroll='2m')
    hits = response['hits']['hits']

# Nettoyer le scroll
es.clear_scroll(scroll_id=scroll_id)
```

### Bulk Import optimisé

Import par batch de 1000 documents:

```python
batch = []
for i in range(0, len(lines), 2):
    batch.append(lines[i])      # Metadata
    batch.append(lines[i + 1])  # Document

    # Bulk insert tous les 1000 docs
    if len(batch) >= 2000:  # 2 lignes par doc
        es.bulk(body=''.join(batch), refresh=True)
        batch = []

# Dernier batch
if batch:
    es.bulk(body=''.join(batch), refresh=True)
```

## 🐛 Dépannage

### Erreur: Connection refused

**Problème**: Impossible de se connecter à Elasticsearch/Kibana

**Solutions**:
```bash
# Vérifier qu'Elasticsearch est démarré
curl http://localhost:9200/_cluster/health

# Vérifier que Kibana est démarré
curl http://localhost:5601/api/status

# Vérifier les ports utilisés
netstat -an | grep 9200
netstat -an | grep 5601
```

### Erreur: Authentication required

**Problème**: Le cluster nécessite une authentification

**Solution**:
```bash
# Ajouter les credentials
python scripts/migrate_elasticsearch.py export \
  --output ./backup \
  --username elastic \
  --password changeme
```

### Erreur: Index already exists

**Problème**: L'index existe déjà sur la destination

**Solution**: Le script supprime automatiquement l'index existant avant l'import.

Si vous souhaitez éviter la suppression, commentez les lignes 211-214 dans le script:
```python
# if self.es.indices.exists(index=index_name):
#     print(f"    ⚠️  Index {index_name} existe déjà, suppression...")
#     self.es.indices.delete(index=index_name)
```

### Erreur: Scroll timeout

**Problème**: Le scroll expire avant la fin de l'export

**Solution**: Augmenter le timeout du scroll (ligne 135):
```python
# De 2m à 5m
response = self.es.search(
    index=index_name,
    scroll='5m',  # Au lieu de '2m'
    size=1000,
    body={"query": {"match_all": {}}}
)
```

### Erreur: Heap overflow sur gros volumes

**Problème**: Mémoire insuffisante pour l'export

**Solutions**:

1. **Réduire la taille des batchs** (ligne 136):
```python
size=500,  # Au lieu de 1000
```

2. **Augmenter la heap Java d'Elasticsearch**:
```bash
# Dans /etc/elasticsearch/jvm.options
-Xms4g
-Xmx4g
```

3. **Export index par index**:
```bash
# Exporter chaque index séparément
python scripts/migrate_elasticsearch.py export-indexes \
  --output ./backup_index1

# Modifier le code pour filtrer un seul index (ligne 106)
index_patterns = ["ml-api-logs-predictions"]  # Un seul index
```

### Erreur: Kibana API returns 404

**Problème**: L'API Kibana n'est pas accessible

**Solution**: Vérifier la version de Kibana et ajuster les URLs si nécessaire.

Pour Kibana 8.x, les endpoints peuvent changer:
```python
# Kibana 7.x
url = f"{self.kibana_url}/api/saved_objects/_find"

# Kibana 8.x (si problème)
url = f"{self.kibana_url}/api/saved_objects/_find?spaces=*"
```

### Performances lentes

**Optimisations**:

1. **Désactiver refresh pendant le bulk import**:
```python
es.bulk(body=''.join(batch), refresh=False)  # Pas de refresh
```

2. **Augmenter la taille des batchs**:
```python
size=2000,  # Au lieu de 1000
```

3. **Désactiver les replicas pendant l'import**:
```bash
# Avant l'import
curl -X PUT "localhost:9200/ml-api-*/_settings" -H 'Content-Type: application/json' -d'
{
  "index": {
    "number_of_replicas": 0
  }
}'

# Après l'import
curl -X PUT "localhost:9200/ml-api-*/_settings" -H 'Content-Type: application/json' -d'
{
  "index": {
    "number_of_replicas": 1
  }
}'
```

## 📊 Monitoring et logs

### Activer le mode verbose

Modifier le script pour ajouter des logs détaillés:

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
```

### Statistiques d'export/import

Le fichier `migration_stats.json` contient toutes les statistiques:

```bash
# Afficher les statistiques
cat ./backup/backup_20250121_153000/migration_stats.json | python -m json.tool

# Exemple de sortie
{
  "timestamp": "20250121_153000",
  "backup_dir": "./backup/backup_20250121_153000",
  "indexes": {
    "exported": 4,
    "documents": 15234,
    "errors": []
  },
  "dataviews": {
    "exported": 2,
    "errors": []
  },
  "dashboards": {
    "exported": 8,
    "errors": []
  }
}
```

### Vérification post-migration

```bash
# Comparer le nombre de documents
curl -X GET "localhost:9200/ml-api-logs-predictions/_count"

# Vérifier les mappings
curl -X GET "localhost:9200/ml-api-logs-predictions/_mapping?pretty"

# Lister les dataviews Kibana
curl -X GET "localhost:5601/api/saved_objects/_find?type=index-pattern" \
  -H 'kbn-xsrf: true'

# Lister les dashboards
curl -X GET "localhost:5601/api/saved_objects/_find?type=dashboard" \
  -H 'kbn-xsrf: true'
```

## 🔒 Sécurité

### Bonnes pratiques

1. **Ne jamais commiter les credentials**:
```bash
# Utiliser des variables d'environnement
export ES_USERNAME=elastic
export ES_PASSWORD=changeme

python scripts/migrate_elasticsearch.py export \
  --output ./backup \
  --username "$ES_USERNAME" \
  --password "$ES_PASSWORD"
```

2. **Chiffrer les backups sensibles**:
```bash
# Chiffrer le backup avec GPG
tar -czf - ./backup/backup_20250121_153000 | \
  gpg --symmetric --cipher-algo AES256 > backup.tar.gz.gpg

# Déchiffrer
gpg --decrypt backup.tar.gz.gpg | tar -xzf -
```

3. **Restreindre les permissions**:
```bash
# Seulement le propriétaire peut lire/écrire
chmod 700 ./backup/
```

4. **Utiliser HTTPS en production**:
```python
# Modifier le script pour utiliser HTTPS
self.es = Elasticsearch(
    [f"https://{es_host}"],  # HTTPS au lieu de HTTP
    basic_auth=(username, password),
    verify_certs=True,
    ca_certs="/path/to/ca.crt"
)
```

## 📚 Ressources

- [Elasticsearch Bulk API](https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-bulk.html)
- [Elasticsearch Scroll API](https://www.elastic.co/guide/en/elasticsearch/reference/current/paginate-search-results.html#scroll-search-results)
- [Kibana Saved Objects API](https://www.elastic.co/guide/en/kibana/current/saved-objects-api.html)
- [Script de migration](../scripts/migrate_elasticsearch.py)

---

**Dernière mise à jour**: 2025-01-21
**Version**: 1.0.0
