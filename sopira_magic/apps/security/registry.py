"""Abstraktný security registry - host app poskytne implementáciu.

Thread-safe registry pre všetky security callbacky.
ConfigDriven & SSOT princíp: všetka projektovo-špecifická logika žije
v callbackoch registrovaných hostiteľskou aplikáciou.
"""

import logging
import os
import threading
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger(__name__)

# Thread-safe lock
_registry_lock = threading.Lock()

# Abstraktné callbacky (None ak nie sú registrované)
_environment_detector: Optional[Callable[[Optional[Any]], str]] = None
_certificate_provider: Optional[Callable[[str, Optional[str]], Dict[str, Any]]] = None
_security_auditor: Optional[Callable[[str], Dict[str, Any]]] = None
_custom_header_provider: Optional[Callable[[Any], Dict[str, str]]] = None


def register_environment_detector(callback: Callable[[Optional[Any]], str]) -> None:
    """Zaregistruj callback pre environment detection.

    Host app musí poskytnúť funkciu, ktorá:
    - ak ``request is None``: vráti default environment ("local", "dev", "production", "cloud", ...)
    - ak ``request`` je HttpRequest: vráti environment podľa requestu
    """

    global _environment_detector
    with _registry_lock:
        _environment_detector = callback


def register_certificate_provider(callback: Callable[[str, Optional[str]], Dict[str, Any]]) -> None:
    """Zaregistruj callback pre SSL/TLS certificate management.

    ``callback(action, domain) -> cert_info``
    - action: "get", "renew", "validate", "status".
    """

    global _certificate_provider
    with _registry_lock:
        _certificate_provider = callback


def register_security_auditor(callback: Callable[[str], Dict[str, Any]]) -> None:
    """Zaregistruj callback pre security auditing.

    ``callback(check_type) -> audit_results``
    - check_type: "quick", "full", "ssl", "headers".
    """

    global _security_auditor
    with _registry_lock:
        _security_auditor = callback


def register_custom_header_provider(callback: Callable[[Any], Dict[str, str]]) -> None:
    """Zaregistruj callback pre custom security headers.

    Host app môže pridať vlastné security headers (napr. tenant, correlation-id a pod.).
    """

    global _custom_header_provider
    with _registry_lock:
        _custom_header_provider = callback


def get_environment(request: Optional[Any] = None) -> str:
    """Vráť aktuálny environment cez registry alebo env var.

    Fallback: ``DJANGO_ENV`` ("local" ak chýba).
    """

    with _registry_lock:
        detector = _environment_detector

    if detector is not None:
        try:
            return detector(request)
        except Exception as exc:  # pragma: no cover - defensívny fallback
            logger.warning("Environment detector failed: %s", exc)

    env = os.getenv("DJANGO_ENV", "local")
    allowed = {"local", "dev", "staging", "production", "cloud"}
    return env if env in allowed else "local"


def get_certificate_info(action: str = "get", domain: Optional[str] = None) -> Dict[str, Any]:
    """Získaj SSL certificate info cez registry.

    Fallback: jednoduchá štruktúra s ``valid=False`` ak provider nie je.
    """

    with _registry_lock:
        provider = _certificate_provider

    if provider is not None:
        try:
            return provider(action, domain)
        except Exception as exc:  # pragma: no cover
            logger.warning("Certificate provider failed: %s", exc)

    return {
        "valid": False,
        "managed": False,
        "reason": "no_certificate_provider_registered",
        "errors": ["SSL certificate provider not configured"],
    }


def get_custom_headers(request: Any) -> Dict[str, str]:
    """Získaj custom security headers cez registry.

    Ak provider nie je registrovaný alebo zlyhá, vráti prázdny dict.
    """

    with _registry_lock:
        provider = _custom_header_provider

    if provider is not None:
        try:
            return provider(request)
        except Exception as exc:  # pragma: no cover
            logger.debug("Custom header provider failed: %s", exc)

    return {}


def is_registry_configured() -> bool:
    """Skontroluj, či sú minimálne povinné registry nastavené.

    Momentálne je povinný iba ``environment_detector``.
    """

    with _registry_lock:
        return _environment_detector is not None
