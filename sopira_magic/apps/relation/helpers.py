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
    """Get all companies for a user."""
    return RelationService.get_related_objects(user, 'user_company')


def get_company_factories(company) -> models.QuerySet:
    """Get all factories for a company."""
    return RelationService.get_related_objects(company, 'company_factory')


def get_factory_production_lines(factory) -> models.QuerySet:
    """Get all production lines for a factory."""
    return RelationService.get_related_objects(factory, 'factory_productionline')


def create_user_company(user, company, metadata: dict = None):
    """Create relation between user and company."""
    RelationService.create_relation(user, company, 'user_company', metadata)


def create_company_factory(company, factory, metadata: dict = None):
    """Create relation between company and factory."""
    RelationService.create_relation(company, factory, 'company_factory', metadata)


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

