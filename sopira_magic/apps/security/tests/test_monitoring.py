"""Unit tests for SecurityAuditor (monitoring and audits)."""

from django.conf import settings

import sopira_magic.apps.security.monitoring as monitoring_mod
from sopira_magic.apps.security.monitoring import SecurityAuditor
from sopira_magic.apps.security.types import EnvironmentType, SecurityLevel


def test_run_audit_full_aggregates_results(monkeypatch):
    def ssl_ok():  # pragma: no cover - trivial
        return {"passed": True}

    def headers_fail():  # pragma: no cover - trivial
        return {"passed": False}

    def cors_ok():  # pragma: no cover - trivial
        return {"passed": True}

    def config_ok():  # pragma: no cover - trivial
        return {"passed": True}

    monkeypatch.setattr(SecurityAuditor, "_check_ssl", staticmethod(ssl_ok))
    monkeypatch.setattr(SecurityAuditor, "_check_headers", staticmethod(headers_fail))
    monkeypatch.setattr(SecurityAuditor, "_check_cors", staticmethod(cors_ok))
    monkeypatch.setattr(SecurityAuditor, "_check_config", staticmethod(config_ok))

    results = SecurityAuditor.run_audit("full")
    assert results["passed"] is False
    assert results["checks"]["headers"]["passed"] is False
    assert results["summary"] == "Security audit failed"


def test_run_audit_quick_pass(monkeypatch):
    def ssl_ok():  # pragma: no cover - trivial
        return {"passed": True}

    def headers_ok():  # pragma: no cover - trivial
        return {"passed": True}

    monkeypatch.setattr(SecurityAuditor, "_check_ssl", staticmethod(ssl_ok))
    monkeypatch.setattr(SecurityAuditor, "_check_headers", staticmethod(headers_ok))

    results = SecurityAuditor.run_audit("quick")
    assert results["passed"] is True
    assert results["summary"] == "Security audit passed"


def test_run_audit_ssl_fail(monkeypatch):
    def ssl_fail():  # pragma: no cover - trivial
        return {"passed": False}

    monkeypatch.setattr(SecurityAuditor, "_check_ssl", staticmethod(ssl_fail))

    results = SecurityAuditor.run_audit("ssl")
    assert results["passed"] is False
    assert results["checks"]["ssl"]["passed"] is False


def test_run_audit_cors_fail(monkeypatch):
    def cors_fail():  # pragma: no cover - trivial
        return {"passed": False}

    monkeypatch.setattr(SecurityAuditor, "_check_cors", staticmethod(cors_fail))

    results = SecurityAuditor.run_audit("cors")
    assert results["passed"] is False
    assert results["checks"]["cors"]["passed"] is False


def test_run_audit_config_fail(monkeypatch):
    def config_fail():  # pragma: no cover - trivial
        return {"passed": False}

    monkeypatch.setattr(SecurityAuditor, "_check_config", staticmethod(config_fail))

    results = SecurityAuditor.run_audit("config")
    assert results["passed"] is False
    assert results["checks"]["config"]["passed"] is False


def test_check_ssl_uses_registry_and_validator(monkeypatch):
    # Registry reports valid
    monkeypatch.setattr(
        monitoring_mod,
        "get_certificate_info",
        lambda action="status": {"valid": True, "warnings": ["w"]},
    )

    result = SecurityAuditor._check_ssl()
    assert result["passed"] is True
    assert result["warnings"] == ["w"]

    # Registry invalid -> fallback to SslValidator.check_status
    def registry_invalid(action="status"):  # pragma: no cover - trivial
        return {"valid": False}

    def ssl_result():  # pragma: no cover - trivial
        return {"valid": False, "warnings": ["w2"], "errors": ["e2"]}

    monkeypatch.setattr(monitoring_mod, "get_certificate_info", registry_invalid)
    monkeypatch.setattr(
        monitoring_mod.SslValidator,
        "check_status",
        staticmethod(lambda domain=None: ssl_result()),
    )

    result = SecurityAuditor._check_ssl()
    assert result["passed"] is False
    assert "e2" in result["errors"]


