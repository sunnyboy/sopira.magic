"""Security utilities - ConfigDriven pomocné funkcie."""

import ipaddress
import re
from typing import List, Optional
from urllib.parse import urlparse


class SecurityUtils:
    """ConfigDriven security utilities - SSOT pre utility funkcie."""

    @staticmethod
    def is_safe_origin(origin: str, allowed_patterns: List[str]) -> bool:
        """Skontroluj, či je origin bezpečný podľa allowed patterns."""

        if not origin:
            return False

        try:
            parsed = urlparse(origin)
            if parsed.scheme not in {"http", "https"}:
                return False

            if origin in allowed_patterns:
                return True

            for pattern in allowed_patterns:
                if "*" in pattern:
                    regex_pattern = pattern.replace(".", r"\.").replace("*", ".*")
                    if re.match(regex_pattern, origin):
                        return True

            for pattern in allowed_patterns:
                if pattern.startswith("."):
                    if origin.endswith(pattern) or origin == pattern[1:]:
                        return True

            return False
        except Exception:  # pragma: no cover
            return False

    @staticmethod
    def validate_ip_address(ip: str) -> bool:
        """Validuj IP adresu."""

        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False

    @staticmethod
    def get_client_ip(request) -> Optional[str]:
        """Získaj IP adresu klienta z requestu."""

        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0].strip()
            if SecurityUtils.validate_ip_address(ip):
                return ip

        ip = request.META.get("REMOTE_ADDR")
        if ip and SecurityUtils.validate_ip_address(ip):
            return ip

        return None

    @staticmethod
    def sanitize_input(input_string: str, max_length: int = 1000) -> str:
        """Sanitizuj user input pre security účely."""

        if not input_string:
            return ""

        sanitized = input_string.strip()

        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]

        sanitized = sanitized.replace("\x00", "")

        sanitized = "".join(
            char for char in sanitized if char.isprintable() or char in "\n\t\r"
        )

        return sanitized

    @staticmethod
    def generate_security_report(audit_results: dict) -> str:
        """Vygeneruj textový security report z výsledkov auditu."""

        lines: List[str] = []

        lines.append("=" * 70)
        lines.append("SECURITY AUDIT REPORT")
        lines.append("=" * 70)
        lines.append(f"Timestamp: {audit_results.get('timestamp')}")
        lines.append(f"Check Type: {audit_results.get('check_type', 'unknown')}")
        lines.append(
            f"Status: {'PASSED' if audit_results.get('passed') else 'FAILED'}"
        )
        lines.append("")

        for check_name, check_results in audit_results.get("checks", {}).items():
            lines.append(f"{check_name.upper()}")
            lines.append(
                f"   Status: {'PASSED' if check_results.get('passed') else 'FAILED'}"
            )
            lines.append(
                f"   Message: {check_results.get('message', 'No message')}"
            )

            if check_results.get("warnings"):
                lines.append("   Warnings:")
                for warning in check_results["warnings"]:
                    lines.append(f"     - {warning}")

            if check_results.get("errors"):
                lines.append("   Errors:")
                for error in check_results["errors"]:
                    lines.append(f"     - {error}")

            lines.append("")

        lines.append("=" * 70)
        lines.append(f"SUMMARY: {audit_results.get('summary', 'No summary')}")
        lines.append("=" * 70)

        return "\n".join(lines)
