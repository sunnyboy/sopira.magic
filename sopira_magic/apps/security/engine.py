"""Security engine - ConfigDriven & SSOT security management.

Hlavná trieda, ktorá spravuje všetky security operácie.
"""

import logging
from typing import Any, Dict, Optional

from django.conf import settings
from django.http import HttpRequest, HttpResponse

from .config import SECURITY_CONFIG_MATRIX
from .registry import get_certificate_info, get_custom_headers, get_environment
from .types import EnvironmentConfig, EnvironmentType
from .validators.cors import CorsValidator
from .validators.csp import CspValidator
from .validators.csrf import CsrfValidator
from .validators.headers import SecurityHeadersValidator
from .validators.ssl import SslValidator

logger = logging.getLogger(__name__)


class SecurityEngine:
    """Security engine - SINGLE SOURCE OF TRUTH pre všetky security decisions.

    - Žiadne hardcodované rozhodnutia mimo SSOT konfigurácie a registry.
    - Všetky kontroly vychádzajú zo ``SECURITY_CONFIG_MATRIX``.
    """

    @classmethod
    def get_config(cls, request: Optional[HttpRequest] = None) -> EnvironmentConfig:
        """Získaj security konfiguráciu pre aktuálny environment.

        Environment je zistený cez registry (alebo fallback env var).
        """

        env_string = get_environment(request)
        try:
            env_type = EnvironmentType(env_string)
        except ValueError:
            logger.warning("Unknown environment type '%s', falling back to LOCAL", env_string)
            env_type = EnvironmentType.LOCAL

        config = SECURITY_CONFIG_MATRIX.get(env_type)
        if not config:
            logger.error("No SSOT configuration found for %s, using LOCAL", env_type)
            config = SECURITY_CONFIG_MATRIX[EnvironmentType.LOCAL]

        return config

    # ------------------------------------------------------------------
    # HEADERS & RESPONSE úroveň
    # ------------------------------------------------------------------
    @classmethod
    def apply_security_headers(
        cls, response: HttpResponse, request: HttpRequest
    ) -> HttpResponse:
        """Aplikuj všetky security headers podľa SSOT konfigurácie."""

        config = cls.get_config(request)

        # 1) CSP header
        csp_header = CspValidator.build_csp_header(config["csp"])
        if csp_header:
            response["Content-Security-Policy"] = csp_header

        # 2) HSTS
        if config["ssl"]["enabled"] and config["ssl"]["hsts_max_age"] > 0:
            hsts_value = f"max-age={config['ssl']['hsts_max_age']}"
            if config["ssl"]["hsts_include_subdomains"]:
                hsts_value += "; includeSubDomains"
            if config["ssl"].get("hsts_preload"):
                hsts_value += "; preload"
            response["Strict-Transport-Security"] = hsts_value

        # 3) Základné security headers
        headers = SecurityHeadersValidator.get_headers(config["headers"])
        for header_name, header_value in headers.items():
            response[header_name] = header_value

        # 4) CORS headers
        cors_headers = CorsValidator.get_headers(request, config["cors"])
        for header_name, header_value in cors_headers.items():
            response[header_name] = header_value

        # 5) Custom headers z registry
        custom_headers = get_custom_headers(request)
        for header_name, header_value in custom_headers.items():
            response[header_name] = header_value

        # 6) Odstránenie sensitívnych headers v dev móde
        if config["env_type"] in [EnvironmentType.LOCAL, EnvironmentType.DEVELOPMENT]:
            cls._remove_sensitive_headers(response)

        return response

    # ------------------------------------------------------------------
    # VALIDÁCIE REQUESTU
    # ------------------------------------------------------------------
    @classmethod
    def validate_cors(
        cls, request: HttpRequest, custom_config: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Validuj CORS request podľa SSOT konfigurácie."""

        config = cls.get_config(request)
        cors_config = custom_config or config["cors"]
        return CorsValidator.validate(request, cors_config)

    @classmethod
    def validate_csrf(cls, request: HttpRequest) -> bool:
        """Validuj CSRF token podľa security level."""

        config = cls.get_config(request)
        from .types import SecurityLevel  # lazy import, aby sa predišlo cyklom

        level = config["security_level"]
        # normalizuj na SecurityLevel enum (ak by prišiel string)
        if not isinstance(level, SecurityLevel):
            try:
                level = SecurityLevel(str(level))
            except ValueError:
                level = SecurityLevel.STANDARD

        return CsrfValidator.validate(request, level)

    @classmethod
    def get_cors_headers(cls, request: HttpRequest) -> Dict[str, str]:
        """Získaj CORS headers pre response."""

        config = cls.get_config(request)
        return CorsValidator.get_headers(request, config["cors"])

    # ------------------------------------------------------------------
    # SSL / HTTPS
    # ------------------------------------------------------------------
    @classmethod
    def check_ssl_status(cls, domain: Optional[str] = None) -> Dict[str, Any]:
        """Skontroluj SSL/TLS stav pre doménu.

        Najprv sa skúsi registry provider, potom fallback na SslValidator.
        """

        cert_info = get_certificate_info("status", domain)
        if not cert_info.get("valid", False):
            return SslValidator.check_status(domain)
        return cert_info

    @classmethod
    def enforce_https_redirect(cls, request: HttpRequest) -> Optional[str]:
        """Vráť HTTPS redirect URL ak je potrebné presmerovanie, inak ``None``."""

        config = cls.get_config(request)
        ssl_cfg = config["ssl"]

        if ssl_cfg.get("enabled") and ssl_cfg.get("redirect_http") and not request.is_secure():
            host = request.get_host()
            if ":" in host:
                host = host.split(":")[0]
            return f"https://{host}{request.get_full_path()}"

        return None

    # ------------------------------------------------------------------
    # AUDIT
    # ------------------------------------------------------------------
    @classmethod
    def security_audit(cls, check_type: str = "quick") -> Dict[str, Any]:
        """Spusť bezpečnostný audit ("quick", "full", ...)."""

        from .monitoring import SecurityAuditor

        try:
            return SecurityAuditor.run_audit(check_type)
        except Exception as exc:  # pragma: no cover - defenzívny fallback
            logger.error("Security audit failed: %s", exc)
            return {
                "passed": False,
                "checks": {},
                "errors": [str(exc)],
                "summary": "Security audit failed to run",
            }

    # ------------------------------------------------------------------
    # INTERNÉ POMOCNÉ METÓDY
    # ------------------------------------------------------------------
    @classmethod
    def _remove_sensitive_headers(cls, response: HttpResponse) -> None:
        """Odstráň sensitívne headers v dev móde pre jednoduchší debugging."""

        headers_to_remove = [
            "Server",
            "X-Powered-By",
            "X-AspNet-Version",
            "X-AspNetMvc-Version",
        ]
        for header in headers_to_remove:
            if header in response:
                del response[header]
