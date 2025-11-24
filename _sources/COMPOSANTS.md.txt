# Composants Technologiques de l'Application

Ce document liste l'ensemble des composants technologiques utilisés dans ce projet.

## Backend

- **Langage de programmation :** Python 3.13
- **Framework API :** FastAPI
- **Serveur ASGI :** Uvicorn
- **Validation des données :** Pydantic

## Frontend

- **Bibliothèque UI :** Gradio

## Modèle de Machine Learning

- **Bibliothèque ML :** Scikit-learn (implicite, via le modèle `.pkl`)

## Infrastructure & Base de Données

- **Base de données In-Memory (cache) :** Redis
- **Conteneurisation :** Docker, Docker Compose

## Qualité de Code & Tests

- **Tests :** Pytest
- **Couverture de code :** Pytest-cov
- **Linting :** flake8
- **Analyse de sécurité :** Bandit, Safety

## Tests de Performance

- **Tests de charge :** JMeter

## Analyse de Données

- **Analyse de drift :** Evidently AI

## Migration de Modèle

- **Format de modèle :** ONNX

## CI/CD

- **Intégration Continue :** GitHub Actions

## Gestion des dépendances

- **Gestionnaire de paquets :** pip, uv
- **Fichier de dépendances :** `pyproject.toml`

## Documentation

- **Générateur de documentation :** Sphinx (déduit de `conf.py` et `.rst` files)
- **Format :** Markdown, reStructuredText