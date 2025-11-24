"""
Configuration du logging avec Redis.

Ce module configure le logger Python standard pour qu'il puisse envoyer
des logs à la fois à la console (stdout) et à une liste Redis.
Le handler Redis est conçu pour être résilient aux erreurs de connexion.

Fonctionnalités:
- Configuration flexible du niveau de log.
- Double-logging (console et Redis) si Redis est disponible.
- Fallback automatique vers logging console seul si Redis est indisponible.
- Fonctions utilitaires pour interagir avec les logs Redis.
"""

import logging
from typing import Dict, List, Optional, Union

import redis

from ..config import settings


class RedisHandler(logging.Handler):
    """
    Handler de logging personnalisé pour stocker les logs dans une liste Redis.

    Les logs sont ajoutés à gauche (LPUSH) et la liste est taillée (LTRIM)
    pour ne pas dépasser une longueur maximale, agissant comme un buffer circulaire.

    Attributes:
        redis_client (redis.Redis): L'instance du client Redis à utiliser.
        key (str): La clé de la liste Redis où les logs sont stockés.
        max_length (int): Le nombre maximum de logs à conserver dans la liste.
    """

    def __init__(
        self,
        redis_client: redis.Redis,
        key: str,
        max_length: int = 1000
    ):
        """
        Initialise le handler Redis.

        Args:
            redis_client: Le client Redis pour communiquer avec le serveur.
            key: La clé de la liste Redis à utiliser pour le stockage des logs.
            max_length: Le nombre maximum de logs à conserver dans la liste.
        """
        super().__init__()
        self.redis_client = redis_client
        self.key = key
        self.max_length = max_length

    def emit(self, record: logging.LogRecord) -> None:
        """
        Formate et publie un enregistrement de log dans Redis.

        Le log formaté est ajouté à la liste avec `LPUSH`. La liste est
        ensuite taillée avec `LTRIM` pour maintenir une taille maximale.
        Toute exception Redis est gérée silencieusement pour ne pas
        interrompre l'application.

        Args:
            record: L'enregistrement de log à publier.
        """
        try:
            log_entry = self.format(record)
            self.redis_client.lpush(self.key, log_entry)
            self.redis_client.ltrim(self.key, 0, self.max_length - 1)
        except Exception:
            self.handleError(record)


def setup_logging(
    log_level: Optional[str] = None,
    redis_client: Optional[redis.Redis] = None
) -> logging.Logger:
    """
    Configure et retourne un logger pour l'application.

    Crée un logger "api" et y attache des handlers en fonction de la
    configuration. Si `LOGGING_HANDLER` est "redis", il tente d'ajouter
    un handler console et un handler Redis. En cas d'échec de connexion à
    Redis, il bascule en mode console uniquement.

    Cette fonction est idempotente : si le logger a déjà des handlers,
    elle le retourne sans modification.

    Args:
        log_level: Le niveau de log (ex: "INFO", "DEBUG"). Si non fourni,
                   utilise la valeur de `settings.LOG_LEVEL`.
        redis_client: Une instance optionnelle de client Redis. Si non
                      fournie, une nouvelle instance sera créée si nécessaire.

    Returns:
        L'instance du logger "api" configurée.
    """
    # Créer ou récupérer le logger
    logger = logging.getLogger("api")

    # Éviter d'ajouter plusieurs handlers
    if logger.handlers:
        return logger

    # Définir le niveau de log
    level = log_level or settings.LOG_LEVEL
    logger.setLevel(getattr(logging, level.upper()))

    # Format des logs
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Déterminer le handler à utiliser selon la configuration
    handler_type = settings.LOGGING_HANDLER.lower()

    if handler_type == "redis":
        # Mode Redis : console + redis
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, level.upper()))
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # Handler Redis
        try:
            if redis_client is None:
                redis_client = redis.Redis(
                    host=settings.REDIS_HOST,
                    port=settings.REDIS_PORT,
                    db=settings.REDIS_DB,
                    decode_responses=True
                )
                # Tester la connexion
                redis_client.ping()

            # Créer le handler Redis personnalisé
            redis_handler = RedisHandler(
                redis_client=redis_client,
                key=settings.REDIS_LOGS_KEY,
                max_length=settings.REDIS_LOGS_MAX_SIZE
            )
            redis_handler.setLevel(getattr(logging, level.upper()))
            redis_handler.setFormatter(formatter)
            logger.addHandler(redis_handler)

            logger.info(
                f"Logging configuré: redis "
                f"({settings.REDIS_HOST}:{settings.REDIS_PORT})"
            )

        except redis.ConnectionError as e:
            logger.warning(
                f"Impossible de se connecter à Redis : {str(e)}. "
                f"Utilisation du mode stdout uniquement."
            )
        except Exception as e:
            logger.warning(
                f"Erreur lors de la configuration du handler Redis : "
                f"{str(e)}. Utilisation du mode stdout uniquement."
            )

    else:
        # Mode stdout : console uniquement
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, level.upper()))
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        logger.info(f"Logging configuré: stdout (level={level})")

    return logger


