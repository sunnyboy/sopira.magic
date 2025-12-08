#..............................................................
#   apps/scoping/apps.py
#   Django AppConfig pre scoping app
#..............................................................

"""
Django AppConfig pre scoping engine.

Konfigurácia cez Django settings:
    
    # Validácia pri štarte aplikácie
    SCOPING_VALIDATE_ON_STARTUP = True  # default: True
    # Ak True, validuje scoping pravidlá pri štarte Django aplikácie
    
    SCOPING_RAISE_ON_VALIDATION_ERRORS = False  # default: False
    # Ak True, vyhodí výnimku pri validácii chýb (inak len loguje)
    
    # Fallback stratégia
    SCOPING_FALLBACK_ENABLED = True  # default: True
    # Ak True, používa fallback stratégie pri chybách scoping engine
    
    # Middleware
    SCOPING_MIDDLEWARE_ENABLED = False  # default: False
    # Ak True, aktivuje ScopingMiddleware pre automatické aplikovanie scoping
"""

import logging
from django.apps import AppConfig
from django.conf import settings

logger = logging.getLogger(__name__)


class ScopingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sopira_magic.apps.scoping'
    verbose_name = 'Scoping Engine'
    
    def ready(self):
        """
        Volá sa pri štarte Django aplikácie.
        Validuje scoping pravidlá a kontroluje konfiguráciu.
        """
        # Validácia pravidiel pri štarte
        # SCOPING_VALIDATE_ON_STARTUP: default True
        validate_on_startup = getattr(settings, 'SCOPING_VALIDATE_ON_STARTUP', True)
        # SCOPING_RAISE_ON_VALIDATION_ERRORS: default False
        raise_on_errors = getattr(settings, 'SCOPING_RAISE_ON_VALIDATION_ERRORS', False)
        
        if validate_on_startup:
            try:
                from .validation import validate_and_raise, validate_all
                
                # Skús získať VIEWS_MATRIX pre kompletnú validáciu
                view_configs = None
                try:
                    from sopira_magic.apps.api.view_configs import VIEWS_MATRIX
                    view_configs = VIEWS_MATRIX
                except ImportError:
                    logger.debug("VIEWS_MATRIX not available, skipping scope_level validation")
                
                if raise_on_errors:
                    validate_and_raise(view_configs, raise_on_warnings=False)
                else:
                    result = validate_all(view_configs)
                    if result['errors']:
                        logger.error(
                            f"Scoping validation found {len(result['errors'])} errors:\n" +
                            "\n".join(f"  - {e}" for e in result['errors'])
                        )
                    if result['warnings']:
                        logger.warning(
                            f"Scoping validation found {len(result['warnings'])} warnings:\n" +
                            "\n".join(f"  - {w}" for w in result['warnings'])
                        )
                
                logger.info("Scoping engine validation completed")
            except Exception as e:
                logger.error(f"Error during scoping validation: {e}", exc_info=True)
                if raise_on_errors:
                    raise

