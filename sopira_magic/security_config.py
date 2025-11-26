#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/security_config.py
#   Security Configuration - Intelligent environment-aware security
#   SSOT for CORS, CSRF, and cookie settings
#..............................................................

"""
Security Configuration - Intelligent Environment-Aware Security.

   Single source of truth for security configuration that automatically adapts
   to deployment environment (local/dev/production/render).

   Key Features:
   - Automatic environment detection from hostname and protocol
   - SSOT configuration for all security settings
   - Environment-specific CORS origins
   - Dynamic CSRF trusted origins
   - Adaptive cookie settings (Secure, HttpOnly, SameSite)

   Environment Detection:
   - local: localhost, 127.0.0.1 (development machine)
   - dev: dev.sopira.magic (development server)
   - production: sopira.magic (production server)
   - render: *.onrender.com (cloud hosting)

   Configuration Flow:
   1. detect_environment_from_request() detects environment from Django request
   2. get_cors_origins() returns allowed origins for current environment
   3. get_csrf_trusted_origins() returns CSRF trusted origins
   4. get_session_cookie_settings() returns session cookie configuration
   5. get_csrf_cookie_settings() returns CSRF cookie configuration

   Usage:
   ```python
   from sopira_magic.security_config import detect_environment_from_request
   env_info = detect_environment_from_request(request)
   # Returns: EnvironmentInfo(env_type, is_https, is_localhost)
   ```
"""

import os
from dataclasses import dataclass
from typing import Literal, NamedTuple, List

EnvType = Literal["local", "dev", "production", "render"]


@dataclass(frozen=True)
class EnvConfig:
    """
    Configuration for specific environment pattern.
    
    Fields:
        pattern: Hostname pattern to match (e.g., 'localhost', 'dev.sopira.magic')
        env_type: Environment type identifier
        is_localhost: True if running on developer's machine
        force_https: True if environment always uses HTTPS (e.g., Render)
    """
    pattern: str
    env_type: EnvType
    is_localhost: bool
    force_https: bool = False


class EnvironmentInfo(NamedTuple):
    """Complete environment information - computed once, used everywhere."""
    env_type: EnvType
    is_https: bool
    is_localhost: bool


# =============================================================================
# 🎯 SINGLE SOURCE OF TRUTH - ENVIRONMENT CONFIGURATIONS
# =============================================================================

ENVIRONMENT_CONFIGS = [
    # Local development (developer's machine)
    EnvConfig(
        pattern='localhost',
        env_type='local',
        is_localhost=True,
    ),
    EnvConfig(
        pattern='127.0.0.1',
        env_type='local',
        is_localhost=True,
    ),
    
    # DEV environment
    EnvConfig(
        pattern='dev.sopira.magic',
        env_type='dev',
        is_localhost=False,
    ),
    
    # Production environment
    EnvConfig(
        pattern='sopira.magic',
        env_type='production',
        is_localhost=False,
    ),
    
    # Render.com deployment (cloud hosting)
    EnvConfig(
        pattern='onrender.com',
        env_type='render',
        is_localhost=False,
        force_https=True,
    ),
]

# Default fallback for unknown domains
DEFAULT_ENV = EnvConfig(
    pattern='*',
    env_type='production',
    is_localhost=False,
)


def detect_environment_from_host(host: str, is_secure: bool = False) -> EnvironmentInfo:
    """
    🎯 SINGLE SOURCE OF TRUTH for environment detection.
    
    Detects environment based on request hostname and protocol.
    """
    host_lower = host.lower().split(':')[0]  # Remove port, normalize
    
    # Find matching environment config
    for config in ENVIRONMENT_CONFIGS:
        if config.pattern in host_lower:
            # Determine actual HTTPS status
            actual_is_https = is_secure or config.force_https
            
            return EnvironmentInfo(
                env_type=config.env_type,
                is_https=actual_is_https,
                is_localhost=config.is_localhost,
            )
    
    # Fallback to default for unknown domains
    return EnvironmentInfo(
        env_type=DEFAULT_ENV.env_type,
        is_https=is_secure,
        is_localhost=DEFAULT_ENV.is_localhost,
    )


def detect_environment_from_request(request) -> EnvironmentInfo:
    """
    🎯 Request-aware environment detection (PREFERRED METHOD).
    
    Automatically extracts host and HTTPS status from Django request.
    """
    host = request.get_host()
    is_secure = request.is_secure()
    return detect_environment_from_host(host, is_secure)


# =============================================================================
# BACKWARD COMPATIBILITY
# =============================================================================

def _env_flag(name: str, default: bool) -> bool:
    """Parse a boolean-ish environment variable."""
    value = os.getenv(name)
    if value is None:
        return default
    value = value.strip().lower()
    if value in {"1", "true", "yes", "on"}:
        return True
    if value in {"0", "false", "no", "off"}:
        return False
    return default


def detect_environment():
    """
    DEPRECATED: Use detect_environment_from_request() instead.
    Returns: (env_type, is_https, is_localhost)
    """
    env_var = os.getenv("ENV", "local")
    use_https_default = False if env_var == "local" else True
    use_https_flag = _env_flag("USE_HTTPS", use_https_default)
    
    allowed_hosts = os.getenv("ALLOWED_HOSTS", "").split(",")
    is_render = "onrender.com" in str(allowed_hosts)
    
    if is_render:
        return ("render", True, False)
    elif env_var == "local":
        return ("local", False, True)
    else:
        return ("production", use_https_flag, False)


def get_cors_origins() -> List[str]:
    """Get allowed CORS origins based on detected environment."""
    env_type, is_https, is_localhost = detect_environment()
    
    if is_localhost:
        return [
            "http://localhost:5173",
            "http://localhost:4173",
            "http://localhost:8000",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:4173",
        ]
    elif env_type == "production":
        return [
            "https://sopira.magic",
            "http://sopira.magic",
            "https://dev.sopira.magic",
            "http://dev.sopira.magic",
        ]
    else:  # render
        return [
            "https://*.onrender.com",
        ]


def get_csrf_trusted_origins() -> List[str]:
    """Get CSRF trusted origins based on detected environment."""
    return get_cors_origins()


def get_session_cookie_settings() -> dict:
    """Get session cookie settings based on detected environment."""
    env_type, is_https, is_localhost = detect_environment()

    if is_localhost or not is_https:
        return {
            "SESSION_COOKIE_SECURE": False,
            "SESSION_COOKIE_HTTPONLY": True,
        }
    else:
        return {
            "SESSION_COOKIE_SAMESITE": "None",
            "SESSION_COOKIE_SECURE": True,
            "SESSION_COOKIE_HTTPONLY": True,
        }


def get_csrf_cookie_settings() -> dict:
    """Get CSRF cookie settings based on detected environment."""
    env_type, is_https, is_localhost = detect_environment()

    if is_localhost or not is_https:
        return {
            "CSRF_COOKIE_SECURE": False,
            "CSRF_COOKIE_HTTPONLY": False,
        }
    else:
        return {
            "CSRF_COOKIE_SAMESITE": "None",
            "CSRF_COOKIE_SECURE": True,
            "CSRF_COOKIE_HTTPONLY": False,
        }

