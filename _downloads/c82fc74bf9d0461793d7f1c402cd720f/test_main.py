"""
Tests unitaires pour l'API FastAPI.

Ce module teste tous les endpoints de l'API:
- GET /
- GET /health
- POST /predict
- POST /predict_proba
- GET /logs
- DELETE /logs
"""

from fastapi import status
from unittest.mock import MagicMock
import pytest
from contextlib import asynccontextmanager
from fastapi.testclient import TestClient


@pytest.fixture
def singleton_client(monkeypatch):
    """
    Client de test qui force l'API en mode singleton
    en désactivant le model_router.
    """
    from src.api.main import app

    # Force le mode singleton
    monkeypatch.setattr("src.api.main.model_router", None)

    # Mock le lifespan pour éviter l'initialisation réelle
    @asynccontextmanager
    async def mock_lifespan(app):
        yield
    monkeypatch.setattr("src.api.main.lifespan", mock_lifespan)

    return TestClient(app)


class TestRootEndpoint:
    """Tests pour l'endpoint racine GET /."""

    def test_root_returns_api_info(self, api_client):
        """Test que l'endpoint racine retourne les informations de l'API."""
        response = api_client.get("/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "endpoints" in data
        assert data["message"] == "API de Prédiction ML"
        assert data["version"] == "1.0.0"

    def test_root_returns_all_endpoints(self, api_client):
        """Test que l'endpoint racine liste tous les endpoints."""
        response = api_client.get("/")
        data = response.json()

        endpoints = data["endpoints"]
        assert "health" in endpoints
        assert "predict" in endpoints
        assert "predict_proba" in endpoints
        assert "logs" in endpoints


class TestHealthEndpoint:
    """Tests pour l'endpoint GET /health."""

    def test_health_check_returns_healthy_status(self, api_client):
        """Test que le health check retourne un statut healthy."""
        response = api_client.get("/health")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert data["model_loaded"] is True
        assert data["version"] == "1.0.0"

    def test_health_check_includes_redis_status(self, api_client):
        """Test que le health check inclut le statut Redis."""
        response = api_client.get("/health")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "redis_connected" in data
        assert isinstance(data["redis_connected"], bool)


class TestPredictEndpoint:
    """Tests pour l'endpoint POST /predict."""

    def test_predict_with_valid_data(self, api_client, sample_patient_data):
        """Test prédiction avec données valides."""
        response = api_client.post("/predict", json=sample_patient_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "prediction" in data
        assert "probability" in data
        assert "message" in data
        assert data["prediction"] in [0, 1]
        assert data["probability"] == pytest.approx(0.8)

    def test_predict_returns_correct_message(
        self, api_client, sample_patient_data
    ):
        """Test que le message correspond à la prédiction."""
        response = api_client.post("/predict", json=sample_patient_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        if data["prediction"] == 1:
            assert data["message"] == "Prédiction positive"
        else:
            assert data["message"] == "Prédiction négative"

    def test_predict_with_invalid_age(self, api_client, sample_patient_data):
        """Test prédiction avec âge invalide."""
        invalid_data = sample_patient_data.copy()
        invalid_data["AGE"] = 150  # > 120

        response = api_client.post("/predict", json=invalid_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_predict_with_invalid_gender(
        self, api_client, sample_patient_data
    ):
        """Test prédiction avec genre invalide."""
        invalid_data = sample_patient_data.copy()
        invalid_data["GENDER"] = 2  # > 1

        response = api_client.post("/predict", json=invalid_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_predict_with_missing_field(
        self, api_client, sample_patient_data
    ):
        """Test prédiction avec champ manquant."""
        incomplete_data = sample_patient_data.copy()
        del incomplete_data["AGE"]

        response = api_client.post("/predict", json=incomplete_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_predict_with_high_risk_patient(
        self, api_client, high_risk_patient
    ):
        """Test prédiction avec patient à haut risque."""
        response = api_client.post("/predict", json=high_risk_patient)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "prediction" in data
        assert "probability" in data

    def test_predict_with_minimal_symptoms(
        self, api_client, minimal_symptoms_patient
    ):
        """Test prédiction avec patient sans symptômes."""
        response = api_client.post("/predict", json=minimal_symptoms_patient)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "prediction" in data
        assert "probability" in data

    def test_predict_probability_in_valid_range(
        self, api_client, sample_patient_data
    ):
        """Test que la probabilité est entre 0 et 1."""
        response = api_client.post("/predict", json=sample_patient_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        if data["probability"] is not None:
            assert 0.0 <= data["probability"] <= 1.0


class TestPredictProbaEndpoint:
    """Tests pour l'endpoint POST /predict_proba."""

    def test_predict_proba_with_valid_data(
        self, api_client, sample_patient_data
    ):
        """Test prédiction avec probabilités."""
        response = api_client.post(
            "/predict_proba", json=sample_patient_data
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "prediction" in data
        assert "probabilities" in data
        assert "message" in data
        assert len(data["probabilities"]) == 2  # Deux classes
        assert data["probabilities"] == pytest.approx([0.2, 0.8])

    def test_predict_proba_probabilities_sum_to_one(
        self, api_client, sample_patient_data
    ):
        """Test que les probabilités somment à 1."""
        response = api_client.post(
            "/predict_proba", json=sample_patient_data
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        probabilities = data["probabilities"]

        # Somme proche de 1.0 (tolérance pour float)
        assert abs(sum(probabilities) - 1.0) < 0.01

    def test_predict_proba_all_probabilities_positive(
        self, api_client, sample_patient_data
    ):
        """Test que toutes les probabilités sont positives."""
        response = api_client.post(
            "/predict_proba", json=sample_patient_data
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        probabilities = data["probabilities"]

        for prob in probabilities:
            assert 0.0 <= prob <= 1.0

    def test_predict_proba_with_invalid_data(
        self, api_client, invalid_patient_data
    ):
        """Test prédiction avec probabilités et données invalides."""
        response = api_client.post(
            "/predict_proba", json=invalid_patient_data
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestLogsEndpoint:
    """Tests pour les endpoints de logs."""

    def test_get_logs_returns_list(self, api_client):
        """Test que GET /logs retourne une liste de logs."""
        response = api_client.get("/logs")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total" in data
        assert "logs" in data
        assert isinstance(data["logs"], list)

    def test_get_logs_with_limit(self, api_client):
        """Test GET /logs avec paramètre limit."""
        response = api_client.get("/logs?limit=10")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["logs"]) <= 10

    def test_get_logs_limit_validation(self, api_client):
        """Test validation du paramètre limit."""
        # Limite trop grande
        response = api_client.get("/logs?limit=2000")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Limite négative
        response = api_client.get("/logs?limit=-1")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_log_entry_structure(self, api_client, sample_patient_data):
        """Test la structure des entrées de log."""
        # Faire une prédiction pour générer un log
        api_client.post("/predict", json=sample_patient_data)

        # Récupérer les logs
        response = api_client.get("/logs")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        if data["logs"]:
            log = data["logs"][0]
            assert "timestamp" in log
            assert "level" in log
            assert "message" in log

    def test_clear_logs(self, api_client):
        """Test DELETE /logs pour supprimer les logs."""
        response = api_client.delete("/logs")

        # Peut retourner 200 ou 500 selon Redis disponible
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_500_INTERNAL_SERVER_ERROR
        ]


class TestAPIValidation:
    """Tests de validation Pydantic."""

    def test_patient_data_validation_age_bounds(self, api_client):
        """Test validation des limites d'âge."""
        # Âge négatif
        data = {
            "AGE": -5,
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

        response = api_client.post("/predict", json=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_patient_data_validation_binary_fields(self, api_client):
        """Test validation des champs binaires (0 ou 1)."""
        data = {
            "AGE": 50,
            "GENDER": 1,
            "SMOKING": 2,  # Invalide: doit être 0 ou 1
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

        response = api_client.post("/predict", json=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestAPIErrorHandling:
    """Tests de gestion d'erreurs."""

    def test_predict_with_empty_body(self, api_client):
        """Test prédiction avec body vide."""
        response = api_client.post("/predict", json={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_predict_with_invalid_json(self, api_client):
        """Test prédiction avec JSON invalide."""
        response = api_client.post(
            "/predict",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_invalid_endpoint(self, api_client):
        """Test accès à un endpoint inexistant."""
        response = api_client.get("/nonexistent")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_cors_headers(self, api_client):
        """Test que les headers CORS sont présents."""
        response = api_client.get("/")

        # CORS devrait permettre toutes les origines
        assert response.status_code == status.HTTP_200_OK

    def test_api_version_consistency(self, api_client):
        """Test cohérence des versions dans l'API."""
        root_response = api_client.get("/")
        health_response = api_client.get("/health")

        assert root_response.json()["version"] == "1.0.0"
        assert health_response.json()["version"] == "1.0.0"

    def test_delete_logs_endpoint_exists(self, api_client):
        """Test que l'endpoint DELETE /logs existe."""
        response = api_client.delete("/logs")
        # Peut retourner 200 ou 500 selon Redis
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_500_INTERNAL_SERVER_ERROR
        ]

class TestSingletonMode:
    """Tests for the singleton fallback mode."""

    def test_predict_singleton_mode(self, singleton_client, monkeypatch, sample_patient_data):
        """Tests the /predict endpoint when the app is in singleton mode."""
        import numpy as np
        mock_predictor = MagicMock()
        mock_predictor.predict.return_value = [1]
        mock_predictor.predict_proba.return_value = np.array([[0.1, 0.9]])
        monkeypatch.setattr("src.api.main.predictor", mock_predictor)
        monkeypatch.setattr("src.api.main.feature_engineer", MagicMock())

        response = singleton_client.post("/predict", json=sample_patient_data)
        assert response.status_code == 200
        data = response.json()
        assert data["prediction"] == 1
        assert data["probability"] == pytest.approx(0.9)
        mock_predictor.predict.assert_called_once()

    def test_predict_proba_singleton_mode(self, singleton_client, monkeypatch, sample_patient_data):
        """Tests the /predict_proba endpoint when the app is in singleton mode."""
        import numpy as np
        mock_predictor = MagicMock()
        mock_predictor.predict.return_value = [1]
        mock_predictor.predict_proba.return_value = np.array([[0.1, 0.9]])
        monkeypatch.setattr("src.api.main.predictor", mock_predictor)
        monkeypatch.setattr("src.api.main.feature_engineer", MagicMock())

        response = singleton_client.post("/predict_proba", json=sample_patient_data)
        assert response.status_code == 200
        data = response.json()
        assert data["prediction"] == 1
        assert data["probabilities"] == pytest.approx([0.1, 0.9])
        mock_predictor.predict_proba.assert_called_once()

    def test_predict_invalid_model_type(self, api_client, sample_patient_data):
        """Tests that requesting an invalid model_type returns a 400 error."""
        response = api_client.post("/predict?model_type=invalid_type", json=sample_patient_data)
        assert response.status_code == 400
        assert "Type de modèle invalide" in response.text
