"""Tests for SecurityHeadersValidator."""

from sopira_magic.apps.security.validators.headers import SecurityHeadersValidator


def test_get_headers_uses_config_and_defaults():
    cfg = {
        "x_frame_options": "SAMEORIGIN",
        # x_content_type_options intentionally omitted to test default
        "x_xss_protection": "1; mode=block",
    }

    headers = SecurityHeadersValidator.get_headers(cfg)

    # Config-driven headers
    assert headers["X-Frame-Options"] == "SAMEORIGIN"
    assert headers["X-XSS-Protection"] == "1; mode=block"

    # Defaults filled in
    assert headers["X-Content-Type-Options"] == "nosniff"


def test_validate_headers_success_and_failures():
    expected_cfg = {
        "x_frame_options": "DENY",
        "x_content_type_options": "nosniff",
    }

    # All good
    response_headers = {
        "X-Frame-Options": "DENY",
        "X-Content-Type-Options": "nosniff",
    }

    ok = SecurityHeadersValidator.validate_headers(response_headers, expected_cfg)
    assert ok["passed"] is True
    assert ok["missing"] == []
    assert ok["incorrect"] == []

    # Missing header
    response_headers = {"X-Frame-Options": "DENY"}
    res = SecurityHeadersValidator.validate_headers(response_headers, expected_cfg)
    assert res["passed"] is False
    assert "X-Content-Type-Options" in res["missing"]

    # Incorrect value
    response_headers = {
        "X-Frame-Options": "ALLOW-FROM",
        "X-Content-Type-Options": "nosniff",
    }
    res = SecurityHeadersValidator.validate_headers(response_headers, expected_cfg)
    assert res["passed"] is False
    assert "X-Frame-Options" in res["incorrect"]
