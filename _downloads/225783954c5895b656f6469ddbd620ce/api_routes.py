"""
Routes FastAPI pour accès HTTP direct dans le Gradio Space.

Ce module définit des routes FastAPI qui sont montées sur l'application
Gradio, permettant un accès direct via HTTP/curl aux endpoints de l'API
sans passer par le client Gradio.

Les routes sont accessibles via:
- https://SPACE-URL/api/health
- https://SPACE-URL/api/predict
- https://SPACE-URL/api/predict_proba
- https://SPACE-URL/api/logs
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict
import logging

from ..proxy.client import APIProxyClient

logger = logging.getLogger(__name__)

# Créer le router FastAPI
api_router = APIRouter(prefix="/api", tags=["API Proxy"])

# Initialiser le client proxy (utilisera localhost:8000 en interne)
proxy_client = APIProxyClient()


@api_router.get("/health")
async def health_check() -> JSONResponse:
    """
    Vérifie la santé de l'API FastAPI interne.

    Returns:
        JSONResponse: État de santé de l'API

    Example:
        ```bash
        curl https://YOUR-SPACE.hf.space/api/health
        ```
    """
    try:
        response_data, status_code = proxy_client.get_health()
        return JSONResponse(content=response_data, status_code=status_code)
    except Exception as e:
        logger.error(f"Erreur health check: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/")
async def get_info() -> JSONResponse:
    """
    Récupère les informations de l'API.

    Returns:
        JSONResponse: Informations de l'API

    Example:
        ```bash
        curl https://YOUR-SPACE.hf.space/api/
        ```
    """
    try:
        response_data, status_code = proxy_client.get_root()
        return JSONResponse(content=response_data, status_code=status_code)
    except Exception as e:
        logger.error(f"Erreur get_info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/predict")
async def predict(patient_data: Dict) -> JSONResponse:
    """
    Effectue une prédiction de cancer du poumon.

    Args:
        patient_data: Dictionnaire avec les 14 features du patient

    Returns:
        JSONResponse: Résultat de la prédiction

    Example:
        ```bash
        curl -X POST https://YOUR-SPACE.hf.space/api/predict \\
          -H "Content-Type: application/json" \\
          -d '{
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
          }'
        ```
    """
    try:
        response_data, status_code = proxy_client.post_predict(patient_data)
        return JSONResponse(content=response_data, status_code=status_code)
    except Exception as e:
        logger.error(f"Erreur predict: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/predict_proba")
async def predict_proba(patient_data: Dict) -> JSONResponse:
    """
    Récupère les probabilités de prédiction.

    Args:
        patient_data: Dictionnaire avec les 14 features du patient

    Returns:
        JSONResponse: Probabilités pour chaque classe

    Example:
        ```bash
        curl -X POST https://YOUR-SPACE.hf.space/api/predict_proba \\
          -H "Content-Type: application/json" \\
          -d '{
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
          }'
        ```
    """
    try:
        response_data, status_code = proxy_client.post_predict_proba(
            patient_data
        )
        return JSONResponse(content=response_data, status_code=status_code)
    except Exception as e:
        logger.error(f"Erreur predict_proba: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/logs")
async def get_logs(
    limit: int = 100,
    offset: int = 0
) -> JSONResponse:
    """
    Récupère les logs de l'API.

    Args:
        limit: Nombre de logs à récupérer (max: 1000)
        offset: Nombre de logs à sauter (pagination)

    Returns:
        JSONResponse: Liste des logs

    Example:
        ```bash
        curl "https://YOUR-SPACE.hf.space/api/logs?limit=10&offset=0"
        ```
    """
    try:
        response_data, status_code = proxy_client.get_logs(limit, offset)
        return JSONResponse(content=response_data, status_code=status_code)
    except Exception as e:
        logger.error(f"Erreur get_logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.delete("/logs")
async def delete_logs() -> JSONResponse:
    """
    Vide le cache Redis des logs.

    Returns:
        JSONResponse: Confirmation de la suppression

    Example:
        ```bash
        curl -X DELETE https://YOUR-SPACE.hf.space/api/logs
        ```
    """
    try:
        response_data, status_code = proxy_client.delete_logs()
        return JSONResponse(content=response_data, status_code=status_code)
    except Exception as e:
        logger.error(f"Erreur delete_logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))
