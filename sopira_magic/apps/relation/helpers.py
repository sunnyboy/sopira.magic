#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/relation/helpers.py
#   Relation Helpers - Convenience functions
#   Easy-to-use helper functions for common relation operations
#..............................................................

"""
Relation Helpers - Convenience Functions.

   Convenience functions for common relation operations.
   Provides easy-to-use wrappers around RelationService for common use cases.

   Helper Functions:

   Query Functions:
   - get_user_companies(user): Get all companies for a user
   - get_company_factories(company): Get all factories for a company
   - get_factory_production_lines(factory): Get all production lines for a factory

   Creation Functions:
   - create_user_company(user, company, metadata): Create user-company relation
   - create_company_factory(company, factory, metadata): Create company-factory relation
   - create_factory_production_line(factory, production_line, metadata): Create factory-productionline relation

   Query Builder Functions:
   - query_companies_by_user(user): Query companies filtered by user
   - query_factories_by_company(company): Query factories filtered by company
   - query_production_lines_by_factory(factory): Query production lines filtered by factory

   Usage:
   ```python
   from sopira_magic.apps.relation.helpers import get_user_companies, create_user_company
   companies = get_user_companies(user)
   create_user_company(user, company)
   ```
"""

from typing import Any
from django.db import models
from .services import RelationService


def get_user_companies(user) -> models.QuerySet:
    """Get all companies for a user (bivalent: config-driven or hardcoded M2M)."""
    from sopira_magic.apps.relation.config import RELATION_CONFIG
    
    # Try config-driven first (if user_company exists in config)
    if 'user_company' in RELATION_CONFIG:
        return RelationService.get_related_objects(user, 'user_company')
    
    # Fallback to hardcoded M2M (UserCompany)
    from sopira_magic.apps.m_company.models import Company
    return Company.objects.filter(users=user, active=True)


def get_company_factories(company) -> models.QuerySet:
    """Get all factories for a company (bivalent: config-driven or hardcoded FK)."""
    from sopira_magic.apps.relation.config import RELATION_CONFIG
    
    # Try config-driven first (if company_factory exists in config)
    if 'company_factory' in RELATION_CONFIG:
        return RelationService.get_related_objects(company, 'company_factory')
    
    # Fallback to hardcoded FK (Factory.company)
    from sopira_magic.apps.m_factory.models import Factory
    return Factory.objects.filter(company=company, active=True)


def get_factory_production_lines(factory) -> models.QuerySet:
    """Get all production lines for a factory."""
    return RelationService.get_related_objects(factory, 'factory_productionline')


def create_user_company(user, company, metadata: dict = None):
    """Create relation between user and company (bivalent: config or hardcoded M2M)."""
    from sopira_magic.apps.relation.config import RELATION_CONFIG
    
    # Try config-driven first
    if 'user_company' in RELATION_CONFIG:
        RelationService.create_relation(user, company, 'user_company', metadata)
    else:
        # Use hardcoded M2M (UserCompany)
        from sopira_magic.apps.m_company.models import UserCompany
        role = metadata.get('role', 'member') if metadata else 'member'
        UserCompany.objects.get_or_create(
            user=user,
            company=company,
            defaults={'role': role}
        )


def create_company_factory(company, factory, metadata: dict = None):
    """Create relation between company and factory (bivalent: config or hardcoded FK)."""
    from sopira_magic.apps.relation.config import RELATION_CONFIG
    
    # Try config-driven first
    if 'company_factory' in RELATION_CONFIG:
        RelationService.create_relation(company, factory, 'company_factory', metadata)
    else:
        # Use hardcoded FK (Factory.company) - already set during factory creation
        # This function becomes a no-op for hardcoded relations
        pass


def create_factory_production_line(factory, production_line, metadata: dict = None):
    """Create relation between factory and production line."""
    RelationService.create_relation(factory, production_line, 'factory_productionline', metadata)


def query_companies_by_user(user_id: Any) -> models.QuerySet:
    """Query companies filtered by user ID."""
    return RelationService.build_query('company.Company', {'user': user_id})


def query_factories_by_company(company_id: Any) -> models.QuerySet:
    """Query factories filtered by company ID."""
    return RelationService.build_query('factory.Factory', {'company': company_id})


def query_production_lines_by_factory(factory_id: Any) -> models.QuerySet:
    """Query production lines filtered by factory ID."""
    return RelationService.build_query('productionline.ProductionLine', {'factory': factory_id})

