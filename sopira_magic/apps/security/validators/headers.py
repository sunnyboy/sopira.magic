"""Security headers validator - ConfigDriven security headers."""

from typing import Any, Dict


class SecurityHeadersValidator:
    """ConfigDriven security headers validator - SSOT pre headers."""

    @staticmethod
    def get_headers(headers_config: Dict[str, str]) -> Dict[str, str]:
        """Vráť security headers podľa SSOT konfigurácie."""

        headers: Dict[str, str] = {}

        header_mapping = {
            "x_frame_options": "X-Frame-Options",
            "x_content_type_options": "X-Content-Type-Options",
            "x_xss_protection": "X-XSS-Protection",
            "referrer_policy": "Referrer-Policy",
            "permissions_policy": "Permissions-Policy",
            "expect_ct": "Expect-CT",
        }

        for config_key, header_name in header_mapping.items():
            if config_key in headers_config:
                headers[header_name] = headers_config[config_key]

        # Default hodnoty, ak nie sú v konfigurácii
        headers.setdefault("X-Content-Type-Options", "nosniff")
        headers.setdefault("X-Frame-Options", "DENY")

        return headers

    @staticmethod
    def validate_headers(
        response_headers: Dict[str, str], expected_config: Dict[str, str]
    ) -> Dict[str, Any]:
        """Validuj, či sú všetky security headers prítomné a s očakávanou hodnotou."""

        results: Dict[str, Any] = {
            "passed": True,
            "missing": [],
            "incorrect": [],
            "details": {},
        }

        headers = SecurityHeadersValidator.get_headers(expected_config)
        for header_name, expected_value in headers.items():
            actual_value = response_headers.get(header_name)
            if not actual_value:
                results["passed"] = False
                results["missing"].append(header_name)
                results["details"][header_name] = {
                    "expected": expected_value,
                    "actual": None,
                    "status": "MISSING",
                }
            elif actual_value != expected_value:
                results["passed"] = False
                results["incorrect"].append(header_name)
                results["details"][header_name] = {
                    "expected": expected_value,
                    "actual": actual_value,
                    "status": "INCORRECT",
                }
            else:
                results["details"][header_name] = {
                    "expected": expected_value,
                    "actual": actual_value,
                    "status": "OK",
                }

        return results