def test_check_headers_uses_client_and_validator(monkeypatch):
    class DummyResponse:
        def __init__(self, headers):  # pragma: no cover - trivial
            self.headers = headers

    class DummyClient:
        def get(self, path):  # pragma: no cover - trivial
            return DummyResponse(
                {
                    "X-Frame-Options": "DENY",
                    "X-Content-Type-Options": "nosniff",
                }
            )

    def fake_get_config(request):  # pragma: no cover - trivial
        return {
            "headers": {
                "x_frame_options": "DENY",
                "x_content_type_options": "nosniff",
            }
        }

    monkeypatch.setattr(monitoring_mod, "Client", DummyClient)
    monkeypatch.setattr(
        monitoring_mod.SecurityEngine,
        "get_config",
        staticmethod(fake_get_config),
    )

    result = SecurityAuditor._check_headers()
    assert result["passed"] is True
    assert "All security headers present" in result["message"]


def test_check_headers_failure(monkeypatch):
    class DummyResponse:
        def __init__(self, headers):  # pragma: no cover - trivial
            self.headers = headers

    class DummyClient:
        def get(self, path):  # pragma: no cover - trivial
            return DummyResponse({})  # No headers at all

    def fake_get_config(request):  # pragma: no cover - trivial
        return {
            "headers": {
                "x_frame_options": "DENY",
                "x_content_type_options": "nosniff",
            }
        }

    class DummyValidator:
        @staticmethod
        def validate_headers(resp_headers, expected_cfg):  # pragma: no cover - trivial
            return {
                "passed": False,
                "missing": ["X-Frame-Options"],
                "incorrect": [],
                "details": {},
            }

    monkeypatch.setattr(monitoring_mod, "Client", DummyClient)
    monkeypatch.setattr(
        monitoring_mod.SecurityEngine,
        "get_config",
        staticmethod(fake_get_config),
    )
    monkeypatch.setattr(
        monitoring_mod,
        "SecurityHeadersValidator",
        DummyValidator,
    )

    result = SecurityAuditor._check_headers()
    assert result["passed"] is False
    assert "Missing or incorrect security headers" in result["message"]


def test_check_cors_pass_and_fail(monkeypatch):
    def cfg_with_cors(request):  # pragma: no cover - trivial
        return {"cors": {"allowed_origins": ["https://client"]}}

    def cfg_without_cors(request):  # pragma: no cover - trivial
        return {"cors": {"allowed_origins": []}}

    monkeypatch.setattr(
        monitoring_mod.SecurityEngine,
        "get_config",
        staticmethod(cfg_with_cors),
    )
    result = SecurityAuditor._check_cors()
    assert result["passed"] is True

    monkeypatch.setattr(
        monitoring_mod.SecurityEngine,
        "get_config",
        staticmethod(cfg_without_cors),
    )
    result = SecurityAuditor._check_cors()
    assert result["passed"] is False
    assert "CORS not configured" in result["errors"][0]


def test_check_config_pass_and_fail(monkeypatch, settings):
    # Pass case: local env with sane Django settings
    def cfg_local(request):  # pragma: no cover - trivial
        return {
            "env_type": EnvironmentType.LOCAL,
            "security_level": SecurityLevel.MINIMAL,
        }

    monkeypatch.setattr(
        monitoring_mod.SecurityEngine,
        "get_config",
        staticmethod(cfg_local),
    )

    settings.DEBUG = False
    settings.ALLOWED_HOSTS = ["testserver"]
    settings.SECRET_KEY = "safe-key"

    result = SecurityAuditor._check_config()
    assert result["passed"] is True

    # Fail case: production-like env with bad settings
    def cfg_prod(request):  # pragma: no cover - trivial
        return {
            "env_type": EnvironmentType.PRODUCTION,
            "security_level": SecurityLevel.STRICT,
        }

    monkeypatch.setattr(
        monitoring_mod.SecurityEngine,
        "get_config",
        staticmethod(cfg_prod),
    )

    settings.DEBUG = True
    settings.ALLOWED_HOSTS = []
    settings.SECRET_KEY = "dev-only-insecure-key"

    result = SecurityAuditor._check_config()
    assert result["passed"] is False
    assert any("DEBUG mode enabled" in e for e in result["errors"])
    assert any("ALLOWED_HOSTS" in e for e in result["errors"])
    assert any("Insecure SECRET_KEY" in e for e in result["errors"])
