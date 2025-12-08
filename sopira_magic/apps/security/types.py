"""Security type definitions - SSOT pre všetky security typy.

Obsahuje Enumy a TypedDict-y používané v security engine.
"""

from enum import Enum
from typing import Any, Dict, List, Optional, TypedDict


class EnvironmentType(str, Enum):
    """Typy environmentov - SSOT."""

    LOCAL = "local"
    DEVELOPMENT = "dev"
    STAGING = "staging"
    PRODUCTION = "production"
    CLOUD = "cloud"  # Render, Heroku, AWS, atď.


class SecurityLevel(str, Enum):
    """Úrovne bezpečnosti - SSOT."""

    MINIMAL = "minimal"  # Lokálny vývoj
    STANDARD = "standard"  # Dev/Staging
    STRICT = "strict"  # Produkcia
    PARANOID = "paranoid"  # High-security aplikácie


class CorsConfig(TypedDict, total=False):
    """CORS konfigurácia."""

    allowed_origins: List[str]
    allowed_methods: List[str]
    allowed_headers: List[str]
    exposed_headers: List[str]
    allow_credentials: bool
    max_age: int


class CspConfig(TypedDict, total=False):
    """Content-Security-Policy konfigurácia."""

    default_src: List[str]
    script_src: List[str]
    style_src: List[str]
    img_src: List[str]
    connect_src: List[str]
    font_src: List[str]
    object_src: List[str]
    media_src: List[str]
    frame_src: List[str]
    sandbox: List[str]
    report_uri: str


class SslConfig(TypedDict, total=False):
    """SSL/TLS konfigurácia."""

    enabled: bool
    redirect_http: bool
    hsts_max_age: int
    hsts_include_subdomains: bool
    hsts_preload: bool
    certificate_provider: str  # "letsencrypt", "certbot", "render", "custom", "none"
    auto_renew: bool
    renew_before_days: int


class SecurityHeaders(TypedDict, total=False):
    """Security headers konfigurácia."""

    x_frame_options: str
    x_content_type_options: str
    x_xss_protection: str
    referrer_policy: str
    permissions_policy: str
    expect_ct: str


class EnvironmentConfig(TypedDict):
    """Kompletná konfigurácia environmentu - SSOT."""

    name: str
    env_type: EnvironmentType
    security_level: SecurityLevel
    force_https: bool
    allowed_hosts: List[str]
    cors: CorsConfig
    csp: CspConfig
    ssl: SslConfig
    headers: SecurityHeaders
