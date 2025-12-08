"""Unit tests pre SSOT validation."""

from unittest.mock import patch

import pytest
from django.test import TestCase

from sopira_magic.apps.security.config import SECURITY_CONFIG_MATRIX, EnvironmentType
from sopira_magic.apps.security.validation import validate_security_config


class TestSecurityConfigValidation(TestCase):
    """Testy pre validáciu SSOT security konfigurácie."""

    def test_validate_empty_config(self):
        """Validácia s prázdnou konfiguráciou vráti chybu."""

        with patch(
            "sopira_magic.apps.security.validation.SECURITY_CONFIG_MATRIX", {}
        ):
            errors = validate_security_config()
            assert len(errors) > 0
            assert any("No environment configurations" in e for e in errors)

    def test_validate_missing_required_fields(self):
        """Validácia s chýbajúcimi povinnými poľami."""

        invalid_config = {
            EnvironmentType.LOCAL: {
                "name": "Test",
            }
        }

        with patch(
            "sopira_magic.apps.security.validation.SECURITY_CONFIG_MATRIX",
            invalid_config,
        ):
            errors = validate_security_config()
            assert len(errors) > 0
            assert any("Missing required field" in e for e in errors)

    def test_validate_invalid_security_level(self):
        """Validácia s neplatným security level."""

        invalid_config = {
            EnvironmentType.LOCAL: {
                **SECURITY_CONFIG_MATRIX[EnvironmentType.LOCAL],
                "security_level": "INVALID_LEVEL",
            }
        }

        with patch(
            "sopira_magic.apps.security.validation.SECURITY_CONFIG_MATRIX",
            invalid_config,
        ):
            errors = validate_security_config()
            assert len(errors) > 0
            assert any("Invalid security level" in e for e in errors)

    def test_validate_invalid_environment_type(self):
        """Validácia s nezhodujúcim sa environment type."""

        invalid_config = {
            EnvironmentType.LOCAL: {
                **SECURITY_CONFIG_MATRIX[EnvironmentType.LOCAL],
                "env_type": EnvironmentType.PRODUCTION,
            }
        }

        with patch(
            "sopira_magic.apps.security.validation.SECURITY_CONFIG_MATRIX",
            invalid_config,
        ):
            errors = validate_security_config()
            assert len(errors) > 0
            assert any("does not match key" in e for e in errors)

    def test_validate_cors_credentials_with_wildcard(self):
        """CORS allow_credentials=True s wildcard origin je chyba."""

        invalid_config = {
            EnvironmentType.LOCAL: {
                **SECURITY_CONFIG_MATRIX[EnvironmentType.LOCAL],
                "cors": {
                    **SECURITY_CONFIG_MATRIX[EnvironmentType.LOCAL]["cors"],
                    "allow_credentials": True,
                    "allowed_origins": ["*"],
                },
            }
        }

        with patch(
            "sopira_magic.apps.security.validation.SECURITY_CONFIG_MATRIX",
            invalid_config,
        ):
            errors = validate_security_config()
            assert len(errors) > 0
            assert any(
                "CORS allow_credentials with wildcard" in e for e in errors
            )

    def test_validate_ssl_configuration(self):
        """Validácia SSL konfigurácie - neplatný HSTS max_age."""

        invalid_config = {
            EnvironmentType.LOCAL: {
                **SECURITY_CONFIG_MATRIX[EnvironmentType.LOCAL],
                "ssl": {
                    **SECURITY_CONFIG_MATRIX[EnvironmentType.LOCAL]["ssl"],
                    "enabled": True,
                    "hsts_max_age": -1,
                },
            }
        }

        with patch(
            "sopira_magic.apps.security.validation.SECURITY_CONFIG_MATRIX",
            invalid_config,
        ):
            errors = validate_security_config()
            assert len(errors) > 0
            assert any("Invalid HSTS max_age" in e for e in errors)

    def test_validate_csp_configuration(self):
        """Validácia CSP konfigurácie - prázdny default_src."""

        invalid_config = {
            EnvironmentType.LOCAL: {
                **SECURITY_CONFIG_MATRIX[EnvironmentType.LOCAL],
                "csp": {"default_src": []},
            }
        }

        with patch(
            "sopira_magic.apps.security.validation.SECURITY_CONFIG_MATRIX",
            invalid_config,
        ):
            errors = validate_security_config()
            assert len(errors) > 0
            assert any("CSP default_src cannot be empty" in e for e in errors)

    def test_validate_duplicate_origins(self):
        """Validácia duplicitných CORS origins."""

        invalid_config = {
            EnvironmentType.LOCAL: {
                **SECURITY_CONFIG_MATRIX[EnvironmentType.LOCAL],
                "cors": {
                    **SECURITY_CONFIG_MATRIX[EnvironmentType.LOCAL]["cors"],
                    "allowed_origins": [
                        "http://localhost:5173",
                        "http://localhost:5173",
                    ],
                },
            }
        }

        with patch(
            "sopira_magic.apps.security.validation.SECURITY_CONFIG_MATRIX",
            invalid_config,
        ):
            errors = validate_security_config()
            assert len(errors) > 0
            assert any("Duplicate CORS origin" in e for e in errors)

    def test_validate_invalid_cors_type(self):
        """CORS allowed_origins musí byť list, inak chyba."""

        invalid_config = {
            EnvironmentType.LOCAL: {
                **SECURITY_CONFIG_MATRIX[EnvironmentType.LOCAL],
                "cors": {
                    **SECURITY_CONFIG_MATRIX[EnvironmentType.LOCAL]["cors"],
                    "allowed_origins": "not-a-list",
                },
            }
        }

        with patch(
            "sopira_magic.apps.security.validation.SECURITY_CONFIG_MATRIX",
            invalid_config,
        ):
            errors = validate_security_config()
            assert any("invalid cors.allowed_origins" in e for e in errors)

    def test_validate_invalid_headers_type(self):
        """Headers konfigurácia musí byť dict, inak chyba."""

        invalid_config = {
            EnvironmentType.LOCAL: {
                **SECURITY_CONFIG_MATRIX[EnvironmentType.LOCAL],
                "headers": "not-a-dict",
            }
        }

        with patch(
            "sopira_magic.apps.security.validation.SECURITY_CONFIG_MATRIX",
            invalid_config,
        ):
            errors = validate_security_config()
            assert any("invalid headers configuration" in e for e in errors)

    def test_validate_successful_configuration(self):
        """Platná konfigurácia nevracia chyby."""

        errors = validate_security_config()
        assert errors == [], f"Valid configuration should have no errors: {errors}"

    def test_validate_all_environments_present(self):
        """Všetky EnvironmentType musia mať konfiguráciu."""

        errors = validate_security_config()
        assert errors == []

        for env_type in EnvironmentType:
            if env_type not in SECURITY_CONFIG_MATRIX:
                pytest.fail(f"Missing configuration for environment: {env_type}")
