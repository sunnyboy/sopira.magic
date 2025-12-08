"""Tests for security type definitions (enums and typed dicts)."""

import pytest

from sopira_magic.apps.security.types import (
    EnvironmentType,
    SecurityLevel,
    CorsConfig,
    CspConfig,
    SslConfig,
    SecurityHeaders,
    EnvironmentConfig,
)


def test_environment_type_values_and_coercion():
    """EnvironmentType has stable values and supports string coercion."""

    assert EnvironmentType.LOCAL.value == "local"
    assert EnvironmentType.DEVELOPMENT.value == "dev"
    assert EnvironmentType.PRODUCTION.value == "production"

    assert EnvironmentType("local") is EnvironmentType.LOCAL
    assert EnvironmentType("dev") is EnvironmentType.DEVELOPMENT
    assert EnvironmentType("production") is EnvironmentType.PRODUCTION

    with pytest.raises(ValueError):
        EnvironmentType("unknown-env")


def test_security_level_values_and_coercion():
    """SecurityLevel enum behaves as expected for string values."""

    assert SecurityLevel.MINIMAL.value == "minimal"
    assert SecurityLevel.STANDARD.value == "standard"
    assert SecurityLevel.STRICT.value == "strict"

    assert SecurityLevel("minimal") is SecurityLevel.MINIMAL
    assert SecurityLevel("strict") is SecurityLevel.STRICT

    with pytest.raises(ValueError):
        SecurityLevel("invalid-level")


def test_environment_config_typed_dict_shape():
    """EnvironmentConfig behaves like a mapping with expected keys/types."""

    cors: CorsConfig = {
        "allowed_origins": ["http://localhost"],
        "allowed_methods": ["GET"],
        "allowed_headers": ["*"],
        "allow_credentials": True,
        "max_age": 10,
    }

    csp: CspConfig = {
        "default_src": ["'self'"],
        "script_src": ["'self'"],
        "style_src": ["'self'"],
    }

    ssl: SslConfig = {
        "enabled": False,
        "redirect_http": False,
        "hsts_max_age": 0,
    }

    headers: SecurityHeaders = {
        "x_frame_options": "DENY",
        "x_content_type_options": "nosniff",
    }

    env_cfg: EnvironmentConfig = {
        "name": "Test Env",
        "env_type": EnvironmentType.LOCAL,
        "security_level": SecurityLevel.MINIMAL,
        "force_https": False,
        "allowed_hosts": ["localhost"],
        "cors": cors,
        "csp": csp,
        "ssl": ssl,
        "headers": headers,
    }

    assert env_cfg["env_type"] is EnvironmentType.LOCAL
    assert env_cfg["security_level"] is SecurityLevel.MINIMAL
    assert "allowed_origins" in env_cfg["cors"]
    assert "default_src" in env_cfg["csp"]
    assert "x_frame_options" in env_cfg["headers"]
