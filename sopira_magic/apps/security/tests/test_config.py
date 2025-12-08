"""Unit tests pre SSOT Security Configuration.

Testuje správnosť konfigurácie pre všetky environmenty.
"""

import copy
import time
from typing import Dict, List

import pytest
from django.test import TestCase

from sopira_magic.apps.security.types import EnvironmentType, SecurityLevel
from sopira_magic.apps.security.config import SECURITY_CONFIG_MATRIX, EnvironmentConfig


class TestSecurityConfigSSOT(TestCase):
    """Testy pre SINGLE SOURCE OF TRUTH - Security Configuration Matrix."""

    def test_config_matrix_structure(self):
        """Konfiguračná matica má správnu štruktúru."""

        expected_envs = [
            EnvironmentType.LOCAL,
            EnvironmentType.DEVELOPMENT,
            EnvironmentType.PRODUCTION,
            EnvironmentType.CLOUD,
        ]

        for env in expected_envs:
            assert env in SECURITY_CONFIG_MATRIX, f"Missing config for {env}"
            config = SECURITY_CONFIG_MATRIX[env]

            required_fields = [
                "name",
                "env_type",
                "security_level",
                "force_https",
                "allowed_hosts",
                "cors",
                "csp",
                "ssl",
                "headers",
            ]

            for field in required_fields:
                assert field in config, f"Missing field {field} in {env} config"

    def test_local_development_config(self):
        """Konfigurácia pre lokálny vývoj."""

        config = SECURITY_CONFIG_MATRIX[EnvironmentType.LOCAL]

        assert config["name"] == "Local Development"
        assert config["env_type"] == EnvironmentType.LOCAL
        assert config["security_level"] == SecurityLevel.MINIMAL
        assert config["force_https"] is False

        cors = config["cors"]
        assert "http://localhost:5173" in cors["allowed_origins"]
        assert "http://127.0.0.1:5173" in cors["allowed_origins"]
        assert cors["allow_credentials"] is True

        ssl = config["ssl"]
        assert ssl["enabled"] is False
        assert ssl["redirect_http"] is False
        assert ssl["hsts_max_age"] == 0

        csp = config["csp"]
        assert "'unsafe-inline'" in csp["script_src"]
        assert "'unsafe-eval'" in csp["script_src"]
        assert "ws://localhost:*" in csp["connect_src"]

    def test_development_config(self):
        """Konfigurácia pre dev server."""

        config = SECURITY_CONFIG_MATRIX[EnvironmentType.DEVELOPMENT]

        assert config["name"] == "Development Server"
        assert config["env_type"] == EnvironmentType.DEVELOPMENT
        assert config["security_level"] == SecurityLevel.STANDARD
        assert config["force_https"] is True

        allowed_hosts = config["allowed_hosts"]
        # Dev config musí mať aspoň tieto hosty
        assert "dev.sopira.magic" in allowed_hosts or "dev.thermal-eye.sopira.com" in allowed_hosts

        ssl = config["ssl"]
        assert ssl["enabled"] is True
        assert ssl["redirect_http"] is True
        assert ssl["hsts_max_age"] == 31536000
        assert ssl["certificate_provider"] in {"letsencrypt", "render", "none"}
        assert ssl["auto_renew"] is True

    def test_production_config(self):
        """Konfigurácia pre produkciu."""

        config = SECURITY_CONFIG_MATRIX[EnvironmentType.PRODUCTION]

        assert config["name"] == "Production"
        assert config["env_type"] == EnvironmentType.PRODUCTION
        assert config["security_level"] == SecurityLevel.STRICT
        assert config["force_https"] is True

        cors = config["cors"]
        # Produkcia má striktné HTTPS origins
        for origin in cors["allowed_origins"]:
            assert origin.startswith("https://")

        csp = config["csp"]
        assert "'unsafe-inline'" not in csp["script_src"]
        assert "'unsafe-eval'" not in csp["script_src"]
        assert "'self'" in csp["script_src"]

        ssl = config["ssl"]
        assert ssl["hsts_preload"] is True
        assert ssl["renew_before_days"] == 30

    def test_cloud_config(self):
        """Konfigurácia pre cloud (Render)."""

        config = SECURITY_CONFIG_MATRIX[EnvironmentType.CLOUD]

        assert config["name"].startswith("Cloud Deployment")
        assert config["env_type"] == EnvironmentType.CLOUD
        assert config["security_level"] == SecurityLevel.STRICT

        allowed_hosts = config["allowed_hosts"]
        assert any(".onrender.com" in h for h in allowed_hosts)

        ssl = config["ssl"]
        assert ssl["certificate_provider"] in {"render", "letsencrypt", "none"}

    def test_security_level_progression(self):
        """Progresia security levels medzi environmentami."""

        security_levels = {
            EnvironmentType.LOCAL: SecurityLevel.MINIMAL,
            EnvironmentType.DEVELOPMENT: SecurityLevel.STANDARD,
            EnvironmentType.PRODUCTION: SecurityLevel.STRICT,
            EnvironmentType.CLOUD: SecurityLevel.STRICT,
        }

        for env_type, expected_level in security_levels.items():
            config = SECURITY_CONFIG_MATRIX[env_type]
            assert (
                config["security_level"] == expected_level
            ), f"{env_type} should have {expected_level} security level"

    def test_cors_config_consistency(self):
        """Konzistencia CORS konfigurácie."""

        for env_type, config in SECURITY_CONFIG_MATRIX.items():
            cors = config["cors"]

            required_cors_fields = [
                "allowed_origins",
                "allowed_methods",
                "allow_credentials",
                "max_age",
            ]

            for field in required_cors_fields:
                assert field in cors, f"Missing CORS field {field} in {env_type}"

            assert cors["max_age"] > 0, f"Invalid max_age in {env_type}"

            if config["force_https"]:
                for origin in cors["allowed_origins"]:
                    if origin.startswith("http://") and "localhost" not in origin:
                        pytest.fail(
                            f"HTTP origin in HTTPS environment {env_type}: {origin}"
                        )

    def test_ssl_config_consistency(self):
        """Konzistencia SSL konfigurácie."""

        for env_type, config in SECURITY_CONFIG_MATRIX.items():
            ssl = config["ssl"]

            required_ssl_fields = [
                "enabled",
                "redirect_http",
                "hsts_max_age",
                "certificate_provider",
                "auto_renew",
                "renew_before_days",
            ]

            for field in required_ssl_fields:
                assert field in ssl, f"Missing SSL field {field} in {env_type}"

            if ssl["enabled"]:
                assert (
                    ssl["redirect_http"] is True
                ), f"SSL enabled but redirect_http=False in {env_type}"
                assert (
                    ssl["hsts_max_age"] > 0
                ), f"SSL enabled but HSTS max_age=0 in {env_type}"

    def test_allowed_hosts_not_empty(self):
        """allowed_hosts nie je prázdne pre žiadny environment."""

        for env_type in [
            EnvironmentType.LOCAL,
            EnvironmentType.DEVELOPMENT,
            EnvironmentType.STAGING,
            EnvironmentType.PRODUCTION,
            EnvironmentType.CLOUD,
        ]:
            config = SECURITY_CONFIG_MATRIX[env_type]
            allowed_hosts = config["allowed_hosts"]

            assert isinstance(allowed_hosts, list)
            assert len(allowed_hosts) > 0, f"Empty allowed_hosts for {env_type}"

            for host in allowed_hosts:
                assert host.strip() != "", f"Empty string in allowed_hosts for {env_type}"

    def test_csp_config_for_all_environments(self):
        """CSP konfigurácia pre všetky environmenty."""

        for env_type, config in SECURITY_CONFIG_MATRIX.items():
            csp = config["csp"]

            required_csp_fields = ["default_src", "script_src", "style_src"]

            for field in required_csp_fields:
                assert field in csp, f"Missing CSP field {field} in {env_type}"
                assert isinstance(
                    csp[field], list
                ), f"CSP field {field} must be list in {env_type}"
                assert (
                    len(csp[field]) > 0
                ), f"Empty CSP {field} in {env_type}"

            assert "'self'" in csp["default_src"], (
                "Missing 'self' in default_src for {env_type}"
            )

            if "object_src" in csp:
                assert "'none'" in csp["object_src"], (
                    f"object_src should contain 'none' in {env_type}"
                )

            if "frame_src" in csp:
                assert "'none'" in csp["frame_src"], (
                    f"frame_src should contain 'none' in {env_type}"
                )

    def test_headers_config_consistency(self):
        """Konzistencia security headers."""

        for env_type, config in SECURITY_CONFIG_MATRIX.items():
            headers = config["headers"]

            required_headers = ["x_frame_options", "x_content_type_options"]

            for header in required_headers:
                assert header in headers, f"Missing header {header} in {env_type}"
                assert headers[header], f"Empty header {header} in {env_type}"

            valid_frame_options = ["DENY", "SAMEORIGIN"]
            assert (
                headers["x_frame_options"] in valid_frame_options
            ), f"Invalid X-Frame-Options in {env_type}: {headers['x_frame_options']}"

            assert (
                headers["x_content_type_options"] == "nosniff"
            ), f"Invalid X-Content-Type-Options in {env_type}"

    def test_config_immutability(self):
        """Konfigurácia by sa nemala meniť počas behu (konštanta)."""

        # Vytvor si kópiu konfigurácie ako bežné dict-y
        original_config = {
            env: dict(cfg) for env, cfg in SECURITY_CONFIG_MATRIX.items()
        }

        try:
            SECURITY_CONFIG_MATRIX[EnvironmentType.LOCAL]["name"] = "Modified"
        except TypeError:
            # Toto je ideálny prípad – konfigurácia je immutable
            pass

        assert (
            original_config[EnvironmentType.LOCAL]["name"]
            == SECURITY_CONFIG_MATRIX[EnvironmentType.LOCAL]["name"]
            == "Local Development"
        )

    def test_environment_specific_rules(self):
        """Environment-specific business rules."""

        local_config = SECURITY_CONFIG_MATRIX[EnvironmentType.LOCAL]
        assert local_config["force_https"] is False
        assert local_config["ssl"]["enabled"] is False

        for env in [
            EnvironmentType.DEVELOPMENT,
            EnvironmentType.PRODUCTION,
            EnvironmentType.CLOUD,
        ]:
            config = SECURITY_CONFIG_MATRIX[env]
            assert config["force_https"] is True
            assert config["ssl"]["enabled"] is True

        prod_cors = SECURITY_CONFIG_MATRIX[EnvironmentType.PRODUCTION]["cors"]
        assert len(prod_cors["allowed_origins"]) <= 4

        local_cors = SECURITY_CONFIG_MATRIX[EnvironmentType.LOCAL]["cors"]
        assert len(local_cors["allowed_origins"]) >= 2


class TestSecurityConfigPerformance(TestCase):
    """Performance testy pre konfiguráciu (základné sanity checks)."""

    def test_config_access_performance(self):
        """Prístup ku konfigurácii by mal byť rýchly."""

        iterations = 1000
        start_time = time.time()

        for _ in range(iterations):
            config = SECURITY_CONFIG_MATRIX[EnvironmentType.PRODUCTION]
            _ = config["cors"]["allowed_origins"]
            _ = config["ssl"]["enabled"]

        elapsed_time = time.time() - start_time
        avg_time = elapsed_time / iterations

        assert avg_time < 0.001, f"Config access too slow: {avg_time * 1000:.2f}ms"
