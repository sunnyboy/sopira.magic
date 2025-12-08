"""Test data factories pre Security Module."""

from typing import Dict, List

from sopira_magic.apps.security.types import EnvironmentType, SecurityLevel


class SecurityConfigFactory:
    """Factory pre vytváranie testovacích security konfigurácií."""

    @staticmethod
    def create_local_config() -> Dict:
        """Vytvor lokálnu konfiguráciu."""

        return {
            "name": "Local Development",
            "env_type": EnvironmentType.LOCAL,
            "security_level": SecurityLevel.MINIMAL,
            "force_https": False,
            "allowed_hosts": ["localhost", "127.0.0.1"],
            "cors": {
                "allowed_origins": ["http://localhost:5173"],
                "allowed_methods": ["GET", "POST"],
                "allowed_headers": ["*"],
                "allow_credentials": True,
                "max_age": 86400,
            },
            "csp": {
                "default_src": ["'self'"],
                "script_src": ["'self'", "'unsafe-inline'"],
            },
            "ssl": {
                "enabled": False,
                "redirect_http": False,
                "hsts_max_age": 0,
                "hsts_include_subdomains": False,
                "hsts_preload": False,
                "certificate_provider": "none",
                "auto_renew": False,
                "renew_before_days": 30,
            },
            "headers": {
                "x_frame_options": "DENY",
                "x_content_type_options": "nosniff",
            },
        }

    @staticmethod
    def create_production_config() -> Dict:
        """Vytvor produkčnú konfiguráciu."""

        return {
            "name": "Production",
            "env_type": EnvironmentType.PRODUCTION,
            "security_level": SecurityLevel.STRICT,
            "force_https": True,
            "allowed_hosts": ["thermal-eye.sopira.com"],
            "cors": {
                "allowed_origins": ["https://thermal-eye.sopira.com"],
                "allowed_methods": ["GET", "POST", "PUT", "DELETE"],
                "allowed_headers": ["Authorization", "Content-Type"],
                "allow_credentials": True,
                "max_age": 86400,
            },
            "csp": {
                "default_src": ["'self'"],
                "script_src": ["'self'"],
                "style_src": ["'self'"],
            },
            "ssl": {
                "enabled": True,
                "redirect_http": True,
                "hsts_max_age": 31536000,
                "hsts_include_subdomains": True,
                "hsts_preload": True,
                "certificate_provider": "letsencrypt",
                "auto_renew": True,
                "renew_before_days": 30,
            },
            "headers": {
                "x_frame_options": "DENY",
                "x_content_type_options": "nosniff",
                "x_xss_protection": "1; mode=block",
                "referrer_policy": "strict-origin-when-cross-origin",
            },
        }

    @staticmethod
    def create_invalid_config() -> Dict:
        """Vytvor neplatnú konfiguráciu pre testovanie validácie."""

        return {
            "name": "Invalid Config",
            # Chýbajú povinné polia
        }

    @staticmethod
    def create_cors_config_with_wildcard() -> Dict:
        """Vytvor CORS config s wildcard (nebezpečné s credentials)."""

        return {
            "allowed_origins": ["*"],
            "allowed_methods": ["*"],
            "allowed_headers": ["*"],
            "allow_credentials": True,
            "max_age": 86400,
        }
