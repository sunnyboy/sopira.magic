"""Tests for CspValidator.build_csp_header."""

from sopira_magic.apps.security.validators.csp import CspValidator


def test_build_csp_header_from_full_config():
    cfg = {
        "default_src": ["'self'"],
        "script_src": ["'self'", "'unsafe-inline'"],
        "style_src": ["'self'"],
        "img_src": ["https://images.example.com"],
        "connect_src": ["'self'"],
        "font_src": ["https://fonts.example.com"],
        "object_src": ["'none'"],
        "media_src": ["'self'"],
        "frame_src": ["'none'"],
        "sandbox": [""],  # special-case -> "sandbox" directive
        "report_uri": "/csp-report/",
    }

    header = CspValidator.build_csp_header(cfg)

    assert "default-src 'self'" in header
    assert "script-src 'self' 'unsafe-inline'" in header
    assert "img-src https://images.example.com" in header
    assert "sandbox" in header
    assert "report-uri /csp-report/" in header


def test_build_csp_header_empty_config_returns_empty_string():
    assert CspValidator.build_csp_header({}) == ""
