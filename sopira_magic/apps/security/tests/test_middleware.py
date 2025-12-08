"""Unit tests for SecurityMiddleware request/response behavior."""

from django.http import HttpResponse
from django.test import RequestFactory

from sopira_magic.apps.security.middleware import SecurityMiddleware
import sopira_magic.apps.security.engine as engine_mod
from sopira_magic.apps.security.types import EnvironmentType, SecurityLevel


rf = RequestFactory()


def _make_middleware():
    return SecurityMiddleware(lambda request: HttpResponse("OK"))


def test_process_request_redirects_to_https(monkeypatch):
    monkeypatch.setattr(
        engine_mod.SecurityEngine,
        "enforce_https_redirect",
        staticmethod(lambda request: "https://example.com/path"),
    )

    request = rf.get("/path")
    middleware = _make_middleware()

    response = middleware.process_request(request)
    assert response.status_code == 307
    assert response["Location"] == "https://example.com/path"


def test_process_request_handles_cors_preflight(monkeypatch):
    monkeypatch.setattr(
        engine_mod.SecurityEngine,
        "enforce_https_redirect",
        staticmethod(lambda request: None),
    )
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

    request = rf.options("/path", HTTP_ORIGIN="https://client")
    middleware = _make_middleware()

    response = middleware.process_request(request)
    assert response.status_code == 200
    assert response["Access-Control-Allow-Origin"] == "https://client"


def test_process_request_csrf_failure_returns_403(monkeypatch):
    monkeypatch.setattr(
        engine_mod.SecurityEngine,
        "enforce_https_redirect",
        staticmethod(lambda request: None),
    )
    monkeypatch.setattr(
        engine_mod.SecurityEngine,
        "validate_csrf",
        staticmethod(lambda request: False),
    )

    request = rf.post("/api/endpoint/", data={})
    middleware = _make_middleware()

    response = middleware.process_request(request)
    assert response.status_code == 403
    assert b"CSRF validation failed" in response.content


def test_process_request_logs_debug_for_local_env(monkeypatch, caplog):
    monkeypatch.setattr(
        engine_mod.SecurityEngine,
        "enforce_https_redirect",
        staticmethod(lambda request: None),
    )
    monkeypatch.setattr(
        engine_mod.SecurityEngine,
        "validate_csrf",
        staticmethod(lambda request: True),
    )

    def fake_get_config(cls, request):  # pragma: no cover - trivial
        return {
            "env_type": EnvironmentType.LOCAL,
            "security_level": SecurityLevel.MINIMAL,
        }

    monkeypatch.setattr(
        engine_mod.SecurityEngine,
        "get_config",
        classmethod(fake_get_config),
    )

    request = rf.get("/path")
    middleware = _make_middleware()

    with caplog.at_level("DEBUG"):
        result = middleware.process_request(request)

    assert result is None


def test_process_response_applies_headers_and_debug_config(monkeypatch):
    def fake_apply_headers(response, request):  # pragma: no cover - trivial
        response["X-From-Engine"] = "1"
        return response

    def fake_get_config(cls, request):  # pragma: no cover - trivial
        return {
            "env_type": EnvironmentType.LOCAL,
            "security_level": SecurityLevel.MINIMAL,
        }

    monkeypatch.setattr(
        engine_mod.SecurityEngine,
        "apply_security_headers",
        staticmethod(fake_apply_headers),
    )
    monkeypatch.setattr(
        engine_mod.SecurityEngine,
        "get_config",
        classmethod(fake_get_config),
    )

    request = rf.get("/path/?_security_debug=1")
    response = HttpResponse("OK")
    middleware = _make_middleware()

    result = middleware.process_response(request, response)
    assert result["X-From-Engine"] == "1"
    assert result["X-Security-Config"] == "env=local, level=minimal"


def test_process_exception_logs_security_issues(monkeypatch, caplog):
    middleware = _make_middleware()
    request = rf.get("/path")

    with caplog.at_level("WARNING"):
        result = middleware.process_exception(request, Exception("CSRF token missing"))

    assert result is None
    # A warning about a security exception should have been logged
    assert any("Security exception" in rec.getMessage() for rec in caplog.records)
