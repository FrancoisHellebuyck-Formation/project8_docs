# Guide de Couverture de Tests - Project8

## 📋 Vue d'ensemble

Ce projet implémente un contrôle automatique de la couverture de tests pour garantir la qualité du code, particulièrement pour l'API qui est le composant critique du système.

## 🎯 Seuils de Couverture

### Couverture Globale
- **Seuil minimum**: 80%
- **Scope**: Tous les modules (`src/`)
- **Commande**: `make test-coverage`

### Couverture API (Critique)
- **Seuil minimum**: 85%
- **Scope**: Module API uniquement (`src/api/`)
- **Commande**: `make test-api-coverage`
- **Raison**: L'API est le composant le plus critique et doit être rigoureusement testée

## 🚀 Utilisation

### 1. Vérifier la couverture globale

```bash
# Lance tous les tests avec rapport de couverture
make test-coverage

# Ouvrir le rapport HTML
open htmlcov/index.html
```

### 2. Vérifier la couverture de l'API

```bash
# Lance les tests API avec vérification stricte (≥85%)
make test-api-coverage

# Ouvrir le rapport HTML spécifique à l'API
open htmlcov-api/index.html
```

### 3. Utiliser le script de vérification

```bash
# Vérification avec seuil par défaut (85%)
python scripts/check_api_coverage.py

# Vérification avec seuil personnalisé
python scripts/check_api_coverage.py --min-coverage 90

# Mode strict (échoue immédiatement)
python scripts/check_api_coverage.py --strict
```

## 🔧 Configuration

### pyproject.toml

```toml
[tool.coverage.run]
source = ["src"]
omit = [
    "src/ui/*",              # UI Gradio exclue
    "src/simulator/*",       # Simulateur exclu
    "src/logs_pipeline/*",   # Pipeline logs exclu
]

[tool.coverage.report]
fail_under = 80              # Seuil global
show_missing = true          # Afficher les lignes manquantes
precision = 2                # Précision à 2 décimales
```

### .github/workflows/cicd.yml

Le workflow CI/CD inclut plusieurs étapes de vérification :

1. **Tests globaux** avec couverture ≥80%
2. **Tests API** avec couverture ≥85%
3. **Upload vers Codecov** (optionnel)
4. **Affichage du résumé** dans les logs

## 🎓 Bonnes Pratiques

### 1. Avant de Committer

```bash
# Vérifier que tous les tests passent
make test

# Vérifier la couverture globale
make test-coverage

# Vérifier la couverture API si vous avez modifié src/api/
make test-api-coverage
```

### 2. Installation du Pre-commit Hook (Recommandé)

```bash
# Installer pre-commit
pip install pre-commit

# Installer les hooks
pre-commit install

# Tester manuellement
pre-commit run --all-files
```

Avec le hook installé, la couverture sera vérifiée **automatiquement** avant chaque commit.

### 3. Lors d'une Pull Request

Le CI/CD vérifiera automatiquement :
- ✅ Tous les tests passent
- ✅ Couverture globale ≥ 80%
- ✅ Couverture API ≥ 85%
- ✅ Flake8 compliance
- ✅ Aucun test manquant

## 📊 Interpréter les Résultats

### Exemple de Rapport Console

```
=================================================
📈 Résumé de la couverture de l'API
=================================================
Couverture totale API: 87.42%

Détail par fichier:
  main.py: 92.15%
  __init__.py: 100.00%
  routes.py: 85.30%
  middleware.py: 82.45%  ⚠️ (< 85%)
=================================================
```

### Fichiers avec Faible Couverture

Si un fichier a une couverture < 85%, vous verrez :

```
⚠️  FICHIERS AVEC COUVERTURE INSUFFISANTE:
------------------------------------------------------------
  • middleware.py: 82.45% (manque 2.55%)
------------------------------------------------------------
```

**Action requise** : Ajouter des tests pour `middleware.py`

## 🛠️ Ajouter des Tests

### Exemple : Augmenter la couverture de `middleware.py`

1. **Identifier les lignes non couvertes** :
   ```bash
   make test-api-coverage
   # Ouvrir htmlcov-api/index.html
   # Cliquer sur middleware.py
   # Les lignes rouges ne sont pas testées
   ```

2. **Créer ou compléter le fichier de test** :
   ```python
   # tests/test_middleware.py

   def test_middleware_fonction_non_testée():
       """Test de la fonction précédemment non couverte."""
       # Arrange
       ...
       # Act
       ...
       # Assert
       ...
   ```

3. **Vérifier l'amélioration** :
   ```bash
   make test-api-coverage
   # La couverture de middleware.py devrait augmenter
   ```

## 📝 Exclusions de Couverture

### Lignes à Exclure

Utilisez `# pragma: no cover` pour exclure des lignes :

```python
def fonction_debug():  # pragma: no cover
    """Fonction de debug non testée."""
    print("Debug info")
```

### Blocs à Exclure

```python
if __name__ == "__main__":  # pragma: no cover
    # Code de point d'entrée non testé
    main()
```

## 🚨 Que Faire si le CI/CD Échoue ?

### Erreur : "Couverture insuffisante"

```
❌ Tests API échoués ou couverture < 85%
```

**Solution** :
1. Exécuter localement `make test-api-coverage`
2. Identifier les fichiers avec faible couverture
3. Ajouter des tests pour ces fichiers
4. Relancer `make test-api-coverage`
5. Committer les nouveaux tests

### Erreur : "Tests échoués"

```
❌ Tests échoués
```

**Solution** :
1. Exécuter localement `make test`
2. Corriger les tests qui échouent
3. Vérifier que les changements n'ont pas cassé d'anciens tests
4. Relancer `make test`
5. Committer les corrections

## 📈 Objectifs de Couverture

### Court Terme
- ✅ Couverture globale : 80%
- ✅ Couverture API : 85%

### Moyen Terme
- 🎯 Couverture globale : 85%
- 🎯 Couverture API : 90%

### Long Terme
- 🚀 Couverture globale : 90%
- 🚀 Couverture API : 95%

## 🔗 Ressources

- [pytest-cov documentation](https://pytest-cov.readthedocs.io/)
- [Coverage.py documentation](https://coverage.readthedocs.io/)
- [pre-commit documentation](https://pre-commit.com/)

## 💡 Conseils

### 1. Test-Driven Development (TDD)

Écrivez les tests **avant** le code :
```bash
# 1. Créer le test (qui échoue)
# 2. Écrire le code (le test passe)
# 3. Vérifier la couverture
make test-api-coverage
```

### 2. Tests Unitaires vs Tests d'Intégration

- **Tests unitaires** : Testent une fonction/classe isolée
- **Tests d'intégration** : Testent plusieurs composants ensemble

Privilégiez les tests unitaires pour augmenter rapidement la couverture.

### 3. Mock et Fixtures

Utilisez `pytest` fixtures et `unittest.mock` pour isoler les tests :

```python
from unittest.mock import Mock, patch

@patch('src.api.main.get_redis_client')
def test_api_endpoint(mock_redis):
    mock_redis.return_value = Mock()
    # Test isolé sans dépendance Redis réelle
```

## 📞 Support

Si vous rencontrez des problèmes avec la couverture :
1. Vérifiez les logs du CI/CD
2. Exécutez `make test-api-coverage` localement
3. Consultez le rapport HTML pour les détails
4. Demandez de l'aide à l'équipe

---

**Dernière mise à jour** : 2025-01-21
**Mainteneur** : Project8 Team
