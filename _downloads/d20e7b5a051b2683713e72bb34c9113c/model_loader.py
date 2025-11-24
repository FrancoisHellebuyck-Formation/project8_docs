"""
Module pour le chargement du modèle ML avec pattern Singleton.

Le modèle est chargé une seule fois au démarrage de l'application
pour optimiser les performances.
"""

import pickle
from pathlib import Path
from typing import Any, Optional

from ..config import settings


class ModelLoader:
    """
    Classe Singleton pour charger le modèle ML.

    Le modèle est chargé une seule fois et réutilisé pour
    toutes les prédictions.
    """

    _instance: Optional["ModelLoader"] = None
    _model: Optional[Any] = None

    def __new__(cls) -> "ModelLoader":
        """
        Crée ou retourne l'instance unique de ModelLoader.

        Returns:
            ModelLoader: L'instance unique du loader.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load_model(self, model_path: Optional[str] = None) -> Any:
        """
        Charge le modèle ML depuis le fichier pickle.

        Args:
            model_path: Chemin vers le fichier du modèle.
                       Si None, utilise le chemin par défaut.

        Returns:
            Any: Le modèle chargé.

        Raises:
            FileNotFoundError: Si le fichier du modèle n'existe pas.
            Exception: Si le chargement du modèle échoue.
        """
        if self._model is not None:
            return self._model

        if model_path is None:
            # Utilise le chemin du modèle depuis les variables d'env
            model_path = Path(settings.MODEL_PATH)
            # Si le chemin est relatif, le résoudre depuis la racine
            if not model_path.is_absolute():
                project_root = Path(__file__).parent.parent.parent
                model_path = project_root / model_path
        else:
            model_path = Path(model_path)

        if not model_path.exists():
            raise FileNotFoundError(
                f"Le fichier du modèle n'existe pas : {model_path}"
            )

        try:
            with open(model_path, "rb") as f:
                self._model = pickle.load(f)
            print(f"Modèle chargé avec succès depuis {model_path}")
            return self._model
        except Exception as e:
            raise Exception(
                f"Erreur lors du chargement du modèle : {str(e)}"
            ) from e

    @property
    def model(self) -> Any:
        """
        Retourne le modèle chargé.

        Returns:
            Any: Le modèle ML.

        Raises:
            RuntimeError: Si le modèle n'a pas été chargé.
        """
        if self._model is None:
            raise RuntimeError(
                "Le modèle n'a pas été chargé. "
                "Appelez load_model() d'abord."
            )
        return self._model

    def is_loaded(self) -> bool:
        """
        Vérifie si le modèle est chargé.

        Returns:
            bool: True si le modèle est chargé, False sinon.
        """
        return self._model is not None
