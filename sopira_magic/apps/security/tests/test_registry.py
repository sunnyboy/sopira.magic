"""Tests for the security registry (environment, certificates, headers)."""

import os

import pytest

from sopira_magic.apps.security import registry


def test_get_environment_falls_back_to_env_var(monkeypatch):
    """When no detector is registered, DJANGO_ENV is used with a safe fallback."""

    # Ensure detector is cleared
    monkeypatch.setattr(registry, "_environment_detector", None)

    monkeypatch.setenv("DJANGO_ENV", "production")
    assert registry.get_environment() == "production"

    monkeypatch.setenv("DJANGO_ENV", "unknown-env")
    # Unknown values fall back to "local"
    assert registry.get_environment() == "local"


def test_register_environment_detector_and_is_configured(monkeypatch):
    monkeypatch.setattr(registry, "_environment_detector", None)

    assert registry.is_registry_configured() is False

    def detector(request=None):  # pragma: no cover - trivial callback
        return "dev"

    registry.register_environment_detector(detector)
    assert registry.is_registry_configured() is True
    assert registry.get_environment(None) == "dev"


def test_get_certificate_info_without_provider_returns_placeholder(monkeypatch):
    monkeypatch.setattr(registry, "_certificate_provider", None)

    info = registry.get_certificate_info("status", "example.com")
    assert info["valid"] is False
    assert info["managed"] is False
    assert "no_certificate_provider_registered" in info["reason"]


def test_register_certificate_provider_is_used(monkeypatch):
    monkeypatch.setattr(registry, "_certificate_provider", None)

    calls = {}

    def provider(action, domain=None):  # pragma: no cover - simple callback
        calls["action"] = action
        calls["domain"] = domain
        return {"valid": True, "managed": True, "domain": domain}

    registry.register_certificate_provider(provider)

    info = registry.get_certificate_info("status", "example.com")
    assert info["valid"] is True
    assert info["managed"] is True
    assert info["domain"] == "example.com"
    assert calls == {"action": "status", "domain": "example.com"}


def test_get_custom_headers_without_and_with_provider(monkeypatch):
    monkeypatch.setattr(registry, "_custom_header_provider", None)

    class DummyRequest:
        pass

    request = DummyRequest()

    # No provider -> empty dict
    assert registry.get_custom_headers(request) == {}

    # Register provider and ensure headers are returned
    def header_provider(req):  # pragma: no cover - simple callback
        assert req is request
        return {"X-Custom": "value"}

    registry.register_custom_header_provider(header_provider)

    headers = registry.get_custom_headers(request)
    assert headers == {"X-Custom": "value"}


def test_register_security_auditor(monkeypatch):
    monkeypatch.setattr(registry, "_security_auditor", None)

    def auditor(check_type):  # pragma: no cover - trivial
        return {"check_type": check_type}

    registry.register_security_auditor(auditor)
    # No direct getter, but internal state should now hold the callback
    assert registry._security_auditor is auditor
