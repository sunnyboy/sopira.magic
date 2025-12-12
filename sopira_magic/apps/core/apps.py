#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/core/apps.py
#   Core App Config - Project-wide initialization hooks
#   Scoping registry callbacks for full scope-aware functionality
#..............................................................

"""
Core AppConfig for project-wide initialization.

Registers scoping engine callbacks so that the ScopingEngine can map from
the project's user model and roles to abstract scoping roles and scope values.

Key Features:
- Full scope-aware functionality for notifications
- Company and Factory scope resolution
- User role mapping to scoping roles  
- Integration with mystate for accessible scopes

Scoping Levels:
- Level 0: User (user.id)
- Level 1: Company (company.id)
- Level 2: Factory (factory.id)
"""

import logging
from django.apps import AppConfig
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "sopira_magic.apps.core"
    verbose_name = "Core"

    def ready(self):
        """Initialize scoping callbacks and signals."""
        # Register signals
        import sopira_magic.apps.core.signals  # noqa: F401
        
        # Register scoping callbacks
        self._register_scoping_callbacks()
    
    def _register_scoping_callbacks(self):
        """Register scope_provider and role_provider with scoping engine."""
        try:
            from sopira_magic.apps.scoping import register_scope_provider, register_role_provider
            
            User = get_user_model()
            
            def role_provider(scope_owner):
                """Map project-specific User.role to scoping roles."""
                if not isinstance(scope_owner, User):
                    return "reader"
                
                if getattr(scope_owner, 'is_superuser', False):
                    return "superuser"
                
                role = getattr(scope_owner, "role", None)
                if not role:
                    return "reader"
                
                role_lower = role.lower()
                if role_lower == "superadmin":
                    return "superuser"
                elif role_lower == "admin":
                    return "admin"
                elif role_lower == "staff":
                    return "staff"
                elif role_lower == "editor":
                    return "editor"
                elif role_lower == "adhoc":
                    return "adhoc"
                else:
                    return "reader"
            
            def scope_provider(scope_level, scope_owner, scope_type, request=None):
                """Return scope values for a given scope level."""
                if not isinstance(scope_owner, User):
                    return []
                
                if getattr(scope_owner, 'is_superuser', False) or getattr(scope_owner, 'role', '').lower() == 'superadmin':
                    return get_all_scope_values(scope_level)
                
                if scope_level == 0:
                    return [str(scope_owner.id)]
                
                try:
                    if scope_type == 'selected':
                        return get_selected_scope(scope_owner, scope_level, request)
                    elif scope_type == 'accessible':
                        return get_accessible_scope(scope_owner, scope_level, request)
                except Exception as e:
                    logger.warning(f"Scope resolution failed: {e}")
                    return []
                
                return []
            
            def get_all_scope_values(scope_level):
                """Get all scope values for superuser."""
                try:
                    if scope_level == 0:
                        from sopira_magic.apps.m_user.models import User
                        return [str(uid) for uid in User.objects.values_list('id', flat=True)]
                    elif scope_level == 1:
                        from sopira_magic.apps.m_company.models import Company
                        return [str(cid) for cid in Company.objects.filter(active=True).values_list('id', flat=True)]
                    elif scope_level == 2:
                        from sopira_magic.apps.m_factory.models import Factory
                        return [str(fid) for fid in Factory.objects.filter(active=True).values_list('id', flat=True)]
                except Exception as e:
                    logger.error(f"Failed to get all scope values: {e}")
                    return []
                return []
            
            def get_selected_scope(user, scope_level, request=None):
                """Get currently selected scope.
                
                NOTE: Current state is stored in LocalStorage (frontend), not in database.
                SavedState model contains only saved presets, not current state.
                
                For now, fallback to accessible scope (all scopes user has access to).
                In future, could be extended to read from request session or other
                persisted storage.
                """
                try:
                    # Fallback to accessible scope
                    # (returns all companies/factories user has access to)
                    return get_accessible_scope(user, scope_level, request)
                except Exception as e:
                    logger.debug(f"Could not get selected scope for {user.username}: {e}")
                    return []
            
            def get_accessible_scope(user, scope_level, request=None):
                """Get all accessible scopes using relation system."""
                try:
                    if scope_level == 1:
                        return get_user_companies(user)
                    elif scope_level == 2:
                        return get_user_factories(user)
                except Exception as e:
                    logger.error(f"Failed to get accessible scope: {e}")
                    return []
                return []
            
            def get_user_companies(user):
                """Get companies accessible to user."""
                try:
                    from sopira_magic.apps.relation.helpers import get_user_companies
                    companies = get_user_companies(user)
                    return [str(c.id) for c in companies]
                except ImportError:
                    from sopira_magic.apps.m_company.models import Company
                    return [str(cid) for cid in Company.objects.filter(active=True).values_list('id', flat=True)]
                except Exception as e:
                    logger.error(f"Failed to get user companies: {e}")
                    return []
            
            def get_user_factories(user):
                """Get factories accessible to user."""
                try:
                    company_ids = get_user_companies(user)
                    if not company_ids:
                        return []
                    from sopira_magic.apps.m_factory.models import Factory
                    factories = Factory.objects.filter(company_id__in=company_ids, active=True)
                    return [str(f.id) for f in factories]
                except Exception as e:
                    logger.error(f"Failed to get user factories: {e}")
                    return []
            
            register_scope_provider(scope_provider)
            register_role_provider(role_provider)
            logger.info("✅ Scoping registry callbacks registered (FULL IMPLEMENTATION)")
        
        except Exception as e:
            logger.warning(f"⚠️  Could not register scoping callbacks: {e}")

