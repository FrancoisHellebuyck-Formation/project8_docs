ML API Project Documentation
============================

Bienvenue dans la documentation du projet ML API - OpenClassrooms Project 8.

Ce projet est une infrastructure MLOps complète incluant :

- Une API REST FastAPI pour servir un modèle de machine learning
- Un modèle de prédiction de cancer du poumon
- Une interface utilisateur Gradio
- Un système de logging avec Redis
- Un pipeline de collecte de logs avec Elasticsearch
- Un simulateur de charge et de drift

.. toctree::
   :maxdepth: 2
   :caption: Contenu:

   readme

.. toctree::
   :maxdepth: 2
   :caption: Modules API:

   modules/api
   modules/model
   modules/ui
   modules/simulator
   modules/logs_pipeline

.. toctree::
   :maxdepth: 2
   :caption: Guides et Documentation:

   guides/docker
   guides/scripts
   guides/model
   guides/proxy
   guides/jmeter

.. toctree::
   :maxdepth: 2
   :caption: Architecture:

   architecture/architecture
   architecture/pipeline

Vue d'ensemble de l'Architecture
---------------------------------

Le projet est organisé en plusieurs modules :

API Module
~~~~~~~~~~
L'API FastAPI expose les endpoints pour faire des prédictions et gérer les logs.

Model Module
~~~~~~~~~~~~
Gestion du modèle ML avec support pour sklearn et ONNX, pattern Singleton et pool de modèles.

UI Module
~~~~~~~~~
Interface utilisateur Gradio pour interagir avec l'API.

Simulator Module
~~~~~~~~~~~~~~~~
Simulateur de charge et de data drift pour tester la robustesse du modèle.

Logs Pipeline Module
~~~~~~~~~~~~~~~~~~~~
Pipeline de collecte et d'indexation des logs dans Elasticsearch.

Indices et tables
=================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
