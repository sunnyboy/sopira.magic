#*........................................................
#*       sopira_magic/apps/api/views_db_watchdog.py
#*       DB Watchdog API endpoint - exposes query metrics
#*........................................................

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import connection
import logging

logger = logging.getLogger(__name__)

# In-memory storage for recent high DB usage warnings (last 50)
_recent_warnings = []
MAX_WARNINGS = 50


def log_high_db_usage(method: str, path: str, query_count: int, top_queries: list):
    """
    Called by DatabaseDebugMiddleware to log high DB usage.
    Stores warning in memory for dashboard display.
    """
    warning = {
        "timestamp": __import__('datetime').datetime.now().isoformat(),
        "method": method,
        "path": path,
        "query_count": query_count,
        "top_queries": top_queries[:3],  # Only top 3
    }
    
    _recent_warnings.insert(0, warning)
    
    # Keep only last MAX_WARNINGS
    if len(_recent_warnings) > MAX_WARNINGS:
        _recent_warnings.pop()


@api_view(['GET'])
def db_watchdog_view(request):
    """
    Returns recent DB high-usage warnings for dashboard display.
    
    Response format:
    {
        "warnings": [
            {
                "timestamp": "2025-12-13T23:45:00",
                "method": "GET",
                "path": "/api/factories/",
                "query_count": 24,
                "top_queries": [
                    {"time": "0.002s", "sql": "SELECT ... (truncated)"},
                    ...
                ]
            },
            ...
        ],
        "total": 10
    }
    """
    return Response({
        "warnings": _recent_warnings,
        "total": len(_recent_warnings),
    })

