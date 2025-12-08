#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/core/apps.py
#   Core App Config - Project-wide initialization hooks
#   Used here to configure scoping registry callbacks
#..............................................................

"""
Core AppConfig for project-wide initialization.

Currently used to register scoping engine callbacks so that the
ScopingEngine can map from the project's user model and roles to
abstract scoping roles and scope values.
"""

from django.apps import AppConfig
from django.contrib.auth import get_user_model

from sopira_magic.apps.scoping.registry import (
    register_scope_provider,
    register_role_provider,
)


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "sopira_magic.apps.core"
    verbose_name = "Core"

    def ready(self):  # pragma: no cover - startup wiring
        User = get_user_model()

        def scope_provider(scope_level, scope_owner, scope_type, request=None):
            """Return scope values for a given scope level.

            For the users table we rely purely on the `is_owner` condition,
            so we do not need any external scope values here. Returning an
            empty list is safe and means "no additional scope-based filter".
            """

            return []

        def role_provider(scope_owner):
            """Map project-specific User.role to scoping roles.

            - SUPERADMIN → "superuser"
            - ADMIN      → "admin"
            - others     → "reader" (sufficient for current users rules)
            """

            if not isinstance(scope_owner, User):
                return "reader"

            role = getattr(scope_owner, "role", None)
            if role == User.UserRole.SUPERADMIN:
                return "superuser"
            if role == User.UserRole.ADMIN:
                return "admin"
            # For now, all other roles behave as "reader" for scoping
            return "reader"

        # Register callbacks once at startup
        register_scope_provider(scope_provider)
        register_role_provider(role_provider)

#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/core/apps.py
#   Core App Config - Django app configuration
#   Core application configuration
#..............................................................

"""
   Core App Config - Django App Configuration.

   Django AppConfig for core application.
   Provides base models, utilities, and middleware for the project.

   Configuration:
   - App name: sopira_magic.apps.core
   - Verbose name: Core
   - Default auto field: BigAutoField
   
   Signals:
   - Automatically registers universal cross-database cascade delete signals
   
   Important:
   - NO HARDCODING: All solutions must be universal and config-driven
   - No model-specific or app-specific hardcoded logic
"""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sopira_magic.apps.core'
    verbose_name = 'Core'
    
    def ready(self):
        """Register signals when app is ready."""
        import sopira_magic.apps.core.signals  # noqa: F401

