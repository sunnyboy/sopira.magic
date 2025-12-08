"""Tests for SslValidator behavior (no real network calls)."""

import datetime as dt

import pytest

from sopira_magic.apps.security.validators import ssl as ssl_validator_mod
from sopira_magic.apps.security.validators.ssl import SslValidator


class _FakeSocket:
    def __enter__(self):  # pragma: no cover - trivial
        return self

    def __exit__(self, exc_type, exc, tb):  # pragma: no cover - trivial
        return False


class _FakeWrappedSocket(_FakeSocket):
    def __init__(self, cert, cipher_name):
        self._cert = cert
        self._cipher_name = cipher_name

    def getpeercert(self):
        return self._cert

    def cipher(self):
        return (self._cipher_name, None, None)


class _FakeContext:
    def __init__(self, cert, cipher_name):
        self._cert = cert
        self._cipher_name = cipher_name

    def wrap_socket(self, sock, server_hostname=None):  # pragma: no cover - trivial
        return _FakeWrappedSocket(self._cert, self._cipher_name)


def _build_cert(days_delta: int) -> dict:
    expires = dt.datetime.now() + dt.timedelta(days=days_delta)
    not_after = expires.strftime("%b %d %H:%M:%S %Y GMT")
    return {
        "notAfter": not_after,
        # Shape mimics what ssl.getpeercert() returns sufficiently for our usage
        # issuer = ((('organizationName', 'Test CA'),), ...)
        "issuer": ((("organizationName", "Test CA"),),),
        "subject": ((("commonName", "example.com"),),),
        "subjectAltName": [("DNS", "example.com"), ("DNS", "www.example.com")],
        "serialNumber": "01",
        "version": 3,
    }


def test_check_status_success_with_warning(monkeypatch):
    cert = _build_cert(days_delta=10)  # <30 days triggers warning

    def fake_create_default_context():  # pragma: no cover - trivial
        return _FakeContext(cert, "TLS_AES_256_GCM_SHA384")

    def fake_create_connection(addr, timeout=10):  # pragma: no cover - trivial
        return _FakeSocket()

    monkeypatch.setattr(ssl_validator_mod.ssl, "create_default_context", fake_create_default_context)
    monkeypatch.setattr(ssl_validator_mod.socket, "create_connection", fake_create_connection)

    result = SslValidator.check_status("example.com")

    assert result["valid"] is True
    assert result["domain"] == "example.com"
    assert result["days_remaining"] >= 0
    assert any("30 days" in w for w in result["warnings"])


def test_check_status_uses_default_domain_and_expired_and_soon(monkeypatch):
    # Expired certificate (<0 days)
    expired_cert = _build_cert(days_delta=-1)

    def ctx_expired():  # pragma: no cover - trivial
        return _FakeContext(expired_cert, "TLS_AES_256_GCM_SHA384")

    def conn_expired(addr, timeout=10):  # pragma: no cover - trivial
        return _FakeSocket()

    monkeypatch.setattr(ssl_validator_mod.ssl, "create_default_context", ctx_expired)
    monkeypatch.setattr(ssl_validator_mod.socket, "create_connection", conn_expired)
    monkeypatch.setattr(ssl_validator_mod.socket, "getfqdn", lambda: "expired.example.com")

    result = SslValidator.check_status(None)
    assert result["domain"] == "expired.example.com"
    assert result["valid"] is False
    assert any("Certificate has expired" in e for e in result["errors"])

    # <7 days remaining triggers different warning branch
    soon_cert = _build_cert(days_delta=3)

    def ctx_soon():  # pragma: no cover - trivial
        return _FakeContext(soon_cert, "TLS_AES_256_GCM_SHA384")

    def conn_soon(addr, timeout=10):  # pragma: no cover - trivial
        return _FakeSocket()

    monkeypatch.setattr(ssl_validator_mod.ssl, "create_default_context", ctx_soon)
    monkeypatch.setattr(ssl_validator_mod.socket, "create_connection", conn_soon)

    result = SslValidator.check_status("soon.example.com")
    assert result["valid"] is True
    assert any("7 days" in w for w in result["warnings"])


def test_check_status_ssl_error(monkeypatch):
    class DummyError(ssl_validator_mod.ssl.SSLError):
        pass

    def failing_connection(addr, timeout=10):  # pragma: no cover - trivial
        raise DummyError("bad cert")

    monkeypatch.setattr(ssl_validator_mod.socket, "create_connection", failing_connection)

    result = SslValidator.check_status("bad.example.com")
    assert result["valid"] is False
    assert any("SSL error" in e for e in result["errors"])


def test_check_status_timeout(monkeypatch):
    def timeout_connection(addr, timeout=10):  # pragma: no cover - trivial
        raise ssl_validator_mod.socket.timeout()

    monkeypatch.setattr(ssl_validator_mod.socket, "create_connection", timeout_connection)

    result = SslValidator.check_status("timeout.example.com")
    assert result["valid"] is False
    assert any("Connection timeout" in e for e in result["errors"])


def test_should_enforce_https_and_recommendations():
    cfg = {"enabled": True, "redirect_http": True}
    assert SslValidator.should_enforce_https(cfg) is True

    cfg = {"enabled": True, "redirect_http": False}
    assert SslValidator.should_enforce_https(cfg) is False

    # Invalid certificate -> immediate recommendation
    recs = SslValidator.get_recommendations({"valid": False})
    assert "invalid or expired" in recs[0]

    # Valid but expiring soon and weak cipher
    recs = SslValidator.get_recommendations(
        {
            "valid": True,
            "days_remaining": 5,
            "algorithm": "RC4-MD5",
        }
    )
    assert any("Renew certificate" in r for r in recs)
    assert any("weak cipher" in r for r in recs)
