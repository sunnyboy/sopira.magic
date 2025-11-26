#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/shared/decorators.py
#   Shared Decorators - Custom decorators
#   Reusable decorators for caching, permissions, timing
#..............................................................

"""
   Shared Decorators - Custom Decorators.

   Reusable decorators for common functionality like caching,
   permission checking, timing, and API response caching.

   Decorators:

   1. cache_result(timeout)
      - Cache function result
      - Args: timeout (int, default 3600 seconds)
      - Uses Django cache with function name + args as key

   2. require_permission(permission)
      - Require specific permission for view function
      - Args: permission (str, e.g., 'app.permission')
      - Returns: JsonResponse with error if permission denied

   3. timing_decorator(func)
      - Measure function execution time
      - Logs execution time (can be extended for logging)

   4. api_cache(timeout)
      - Cache API view responses
      - Args: timeout (int, default 300 seconds)
      - Varies cache on Authorization header
      - Uses Django's cache_page decorator

   Usage:
   ```python
   from sopira_magic.apps.shared.decorators import cache_result, require_permission
   
   @cache_result(timeout=3600)
   def expensive_function():
       return compute_value()
   
   @require_permission('app.view_model')
   def my_view(request):
       return JsonResponse({'data': '...'})
   ```
"""

from functools import wraps
from django.core.cache import cache
from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
import time


def cache_result(timeout: int = 3600):
    """
    Decorator to cache function result.
    
    Args:
        timeout: Cache timeout in seconds
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            result = cache.get(cache_key)
            if result is None:
                result = func(*args, **kwargs)
                cache.set(cache_key, result, timeout)
            return result
        return wrapper
    return decorator


def require_permission(permission: str):
    """
    Decorator to require specific permission.
    
    Args:
        permission: Permission string (e.g., 'app.permission')
    """
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if not request.user.has_perm(permission):
                return JsonResponse({'error': 'Permission denied'}, status=403)
            return func(request, *args, **kwargs)
        return wrapper
    return decorator


def timing_decorator(func):
    """Decorator to measure function execution time."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        # Log execution time if needed
        return result
    return wrapper


def api_cache(timeout: int = 300):
    """
    Decorator for API view caching.
    
    Args:
        timeout: Cache timeout in seconds
    """
    def decorator(func):
        @wraps(func)
        @cache_page(timeout)
        @vary_on_headers('Authorization')
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator
