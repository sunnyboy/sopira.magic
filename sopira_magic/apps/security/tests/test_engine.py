"""Unit tests for SecurityEngine core behavior."""

from django.http import HttpRequest, HttpResponse
from django.test import RequestFactory

import sopira_magic.apps.security.engine as engine_mod
from sopira_magic.apps.security.engine import SecurityEngine
from sopira_magic.apps.security.types import EnvironmentType, SecurityLevel


rf = RequestFactory()


def test_get_config_known_and_unknown_env(monkeypatch):
    # Known environment string -> mapped via EnvironmentType
    monkeypatch.setattr(engine_mod, "get_environment", lambda request=None: "production")
    cfg = SecurityEngine.get_config(None)
    assert cfg["env_type"] is EnvironmentType.PRODUCTION

    # Unknown environment string -> fallback to LOCAL
    monkeypatch.setattr(engine_mod, "get_environment", lambda request=None: "unknown")
    cfg = SecurityEngine.get_config(None)
    assert cfg["env_type"] is EnvironmentType.LOCAL


def test_get_config_falls_back_when_missing_env_config(monkeypatch):
    """If SECURITY_CONFIG_MATRIX lacks the env key, LOCAL is used as fallback."""

    from sopira_magic.apps.security.types import EnvironmentType as EnvType
    from sopira_magic.apps.security.config import SECURITY_CONFIG_MATRIX as REAL_MATRIX

    local_cfg = REAL_MATRIX[EnvType.LOCAL]

    monkeypatch.setattr(engine_mod, "get_environment", lambda request=None: "staging")
    monkeypatch.setattr(
        engine_mod,
        "SECURITY_CONFIG_MATRIX",
        {EnvType.LOCAL: local_cfg},
    )

    cfg = SecurityEngine.get_config(None)
    assert cfg["env_type"] is EnvType.LOCAL


def test_apply_security_headers_sets_core_headers(monkeypatch):
    # Force production config so that HSTS and strict headers are applied
    monkeypatch.setattr(engine_mod, "get_environment", lambda request=None: "production")
    monkeypatch.setattr(
        engine_mod,
        "get_custom_headers",
        lambda request: {"X-From-Registry": "1"},
    )

    request = rf.get("/")
    response = HttpResponse("OK")

    result = SecurityEngine.apply_security_headers(response, request)

    # CSP and basic security headers should be present
    assert "Content-Security-Policy" in result
    assert "X-Content-Type-Options" in result
    assert "X-Frame-Options" in result
    # Custom headers from registry should be applied
    assert result["X-From-Registry"] == "1"


def test_apply_security_headers_removes_sensitive_in_local(monkeypatch):
    monkeypatch.setattr(engine_mod, "get_environment", lambda request=None: "local")

    request = rf.get("/")
    response = HttpResponse("OK")
    response["Server"] = "TestServer"
    response["X-Powered-By"] = "Django"

    result = SecurityEngine.apply_security_headers(response, request)
    assert "Server" not in result
    assert "X-Powered-By" not in result


def test_validate_cors_uses_custom_config(monkeypatch):
    calls = {}

    def fake_validate(request, cors_cfg):  # pragma: no cover - trivial
        calls["request"] = request
        calls["cors"] = cors_cfg
        return True

    monkeypatch.setattr(engine_mod.CorsValidator, "validate", staticmethod(fake_validate))

    request = rf.get("/", HTTP_ORIGIN="https://client.example.com")
    custom_cfg = {"allowed_origins": ["https://client.example.com"]}

    assert SecurityEngine.validate_cors(request, custom_cfg) is True
    assert calls["cors"] is custom_cfg


def test_validate_csrf_normalizes_string_security_level(monkeypatch):
    # Patch get_config to return a string security level
    def fake_get_config(cls, request):  # pragma: no cover - trivial
        return {"security_level": "standard"}

    monkeypatch.setattr(SecurityEngine, "get_config", classmethod(fake_get_config))

    seen = {}

    def fake_csrf_validate(request, level):  # pragma: no cover - trivial
        seen["level"] = level
        return True

    monkeypatch.setattr(engine_mod.CsrfValidator, "validate", staticmethod(fake_csrf_validate))

    request = rf.post("/api/", data={})
    assert SecurityEngine.validate_csrf(request) is True
    assert isinstance(seen["level"], SecurityLevel)
    assert seen["level"] is SecurityLevel.STANDARD


