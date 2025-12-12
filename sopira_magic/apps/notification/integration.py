#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/notification/integration.py
#   Integration - Integration with Auth module
#   Registry callback for authentication notifications
#..............................................................

"""
Integration - Integration with Auth Module.

Registers notification handler with authentification module via registry pattern.
Allows auth module to trigger notifications without tight coupling.

Integration Flow:
1. Auth module triggers notification via registry callback
2. Callback forwards to NotificationEngine
3. NotificationEngine processes notification (resolve, render, send, log)

Usage:
This module is automatically loaded via apps.py ready() method.
No manual registration needed.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


def notification_handler(notification_type: str, data: Dict[str, Any]) -> None:
    """Handler for authentification notifications.
    
    This function is registered as callback with auth module.
    Auth module calls this function when authentication events occur.
    
    Args:
        notification_type: Type of notification (e.g., 'login_notification', 'signup_notification')
        data: Context data for notification (user, ip_address, etc.)
    
    Example:
        Auth module calls:
        ```python
        notification_handler('login_notification', {
            'user': user,
            'ip_address': '192.168.1.1',
            'user_agent': 'Mozilla/5.0'
        })
        ```
    """
    from .engine import NotificationEngine
    
    logger.info(f"📬 Notification handler triggered: {notification_type}")
    
    try:
        # Forward to NotificationEngine
        result = NotificationEngine.send_notification(
            notification_type=notification_type,
            context=data
        )
        
        if result['success']:
            logger.info(
                f"✅ Notification {notification_type} sent successfully: "
                f"{result['sent_count']} sent, {result['failed_count']} failed"
            )
        else:
            logger.warning(
                f"⚠️  Notification {notification_type} partially failed: "
                f"{result['sent_count']} sent, {result['failed_count']} failed, "
                f"errors: {result['errors']}"
            )
    
    except Exception as e:
        logger.error(f"❌ Notification handler error for {notification_type}: {e}", exc_info=True)


def register_with_auth() -> None:
    """Register notification handler with authentification module.
    
    This function is called automatically from apps.py ready() method.
    Registers notification_handler as callback for auth notifications.
    
    Note:
        Uses loose coupling via registry pattern - no direct imports of auth internals.
    """
    try:
        from sopira_magic.apps.authentification.integration.notification import register_notification_integration
        
        # Register our handler
        register_notification_integration(notification_handler)
        
        logger.info("✅ Notification integration registered with Auth module")
    
    except ImportError as e:
        logger.warning(f"⚠️  Could not register notification integration with Auth module: {e}")
    
    except Exception as e:
        logger.error(f"❌ Error registering notification integration: {e}", exc_info=True)


def unregister_with_auth() -> None:
    """Unregister notification handler (for testing/cleanup).
    
    Note: Currently not implemented in auth module registry.
    """
    logger.info("Notification integration unregister called (not implemented)")

