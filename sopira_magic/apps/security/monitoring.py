"""Security monitoring & audit - ConfigDriven security monitoring."""

import logging
from datetime import datetime
from typing import Any, Dict

from django.conf import settings
from django.test import Client

from .config import SECURITY_CONFIG_MATRIX
from .engine import SecurityEngine
from .registry import get_certificate_info
from .validators.headers import SecurityHeadersValidator
from .validators.ssl import SslValidator

logger = logging.getLogger(__name__)


class SecurityAuditor:
    """ConfigDriven security auditor - SSOT pre security audity."""

    @staticmethod
    def run_audit(check_type: str = "quick") -> Dict[str, Any]:
        """Spusť security audit podľa typu.

        ``check_type``: "quick", "full", "ssl", "headers", "cors", "config".
        """

        results: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "check_type": check_type,
            "passed": True,
            "checks": {},
            "warnings": [],
            "errors": [],
            "recommendations": [],
        }

        if check_type in {"quick", "full", "ssl"}:
            ssl_results = SecurityAuditor._check_ssl()
            results["checks"]["ssl"] = ssl_results
            if not ssl_results["passed"]:
                results["passed"] = False

        if check_type in {"quick", "full", "headers"}:
            headers_results = SecurityAuditor._check_headers()
            results["checks"]["headers"] = headers_results
            if not headers_results["passed"]:
                results["passed"] = False

        if check_type in {"full", "cors"}:
            cors_results = SecurityAuditor._check_cors()
            results["checks"]["cors"] = cors_results
            if not cors_results["passed"]:
                results["passed"] = False

        if check_type in {"full", "config"}:
            config_results = SecurityAuditor._check_config()
            results["checks"]["config"] = config_results
            if not config_results["passed"]:
                results["passed"] = False

        if not results["passed"]:
            results["summary"] = "Security audit failed"
        else:
            results["summary"] = "Security audit passed"

        return results

    # ------------------------------------------------------------------
    # Interné kontroly
    # ------------------------------------------------------------------
    @staticmethod
    def _check_ssl() -> Dict[str, Any]:
        cert_info = get_certificate_info("status")
        if cert_info.get("valid", False):
            return {
                "passed": True,
                "message": "SSL certificate is valid",
                "details": cert_info,
                "warnings": cert_info.get("warnings", []),
                "errors": [],
            }

        try:
            cert_info = SslValidator.check_status()
            passed = cert_info.get("valid", False)
            return {
                "passed": passed,
                "message": "SSL check completed" if passed else "SSL check failed",
                "details": cert_info,
                "warnings": cert_info.get("warnings", []),
                "errors": cert_info.get("errors", []),
            }
        except Exception as exc:  # pragma: no cover
            return {
                "passed": False,
                "message": f"SSL check error: {exc}",
                "details": {},
                "warnings": [],
                "errors": [str(exc)],
            }

    @staticmethod
    def _check_headers() -> Dict[str, Any]:
        try:
            client = Client()
            response = client.get("/")

            # Očakávame aspoň základné security headers
            env_cfg = SecurityEngine.get_config(None)
            expected_cfg = env_cfg["headers"]
            results = SecurityHeadersValidator.validate_headers(
                dict(response.headers), expected_cfg
            )

            if results["passed"]:
                return {
                    "passed": True,
                    "message": "All security headers present",
                    "details": results["details"],
                    "warnings": [],
                    "errors": [],
                }

            return {
                "passed": False,
                "message": "Missing or incorrect security headers",
                "details": results["details"],
                "warnings": [],
                "errors": results["missing"] + results["incorrect"],
            }
        except Exception as exc:  # pragma: no cover
            return {
                "passed": False,
                "message": f"Headers check error: {exc}",
                "details": {},
                "warnings": [],
                "errors": [str(exc)],
            }

    @staticmethod
    def _check_cors() -> Dict[str, Any]:
        cfg = SecurityEngine.get_config(None)
        cors_cfg = cfg.get("cors", {})
        if not cors_cfg.get("allowed_origins"):
            return {
                "passed": False,
                "message": "CORS configuration missing",
                "details": cors_cfg,
                "warnings": ["No CORS allowed_origins configured"],
                "errors": ["CORS not configured"],
            }

        return {
            "passed": True,
            "message": "CORS configuration present",
            "details": cors_cfg,
            "warnings": [],
            "errors": [],
        }

    @staticmethod
    def _check_config() -> Dict[str, Any]:
        cfg = SecurityEngine.get_config(None)
        env_type = cfg["env_type"].value

        issues = []

        if settings.DEBUG and env_type not in {"local", "dev"}:
            issues.append("DEBUG mode enabled in non-development environment")

        allowed_hosts = getattr(settings, "ALLOWED_HOSTS", [])
        if not allowed_hosts and env_type != "local":
            issues.append("ALLOWED_HOSTS not configured")

        secret_key = getattr(settings, "SECRET_KEY", "")
        if not secret_key or secret_key.startswith("dev-only-insecure"):
            issues.append("Insecure SECRET_KEY")

        if issues:
            return {
                "passed": False,
                "message": f"Configuration issues: {len(issues)}",
                "details": {
                    "DEBUG": settings.DEBUG,
                    "ALLOWED_HOSTS": allowed_hosts,
                    "SECRET_KEY_set": bool(secret_key),
                },
                "warnings": [],
                "errors": issues,
            }

        return {
            "passed": True,
            "message": "Configuration check passed",
            "details": {
                "DEBUG": settings.DEBUG,
                "ALLOWED_HOSTS": allowed_hosts,
                "SECRET_KEY_set": bool(secret_key),
            },
            "warnings": [],
            "errors": [],
        }
