"""Tests for CorsValidator (CORS request validation and headers)."""

from django.http import HttpRequest

from sopira_magic.apps.security.validators.cors import CorsValidator


def make_request(method: str = "GET", origin: str | None = None) -> HttpRequest:
    req = HttpRequest()
    req.method = method
    req.META = {}
    if origin is not None:
        req.META["HTTP_ORIGIN"] = origin
    return req


def test_validate_allows_when_no_origin_header():
    request = make_request(origin=None)
    cors_cfg = {"allowed_origins": ["https://example.com"]}

    assert CorsValidator.validate(request, cors_cfg) is True


def test_validate_exact_origin_and_wildcard_match():
    origin = "https://foo.sopira.com"
    request = make_request(origin=origin)

    cors_cfg = {
        "allowed_origins": [
            "https://api.example.com",
            "https://*.sopira.com",
        ]
    }

    assert CorsValidator.validate(request, cors_cfg) is True


def test_validate_rejects_disallowed_origin():
    origin = "https://evil.com"
    request = make_request(origin=origin)

    cors_cfg = {"allowed_origins": ["https://good.com"]}
    assert CorsValidator.validate(request, cors_cfg) is False


def test_get_headers_for_simple_and_preflight_requests():
    origin = "https://client.example.com"

    cors_cfg = {
        "allowed_origins": [origin],
        "allowed_methods": ["GET", "POST"],
        "allowed_headers": ["Authorization"],
        "exposed_headers": ["X-Total-Count"],
        "allow_credentials": True,
        "max_age": 600,
    }

    # Simple GET request -> origin + credentials only
    get_request = make_request(method="GET", origin=origin)
    headers = CorsValidator.get_headers(get_request, cors_cfg)
    assert headers["Access-Control-Allow-Origin"] == origin
    assert headers["Access-Control-Allow-Credentials"] == "true"
    assert "Access-Control-Allow-Methods" not in headers

    # OPTIONS preflight -> full header set
    options_request = make_request(method="OPTIONS", origin=origin)
    preflight_headers = CorsValidator.get_headers(options_request, cors_cfg)

    assert preflight_headers["Access-Control-Allow-Origin"] == origin
    assert (
        preflight_headers["Access-Control-Allow-Methods"]
        == "GET, POST"
    )
    assert (
        preflight_headers["Access-Control-Allow-Headers"]
        == "Authorization"
    )
    assert (
        preflight_headers["Access-Control-Expose-Headers"]
        == "X-Total-Count"
    )
    assert preflight_headers["Access-Control-Max-Age"] == "600"
