#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/core/apps.py
#   Core App Config - CLEAN VERSION
#..............................................................

import logging
from django.apps import AppConfig
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sopira_magic.apps.core'
    
    def ready(self):
        self._register_scoping_callbacks()
    
    def _register_scoping_callbacks(self):
        try:
            from sopira_magic.apps.scoping import register_scope_resolver, register_role_provider
            User = get_user_model()
            
            # Role provider
            def role_provider(user):
                if not isinstance(user, User):
                    return "reader"
                if getattr(user, 'is_superuser', False):
                    return "superuser"
                role = getattr(user, 'role', '').lower()
                if role == 'superadmin':
                    return 'superuser'
                return role if role in ['admin', 'staff', 'editor', 'reader'] else 'reader'
            
            # Scope resolver
            def scope_resolver(level, user, scope_type):
                if not isinstance(user, User):
                    return []
                
                if level == 0:
                    return [str(user.id)]
                
                if level == 1:
                    try:
                        from sopira_magic.apps.relation.helpers import get_user_companies
                        companies = get_user_companies(user)
                        return [str(c.id) for c in companies]
                    except:
                        return []
                
                if level == 2:
                    try:
                        company_ids = scope_resolver(1, user, scope_type)
                        if not company_ids:
                            return []
                        from sopira_magic.apps.m_factory.models import Factory
                        factories = Factory.objects.filter(company_id__in=company_ids, active=True)
                        return [str(f.id) for f in factories]
                    except:
                        return []
                
                if level == 3:
                    try:
                        factory_ids = scope_resolver(2, user, scope_type)
                        if not factory_ids:
                            return []
                        from sopira_magic.apps.m_location.models import Location
                        locations = Location.objects.filter(factory_id__in=factory_ids, active=True)
                        return [str(loc.id) for loc in locations]
                    except:
                        return []
                
                return []
            
            register_role_provider(role_provider)
            register_scope_resolver(scope_resolver)
            logger.info("✅ Scoping callbacks registered (CLEAN)")
        
        except Exception as e:
            logger.warning(f"⚠️  Scoping registration failed: {e}")
