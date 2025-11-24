"""
FastAPI app principal avec Gradio monté dessus.

Cette approche permet d'avoir à la fois:
1. Des endpoints REST FastAPI standard (accessibles via curl)
2. L'interface Gradio montée sur un chemin spécifique

Architecture:
- GET /api/health -> Endpoint FastAPI direct
- GET /api/predict -> Endpoint FastAPI direct
- GET / -> Interface Gradio
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import gradio as gr
import logging

from ..proxy.client import APIProxyClient

logger = logging.getLogger(__name__)

# Créer l'application FastAPI principale
app = FastAPI(
    title="ML Lung Cancer Prediction - Full Stack",
    description="FastAPI + Gradio UI avec accès REST direct",
    version="1.0.0"
)

# Créer le client proxy pour accéder à l'API backend
proxy_client = APIProxyClient()


# ===== ROUTES FASTAPI DIRECTES =====

@app.get("/api/health")
async def api_health():
    """
    Vérifie la santé de l'API backend.

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
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )


@app.get("/api/info")
async def api_info():
    """
    Récupère les informations de l'API backend.

    Example:
        ```bash
        curl https://YOUR-SPACE.hf.space/api/info
        ```
    """
    try:
        response_data, status_code = proxy_client.get_root()
        return JSONResponse(content=response_data, status_code=status_code)
    except Exception as e:
        logger.error(f"Erreur get_info: {e}")
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )


@app.post("/api/predict")
async def api_predict(patient_data: dict):
    """
    Effectue une prédiction de cancer du poumon.

    Args:
        patient_data: Dictionnaire avec les 14 features du patient

    Example:
        ```bash
        curl -X POST https://YOUR-SPACE.hf.space/api/predict \\
          -H "Content-Type: application/json" \\
          -d '{
            "AGE": 50, "GENDER": 1, "SMOKING": 1,
            "ALCOHOL CONSUMING": 0, "PEER_PRESSURE": 0,
            "YELLOW_FINGERS": 1, "ANXIETY": 0, "FATIGUE": 1,
            "ALLERGY": 0, "WHEEZING": 1, "COUGHING": 1,
            "SHORTNESS OF BREATH": 1, "SWALLOWING DIFFICULTY": 0,
            "CHEST PAIN": 1, "CHRONIC DISEASE": 0
          }'
        ```
    """
    try:
        response_data, status_code = proxy_client.post_predict(patient_data)
        return JSONResponse(content=response_data, status_code=status_code)
    except Exception as e:
        logger.error(f"Erreur predict: {e}")
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )


@app.post("/api/predict_proba")
async def api_predict_proba(patient_data: dict):
    """
    Récupère les probabilités de prédiction.

    Example:
        ```bash
        curl -X POST https://YOUR-SPACE.hf.space/api/predict_proba \\
          -H "Content-Type: application/json" \\
          -d '{"AGE": 50, ...}'
        ```
    """
    try:
        response_data, status_code = proxy_client.post_predict_proba(
            patient_data
        )
        return JSONResponse(content=response_data, status_code=status_code)
    except Exception as e:
        logger.error(f"Erreur predict_proba: {e}")
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )


@app.get("/api/logs")
async def api_logs(limit: int = 100, offset: int = 0):
    """
    Récupère les logs de l'API.

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
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )


@app.delete("/api/logs")
async def api_delete_logs():
    """
    Vide le cache Redis des logs.

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
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )


# ===== MONTER L'INTERFACE GRADIO =====

def create_full_app():
    """Crée l'app FastAPI complète avec Gradio monté."""
    from .app import create_interface

    # Créer l'interface Gradio
    gradio_app = create_interface()

    # Monter Gradio sur le chemin racine de l'app FastAPI
    # gr.mount_gradio_app retourne l'app FastAPI modifiée
    full_app = gr.mount_gradio_app(
        app,  # L'app FastAPI définie plus haut
        gradio_app,  # L'interface Gradio
        path="/"  # Monter sur la racine
    )

    logger.info("✅ Interface Gradio montée sur /")
    logger.info("✅ Endpoints REST API disponibles sur /api/*")

    return full_app


# Créer l'app complète
app = create_full_app()


if __name__ == "__main__":
    import uvicorn

    print("🚀 Lancement FastAPI + Gradio")
    print("📍 Interface Gradio: http://localhost:7860/")
    print("📍 API REST:")
    print("   - GET  /api/health")
    print("   - POST /api/predict")
    print("   - POST /api/predict_proba")
    print("   - GET  /api/logs")
    print("   - DELETE /api/logs")
    print("\n🔧 Test:")
    print("   curl http://localhost:7860/api/health")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=7860
    )
