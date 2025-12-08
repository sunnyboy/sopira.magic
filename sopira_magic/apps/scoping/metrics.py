#..............................................................
#   apps/scoping/metrics.py
#   Monitoring a metriky pre scoping engine
#..............................................................

"""
Monitoring a metriky pre scoping engine.

Umožňuje sledovanie výkonu scoping engine - počet vykonaní, priemerný čas spracovania,
chyby. Nevyhnutné pre capacity planning a detekciu performance problémov.
"""

import time
import threading
import logging
from typing import Dict, List, Any, Optional
from collections import defaultdict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Thread-safe storage pre metriky
_metrics_lock = threading.Lock()
_metrics: Dict[str, Any] = {
    'executions': defaultdict(int),  # (table_name, role) -> count
    'durations': defaultdict(list),  # (table_name, role) -> [durations]
    'errors': defaultdict(int),  # (table_name, role) -> error_count
    'cache_hits': defaultdict(int),  # (table_name, role) -> cache_hit_count
    'cache_misses': defaultdict(int),  # (table_name, role) -> cache_miss_count
    'start_time': datetime.now(),
}


def record_scoping_execution(
    table_name: str,
    role: str,
    duration: float,
    success: bool = True,
    cache_hit: bool = False
):
    """
    Zaznamená vykonanie scoping engine.
    
    Thread-safe: Všetky operácie sú chránené lockom.
    
    Args:
        table_name: Názov tabuľky
        role: Role scope_owner
        duration: Čas vykonania v sekundách
        success: True ak bolo úspešné, False ak došlo k chybe
        cache_hit: True ak bol použitý cache
    """
    key = (table_name, role)
    
    with _metrics_lock:
        _metrics['executions'][key] += 1
        
        if success:
            _metrics['durations'][key].append(duration)
            # Udržiavame len posledných 1000 meraní pre každý key
            if len(_metrics['durations'][key]) > 1000:
                _metrics['durations'][key] = _metrics['durations'][key][-1000:]
        else:
            _metrics['errors'][key] += 1
        
        if cache_hit:
            _metrics['cache_hits'][key] += 1
        else:
            _metrics['cache_misses'][key] += 1


def get_metrics() -> Dict[str, Any]:
    """
    Vráti aktuálne metriky.
    
    Thread-safe: Čítanie je chránené lockom.
    
    Returns:
        Dict s metrikami:
        - executions: Dict[(table, role)] -> count
        - avg_durations: Dict[(table, role)] -> avg_duration
        - errors: Dict[(table, role)] -> error_count
        - cache_hit_rate: Dict[(table, role)] -> hit_rate (0-1)
        - total_executions: int
        - total_errors: int
        - uptime_seconds: float
    """
    with _metrics_lock:
        executions = dict(_metrics['executions'])
        durations = dict(_metrics['durations'])
        errors = dict(_metrics['errors'])
        cache_hits = dict(_metrics['cache_hits'])
        cache_misses = dict(_metrics['cache_misses'])
        start_time = _metrics['start_time']
    
    # Vypočítaj priemerné časy
    avg_durations = {}
    for key, duration_list in durations.items():
        if duration_list:
            avg_durations[key] = sum(duration_list) / len(duration_list)
        else:
            avg_durations[key] = 0.0
    
    # Vypočítaj cache hit rate
    cache_hit_rates = {}
    for key in set(list(cache_hits.keys()) + list(cache_misses.keys())):
        hits = cache_hits.get(key, 0)
        misses = cache_misses.get(key, 0)
        total = hits + misses
        if total > 0:
            cache_hit_rates[key] = hits / total
        else:
            cache_hit_rates[key] = 0.0
    
    # Celkové štatistiky
    total_executions = sum(executions.values())
    total_errors = sum(errors.values())
    uptime = (datetime.now() - start_time).total_seconds()
    
    return {
        'executions': executions,
        'avg_durations': avg_durations,
        'errors': errors,
        'cache_hit_rates': cache_hit_rates,
        'total_executions': total_executions,
        'total_errors': total_errors,
        'error_rate': total_errors / total_executions if total_executions > 0 else 0.0,
        'uptime_seconds': uptime,
        'start_time': start_time.isoformat(),
    }


def reset_metrics():
    """
    Resetuje všetky metriky.
    
    Thread-safe: Operácia je chránená lockom.
    """
    global _metrics
    with _metrics_lock:
        _metrics = {
            'executions': defaultdict(int),
            'durations': defaultdict(list),
            'errors': defaultdict(int),
            'cache_hits': defaultdict(int),
            'cache_misses': defaultdict(int),
            'start_time': datetime.now(),
        }


def export_metrics(format: str = 'json') -> str:
    """
    Exportuje metriky v zadanom formáte.
    
    Args:
        format: 'json' alebo 'text'
        
    Returns:
        String reprezentácia metrík
    """
    metrics = get_metrics()
    
    if format == 'json':
        import json
        return json.dumps(metrics, indent=2, default=str)
    elif format == 'text':
        lines = [
            "Scoping Engine Metrics",
            "=" * 80,
            f"Uptime: {metrics['uptime_seconds']:.2f} seconds",
            f"Total Executions: {metrics['total_executions']}",
            f"Total Errors: {metrics['total_errors']}",
            f"Error Rate: {metrics['error_rate']:.2%}",
            "",
            "Per Table/Role:",
            "-" * 80,
        ]
        
        for (table, role), count in sorted(metrics['executions'].items()):
            avg_duration = metrics['avg_durations'].get((table, role), 0.0)
            error_count = metrics['errors'].get((table, role), 0)
            cache_rate = metrics['cache_hit_rates'].get((table, role), 0.0)
            
            lines.append(
                f"{table}/{role}: "
                f"executions={count}, "
                f"avg_duration={avg_duration*1000:.2f}ms, "
                f"errors={error_count}, "
                f"cache_hit_rate={cache_rate:.2%}"
            )
        
        return "\n".join(lines)
    else:
        raise ValueError(f"Unknown format: {format}. Must be 'json' or 'text'")


# Context manager pre automatické zaznamenávanie metrík
class ScopingMetricsContext:
    """Context manager pre automatické zaznamenávanie metrík."""
    
    def __init__(self, table_name: str, role: str):
        self.table_name = table_name
        self.role = role
        self.start_time = None
        self.success = False
        self.cache_hit = False
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        self.success = exc_type is None
        record_scoping_execution(
            self.table_name,
            self.role,
            duration,
            success=self.success,
            cache_hit=self.cache_hit
        )
        return False  # Nezabráni propagácii výnimky

