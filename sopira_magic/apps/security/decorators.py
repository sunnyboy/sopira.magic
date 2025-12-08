"""Security decorators - ConfigDriven decorators pre views."""

import logging
from functools import wraps
from typing import Callable

from django.http import HttpRequest, HttpResponse, JsonResponse

from .engine import SecurityEngine
from .utils import SecurityUtils

logger = logging.getLogger(__name__)


def require_https(view_func: Callable) -> Callable:
    """Decorator, ktorý vynucuje HTTPS pre daný view."""

    @wraps(view_func)
    def wrapper(request: HttpRequest, *args, **kwargs):
        redirect_url = SecurityEngine.enforce_https_redirect(request)
        if redirect_url:
            response = HttpResponse(status=307)
            response["Location"] = redirect_url
            return response
        return view_func(request, *args, **kwargs)

    return wrapper


def cors_enabled(view_func: Callable) -> Callable:
    """Decorator, ktorý pridáva CORS podporu pre view."""

    @wraps(view_func)
    def wrapper(request: HttpRequest, *args, **kwargs):
        if request.method == "OPTIONS":
            if SecurityEngine.validate_cors(request):
                response = HttpResponse(status=200)
                cors_headers = SecurityEngine.get_cors_headers(request)
                for key, value in cors_headers.items():
                    response[key] = value
                return response
            return HttpResponse(status=403)

        response = view_func(request, *args, **kwargs)

        if isinstance(response, HttpResponse):
            cors_headers = SecurityEngine.get_cors_headers(request)
            for key, value in cors_headers.items():
                response[key] = value

        return response

    return wrapper


def security_headers(view_func: Callable) -> Callable:
    """Decorator, ktorý aplikuje security headers len na daný view."""

    @wraps(view_func)
    def wrapper(request: HttpRequest, *args, **kwargs):
        response = view_func(request, *args, **kwargs)
        if isinstance(response, HttpResponse):
            response = SecurityEngine.apply_security_headers(response, request)
        return response

    return wrapper


def rate_limit(max_requests: int = 100, window: int = 60) -> Callable:
    """Decorator pre jednoduchý rate limiting podľa IP + path."""

    from django.core.cache import cache

    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        def wrapper(request: HttpRequest, *args, **kwargs):
            client_ip = SecurityUtils.get_client_ip(request)
            if not client_ip:
                return JsonResponse({"error": "Cannot identify client"}, status=400)

            cache_key = f"rate_limit:{client_ip}:{request.path}"
            current = cache.get(cache_key, 0)

            if current >= max_requests:
                return JsonResponse(
                    {"error": "Rate limit exceeded", "retry_after": window},
                    status=429,
                )

            cache.set(cache_key, current + 1, window)
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


def require_security_level(level: str) -> Callable:
    """Decorator, ktorý vyžaduje minimálny security level pre view."""

    from .types import SecurityLevel

    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        def wrapper(request: HttpRequest, *args, **kwargs):
            config = SecurityEngine.get_config(request)
            current_level = config["security_level"]

            try:
                required_level = SecurityLevel(level)
                current_level_enum = (
                    current_level
                    if isinstance(current_level, SecurityLevel)
                    else SecurityLevel(current_level)
                )
            except ValueError:
                logger.error("Invalid security level: %s", level)
                return JsonResponse(
                    {"error": "Invalid security configuration"}, status=500
                )

            level_order = {
                SecurityLevel.MINIMAL: 0,
                SecurityLevel.STANDARD: 1,
                SecurityLevel.STRICT: 2,
                SecurityLevel.PARANOID: 3,
            }

            if level_order[current_level_enum] < level_order[required_level]:
                return JsonResponse(
                    {
                        "error": (
                            "Insufficient security level. "
                            f"Required: {level}, Current: {current_level_enum.value}"
                        )
                    },
                    status=403,
                )

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator
