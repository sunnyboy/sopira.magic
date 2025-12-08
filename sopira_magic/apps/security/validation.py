"""Validation utils pre security konfiguráciu (SSOT).

Používa sa pri štarte aplikácie na overenie konzistencie
``SECURITY_CONFIG_MATRIX`` a súvisiacich typov.
"""

from typing import Dict, List

from .config import SECURITY_CONFIG_MATRIX
from .types import EnvironmentConfig, EnvironmentType, SecurityHeaders, SecurityLevel


REQUIRED_FIELDS = [
    "name",
    "env_type",
    "security_level",
    "force_https",
    "allowed_hosts",
    "cors",
    "csp",
    "ssl",
    "headers",
]


def _validate_single_env(env_type: EnvironmentType, cfg: EnvironmentConfig, errors: List[str]) -> None:
    """Validate configuration for a single environment and append errors in-place."""

    # Required top-level fields
    for field in REQUIRED_FIELDS:
        if field not in cfg:
            errors.append(
                f"Missing required field '{field}' in environment {env_type.value}"
            )

    # env_type field vs key
    if cfg.get("env_type") != env_type:
        errors.append(
            f"env_type {cfg.get('env_type')} does not match key {env_type.value}"
        )

    # security_level must be valid
    level = cfg.get("security_level")
    if not isinstance(level, SecurityLevel):
        try:
            SecurityLevel(str(level))
        except Exception:
            errors.append(
                f"Invalid security level '{level}' in environment {env_type.value}"
            )

    # allowed_hosts non-empty (except LOCAL may be more relaxed)
    allowed_hosts = cfg.get("allowed_hosts", [])
    if not isinstance(allowed_hosts, list) or not allowed_hosts:
        errors.append(
            f"Missing or empty allowed_hosts in environment {env_type.value}"
        )

    # CORS validation
    cors_cfg: Dict = cfg.get("cors", {})  # type: ignore[assignment]
    origins = cors_cfg.get("allowed_origins", [])
    if not isinstance(origins, list):
        errors.append(
            f"Environment {env_type.value} has invalid cors.allowed_origins (must be list)"
        )
    else:
        # Duplicate origins
        if len(origins) != len(set(origins)):
            errors.append(
                f"Duplicate CORS origin in environment {env_type.value}: {origins}"
            )
        # CORS allow_credentials + wildcard ('*' ako doslovný origin)
        if cors_cfg.get("allow_credentials") and any(
            o.strip() == "*" for o in origins
        ):
            errors.append(
                f"CORS allow_credentials with wildcard in environment {env_type.value}"
            )

    # CSP validation
    csp_cfg: Dict = cfg.get("csp", {})  # type: ignore[assignment]
    default_src = csp_cfg.get("default_src")
    if not default_src:
        errors.append(
            f"CSP default_src cannot be empty in environment {env_type.value}"
        )

    # SSL validation
    ssl_cfg: Dict = cfg.get("ssl", {})  # type: ignore[assignment]
    if ssl_cfg.get("enabled"):
        hsts_max_age = ssl_cfg.get("hsts_max_age", 0)
        if not isinstance(hsts_max_age, int) or hsts_max_age <= 0:
            errors.append(
                f"Invalid HSTS max_age in environment {env_type.value}: {hsts_max_age}"
            )

    # Headers validation
    headers_cfg: SecurityHeaders = cfg.get("headers", {})  # type: ignore[assignment]
    if not isinstance(headers_cfg, dict):
        errors.append(
            f"Environment {env_type.value} has invalid headers configuration (must be dict)"
        )


def validate_security_config() -> List[str]:
    """Validuj ``SECURITY_CONFIG_MATRIX`` a vráť zoznam chýb (alebo [] ak OK).

    Funkcia je navrhnutá tak, aby poskytovala detailné chybové hlásenia,
    ktoré zodpovedajú testom v test_strategy ("Missing required field",
    "Invalid security level", "CORS allow_credentials with wildcard", atď.).
    """

    errors: List[str] = []

    # Empty matrix
    if not SECURITY_CONFIG_MATRIX:
        errors.append("No environment configurations defined")
        return errors

    # Každý EnvironmentType musí mať konfiguráciu
    for env_type in EnvironmentType:
        if env_type not in SECURITY_CONFIG_MATRIX:
            errors.append(f"Missing configuration for environment {env_type.value}")
            continue

        cfg: EnvironmentConfig = SECURITY_CONFIG_MATRIX[env_type]
        _validate_single_env(env_type, cfg, errors)

    return errors
