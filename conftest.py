#..............................................................
#   ~/sopira.magic/version_01/conftest.py
#   Pytest Configuration - Global fixtures
#   Global pytest fixtures for all tests
#..............................................................

"""
   Pytest Configuration - Global Fixtures.

   Global pytest fixtures available to all tests.
   Provides common test setup and utilities.
"""

import pytest
from django.contrib.auth import get_user_model
from django.test import Client

User = get_user_model()


@pytest.fixture(scope='function')
def db_access(request):
    """
    Ensure database access for tests.
    This fixture is automatically used by pytest-django.
    """
    pass


@pytest.fixture
def api_client():
    """
    Django REST Framework API client fixture.
    """
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def django_client():
    """
    Django test client fixture.
    """
    return Client()


@pytest.fixture
def test_user(db):
    """
    Create a test user for testing.
    """
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def admin_user(db):
    """
    Create an admin user for testing.
    """
    return User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='adminpass123'
    )


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """
    Enable database access for all tests automatically.
    This ensures all tests can access the database without
    explicitly using @pytest.mark.django_db decorator.
    """
    pass

