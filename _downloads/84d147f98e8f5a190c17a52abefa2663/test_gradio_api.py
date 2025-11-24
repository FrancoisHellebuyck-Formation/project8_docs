#!/usr/bin/env python3
"""
Script de test pour les endpoints Gradio API (compatibles HF Spaces).

Ce script teste les endpoints via l'API native de Gradio qui fonctionne
aussi bien en local que sur Hugging Face Spaces.

Usage:
    # Local (par défaut)
    python test_gradio_api.py

    # HuggingFace Spaces (public)
    GRADIO_URL=https://francoisformation-oc-project8.hf.space python test_gradio_api.py

    # HuggingFace Spaces (privé - nécessite un token)
    HF_TOKEN=your_token GRADIO_URL=https://francoisformation-oc-project8.hf.space python test_gradio_api.py

    # Via Makefile
    make test-gradio-api-local
    make test-gradio-api-hf
"""

import json
import os

from gradio_client import Client

# Configuration: priorité à la variable d'environnement GRADIO_URL
GRADIO_URL = os.environ.get(
    "GRADIO_URL",
    "http://localhost:7860"  # Valeur par défaut: local
)

# Token HuggingFace pour les Spaces privés (optionnel)
HF_TOKEN = os.environ.get("HF_TOKEN", None)

# Payload de test
test_payload = {
    "AGE": 65,
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
    "CHRONIC DISEASE": 0,
}


def test_health():
    """Test de l'endpoint health via Gradio API."""
    print("\n" + "=" * 60)
    print("TEST: Gradio API - Health Check")
    print("=" * 60)

    try:
        client = Client(GRADIO_URL, hf_token=HF_TOKEN)
        result = client.predict(api_name="/health")
        print("Status: ✅ SUCCESS")
        print(f"Response: {json.dumps(result, indent=2)}")
        return True
    except Exception as e:
        print("Status: ❌ FAIL")
        print(f"Error: {e}")
        return False


def test_predict_api():
    """Test de l'endpoint predict via Gradio API."""
    print("\n" + "=" * 60)
    print("TEST: Gradio API - Predict")
    print("=" * 60)

    try:
        client = Client(GRADIO_URL, hf_token=HF_TOKEN)
        result = client.predict(test_payload, api_name="/predict_api")
        print("Status: ✅ SUCCESS")
        print(f"Payload: {json.dumps(test_payload, indent=2)}")
        print(f"Response: {json.dumps(result, indent=2)}")
        return True
    except Exception as e:
        print("Status: ❌ FAIL")
        print(f"Error: {e}")
        return False


def test_predict_proba_api():
    """Test de l'endpoint predict_proba via Gradio API."""
    print("\n" + "=" * 60)
    print("TEST: Gradio API - Predict Proba")
    print("=" * 60)

    try:
        client = Client(GRADIO_URL, hf_token=HF_TOKEN)
        result = client.predict(test_payload, api_name="/predict_proba_api")
        print("Status: ✅ SUCCESS")
        print(f"Response: {json.dumps(result, indent=2)}")
        return True
    except Exception as e:
        print("Status: ❌ FAIL")
        print(f"Error: {e}")
        return False


def test_logs_api():
    """Test de l'endpoint logs via Gradio API."""
    print("\n" + "=" * 60)
    print("TEST: Gradio API - Logs")
    print("=" * 60)

    try:
        client = Client(GRADIO_URL, hf_token=HF_TOKEN)
        result = client.predict(10, api_name="/logs_api")
        print("Status: ✅ SUCCESS")
        print(f"Response (logs count): {len(result.get('logs', []))}")
        print(f"Response (extrait): {json.dumps(result, indent=2)[:500]}...")
        return True
    except Exception as e:
        print("Status: ❌ FAIL")
        print(f"Error: {e}")
        return False


def main():
    """Exécute tous les tests."""
    print("\n🧪 Tests des endpoints Gradio API")
    print(f"URL: {GRADIO_URL}")

    if HF_TOKEN:
        print("🔐 Token HuggingFace: Configuré (Space privé)")
    else:
        print("🔓 Token HuggingFace: Non configuré (Space public ou local)")

    if "localhost" in GRADIO_URL or "127.0.0.1" in GRADIO_URL:
        print("\nAssurez-vous que:")
        print("1. L'API FastAPI tourne sur http://localhost:8000")
        print("2. L'interface Gradio tourne sur http://localhost:7860")
        print("3. Redis est accessible")
    elif "hf.space" in GRADIO_URL or "huggingface" in GRADIO_URL:
        print("\n📍 Test sur HuggingFace Spaces")
        if not HF_TOKEN:
            print("⚠️  Si le Space est privé, définissez HF_TOKEN")
    else:
        print("\n📍 Test sur une URL personnalisée")

    results = {
        "Health": test_health(),
        "Predict": test_predict_api(),
        "Predict Proba": test_predict_proba_api(),
        "Logs": test_logs_api(),
    }

    # Résumé
    print("\n" + "=" * 60)
    print("RÉSUMÉ DES TESTS")
    print("=" * 60)

    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:20} : {status}")

    total = len(results)
    passed = sum(results.values())
    print(f"\nRésultat: {passed}/{total} tests réussis")

    if passed == total:
        print("\n🎉 Tous les tests ont réussi !")
        print("\n📍 Pour tester sur HF Spaces, utilisez make test-gradio-api-hf")
        return 0
    else:
        print("\n⚠️ Certains tests ont échoué")
        return 1


if __name__ == "__main__":
    exit(main())
