"""Security middleware - ConfigDriven security middleware."""

import logging

from django.http import HttpRequest, HttpResponse
from django.utils.deprecation import MiddlewareMixin

from .engine import SecurityEngine

logger = logging.getLogger(__name__)


class SecurityMiddleware(MiddlewareMixin):
    """ConfigDriven security middleware - SSOT pre všetky security policies."""

    def __init__(self, get_response):
        super().__init__(get_response)
        self.get_response = get_response

    def process_request(self, request: HttpRequest):
        """Spracuj request pred view - SSOT security decisions."""

        # 1) HTTPS redirect
        redirect_url = SecurityEngine.enforce_https_redirect(request)
        if redirect_url:
            logger.debug("Redirecting to HTTPS: %s", redirect_url)
            response = HttpResponse(status=307)
            response["Location"] = redirect_url
            return response

        # 2) CORS preflight
        if request.method == "OPTIONS":
            if SecurityEngine.validate_cors(request):
                response = HttpResponse(status=200)
                cors_headers = SecurityEngine.get_cors_headers(request)
                for key, value in cors_headers.items():
                    response[key] = value
                return response

        # 3) CSRF validácia (len pre state-changing metódy)
        if request.method not in ["GET", "HEAD", "OPTIONS", "TRACE"]:
            if not SecurityEngine.validate_csrf(request):
                logger.warning(
                    "CSRF validation failed for %s %s", request.method, request.path
                )
                return HttpResponse("CSRF validation failed", status=403)

        # 4) Debug logging v nízkych environmentoch
        config = SecurityEngine.get_config(request)
        if config["env_type"].value in {"local", "dev"}:
            logger.debug("Security check passed for %s %s", request.method, request.path)

        return None

    def process_response(
        self, request: HttpRequest, response: HttpResponse
    ) -> HttpResponse:
        """Spracuj response po view - aplikuj security headers."""

        response = SecurityEngine.apply_security_headers(response, request)

        if request.GET.get("_security_debug"):
            config = SecurityEngine.get_config(request)
            response["X-Security-Config"] = (
                f"env={config['env_type'].value}, level={config['security_level'].value}"
            )

        return response

    def process_exception(self, request: HttpRequest, exception):
        """Spracuj výnimku - security logovanie."""

        msg = str(exception).lower()
        if "csrf" in msg or "forbidden" in msg:
            logger.warning(
                "Security exception: %s for %s %s", exception, request.method, request.path
            )

        return None
