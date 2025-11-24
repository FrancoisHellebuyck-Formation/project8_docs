"""
Module de monitoring des performances d'inférence.

Utilise cProfile pour mesurer les performances du modèle ML.
Les métriques collectées incluent :
- CPU time
- RAM usage
- Inference time
- Latency
- Throughput

Le monitoring peut être activé/désactivé via la variable d'environnement
ENABLE_PERFORMANCE_MONITORING.
"""

import cProfile
import logging
import pstats
import time
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Optional, Dict, Any
import psutil
import os

from src.config import settings

# Utiliser le logger "api" configuré avec Redis/stdout
logger = logging.getLogger("api")


@dataclass
class PerformanceMetrics:
    """Métriques de performance d'une inférence."""
    inference_time_ms: float
    cpu_time_ms: float
    memory_mb: float
    memory_delta_mb: float
    function_calls: int
    top_functions: list[Dict[str, Any]]


class PerformanceMonitor:
    """
    Moniteur de performances pour l'inférence du modèle.

    Utilise cProfile pour profiler l'exécution et psutil pour
    mesurer l'utilisation des ressources système.
    """

    def __init__(self):
        """Initialise le moniteur de performances."""
        self.enabled = settings.ENABLE_PERFORMANCE_MONITORING
        self._profiler: Optional[cProfile.Profile] = None
        self._start_time: float = 0
        self._start_memory: float = 0
        self._process = psutil.Process(os.getpid())

    @contextmanager
    def profile(self):
        """
        Context manager pour profiler une section de code.

        Yields:
            None

        Example:
            with monitor.profile():
                result = model.predict(data)
        """
        if not self.enabled:
            yield
            return

        # Mesures initiales
        self._start_time = time.perf_counter()
        self._start_memory = self._get_memory_usage()

        # Créer et démarrer le profiler
        self._profiler = cProfile.Profile()
        self._profiler.enable()

        try:
            yield
        finally:
            # Arrêter le profiler
            self._profiler.disable()

    def get_metrics(self) -> Optional[PerformanceMetrics]:
        """
        Récupère les métriques de performance après le profiling.

        Returns:
            PerformanceMetrics ou None si le monitoring est désactivé
        """
        if not self.enabled or self._profiler is None:
            return None

        # Mesures finales
        end_time = time.perf_counter()
        end_memory = self._get_memory_usage()

        # Temps d'inférence
        inference_time_ms = (end_time - self._start_time) * 1000

        # Utilisation mémoire
        memory_mb = end_memory
        memory_delta_mb = end_memory - self._start_memory

        # Analyser les stats du profiler
        stats = pstats.Stats(self._profiler)
        stats.strip_dirs()
        stats.sort_stats('cumulative')

        # Compter le nombre total d'appels de fonction
        function_calls = stats.total_calls

        # Extraire le CPU time total
        cpu_time_ms = sum(
            stat[2] for stat in stats.stats.values()
        ) * 1000

        # Extraire les top fonctions (top 5)
        top_functions = self._extract_top_functions(stats, limit=5)

        return PerformanceMetrics(
            inference_time_ms=inference_time_ms,
            cpu_time_ms=cpu_time_ms,
            memory_mb=memory_mb,
            memory_delta_mb=memory_delta_mb,
            function_calls=function_calls,
            top_functions=top_functions
        )

    def _get_memory_usage(self) -> float:
        """
        Récupère l'utilisation mémoire actuelle du processus en MB.

        Returns:
            float: Mémoire utilisée en MB
        """
        return self._process.memory_info().rss / (1024 * 1024)

    def _extract_top_functions(
        self,
        stats: pstats.Stats,
        limit: int = 5
    ) -> list[Dict[str, Any]]:
        """
        Extrait les fonctions les plus coûteuses.

        Args:
            stats: Statistiques du profiler
            limit: Nombre de fonctions à extraire

        Returns:
            Liste de dictionnaires avec les infos des fonctions
        """
        top_functions = []

        # Trier par temps cumulatif
        sorted_stats = sorted(
            stats.stats.items(),
            key=lambda x: x[1][3],  # cumulative time
            reverse=True
        )

        for func, (cc, nc, tt, ct, callers) in sorted_stats[:limit]:
            filename, line, func_name = func
            top_functions.append({
                'function': func_name,
                'file': filename,
                'line': line,
                'calls': nc,
                'total_time_ms': tt * 1000,
                'cumulative_time_ms': ct * 1000
            })

        return top_functions

    def log_metrics(
        self,
        metrics: Optional[PerformanceMetrics],
        transaction_id: Optional[str] = None
    ):
        """
        Log les métriques de performance en format JSON.

        Args:
            metrics: Métriques à logger
            transaction_id: ID unique de la transaction (optionnel)
        """
        if metrics is None or not self.enabled:
            return

        import json

        # Créer le dictionnaire de métriques complet
        metrics_dict = {
            'performance_metrics': {
                'inference_time_ms': round(metrics.inference_time_ms, 2),
                'cpu_time_ms': round(metrics.cpu_time_ms, 2),
                'memory_mb': round(metrics.memory_mb, 2),
                'memory_delta_mb': round(metrics.memory_delta_mb, 2),
                'function_calls': metrics.function_calls,
                'latency_ms': round(metrics.inference_time_ms, 2),
                'top_functions': [
                    {
                        'function': f['function'],
                        'file': f['file'],
                        'line': f['line'],
                        'cumulative_time_ms': round(
                            f['cumulative_time_ms'], 2
                        ),
                        'total_time_ms': round(f['total_time_ms'], 2),
                        'calls': f['calls']
                    }
                    for f in metrics.top_functions
                ]
            }
        }

        # Ajouter l'ID de transaction si fourni
        if transaction_id:
            metrics_dict['performance_metrics']['transaction_id'] = (
                transaction_id
            )

        # Logger en JSON
        logger.info(json.dumps(metrics_dict))

    def format_metrics_dict(
        self,
        metrics: Optional[PerformanceMetrics]
    ) -> Dict[str, Any]:
        """
        Formate les métriques en dictionnaire pour les logs structurés.

        Args:
            metrics: Métriques à formater

        Returns:
            Dictionnaire avec les métriques
        """
        if metrics is None or not self.enabled:
            return {}

        return {
            'performance': {
                'inference_time_ms': round(metrics.inference_time_ms, 2),
                'cpu_time_ms': round(metrics.cpu_time_ms, 2),
                'memory_mb': round(metrics.memory_mb, 2),
                'memory_delta_mb': round(metrics.memory_delta_mb, 2),
                'function_calls': metrics.function_calls,
                'top_functions': [
                    {
                        'function': f['function'],
                        'cumulative_time_ms': round(
                            f['cumulative_time_ms'], 2
                        ),
                        'calls': f['calls']
                    }
                    for f in metrics.top_functions[:3]  # Top 3 seulement
                ]
            }
        }


# Instance globale du moniteur
performance_monitor = PerformanceMonitor()
