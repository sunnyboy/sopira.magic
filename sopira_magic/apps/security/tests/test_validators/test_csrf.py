"""Tests for CsrfValidator behavior across security levels."""

from types import SimpleNamespace

from django.http import HttpRequest

from sopira_magic.apps.security.types import SecurityLevel
from sopira_magic.apps.security.validators.csrf import CsrfValidator


def test_validate_minimal_level_short_circuits_for_json():
    request = HttpRequest()
    request.method = "POST"
    request.META = {}
    request.content_type = "application/json"

    assert CsrfValidator.validate(request, SecurityLevel.MINIMAL) is True


def test_validate_uses_middleware_for_higher_levels(monkeypatch):
    """For non-MINIMAL levels, CsrfViewMiddleware hooks are consulted."""

    calls = {}

    class DummyMiddleware:
        def __init__(self, get_response):  # pragma: no cover - trivial
            self.get_response = get_response

        def process_request(self, request):  # pragma: no cover - trivial
            calls["processed"] = True

        def _reject(self, request, reason):
            calls["rejected_reason"] = reason
            return None  # Accept request

    monkeypatch.setattr(
        "sopira_magic.apps.security.validators.csrf.CsrfViewMiddleware",
        DummyMiddleware,
    )

    request = HttpRequest()
    request.method = "POST"
    request.META = {}
    request.content_type = "text/html"

    assert CsrfValidator.validate(request, SecurityLevel.STANDARD) is True
    assert calls["processed"] is True
    assert calls["rejected_reason"] is None


def test_validate_rejects_when_middleware_returns_reason(monkeypatch):
    class RejectingMiddleware:
        def __init__(self, get_response):  # pragma: no cover - trivial
            self.get_response = get_response

        def process_request(self, request):  # pragma: no cover - trivial
            pass

        def _reject(self, request, reason):
            return "CSRF failed"

    monkeypatch.setattr(
        "sopira_magic.apps.security.validators.csrf.CsrfViewMiddleware",
        RejectingMiddleware,
    )

    request = HttpRequest()
    request.method = "POST"
    request.META = {}
    request.content_type = "text/html"

    assert CsrfValidator.validate(request, SecurityLevel.STANDARD) is False


def test_get_cookie_settings_for_various_levels():
    # MINIMAL or non-HTTPS -> relaxed settings
    cfg = CsrfValidator.get_cookie_settings(SecurityLevel.MINIMAL, is_https=True)
    assert cfg["CSRF_COOKIE_SAMESITE"] == "Lax"
    assert cfg["CSRF_COOKIE_SECURE"] is False

    cfg = CsrfValidator.get_cookie_settings(SecurityLevel.STANDARD, is_https=False)
    assert cfg["CSRF_COOKIE_SECURE"] is False

    # STANDARD + HTTPS
    cfg = CsrfValidator.get_cookie_settings(SecurityLevel.STANDARD, is_https=True)
    assert cfg["CSRF_COOKIE_SAMESITE"] == "Lax"
    assert cfg["CSRF_COOKIE_SECURE"] is True
    assert cfg["CSRF_COOKIE_HTTPONLY"] is False

    # STRICT/PARANOID
    for level in (SecurityLevel.STRICT, SecurityLevel.PARANOID):
        cfg = CsrfValidator.get_cookie_settings(level, is_https=True)
        assert cfg["CSRF_COOKIE_SAMESITE"] == "Strict"
        assert cfg["CSRF_COOKIE_SECURE"] is True
        assert cfg["CSRF_COOKIE_HTTPONLY"] is True
