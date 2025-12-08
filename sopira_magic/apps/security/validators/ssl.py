"""SSL/TLS validator - ConfigDriven SSL validácia a management."""

import datetime
import socket
import ssl
from typing import Any, Dict, List, Optional


class SslValidator:
    """ConfigDriven SSL validator - SSOT pre SSL rozhodnutia."""

    @staticmethod
    def check_status(domain: Optional[str] = None) -> Dict[str, Any]:
        """Skontroluj SSL certifikát pre doménu.

        Ak ``domain`` nie je zadaná, použije sa ``socket.getfqdn()``.
        """

        if not domain:
            domain = socket.getfqdn()

        try:
            context = ssl.create_default_context()
            with socket.create_connection((domain, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()

                    expires_str = cert["notAfter"]
                    expires = datetime.datetime.strptime(
                        expires_str, "%b %d %H:%M:%S %Y %Z"
                    )
                    now = datetime.datetime.now()
                    days_remaining = (expires - now).days

                    issuer = dict(x[0] for x in cert["issuer"])
                    subject = dict(x[0] for x in cert["subject"])

                    san = [ext[1] for ext in cert.get("subjectAltName", [])]

                    result: Dict[str, Any] = {
                        "valid": True,
                        "domain": domain,
                        "days_remaining": days_remaining,
                        "expires": expires_str,
                        "issuer": issuer.get("organizationName", "Unknown"),
                        "issued_by": issuer,
                        "subject": subject,
                        "subject_alt_names": san,
                        "serial_number": cert.get("serialNumber"),
                        "version": cert.get("version"),
                        "algorithm": ssock.cipher()[0],
                        "warnings": [],
                        "errors": [],
                    }

                    if days_remaining < 0:
                        result["valid"] = False
                        result["errors"].append("Certificate has expired")
                    elif days_remaining < 7:
                        result["warnings"].append(
                            "Certificate expiring in less than 7 days"
                        )
                    elif days_remaining < 30:
                        result["warnings"].append(
                            "Certificate expiring in less than 30 days"
                        )

                    return result

        except ssl.SSLError as exc:
            return {
                "valid": False,
                "domain": domain,
                "errors": [f"SSL error: {exc}"],
                "warnings": [],
            }
        except socket.timeout:
            return {
                "valid": False,
                "domain": domain,
                "errors": ["Connection timeout"],
                "warnings": [],
            }
        except Exception as exc:  # pragma: no cover
            return {
                "valid": False,
                "domain": domain,
                "errors": [f"Unexpected error: {exc}"],
                "warnings": [],
            }

    @staticmethod
    def should_enforce_https(ssl_config: Dict) -> bool:
        """Má byť vynútené HTTPS podľa konfigurácie?"""

        return bool(ssl_config.get("enabled") and ssl_config.get("redirect_http"))

    @staticmethod
    def get_recommendations(cert_info: Dict[str, Any]) -> List[str]:
        """Vráť odporúčania pre SSL certifikát."""

        recommendations: List[str] = []

        if not cert_info.get("valid", False):
            recommendations.append("Certificate is invalid or expired")
            return recommendations

        days_remaining = cert_info.get("days_remaining", 0)
        if days_remaining < 30:
            recommendations.append(
                f"Renew certificate (expires in {days_remaining} days)"
            )

        algorithm = cert_info.get("algorithm", "")
        weak_algorithms = ["RC4", "DES", "3DES", "MD5", "SHA1"]
        if any(weak in algorithm for weak in weak_algorithms):
            recommendations.append(f"Upgrade from weak cipher: {algorithm}")

        return recommendations
