#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/authentification/integration/audit.py
#   Audit Integration - Integration with audit module
#   Abstract audit logging via registry pattern
#..............................................................

"""
Audit Integration - Integration with Audit Module.

Abstract integration with audit module via registry pattern.
Allows audit module to register callback for authentication audit logging.

Usage:
```python
from sopira_magic.apps.authentification.integration.audit import register_audit_integration

def audit_logger(action, user, **kwargs):
    # Log to audit system
    pass

register_audit_integration(audit_logger)
```
"""

import logging

from ..registry import register_audit_logger

logger = logging.getLogger(__name__)


def register_audit_integration(audit_callback):
    """Register audit integration callback.

    Args:
        audit_callback: Function that accepts (action, user, **kwargs) and logs audit events

    Example:
        ```python
        def my_audit_logger(action, user, **kwargs):
            AuditLog.objects.create(
                action=action,
                user=user,
                ip_address=kwargs.get('ip_address'),
                user_agent=kwargs.get('user_agent'),
                success=kwargs.get('success', True),
            )

        register_audit_integration(my_audit_logger)
        ```
    """
    register_audit_logger(audit_callback)
    logger.info("Audit integration registered")

