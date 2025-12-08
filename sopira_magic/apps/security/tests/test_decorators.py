"""Unit tests for security decorators."""

import json

from django.core.cache import cache
from django.http import HttpResponse, JsonResponse
from django.test import RequestFactory

import sopira_magic.apps.security.engine as engine_mod
from sopira_magic.apps.security.decorators import (
    require_https,
    cors_enabled,
    security_headers,
    rate_limit,
    require_security_level,
)
from sopira_magic.apps.security.types import EnvironmentType, SecurityLevel
from sopira_magic.apps.security.utils import SecurityUtils


rf = RequestFactory()


def test_require_https_redirects_when_engine_requests(monkeypatch):
    monkeypatch.setattr(
        engine_mod.SecurityEngine,
        "enforce_https_redirect",
        staticmethod(lambda request: "https://example.com/secure"),
    )

    @require_https
    def view(request):  # pragma: no cover - trivial
        return HttpResponse("OK")

    request = rf.get("/path")
    response = view(request)
    assert response.status_code == 307
    assert response["Location"] == "https://example.com/secure"


def test_require_https_allows_when_no_redirect(monkeypatch):
    monkeypatch.setattr(
        engine_mod.SecurityEngine,
        "enforce_https_redirect",
        staticmethod(lambda request: None),
    )

    @require_https
    def view(request):  # pragma: no cover - trivial
        return HttpResponse("OK")

    request = rf.get("/path")
    response = view(request)
    assert response.status_code == 200


def test_cors_enabled_handles_preflight_and_get(monkeypatch):
    monkeypatch.setattr(
        engine_mod.SecurityEngine,
        "validate_cors",
        staticmethod(lambda request: True),
    )
    monkeypatch.setattr(
        engine_mod.SecurityEngine,
        "get_cors_headers",
        staticmethod(lambda request: {"Access-Control-Allow-Origin": "https://client"}),
    )

    @cors_enabled
    def view_should_not_be_called(request):  # pragma: no cover - trivial
        raise AssertionError("View should not be called for OPTIONS")

    options_request = rf.options("/path", HTTP_ORIGIN="https://client")
    response = view_should_not_be_called(options_request)
    assert response.status_code == 200
    assert response["Access-Control-Allow-Origin"] == "https://client"

    @cors_enabled
    def normal_view(request):  # pragma: no cover - trivial
        return HttpResponse("OK")

    get_request = rf.get("/path", HTTP_ORIGIN="https://client")
    response = normal_view(get_request)
    assert response.status_code == 200
    assert response["Access-Control-Allow-Origin"] == "https://client"


def test_cors_enabled_rejects_invalid_preflight(monkeypatch):
    """OPTIONS request with failed CORS validation returns 403."""

    monkeypatch.setattr(
        engine_mod.SecurityEngine,
        "validate_cors",
        staticmethod(lambda request: False),
    )

    @cors_enabled
    def view(request):  # pragma: no cover - trivial
        return HttpResponse("OK")

    options_request = rf.options("/path", HTTP_ORIGIN="https://client")
    response = view(options_request)
    assert response.status_code == 403


def test_security_headers_decorator_applies_engine_headers(monkeypatch):
    def fake_apply(response, request):  # pragma: no cover - trivial
        response["X-From-Engine"] = "1"
        return response

    monkeypatch.setattr(
        engine_mod.SecurityEngine,
        "apply_security_headers",
        staticmethod(fake_apply),
    )

    @security_headers
    def view(request):  # pragma: no cover - trivial
        return HttpResponse("OK")

    request = rf.get("/path")
    response = view(request)
    assert response["X-From-Engine"] == "1"


def test_rate_limit_allows_then_blocks(monkeypatch):
    cache.clear()
    monkeypatch.setattr(
        SecurityUtils,
        "get_client_ip",
        staticmethod(lambda request: "1.2.3.4"),
    )

    @rate_limit(max_requests=1, window=60)
    def view(request):  # pragma: no cover - trivial
        return JsonResponse({"ok": True})

    request = rf.get("/rate-limited")

    first = view(request)
    assert first.status_code == 200

    second = view(request)
    assert second.status_code == 429
    data = json.loads(second.content.decode())
    assert "retry_after" in data


def test_rate_limit_returns_400_when_ip_missing(monkeypatch):
    cache.clear()
    monkeypatch.setattr(
        SecurityUtils,
        "get_client_ip",
        staticmethod(lambda request: None),
    )

    @rate_limit(max_requests=1, window=60)
    def view(request):  # pragma: no cover - trivial
        return JsonResponse({"ok": True})

    request = rf.get("/rate-limited")
    response = view(request)
    assert response.status_code == 400


def test_require_security_level_success_and_failure(monkeypatch):
    def get_config_strict(cls, request):  # pragma: no cover - trivial
        return {
            "env_type": EnvironmentType.PRODUCTION,
            "security_level": SecurityLevel.STRICT,
        }

    def get_config_minimal(cls, request):  # pragma: no cover - trivial
        return {
            "env_type": EnvironmentType.LOCAL,
            "security_level": SecurityLevel.MINIMAL,
        }

    # Success: STRICT satisfies required STANDARD
    monkeypatch.setattr(
        engine_mod.SecurityEngine,
        "get_config",
        classmethod(get_config_strict),
    )

    @require_security_level("standard")
    def protected_view(request):  # pragma: no cover - trivial
        return JsonResponse({"ok": True})

    request = rf.get("/protected")
    response = protected_view(request)
    assert response.status_code == 200

    # Failure: MINIMAL does not satisfy STRICT
    monkeypatch.setattr(
        engine_mod.SecurityEngine,
        "get_config",
        classmethod(get_config_minimal),
    )

    @require_security_level("strict")
    def strict_view(request):  # pragma: no cover - trivial
        return JsonResponse({"ok": True})

    response = strict_view(request)
    assert response.status_code == 403
    data = json.loads(response.content.decode())
    assert "Insufficient security level" in data["error"]


def test_require_security_level_invalid_required_level(monkeypatch):
    def get_config(cls, request):  # pragma: no cover - trivial
        return {
            "env_type": EnvironmentType.LOCAL,
            "security_level": SecurityLevel.MINIMAL,
        }

    monkeypatch.setattr(
        engine_mod.SecurityEngine,
        "get_config",
        classmethod(get_config),
    )

    @require_security_level("invalid-level")
    def view(request):  # pragma: no cover - trivial
        return JsonResponse({"ok": True})

    request = rf.get("/protected")
    response = view(request)
    assert response.status_code == 500
    data = json.loads(response.content.decode())
    assert "Invalid security configuration" in data["error"]
