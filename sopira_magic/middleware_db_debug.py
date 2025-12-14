#*........................................................
#*       sopira_magic/middleware_db_debug.py
#*       Temporary middleware to detect DB connection leaks
#*........................................................

import logging
from django.db import connection, reset_queries
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class DatabaseDebugMiddleware(MiddlewareMixin):
    """
    Watchdog middleware - loguje všetky DB queries per request.
    POUŽIŤ LEN NA DEBUGGING! Odstráň po nájdení problému.
    """
    
    def process_request(self, request):
        """Reset query counter na začiatku requestu"""
        reset_queries()
    
    def process_response(self, request, response):
        """Log počet queries na konci requestu"""
        queries = len(connection.queries)
        
        # Warn ak je viac ako 5 queries na jeden request (zjemnený threshold)
        if queries > 5:
            # Log ALL queries (nie len top 5)
            logger.warning(
                f"🔥 HIGH DB USAGE: {request.method} {request.path} "
                f"executed {queries} queries"
            )
            
            for i, query in enumerate(connection.queries, 1):
                logger.warning(
                    f"  #{i} ({query['time']}s): {query['sql'][:150]}..."
                )
        else:
            logger.info(
                f"✅ {request.method} {request.path}: {queries} queries"
            )
        
        return response