def get_logger() -> logging.Logger:
    """
    Raccourci pour obtenir l'instance du logger "api".

    Returns:
        L'instance du logger partagé de l'application.
    """
    return logging.getLogger("api")


def get_redis_logs(
    limit: int = 100,
    offset: int = 0,
    redis_client: Optional[redis.Redis] = None
) -> Dict[str, Union[List[str], int]]:
    """
    Récupère les logs depuis Redis avec support de la pagination.

    Args:
        limit: Le nombre maximum de logs à retourner.
        offset: L'index de départ pour la récupération des logs.
        redis_client: Une instance optionnelle de client Redis.

    Returns:
        Un dictionnaire contenant les logs et les métadonnées de pagination.
        Exemple:
        {
            "logs": ["log_entry_1", "log_entry_2"],
            "total": 100,
            "offset": 0,
            "limit": 100
        }
        En cas d'erreur de connexion, retourne une liste de logs vide.
    """
    if redis_client is None:
        try:
            redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True
            )
            redis_client.ping()
        except redis.ConnectionError:
            return {"logs": [], "total": 0, "offset": offset, "limit": limit}

    try:
        # Obtenir le nombre total de logs
        total = redis_client.llen(settings.REDIS_LOGS_KEY)

        # Récupérer les logs avec offset
        logs = redis_client.lrange(
            settings.REDIS_LOGS_KEY,
            offset,
            offset + limit - 1
        )

        return {
            "logs": logs,
            "total": total,
            "offset": offset,
            "limit": limit
        }
    except Exception:
        return {"logs": [], "total": 0, "offset": offset, "limit": limit}


def clear_redis_logs(
    redis_client: Optional[redis.Redis] = None
) -> bool:
    """
    Supprime la clé de logs de Redis, vidant ainsi tous les logs.

    Args:
        redis_client: Une instance optionnelle de client Redis.

    Returns:
        True si la suppression a réussi, False sinon.
    """
    if redis_client is None:
        try:
            redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True
            )
            redis_client.ping()
        except redis.ConnectionError:
            return False

    try:
        redis_client.delete(settings.REDIS_LOGS_KEY)
        return True
    except Exception:
        return False


def is_redis_connected(
    redis_client: Optional[redis.Redis] = None
) -> bool:
    """
    Vérifie si la connexion à Redis est active.

    Tente d'exécuter une commande PING. Si elle réussit, la connexion
    est considérée comme active.

    Args:
        redis_client: Une instance optionnelle de client Redis.

    Returns:
        True si Redis est accessible, False sinon.
    """
    if redis_client is None:
        try:
            redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True
            )
        except Exception:
            return False

    try:
        redis_client.ping()
        return True
    except redis.ConnectionError:
        return False
