"""Unit tests for SecurityUtils helper functions."""

from types import SimpleNamespace

from sopira_magic.apps.security.utils import SecurityUtils


def test_is_safe_origin_exact_and_wildcard_and_suffix():
    allowed = [
        "https://app.example.com",
        "https://*.sopira.com",
        ".trusted.local",
    ]

    assert SecurityUtils.is_safe_origin("https://app.example.com", allowed) is True
    assert (
        SecurityUtils.is_safe_origin("https://foo.sopira.com", allowed)
        is True
    )
    assert (
        SecurityUtils.is_safe_origin("https://my.trusted.local", allowed)
        is True
    )

    # Invalid or disallowed origins
    assert SecurityUtils.is_safe_origin("", allowed) is False
    assert SecurityUtils.is_safe_origin("ftp://example.com", allowed) is False
    assert (
        SecurityUtils.is_safe_origin("https://evil.com", allowed)
        is False
    )


def test_validate_ip_address_valid_and_invalid():
    assert SecurityUtils.validate_ip_address("127.0.0.1") is True
    assert SecurityUtils.validate_ip_address("::1") is True
    assert SecurityUtils.validate_ip_address("not-an-ip") is False


def test_get_client_ip_prefers_forwarded_for_then_remote():
    # X-Forwarded-For with valid IP is preferred
    request = SimpleNamespace(META={"HTTP_X_FORWARDED_FOR": "1.2.3.4, 5.6.7.8"})
    assert SecurityUtils.get_client_ip(request) == "1.2.3.4"

    # Falls back to REMOTE_ADDR when X-Forwarded-For missing/invalid
    request = SimpleNamespace(META={"REMOTE_ADDR": "9.8.7.6"})
    assert SecurityUtils.get_client_ip(request) == "9.8.7.6"

    # Invalid values -> None
    request = SimpleNamespace(META={"REMOTE_ADDR": "invalid"})
    assert SecurityUtils.get_client_ip(request) is None


def test_sanitize_input_trims_limits_and_strips_unprintable():
    raw = "  hello\x00world\n" + "x" * 10
    sanitized = SecurityUtils.sanitize_input(raw, max_length=8)

    # Stripped, truncated, and null bytes removed
    assert "\x00" not in sanitized
    assert sanitized.startswith("hello")
    assert len(sanitized) <= 8


def test_sanitize_input_empty_returns_empty_string():
    assert SecurityUtils.sanitize_input("") == ""


def test_generate_security_report_contains_core_sections():
    audit_results = {
        "timestamp": "2024-01-01T00:00:00",
        "check_type": "quick",
        "passed": False,
        "summary": "Security audit failed",
        "checks": {
            "ssl": {
                "passed": False,
                "message": "SSL certificate is NOT valid",
                "warnings": ["expiring soon"],
                "errors": ["expired"],
            }
        },
    }

    report = SecurityUtils.generate_security_report(audit_results)

    assert "SECURITY AUDIT REPORT" in report
    assert "SSL" in report
    assert "Warnings:" in report
    assert "Errors:" in report
    assert "SUMMARY" in report
