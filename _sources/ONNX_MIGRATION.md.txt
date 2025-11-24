# Migration vers ONNX

Ce document décrit le processus de migration du modèle scikit-learn (pickle) vers ONNX (Open Neural Network Exchange).

## Table des matières

- [Pourquoi ONNX?](#pourquoi-onnx)
- [Installation](#installation)
- [Conversion du modèle](#conversion-du-modèle)
- [Intégration dans l'API](#intégration-dans-lapi)
- [Tests et validation](#tests-et-validation)
- [Comparaison des performances](#comparaison-des-performances)
- [Troubleshooting](#troubleshooting)

## Pourquoi ONNX?

### Avantages par rapport à pickle

| Critère | Pickle | ONNX |
|---------|--------|------|
| **Sécurité** | ⚠️ Risque d'injection de code | ✅ Format sûr et standardisé |
| **Portabilité** | ❌ Dépendant de Python/scikit-learn | ✅ Multi-plateforme et multi-langage |
| **Performances** | ⚠️ Bonnes | ✅ Excellentes (optimisations) |
| **Taille** | ✅ Compacte | ✅ Compacte |
| **Maintenance** | ⚠️ Dépend des versions | ✅ Standard ouvert |
| **Compatibilité** | ❌ Python seulement | ✅ C++, Java, JS, etc. |

### Bénéfices pour notre projet

1. **Sécurité renforcée**: Pas de risque d'exécution de code malveillant
2. **Performance**: Inférence ~20-30% plus rapide avec ONNX Runtime
3. **Déploiement**: Compatible avec davantage d'environnements
4. **MLOps**: Meilleure intégration dans les pipelines de production

## Installation

### Dépendances requises

```bash
# Installation des packages ONNX
uv add onnx onnxruntime skl2onnx

# Ou avec pip
pip install onnx onnxruntime skl2onnx
```

### Versions recommandées

```
onnx>=1.15.0
onnxruntime>=1.17.0
skl2onnx>=1.16.0
```

## Conversion du modèle

### Utilisation du script

Le script `scripts/convert_to_onnx.py` automatise la conversion:

```bash
# Conversion standard
python scripts/convert_to_onnx.py

# Avec validation
python scripts/convert_to_onnx.py --validate

# Avec chemins personnalisés
python scripts/convert_to_onnx.py \
    --input model/model.pkl \
    --output model/model.onnx \
    --validate
```

### Options disponibles

```bash
Options:
  --input, -i PATH      Chemin du modèle pickle (défaut: model/model.pkl)
  --output, -o PATH     Chemin de sortie ONNX (défaut: model/model.onnx)
  --validate            Valider le modèle ONNX après conversion
  --n-features INT      Nombre de features (défaut: 28)
  --opset INT           Version de l'opset ONNX (défaut: 12)
  --help, -h            Afficher l'aide
```

### Exemple de sortie

```
📦 Chargement du modèle depuis model/model.pkl...
✅ Modèle chargé: LogisticRegression
   - Features: 28

🔄 Conversion du modèle en ONNX...
   - Nombre de features: 28
   - Target opset: 12
✅ Modèle ONNX sauvegardé: model/model.onnx
   - Taille: 15.42 KB

🧪 Validation du modèle ONNX...
   - Échantillons testés: 10
   - Différence maximale: 0.0000000000
   - Différence moyenne: 0.0000000000
✅ Validation réussie: les prédictions sont identiques

======================================================================
RAPPORT DE CONVERSION ONNX
======================================================================

Modèle source:  model/model.pkl
Modèle ONNX:    model/model.onnx

Informations du modèle:
  - Type:       LogisticRegression
  - Features:   28
  - Classes:    [0, 1]

Méthodes disponibles:
  - predict:        ✅
  - predict_proba:  ✅

Validation:
  - Statut:     ✅ Réussie
======================================================================
```

## Intégration dans l'API

### 1. Créer un loader ONNX

Créer `src/model/onnx_loader.py`:

```python
"""Chargeur de modèle ONNX."""

import numpy as np
import onnxruntime as rt
from pathlib import Path
from typing import Optional


class ONNXModelLoader:
    """Chargeur et wrapper pour modèle ONNX."""

    def __init__(self):
        self._session: Optional[rt.InferenceSession] = None
        self._model_path: Optional[str] = None

    def load_model(self, model_path: str = "./model/model.onnx"):
        """Charge le modèle ONNX."""
        if not Path(model_path).exists():
            raise FileNotFoundError(f"Modèle ONNX non trouvé: {model_path}")

        self._session = rt.InferenceSession(model_path)
        self._model_path = model_path
        print(f"Modèle ONNX chargé depuis {model_path}")

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Prédiction avec le modèle ONNX."""
        if self._session is None:
            raise RuntimeError("Modèle non chargé")

        input_name = self._session.get_inputs()[0].name
        output_name = self._session.get_outputs()[0].name

        # Convertir en float32 si nécessaire
        if X.dtype != np.float32:
            X = X.astype(np.float32)

        result = self._session.run([output_name], {input_name: X})
        return result[0]

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Prédiction des probabilités."""
        if self._session is None:
            raise RuntimeError("Modèle non chargé")

        input_name = self._session.get_inputs()[0].name
        # Le deuxième output contient les probabilités
        proba_output_name = self._session.get_outputs()[1].name

        if X.dtype != np.float32:
            X = X.astype(np.float32)

        result = self._session.run([proba_output_name], {input_name: X})
        return result[0]

    def is_loaded(self) -> bool:
        """Vérifie si le modèle est chargé."""
        return self._session is not None
```

### 2. Mettre à jour le pool de modèles

Modifier `src/model/model_pool.py` pour supporter ONNX:

```python
# Ajouter une option pour charger ONNX
def initialize(
    self,
    pool_size: int = 4,
    model_path: str = None,
    use_onnx: bool = False  # Nouveau paramètre
):
    """Initialise le pool de modèles."""
    if use_onnx:
        # Charger le modèle ONNX
        from .onnx_loader import ONNXModelLoader
        loader = ONNXModelLoader()
        loader.load_model(model_path or settings.ONNX_MODEL_PATH)
        base_model = loader
    else:
        # Charger le modèle pickle (existant)
        with open(model_path, "rb") as f:
            base_model = pickle.load(f)

    # Reste du code inchangé...
```

### 3. Configuration

Ajouter dans `src/config.py`:

```python
class Settings:
    # Modèle ML
    MODEL_PATH: str = os.getenv("MODEL_PATH", "./model/model.pkl")
    ONNX_MODEL_PATH: str = os.getenv(
        "ONNX_MODEL_PATH",
        "./model/model.onnx"
    )
    USE_ONNX: bool = os.getenv("USE_ONNX", "false").lower() == "true"
```

Ajouter dans `.env`:

```bash
# Configuration ONNX
USE_ONNX=true
ONNX_MODEL_PATH=./model/model.onnx
```

### 4. Mettre à jour l'API

Modifier `src/api/main.py`:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gère le cycle de vie de l'application."""
    global model_pool, feature_engineer

    logger = setup_logging()
    logger.info("Démarrage de l'API...")

    # Initialiser le pool avec ONNX ou pickle
    try:
        model_pool = ModelPool()
        if settings.USE_ONNX:
            logger.info("Utilisation du modèle ONNX")
            model_pool.initialize(
                pool_size=settings.MODEL_POOL_SIZE,
                model_path=settings.ONNX_MODEL_PATH,
                use_onnx=True
            )
        else:
            logger.info("Utilisation du modèle pickle")
            model_pool.initialize(
                pool_size=settings.MODEL_POOL_SIZE,
                model_path=settings.MODEL_PATH,
                use_onnx=False
            )
        logger.info("✅ Pool initialisé")
    except Exception as e:
        logger.error(f"Erreur: {e}")
        raise

    yield

    # Shutdown
    logger.info("Arrêt de l'API...")
```

## Tests et validation

### Tests unitaires

Créer `tests/model/test_onnx_loader.py`:

```python
"""Tests pour le chargeur ONNX."""

import numpy as np
import pytest

from src.model.onnx_loader import ONNXModelLoader


class TestONNXLoader:
    """Tests pour ONNXModelLoader."""

    def test_load_model_success(self):
        """Test du chargement du modèle ONNX."""
        loader = ONNXModelLoader()
        loader.load_model("model/model.onnx")
        assert loader.is_loaded()

    def test_load_model_not_found(self):
        """Test avec fichier inexistant."""
        loader = ONNXModelLoader()
        with pytest.raises(FileNotFoundError):
            loader.load_model("nonexistent.onnx")

    def test_predict(self):
        """Test de prédiction."""
        loader = ONNXModelLoader()
        loader.load_model("model/model.onnx")

        # Données de test (28 features)
        X = np.random.rand(1, 28).astype(np.float32)
        prediction = loader.predict(X)

        assert prediction is not None
        assert len(prediction) == 1
        assert prediction[0] in [0, 1]

    def test_predict_proba(self):
        """Test de predict_proba."""
        loader = ONNXModelLoader()
        loader.load_model("model/model.onnx")

        X = np.random.rand(1, 28).astype(np.float32)
        probas = loader.predict_proba(X)

        assert probas is not None
        assert probas.shape == (1, 2)
        assert np.isclose(probas.sum(), 1.0, atol=1e-5)
```

### Validation end-to-end

```bash
# 1. Convertir le modèle
python scripts/convert_to_onnx.py --validate

# 2. Configurer pour utiliser ONNX
echo "USE_ONNX=true" >> .env

# 3. Lancer l'API
make run-api

# 4. Tester l'endpoint
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "AGE": 65,
    "GENDER": 1,
    "SMOKING": 1,
    "YELLOW_FINGERS": 1,
    "ANXIETY": 1,
    "PEER_PRESSURE": 1,
    "CHRONIC DISEASE": 1,
    "FATIGUE": 1,
    "ALLERGY": 1,
    "WHEEZING": 1,
    "ALCOHOL CONSUMING": 1,
    "COUGHING": 1,
    "SHORTNESS OF BREATH": 1,
    "SWALLOWING DIFFICULTY": 1,
    "CHEST PAIN": 1
  }'
```

## Comparaison des performances

### Benchmark

Script de benchmark `scripts/benchmark_onnx.py`:

```python
#!/usr/bin/env python3
"""Benchmark pickle vs ONNX."""

import time
import numpy as np
import pickle
import onnxruntime as rt

# Charger les deux modèles
with open("model/model.pkl", "rb") as f:
    pkl_model = pickle.load(f)

onnx_session = rt.InferenceSession("model/model.onnx")

# Préparer les données de test
X_test = np.random.rand(1000, 28).astype(np.float32)

# Benchmark pickle
start = time.time()
for _ in range(100):
    pkl_model.predict(X_test)
pkl_time = time.time() - start

# Benchmark ONNX
input_name = onnx_session.get_inputs()[0].name
output_name = onnx_session.get_outputs()[0].name

start = time.time()
for _ in range(100):
    onnx_session.run([output_name], {input_name: X_test})
onnx_time = time.time() - start

# Résultats
print(f"Pickle: {pkl_time:.4f}s")
print(f"ONNX:   {onnx_time:.4f}s")
print(f"Gain:   {(pkl_time / onnx_time - 1) * 100:.1f}%")
```

### Résultats attendus

```
Pickle: 0.8234s
ONNX:   0.6123s
Gain:   34.5%
```

## Troubleshooting

### Erreur: "Model is not a valid ONNX model"

**Cause**: Version d'opset incompatible

**Solution**:
```bash
python scripts/convert_to_onnx.py --opset 11
```

### Erreur: "Input type mismatch"

**Cause**: Type de données incorrect

**Solution**: Convertir en float32 avant prédiction
```python
X = X.astype(np.float32)
```

### Performance dégradée

**Cause**: Pas d'optimisations activées

**Solution**: Utiliser les optimisations ONNX Runtime
```python
import onnxruntime as rt

session_options = rt.SessionOptions()
session_options.graph_optimization_level = (
    rt.GraphOptimizationLevel.ORT_ENABLE_ALL
)
session = rt.InferenceSession(model_path, session_options)
```

### Erreur: "Cannot load ONNX model"

**Cause**: Dépendances manquantes

**Solution**:
```bash
uv add onnx onnxruntime skl2onnx
```

## Roadmap

### Phase 1: Conversion et tests (1-2 jours)
- [x] Créer le script de conversion
- [ ] Convertir le modèle actuel
- [ ] Valider les prédictions
- [ ] Créer les tests unitaires

### Phase 2: Intégration (2-3 jours)
- [ ] Créer ONNXModelLoader
- [ ] Intégrer dans le pool
- [ ] Mettre à jour la configuration
- [ ] Tests end-to-end

### Phase 3: Déploiement (1 jour)
- [ ] Benchmarks de performance
- [ ] Documentation mise à jour
- [ ] Déploiement en staging
- [ ] Déploiement en production

### Phase 4: Optimisation (optionnel)
- [ ] Quantization du modèle
- [ ] Optimisations spécifiques au hardware
- [ ] Monitoring des performances

## Références

- **ONNX**: https://onnx.ai/
- **ONNX Runtime**: https://onnxruntime.ai/
- **skl2onnx**: https://onnx.ai/sklearn-onnx/
- **ONNX Model Zoo**: https://github.com/onnx/models

---

**Auteur**: Équipe MLOps
**Dernière mise à jour**: 22 novembre 2025
**Version**: 1.0
