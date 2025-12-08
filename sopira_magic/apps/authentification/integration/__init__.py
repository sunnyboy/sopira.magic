#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/authentification/integration/__init__.py
#   Authentication Integration - Module exports
#   Integration modules for audit and notification
#..............................................................

"""
Authentication Integration - Module Exports.

Integration modules for audit logging and notifications.
"""

from .audit import register_audit_integration
from .notification import register_notification_integration

__all__ = [
    "register_audit_integration",
    "register_notification_integration",
]

