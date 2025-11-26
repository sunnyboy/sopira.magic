#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/generator/tests/conftest.py
#   Generator Tests Configuration - App-specific fixtures
#   Fixtures specific to generator app tests
#..............................................................

"""
   Generator Tests Configuration - App-Specific Fixtures.

   Pytest fixtures specific to generator app tests.
   Provides test data and utilities for generator tests.
"""

import pytest
from sopira_magic.apps.user.models import User
from sopira_magic.apps.company.models import Company
from sopira_magic.apps.factory.models import Factory
from sopira_magic.apps.productionline.models import ProductionLine
from sopira_magic.apps.photo.models import Photo


@pytest.fixture
def sample_user(db):
    """
    Create a sample user for testing.
    """
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )


@pytest.fixture
def multiple_users(db):
    """
    Create multiple users for testing per_source relations.
    """
    users = []
    for i in range(5):
        user = User.objects.create_user(
            username=f'user{i}',
            email=f'user{i}@example.com',
            password='testpass123',
            first_name=f'User{i}',
            last_name='Test'
        )
        users.append(user)
    return users


@pytest.fixture
def sample_company(db, sample_user):
    """
    Create a sample company for testing.
    """
    return Company.objects.create(
        code='TEST-001',
        name='Test Company',
        comment='Test company for testing'
    )


@pytest.fixture
def clean_generator_config():
    """
    Clean generator config before and after test.
    """
    from sopira_magic.apps.generator.models import GeneratorConfig
    # Clean before test
    GeneratorConfig.objects.all().delete()
    yield
    # Clean after test
    GeneratorConfig.objects.all().delete()


@pytest.fixture(autouse=True)
def clean_relations(db):
    """
    Clean relation instances before each test.
    """
    from sopira_magic.apps.relation.models import RelationInstance
    yield
    # Clean after test
    RelationInstance.objects.all().delete()

