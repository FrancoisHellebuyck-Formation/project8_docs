# Feature Engineering

Ce document explique comment les features dérivées sont calculées automatiquement dans le projet.

## Principe

Le modèle ML utilise **des features calculées automatiquement** en plus des features de base saisies par l'utilisateur. L'utilisateur ne doit **jamais** saisir ces features dérivées - elles sont calculées par le système.

## Features de base (saisies par l'utilisateur)

L'utilisateur doit fournir uniquement les 14 features suivantes :

1. `AGE` - Âge du patient
2. `GENDER` - Genre (0 = Femme, 1 = Homme)
3. `SMOKING` - Fumeur (0 = Non, 1 = Oui)
4. `ALCOHOL CONSUMING` - Consommation d'alcool (0 = Non, 1 = Oui)
5. `PEER_PRESSURE` - Pression sociale (0 = Non, 1 = Oui)
6. `YELLOW_FINGERS` - Doigts jaunes (0 = Non, 1 = Oui)
7. `ANXIETY` - Anxiété (0 = Non, 1 = Oui)
8. `FATIGUE` - Fatigue (0 = Non, 1 = Oui)
9. `ALLERGY` - Allergie (0 = Non, 1 = Oui)
10. `WHEEZING` - Respiration sifflante (0 = Non, 1 = Oui)
11. `COUGHING` - Toux (0 = Non, 1 = Oui)
12. `SHORTNESS OF BREATH` - Essoufflement (0 = Non, 1 = Oui)
13. `SWALLOWING DIFFICULTY` - Difficulté à avaler (0 = Non, 1 = Oui)
14. `CHEST PAIN` - Douleur thoracique (0 = Non, 1 = Oui)

## Features dérivées (calculées automatiquement)

Le système calcule automatiquement les 14 features suivantes :

### 1. Interactions

- `SMOKING_x_AGE` - Interaction entre tabagisme et âge
- `SMOKING_x_ALCOHOL` - Combinaison tabac + alcool (booléen)

### 2. Scores de symptômes

- `RESPIRATORY_SYMPTOMS` - Symptômes respiratoires combinés (0-3)
- `TOTAL_SYMPTOMS` - Score total de tous les symptômes
- `SEVERE_SYMPTOMS` - Score de symptômes graves
- `BEHAVIORAL_RISK_SCORE` - Score de facteurs de risque comportementaux

### 3. Profils de risque

- `AGE_GROUP` - Catégorie d'âge (<50, 50-60, 60-70, 70+)
- `HIGH_RISK_PROFILE` - Profil à haut risque (homme + fumeur + âge > 60)
- `CANCER_TRIAD` - Triade classique du cancer (toux + douleur + essoufflement)

### 4. Transformations

- `AGE_SQUARED` - Âge au carré (relation non-linéaire)
- `SMOKER_WITH_RESP_SYMPTOMS` - Fumeur avec symptômes respiratoires
- `ADVANCED_SYMPTOMS` - Symptômes avancés (dysphagie + douleur)

### 5. Ratios

- `SYMPTOMS_PER_AGE` - Ratio symptômes / âge
- `RESP_SYMPTOM_RATIO` - Proportion de symptômes respiratoires

## Utilisation dans le code

### Exemple 1 : Prédiction simple

```python
from src.model import ModelLoader, Predictor

# Charger le modèle
loader = ModelLoader()
loader.load_model()

# Créer le predictor
predictor = Predictor()

# Données d'entrée (uniquement les features de base)
patient_data = {
    'AGE': 65,
    'GENDER': 1,
    'SMOKING': 1,
    'ALCOHOL CONSUMING': 1,
    'PEER_PRESSURE': 0,
    'YELLOW_FINGERS': 1,
    'ANXIETY': 0,
    'FATIGUE': 1,
    'ALLERGY': 0,
    'WHEEZING': 1,
    'COUGHING': 1,
    'SHORTNESS OF BREATH': 1,
    'SWALLOWING DIFFICULTY': 0,
    'CHEST PAIN': 1
}

# Les features dérivées sont calculées automatiquement
prediction = predictor.predict(patient_data)
print(f"Prédiction : {prediction}")

# Obtenir les probabilités
probabilities = predictor.predict_proba(patient_data)
print(f"Probabilités : {probabilities}")
```

### Exemple 2 : Obtenir la liste des features requises

```python
from src.model import Predictor

predictor = Predictor()

# Obtenir la liste des features à saisir
required_features = predictor.get_required_features()
print("Features requises :")
for feature in required_features:
    print(f"  - {feature}")
```

### Exemple 3 : Utiliser le FeatureEngineer directement

```python
from src.model import FeatureEngineer
import pandas as pd

# Créer le feature engineer
engineer = FeatureEngineer()

# Données de base
data = {
    'AGE': 65,
    'GENDER': 1,
    # ... autres features
}

# Calculer toutes les features (de base + dérivées)
complete_data = engineer.engineer_features(data)
print(complete_data.columns)
```

## Points importants

1. **Ne jamais demander les features dérivées à l'utilisateur** - Elles sont calculées automatiquement
2. **Toujours utiliser le Predictor** - Il applique automatiquement le feature engineering
3. **Cohérence** - Les mêmes transformations sont appliquées à l'entraînement et à la prédiction
4. **Validation** - Le système vérifie que toutes les features de base sont présentes

## Architecture

```
Données utilisateur (14 features)
        ↓
FeatureEngineer.engineer_features()
        ↓
Données complètes (28 features)
        ↓
Modèle ML
        ↓
Prédiction
```
