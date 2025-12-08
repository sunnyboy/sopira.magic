"""Security configuration - SINGLE SOURCE OF TRUTH pre všetky environmenty.

ConfigDriven prístup: všetky security nastavenia sú sústredené v jednej
SSOT matici podľa typu environmentu.
"""

from typing import Dict
from types import MappingProxyType

from .types import EnvironmentConfig, EnvironmentType, SecurityLevel


# =============================================================================
# SECURITY CONFIGURATION MATRIX - SSOT
# =============================================================================

# Poznámka:
# - konfigurácia je odvodená z pôvodného thermal_eye security configu
#   a môže byť ďalej prispôsobená pre konkrétne nasadenia.

_RAW_SECURITY_CONFIG_MATRIX: Dict[EnvironmentType, EnvironmentConfig] = {
    EnvironmentType.LOCAL: {
        "name": "Local Development",
        "env_type": EnvironmentType.LOCAL,
        "security_level": SecurityLevel.MINIMAL,
        "force_https": False,
        "allowed_hosts": ["localhost", "127.0.0.1", "0.0.0.0"],
        "cors": {
            "allowed_origins": [
                "http://localhost:5173",
                "http://localhost:4173",
                "http://127.0.0.1:5173",
                "http://127.0.0.1:4173",
                "http://localhost:8000",
            ],
            "allowed_methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
            "allowed_headers": ["*"],
            "exposed_headers": ["Content-Range", "X-Total-Count"],
            "allow_credentials": True,
            "max_age": 86400,
        },
        "csp": {
            "default_src": ["'self'"],
            "script_src": ["'self'", "'unsafe-inline'", "'unsafe-eval'"],
            "style_src": ["'self'", "'unsafe-inline'"],
            "img_src": ["'self'", "data:", "blob:"],
            "connect_src": ["'self'", "ws://localhost:*", "http://localhost:*"],
            "font_src": ["'self'", "data:"],
            "object_src": ["'none'"],
            "media_src": ["'self'"],
            "frame_src": ["'none'"],
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
            "x_xss_protection": "1; mode=block",
            "referrer_policy": "no-referrer-when-downgrade",
            "permissions_policy": "camera=(), microphone=(), geolocation()",
        },
    },
    EnvironmentType.DEVELOPMENT: {
        "name": "Development Server",
        "env_type": EnvironmentType.DEVELOPMENT,
        "security_level": SecurityLevel.STANDARD,
        "force_https": True,
        "allowed_hosts": [
            "dev.thermal-eye.sopira.com",
            "138.199.224.196",
            "*.sopira.com",
        ],
        "cors": {
            "allowed_origins": [
                "https://dev.thermal-eye.sopira.com",
                "https://138.199.224.196",
            ],
            "allowed_methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
            "allowed_headers": ["Authorization", "Content-Type", "X-CSRFToken"],
            "exposed_headers": ["Content-Range", "X-Total-Count"],
            "allow_credentials": True,
            "max_age": 86400,
        },
        "csp": {
            "default_src": ["'self'"],
            "script_src": ["'self'", "'unsafe-inline'"],
            "style_src": ["'self'", "'unsafe-inline'"],
            "img_src": ["'self'", "data:", "https:"],
            "connect_src": ["'self'"],
            "font_src": ["'self'", "https:"],
            "object_src": ["'none'"],
            "media_src": ["'self'"],
            "frame_src": ["'none'"],
        },
        "ssl": {
            "enabled": True,
            "redirect_http": True,
            "hsts_max_age": 31536000,
            "hsts_include_subdomains": True,
            "hsts_preload": False,
            "certificate_provider": "letsencrypt",
            "auto_renew": True,
            "renew_before_days": 30,
        },
        "headers": {
            "x_frame_options": "DENY",
            "x_content_type_options": "nosniff",
            "x_xss_protection": "1; mode=block",
            "referrer_policy": "strict-origin-when-cross-origin",
            "permissions_policy": "camera=(), microphone=(), geolocation=(), payment=()",
        },
    },
    EnvironmentType.STAGING: {
        "name": "Staging Server",
        "env_type": EnvironmentType.STAGING,
        "security_level": SecurityLevel.STANDARD,
        "force_https": True,
        "allowed_hosts": [
            "staging.thermal-eye.sopira.com",
            "*.sopira.com",
        ],
        "cors": {
            "allowed_origins": [
                "https://staging.thermal-eye.sopira.com",
            ],
            "allowed_methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
            "allowed_headers": ["Authorization", "Content-Type", "X-CSRFToken"],
            "exposed_headers": ["Content-Range", "X-Total-Count"],
            "allow_credentials": True,
            "max_age": 86400,
        },
        "csp": {
            "default_src": ["'self'"],
            "script_src": ["'self'"],
            "style_src": ["'self'", "'unsafe-inline'"],
            "img_src": ["'self'", "data:", "https:"],
            "connect_src": ["'self'"],
            "font_src": ["'self'", "https:"],
            "object_src": ["'none'"],
            "media_src": ["'self'"],
            "frame_src": ["'none'"],
        },
        "ssl": {
            "enabled": True,
            "redirect_http": True,
            "hsts_max_age": 31536000,
            "hsts_include_subdomains": True,
            "hsts_preload": False,
            "certificate_provider": "letsencrypt",
            "auto_renew": True,
            "renew_before_days": 30,
        },
        "headers": {
            "x_frame_options": "DENY",
            "x_content_type_options": "nosniff",
            "x_xss_protection": "1; mode=block",
            "referrer_policy": "strict-origin-when-cross-origin",
            "permissions_policy": "camera=(), microphone=(), geolocation=(), payment()",
        },
    },
    EnvironmentType.PRODUCTION: {
        "name": "Production",
        "env_type": EnvironmentType.PRODUCTION,
        "security_level": SecurityLevel.STRICT,
        "force_https": True,
        "allowed_hosts": [
            "thermal-eye.sopira.com",
            "www.sopira.com",
            "138.199.224.196",
            "*.sopira.com",
        ],
        "cors": {
            "allowed_origins": [
                "https://thermal-eye.sopira.com",
                "https://www.sopira.com",
            ],
            "allowed_methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
            "allowed_headers": ["Authorization", "Content-Type", "X-CSRFToken"],
            "exposed_headers": ["Content-Range", "X-Total-Count"],
            "allow_credentials": True,
            "max_age": 86400,
        },
        "csp": {
            "default_src": ["'self'"],
            "script_src": ["'self'"],
            "style_src": ["'self'", "'unsafe-inline'"],
            "img_src": ["'self'", "data:", "https:"],
            "connect_src": ["'self'"],
            "font_src": ["'self'", "https:"],
            "object_src": ["'none'"],
            "media_src": ["'self'"],
            "frame_src": ["'none'"],
            "sandbox": ["allow-forms", "allow-scripts"],
            "report_uri": "/api/security/csp-report/",
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
            "permissions_policy": "camera=(), microphone=(), geolocation=(), payment=(), usb=()",
            "expect_ct": "max-age=86400, enforce",
        },
    },
    EnvironmentType.CLOUD: {
        "name": "Cloud Deployment (Render)",
        "env_type": EnvironmentType.CLOUD,
        "security_level": SecurityLevel.STRICT,
        "force_https": True,
        "allowed_hosts": [
            "thermal-eye.onrender.com",
            "*.onrender.com",
        ],
        "cors": {
            "allowed_origins": [
                "https://thermal-eye.onrender.com",
                "https://*.onrender.com",
            ],
            "allowed_methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
            "allowed_headers": ["Authorization", "Content-Type", "X-CSRFToken"],
            "exposed_headers": ["Content-Range", "X-Total-Count"],
            "allow_credentials": True,
            "max_age": 86400,
        },
        "csp": {
            "default_src": ["'self'"],
            "script_src": ["'self'"],
            "style_src": ["'self'", "'unsafe-inline'"],
            "img_src": ["'self'", "data:", "https:"],
            "connect_src": ["'self'"],
            "font_src": ["'self'", "https:"],
            "object_src": ["'none'"],
            "media_src": ["'self'"],
            "frame_src": ["'none'"],
        },
        "ssl": {
            "enabled": True,
            "redirect_http": True,
            "hsts_max_age": 31536000,
            "hsts_include_subdomains": True,
            "hsts_preload": False,
            "certificate_provider": "render",
            "auto_renew": True,
            "renew_before_days": 30,
        },
        "headers": {
            "x_frame_options": "DENY",
            "x_content_type_options": "nosniff",
            "x_xss_protection": "1; mode=block",
            "referrer_policy": "strict-origin-when-cross-origin",
            "permissions_policy": "camera=(), microphone=(), geolocation()",
        },
    },
}

# Exponovaná SSOT konfigurácia ako read-only mapping
SECURITY_CONFIG_MATRIX: Dict[EnvironmentType, EnvironmentConfig] = {
    env: MappingProxyType(cfg) for env, cfg in _RAW_SECURITY_CONFIG_MATRIX.items()
}
