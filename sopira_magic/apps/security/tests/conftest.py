"""Test fixtures pre Security Module."""

import pytest
from unittest.mock import Mock
from django.http import HttpRequest

from sopira_magic.apps.security.types import EnvironmentType


@pytest.fixture
def mock_request():
    """Vytvor mock Django request."""
    request = Mock(spec=HttpRequest)
    request.method = "GET"
    request.META = {}
    request.is_secure.return_value = False
    request.get_host.return_value = "localhost:8000"
    request.get_full_path.return_value = "/api/test/"
    return request


@pytest.fixture
def mock_https_request():
    """Vytvor mock HTTPS request."""
    request = Mock(spec=HttpRequest)
    request.method = "GET"
    request.META = {}
    request.is_secure.return_value = True
    request.get_host.return_value = "thermal-eye.sopira.com"
    request.get_full_path.return_value = "/api/test/"
    return request


@pytest.fixture
def mock_request_with_origin():
    """Vytvor mock request s origin header."""
    request = Mock(spec=HttpRequest)
    request.method = "GET"
    request.META = {"HTTP_ORIGIN": "http://localhost:5173"}
    request.is_secure.return_value = False
    request.get_host.return_value = "localhost:8000"
    return request


@pytest.fixture
def local_environment_config():
    """Vráti konfiguráciu pre lokálny vývoj."""
    from sopira_magic.apps.security.config import SECURITY_CONFIG_MATRIX

    return SECURITY_CONFIG_MATRIX[EnvironmentType.LOCAL]


@pytest.fixture
def production_environment_config():
    """Vráti konfiguráciu pre produkciu."""
    from sopira_magic.apps.security.config import SECURITY_CONFIG_MATRIX

    return SECURITY_CONFIG_MATRIX[EnvironmentType.PRODUCTION]


@pytest.fixture
def mock_environment_detector():
    """Vytvor mock environment detector."""

    def detector(request=None):  # pragma: no cover - simple mock
        return "local"

    return detector


@pytest.fixture
def mock_certificate_provider():
    """Vytvor mock certificate provider."""

    def provider(action, domain=None):  # pragma: no cover - simple mock
        return {
            "valid": True,
            "domain": domain or "thermal-eye.sopira.com",
            "days_remaining": 365,
            "issuer": "Let's Encrypt",
        }

    return provider


@pytest.fixture
def security_engine_with_mocks(mock_environment_detector, mock_certificate_provider):
    """Vytvor SecurityEngine s mock registry."""
    from sopira_magic.apps.security.registry import (
        register_environment_detector,
        register_certificate_provider,
    )
    from sopira_magic.apps.security.engine import SecurityEngine

    register_environment_detector(mock_environment_detector)
    register_certificate_provider(mock_certificate_provider)
    return SecurityEngine


@pytest.fixture(params=[EnvironmentType.LOCAL, EnvironmentType.PRODUCTION])
def environment_config(request):
    """Parametrizovaný fixture pre environment konfigurácie."""
    from sopira_magic.apps.security.config import SECURITY_CONFIG_MATRIX

    return SECURITY_CONFIG_MATRIX[request.param]


@pytest.fixture
def all_environment_configs():
    """Vráti všetky environment konfigurácie."""
    from sopira_magic.apps.security.config import SECURITY_CONFIG_MATRIX

    return SECURITY_CONFIG_MATRIX