def test_validate_csrf_invalid_level_defaults_to_standard(monkeypatch):
    """Invalid security level strings are coerced to STANDARD."""

    def fake_get_config(cls, request):  # pragma: no cover - trivial
        return {"security_level": "INVALID"}

    monkeypatch.setattr(SecurityEngine, "get_config", classmethod(fake_get_config))

    seen = {}

    def fake_csrf_validate(request, level):  # pragma: no cover - trivial
        seen["level"] = level
        return True

    monkeypatch.setattr(engine_mod.CsrfValidator, "validate", staticmethod(fake_csrf_validate))

    request = rf.post("/api/", data={})
    assert SecurityEngine.validate_csrf(request) is True
    assert seen["level"] is SecurityLevel.STANDARD


def test_get_cors_headers_delegates_to_validator(monkeypatch):
    expected = {"Access-Control-Allow-Origin": "https://client"}

    def fake_get_headers(request, cfg):  # pragma: no cover - trivial
        return expected

    monkeypatch.setattr(engine_mod.CorsValidator, "get_headers", staticmethod(fake_get_headers))

    request = rf.get("/", HTTP_ORIGIN="https://client")
    headers = SecurityEngine.get_cors_headers(request)
    assert headers is expected


def test_check_ssl_status_uses_registry_and_fallback(monkeypatch):
    # Case 1: registry reports valid -> SslValidator not called
    def registry_valid(action, domain=None):  # pragma: no cover - trivial
        return {"valid": True, "source": "registry", "domain": domain}

    monkeypatch.setattr(engine_mod, "get_certificate_info", registry_valid)
    result = SecurityEngine.check_ssl_status("example.com")
    assert result["source"] == "registry"

    # Case 2: registry invalid -> fallback to SslValidator.check_status
    def registry_invalid(action, domain=None):  # pragma: no cover - trivial
        return {"valid": False}

    def ssl_ok(domain=None):  # pragma: no cover - trivial
        return {"valid": True, "source": "validator", "domain": domain}

    monkeypatch.setattr(engine_mod, "get_certificate_info", registry_invalid)
    monkeypatch.setattr(engine_mod.SslValidator, "check_status", staticmethod(ssl_ok))

    result = SecurityEngine.check_ssl_status("example.com")
    assert result["source"] == "validator"


def test_enforce_https_redirect_builds_url_from_request(monkeypatch):
    # Minimal SSL config with redirect enabled
    def fake_get_config(cls, request):  # pragma: no cover - trivial
        return {
            "ssl": {"enabled": True, "redirect_http": True},
            "env_type": EnvironmentType.PRODUCTION,
        }

    monkeypatch.setattr(SecurityEngine, "get_config", classmethod(fake_get_config))

    request = rf.get("/path/?q=1")
    # Force a host with port to test stripping
    request.get_host = lambda: "example.com:80"  # type: ignore[assignment]

    url = SecurityEngine.enforce_https_redirect(request)
    assert url == "https://example.com/path/?q=1"


def test_enforce_https_redirect_returns_none_for_secure_request(monkeypatch):
    def fake_get_config(cls, request):  # pragma: no cover - trivial
        return {
            "ssl": {"enabled": True, "redirect_http": True},
            "env_type": EnvironmentType.PRODUCTION,
        }

    monkeypatch.setattr(SecurityEngine, "get_config", classmethod(fake_get_config))

    request = rf.get("/secure", secure=True)
    assert SecurityEngine.enforce_https_redirect(request) is None


def test_security_audit_delegates_to_security_auditor(monkeypatch):
    from sopira_magic.apps.security import monitoring as monitoring_mod

    def fake_run_audit(check_type):  # pragma: no cover - trivial
        return {
            "passed": True,
            "check_type": check_type,
            "checks": {},
            "errors": [],
            "summary": "ok",
            "timestamp": "2024-01-01T00:00:00",
        }

    monkeypatch.setattr(
        monitoring_mod.SecurityAuditor,
        "run_audit",
        staticmethod(fake_run_audit),
    )

    result = SecurityEngine.security_audit("quick")
    assert result["passed"] is True
    assert result["check_type"] == "quick"
