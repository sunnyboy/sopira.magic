"""Security module - ConfigDriven & SSOT security engine.

Verejné API pre hostiteľskú aplikáciu (Django projekt).
"""

from .registry import (
    register_environment_detector,
    register_certificate_provider,
    register_security_auditor,
    register_custom_header_provider,
    get_environment,
    get_certificate_info,
    get_custom_headers,
)

from .engine import SecurityEngine
from .middleware import SecurityMiddleware
from .types import EnvironmentType, SecurityLevel

__all__ = [
    # Registry API
    "register_environment_detector",
    "register_certificate_provider",
    "register_security_auditor",
    "register_custom_header_provider",
    "get_environment",
    "get_certificate_info",
    "get_custom_headers",
    # Engine API
    "SecurityEngine",
    # Middleware
    "SecurityMiddleware",
    # Types
    "EnvironmentType",
    "SecurityLevel",
]
