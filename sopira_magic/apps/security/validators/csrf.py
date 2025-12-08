"""CSRF validator - ConfigDriven CSRF validácia podľa security level."""

import logging
from typing import Any, Dict

from django.http import HttpRequest
from django.middleware.csrf import CsrfViewMiddleware

from ..types import SecurityLevel

logger = logging.getLogger(__name__)


class CsrfValidator:
    """ConfigDriven CSRF validator - SSOT pre CSRF rozhodnutia."""

    @staticmethod
    def validate(request: HttpRequest, security_level: SecurityLevel) -> bool:
        """Validuj CSRF token podľa security level.

        - pri MINIMAL level pre JSON API v lokálnom vývoji uľahčuje validáciu,
        - inak sa spolieha na Django ``CsrfViewMiddleware``.
        """

        if security_level == SecurityLevel.MINIMAL:
            content_type = request.content_type or ""
            if "application/json" in content_type:
                return True

        middleware = CsrfViewMiddleware(lambda req: None)
        try:
            middleware.process_request(request)
            reason = middleware._reject(request, None)
            return reason is None
        except Exception as exc:  # pragma: no cover - defenzívny fallback
            logger.debug("CSRF validation failed: %s", exc)
            return False

    @staticmethod
    def get_cookie_settings(security_level: SecurityLevel, is_https: bool) -> Dict[str, Any]:
        """Vráť CSRF cookie nastavenia podľa security level a HTTPS."""

        if security_level == SecurityLevel.MINIMAL or not is_https:
            return {
                "CSRF_COOKIE_SAMESITE": "Lax",
                "CSRF_COOKIE_SECURE": False,
                "CSRF_COOKIE_HTTPONLY": False,
            }

        if security_level == SecurityLevel.STANDARD:
            return {
                "CSRF_COOKIE_SAMESITE": "Lax",
                "CSRF_COOKIE_SECURE": is_https,
                "CSRF_COOKIE_HTTPONLY": False,
            }

        # STRICT alebo PARANOID
        return {
            "CSRF_COOKIE_SAMESITE": "Strict",
            "CSRF_COOKIE_SECURE": True,
            "CSRF_COOKIE_HTTPONLY": True,
        }
