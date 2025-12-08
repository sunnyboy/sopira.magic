"""Tests for security management commands."""

import json
from io import StringIO

import pytest
from django.core.management import call_command

from sopira_magic.apps.security.management.commands import (
    security_audit as cmd_audit,
    security_test as cmd_test,
    ssl_check as cmd_ssl,
)


def test_security_audit_command_pass_and_fail(monkeypatch):
    def audit_pass(check_type):  # pragma: no cover - trivial
        return {
            "passed": True,
            "summary": "All good",
            "timestamp": "2024-01-01T00:00:00",
            "checks": {
                "ssl": {
                    "passed": True,
                    "message": "ok",
                    "warnings": [],
                    "errors": [],
                    "details": {},
                }
            },
        }

    out = StringIO()
    monkeypatch.setattr(
        cmd_audit.SecurityEngine,
        "security_audit",
        staticmethod(audit_pass),
    )

    call_command("security_audit", "--check", "quick", stdout=out)
    text = out.getvalue()
    assert "Security Audit PASSED" in text
    assert "SSL check" in text

    def audit_fail(check_type):  # pragma: no cover - trivial
        return {
            "passed": False,
            "summary": "Problems found",
            "timestamp": "2024-01-01T00:00:00",
            "checks": {
                "ssl": {
                    "passed": False,
                    "message": "bad",
                    "warnings": [],
                    "errors": ["e1"],
                    "details": {},
                }
            },
        }

    out = StringIO()
    monkeypatch.setattr(
        cmd_audit.SecurityEngine,
        "security_audit",
        staticmethod(audit_fail),
    )

    call_command("security_audit", "--check", "quick", "--fix", stdout=out)
    text = out.getvalue()
    assert "Security Audit FAILED" in text
    assert "Fix mode is not implemented yet" in text


def test_security_audit_command_verbose_with_warnings_and_details(monkeypatch):
    def audit_with_warnings(check_type):  # pragma: no cover - trivial
        return {
            "passed": True,
            "summary": "All good",
            "timestamp": "2024-01-01T00:00:00",
            "checks": {
                "ssl": {
                    "passed": True,
                    "message": "ok",
                    "warnings": ["w1"],
                    "errors": [],
                    "details": {"k": "v"},
                }
            },
        }

    out = StringIO()
    monkeypatch.setattr(
        cmd_audit.SecurityEngine,
        "security_audit",
        staticmethod(audit_with_warnings),
    )

    call_command("security_audit", "--check", "quick", "--verbose", stdout=out)
    text = out.getvalue()
    assert "Warning:" in text
    assert "Details:" in text


def test_security_test_command_success_and_validation_failure(monkeypatch):
    # Success case
    monkeypatch.setattr(cmd_test, "validate_security_config", lambda: [])

    def quick_ok(check_type):  # pragma: no cover - trivial
        return {
            "passed": True,
            "summary": "ok",
            "timestamp": "2024-01-01T00:00:00",
            "checks": {},
        }

    monkeypatch.setattr(
        cmd_test.SecurityEngine,
        "security_audit",
        staticmethod(quick_ok),
    )

    out = StringIO()
    call_command("security_test", stdout=out)
    text = out.getvalue()
    assert "Security config validation PASSED" in text
    assert "Quick security audit PASSED" in text

    # Validation failure
    monkeypatch.setattr(cmd_test, "validate_security_config", lambda: ["err"])

    out = StringIO()
    with pytest.raises(SystemExit) as exc:
        call_command("security_test", stdout=out)

    assert exc.value.code == 1
    text = out.getvalue()
    assert "Security config validation FAILED" in text


def test_security_test_command_audit_failure(monkeypatch):
    monkeypatch.setattr(cmd_test, "validate_security_config", lambda: [])

    def quick_fail(check_type):  # pragma: no cover - trivial
        return {
            "passed": False,
            "summary": "bad",
            "timestamp": "2024-01-01T00:00:00",
            "checks": {},
        }

    monkeypatch.setattr(
        cmd_test.SecurityEngine,
        "security_audit",
        staticmethod(quick_fail),
    )

    out = StringIO()
    with pytest.raises(SystemExit) as exc:
        call_command("security_test", stdout=out)

    assert exc.value.code == 2
    text = out.getvalue()
    assert "Quick security audit FAILED" in text


def test_ssl_check_command_valid_invalid_and_json(monkeypatch):
    def ssl_valid(domain=None):  # pragma: no cover - trivial
        return {"valid": True, "domain": domain, "extra": 1}

    def ssl_invalid(domain=None):  # pragma: no cover - trivial
        return {"valid": False, "domain": domain, "errors": ["e1"]}

    # Valid
    monkeypatch.setattr(
        cmd_ssl.SslValidator,
        "check_status",
        staticmethod(ssl_valid),
    )

    out = StringIO()
    call_command("ssl_check", "--domain", "example.com", stdout=out)
    text = out.getvalue()
    assert "SSL certificate is valid" in text
    assert "domain: example.com" in text

    # Invalid
    monkeypatch.setattr(
        cmd_ssl.SslValidator,
        "check_status",
        staticmethod(ssl_invalid),
    )

    out = StringIO()
    call_command("ssl_check", "--domain", "bad.example.com", stdout=out)
    text = out.getvalue()
    assert "SSL certificate is NOT valid" in text

    # JSON output
    monkeypatch.setattr(
        cmd_ssl.SslValidator,
        "check_status",
        staticmethod(ssl_valid),
    )

    out = StringIO()
    call_command("ssl_check", "--domain", "json.example.com", "--json", stdout=out)
    data = json.loads(out.getvalue())
    assert data["domain"] == "json.example.com"
