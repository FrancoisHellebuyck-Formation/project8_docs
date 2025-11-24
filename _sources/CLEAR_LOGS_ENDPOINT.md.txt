# Endpoint DELETE /logs - Vider le cache Redis

## Description

L'endpoint `DELETE /logs` permet de vider complètement le cache des logs stockés dans Redis.

## Détails de l'endpoint

- **URL**: `/logs`
- **Méthode**: `DELETE`
- **Tag OpenAPI**: `Logs`
- **Authentification**: Aucune

## Comportement

Cet endpoint supprime **tous les logs** stockés dans le cache Redis en appelant la fonction `clear_redis_logs()` du module `logging_config`.

### Réponse en cas de succès

**Code HTTP**: `200 OK`

```json
{
  "message": "Logs supprimés avec succès"
}
```

### Réponse en cas d'erreur

**Code HTTP**: `500 Internal Server Error`

```json
{
  "detail": "Échec de la suppression des logs"
}
```

Ou si une exception est levée:

```json
{
  "detail": "Erreur lors de la suppression des logs : <message d'erreur>"
}
```

## Exemples d'utilisation

### Avec cURL (API directe)

```bash
curl -X DELETE "http://localhost:8000/logs"
```

**Réponse**:
```json
{
  "message": "Logs supprimés avec succès"
}
```

### Avec Makefile (recommandé)

#### API locale
```bash
make clear-logs
```

#### Via Gradio local
```bash
make clear-logs-gradio-local
```

#### Via Gradio HuggingFace Spaces
```bash
make clear-logs-gradio-hf
```

**Note** : Les commandes Gradio utilisent le client Gradio pour appeler l'endpoint `/api_clear_logs_proxy` qui fait un proxy vers `DELETE /logs` de l'API.

### Avec HTTPie

```bash
http DELETE http://localhost:8000/logs
```

### Avec Python (requests)

```python
import requests

response = requests.delete("http://localhost:8000/logs")
print(response.status_code)  # 200
print(response.json())       # {"message": "Logs supprimés avec succès"}
```

### Avec Python (httpx)

```python
import httpx

response = httpx.delete("http://localhost:8000/logs")
print(response.status_code)  # 200
print(response.json())       # {"message": "Logs supprimés avec succès"}
```

### Avec JavaScript (fetch)

```javascript
fetch('http://localhost:8000/logs', {
  method: 'DELETE'
})
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error('Error:', error));
```

## Cas d'usage

### 1. Nettoyage après tests

```bash
# Exécuter des tests qui génèrent beaucoup de logs
make test

# Vider les logs après les tests
curl -X DELETE "http://localhost:8000/logs"
```

### 2. Maintenance périodique

```bash
# Script de maintenance quotidien
#!/bin/bash
echo "Nettoyage des logs..."
curl -X DELETE "http://localhost:8000/logs"
echo "Logs supprimés"
```

### 3. Reset avant un nouveau test de charge

```bash
# Vider les logs avant un test de performance
curl -X DELETE "http://localhost:8000/logs"

# Lancer le test de charge
make simulate-load

# Consulter les nouveaux logs
curl "http://localhost:8000/logs?limit=100"
```

## Intégration avec le pipeline Elasticsearch

⚠️ **Important**: Cet endpoint vide **uniquement** le cache Redis local. Les logs déjà indexés dans Elasticsearch ne sont **pas affectés**.

### Workflow complet

```
1. Logs générés par l'API → Redis (cache temporaire)
                          ↓
2. Pipeline collecte les logs depuis Redis
                          ↓
3. Pipeline filtre et indexe dans Elasticsearch
                          ↓
4. Logs persistés dans ES (ml-api-logs, ml-api-message, ml-api-perfs)
```

**Après `DELETE /logs`**:
- ✅ Cache Redis vidé
- ✅ Logs dans Elasticsearch conservés
- ✅ Nouveaux logs continuent d'être collectés

### Pour vider complètement les logs

Si vous voulez supprimer à la fois le cache Redis ET les index Elasticsearch:

```bash
# 1. Vider le cache Redis
curl -X DELETE "http://localhost:8000/logs"

# 2. Vider les index Elasticsearch
make pipeline-clear-indexes
```

## Implémentation technique

### Code source

