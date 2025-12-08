#..............................................................
#   sopira_magic/apps/security/apps.py
#   Security AppConfig - Django app configuration
#..............................................................

"""Security AppConfig - inicializácia security enginu.

- Registruje sa v INSTALLED_APPS ako ``sopira_magic.apps.security``.
- Pri štarte validuje SSOT konfiguráciu a voliteľne spustí rýchly audit.
"""

import logging
from django.apps import AppConfig
from django.conf import settings

from .registry import register_environment_detector

logger = logging.getLogger(__name__)


class SecurityConfig(AppConfig):
    """Django AppConfig pre security engine."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "sopira_magic.apps.security"
    label = "security"
    verbose_name = "Security Engine"

    def ready(self):  # pragma: no cover - startup wiring
        """Validácia security konfigurácie pri štarte aplikácie."""
        validate_on_startup = getattr(settings, "SECURITY_VALIDATE_ON_STARTUP", True)

        if not validate_on_startup:
            return

        try:
            from .validation import validate_security_config
            from .engine import SecurityEngine
            from sopira_magic.security_config import detect_environment_from_request

            # Registruj environment detector callback tak, aby nový engine
            # používal rovnakú logiku ako existujúci security_config modul.
            def _env_detector(request=None) -> str:
                env_info = (
                    detect_environment_from_request(request)
                    if request is not None
                    else detect_environment_from_request_like()
                )
                env_type = env_info.env_type
                # Mapovanie starých hodnôt na EnvironmentType stringy
                if env_type == "render":
                    return "cloud"
                return env_type

            def detect_environment_from_request_like():  # pragma: no cover - simple wrapper
                # V prípade request=None použijeme falošný objekt s hostom z ALLOWED_HOSTS
                from collections import namedtuple

                DummyReq = namedtuple("DummyReq", ["get_host", "is_secure"])

                host = settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else "localhost"
                dummy_request = DummyReq(lambda: host, lambda: False)
                return detect_environment_from_request(dummy_request)

            register_environment_detector(_env_detector)

            errors = validate_security_config()
            if errors:
                logger.error(
                    "Security configuration validation errors: %s",
                    errors,
                )

            audit_enabled = getattr(settings, "SECURITY_AUDIT_ON_STARTUP", False)
            if audit_enabled:
                results = SecurityEngine.security_audit("quick")
                if not results.get("passed", True):
                    logger.warning("Security audit warnings: %s", results)

            logger.info("Security engine initialized and validated")

        except Exception as exc:  # pragma: no cover - defensive logging
            logger.error(
                "Error during security engine validation: %s", exc, exc_info=True
            )
