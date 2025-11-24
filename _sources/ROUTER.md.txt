# Documentation du Routeur de Modèles (ModelRouter)

Le `ModelRouter` est un composant central de l'architecture API qui gère la sélection et la distribution des modèles de Machine Learning. Il implémente un design pattern **Singleton**, garantissant qu'une seule instance du routeur existe à travers l'application, et le **Strategy Pattern** pour permettre le choix dynamique entre différents types de modèles.

Son rôle principal est de :
1.  **Enregistrer et gérer** plusieurs pools de modèles (par exemple, pour les modèles scikit-learn et les modèles ONNX).
2.  **Permettre la sélection** d'un type de modèle spécifique pour une prédiction.
3.  **Définir un type de modèle par défaut** à utiliser si aucun n'est explicitement spécifié.
4.  **Fournir un mécanisme sécurisé** pour acquérir et relâcher les instances de modèle via un gestionnaire de contexte.

## Principes de Fonctionnement

### Types de Modèles Supportés

Le `ModelRouter` utilise l'énumération `ModelType` pour distinguer les types de modèles :
-   `SKLEARN`: Pour les modèles entraînés avec la bibliothèque scikit-learn, généralement sauvegardés au format Pickle.
-   `ONNX`: Pour les modèles optimisés au format ONNX (Open Neural Network Exchange), qui sont exécutés via le runtime ONNX (onnxruntime).

### Gestion des Pools de Modèles

Chaque type de modèle est associé à un `ModelPool` correspondant. Un `ModelPool` est responsable de maintenir un ensemble d'instances de son modèle, permettant ainsi de gérer les requêtes de prédiction concurrentes de manière efficace et thread-safe.

Lors de l'initialisation de l'API (dans la fonction `lifespan` de `src/api/main.py`), le `ModelRouter` est configuré :
-   Un `ModelPool` est créé et initialisé pour les modèles `SKLEARN`, chargeant le modèle `.pkl` spécifié dans la configuration.
-   Si l'activation d'ONNX est configurée (`settings.ENABLE_ONNX` à `True`), un second `ModelPool` est créé et initialisé pour les modèles `ONNX`, chargeant le modèle `.onnx` correspondant.

### Sélection et Routage des Modèles

Les requêtes de prédiction peuvent spécifier le type de modèle qu'elles souhaitent utiliser via un paramètre (`model_type`). Si aucun type n'est spécifié, le `ModelRouter` utilise le type par défaut configuré.

Pour acquérir une instance de modèle, l'API utilise un gestionnaire de contexte (`ModelContextManager`) fourni par le routeur :

```python
async with model_router.acquire_model(requested_type) as model_instance:
    # Utiliser model_instance pour effectuer la prédiction
    predictions = model_instance.predict(data)
```

Ce gestionnaire de contexte garantit que :
1.  Une instance de modèle est acquise du pool approprié avant d'effectuer la prédiction.
2.  L'instance de modèle est correctement libérée et retournée au pool après utilisation, même en cas d'erreur.

### Statistiques et Surveillance

Le `ModelRouter` permet également de récupérer des statistiques sur l'état de chaque pool de modèles, incluant la taille du pool, le nombre d'instances disponibles, et des métriques d'utilisation. Ces informations sont accessibles via l'endpoint `/pool/stats`.

## Intégration

Le `ModelRouter` est initialisé et configuré au démarrage de l'application FastAPI, comme illustré dans la fonction `lifespan` de `src/api/main.py`. Il est ensuite utilisé par les endpoints `/predict` et `/predict_proba` pour acheminer les requêtes vers le bon modèle.

## Exemples d'utilisation avec cURL

Voici des exemples de requêtes `curl` pour interroger l'API en spécifiant le type de modèle. Remplacez `http://localhost:8000` par l'URL de votre API si elle est déployée ailleurs.

### Prédiction avec le modèle scikit-learn

Pour forcer l'utilisation du modèle `scikit-learn`, utilisez le paramètre `model_type=sklearn`.

```bash
curl -X POST "http://localhost:8000/predict?model_type=sklearn" \
-H "Content-Type: application/json" \
-d '{
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
    "CHRONIC DISEASE": 0
}'
```

### Prédiction avec le modèle ONNX

Pour forcer l'utilisation du modèle `ONNX`, utilisez le paramètre `model_type=onnx`.

```bash
curl -X POST "http://localhost:8000/predict?model_type=onnx" \
-H "Content-Type: application/json" \
-d '{
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
    "CHRONIC DISEASE": 0
}'
```

### Prédiction avec le modèle par défaut

Si le paramètre `model_type` est omis, le `ModelRouter` utilisera le modèle configuré par défaut.

```bash
curl -X POST "http://localhost:8000/predict" \
-H "Content-Type: application/json" \
-d '{
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
    "CHRONIC DISEASE": 0
}'
```