[src/api/main.py:416-439](../src/api/main.py#L416-L439)

```python
@app.delete("/logs", tags=["Logs"])
async def clear_logs():
    """
    Supprime tous les logs.

    Returns:
        dict: Message de confirmation.
    """
    try:
        success = clear_redis_logs()

        if success:
            logger.info("Logs supprimés")
            return {"message": "Logs supprimés avec succès"}
        else:
            raise HTTPException(
                status_code=500,
                detail="Échec de la suppression des logs"
            )

    except Exception as e:
        error_msg = f"Erreur lors de la suppression des logs : {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg) from e
```

### Fonction backend

La fonction `clear_redis_logs()` est implémentée dans [src/api/logging_config.py](../src/api/logging_config.py):

```python
def clear_redis_logs() -> bool:
    """
    Supprime tous les logs de Redis.

    Returns:
        bool: True si succès, False sinon
    """
    try:
        redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True
        )
        redis_client.delete("api_logs")
        return True
    except Exception as e:
        print(f"Erreur lors de la suppression des logs Redis: {e}")
        return False
```

## Tests

L'endpoint est testé dans [tests/api/test_main.py](../tests/api/test_main.py):

```python
def test_clear_logs(self, api_client):
    """Test DELETE /logs pour supprimer les logs."""
    response = api_client.delete("/logs")

    # Peut retourner 200 ou 500 selon Redis disponible
    assert response.status_code in [
        status.HTTP_200_OK,
        status.HTTP_500_INTERNAL_SERVER_ERROR
    ]
```

## Documentation OpenAPI

L'endpoint est automatiquement documenté dans Swagger UI:

**URL**: http://localhost:8000/docs#/Logs/clear_logs_logs_delete

![Swagger UI](https://via.placeholder.com/800x400?text=DELETE+/logs+in+Swagger+UI)

## Bonnes pratiques

### ✅ À faire

- Utiliser cet endpoint pour nettoyer les logs de développement
- L'intégrer dans des scripts de maintenance
- Le combiner avec des vérifications de capacité Redis

### ❌ À éviter

- Ne pas l'utiliser en production sans précaution (perte de logs non indexés)
- Ne pas l'appeler trop fréquemment (laissez le pipeline collecter les logs d'abord)
- Ne pas le confondre avec le nettoyage des index Elasticsearch

## Sécurité

⚠️ **Important**: Cet endpoint n'a **aucune authentification**. En production:

1. Ajoutez une authentification (API key, OAuth, etc.)
2. Limitez l'accès par IP
3. Loggez tous les appels à cet endpoint pour l'audit

Exemple de protection par API key:

```python
from fastapi import Depends, Header, HTTPException

async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != settings.API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return x_api_key

@app.delete("/logs", tags=["Logs"], dependencies=[Depends(verify_api_key)])
async def clear_logs():
    # ... rest of the code
```

## Monitoring

Pour monitorer l'utilisation de cet endpoint:

```python
# Dans le middleware de logging
logger.info(
    f"CLEAR_LOGS called from IP: {request.client.host}"
)
```

## FAQ

### Q: Que se passe-t-il si Redis n'est pas disponible ?

**R**: L'endpoint retournera une erreur 500 avec le message "Échec de la suppression des logs".

### Q: Les logs en cours de collecte par le pipeline sont-ils perdus ?

**R**: Oui, si vous videz Redis pendant que le pipeline collecte les logs, les logs non encore indexés dans Elasticsearch seront perdus.

### Q: Peut-on récupérer les logs après suppression ?

**R**: Non, les logs supprimés du cache Redis ne peuvent pas être récupérés. Seuls les logs déjà indexés dans Elasticsearch restent disponibles.

### Q: Combien de temps prend la suppression ?

**R**: Instantané (< 10ms), car Redis exécute la commande DELETE de manière atomique.

### Q: Faut-il redémarrer l'API après avoir vidé les logs ?

**R**: Non, l'API continue de fonctionner normalement et recommence immédiatement à logger.

## Voir aussi

- [API_DOCUMENTATION.md](../API_DOCUMENTATION.md) - Documentation complète de l'API
- [src/api/PERFORMANCE_MONITORING.md](../src/api/PERFORMANCE_MONITORING.md) - Monitoring des performances
- [src/logs_pipeline/README.md](../src/logs_pipeline/README.md) - Pipeline Elasticsearch
