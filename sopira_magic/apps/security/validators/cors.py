"""CORS validator - ConfigDriven CORS validácia."""

import re
from typing import Dict

from django.http import HttpRequest


class CorsValidator:
    """ConfigDriven CORS validator - SSOT pre CORS rozhodnutia."""

    @staticmethod
    def validate(request: HttpRequest, cors_config: Dict) -> bool:
        """Validuj CORS request podľa konfigurácie."""

        origin = request.META.get("HTTP_ORIGIN", "")
        if not origin:
            # Bez Origin headera to typicky nie je cross-origin request
            return True

        allowed_origins = cors_config.get("allowed_origins", [])

        # Presná zhoda
        if origin in allowed_origins:
            return True

        # Wildcard matching typu "https://*.onrender.com"
        for allowed in allowed_origins:
            if "*" in allowed:
                pattern = allowed.replace(".", r"\.").replace("*", ".*")
                if re.match(pattern, origin):
                    return True

        return False

    @staticmethod
    def get_headers(request: HttpRequest, cors_config: Dict) -> Dict[str, str]:
        """Vráť CORS headers pre response podľa konfigurácie."""

        headers: Dict[str, str] = {}
        origin = request.META.get("HTTP_ORIGIN", "")

        if CorsValidator.validate(request, cors_config):
            if origin:
                headers["Access-Control-Allow-Origin"] = origin
            headers["Access-Control-Allow-Credentials"] = "true"

            if request.method == "OPTIONS":
                allowed_methods = cors_config.get("allowed_methods", [])
                allowed_headers = cors_config.get("allowed_headers", [])
                exposed_headers = cors_config.get("exposed_headers", [])
                max_age = cors_config.get("max_age", 86400)

                if allowed_methods:
                    headers["Access-Control-Allow-Methods"] = ", ".join(allowed_methods)
                if allowed_headers:
                    headers["Access-Control-Allow-Headers"] = ", ".join(allowed_headers)
                if exposed_headers:
                    headers["Access-Control-Expose-Headers"] = ", ".join(exposed_headers)

                headers["Access-Control-Max-Age"] = str(max_age)

        return headers
