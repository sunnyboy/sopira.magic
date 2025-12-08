#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/authentification/integration/notification.py
#   Notification Integration - Integration with notification module
#   Abstract notification sending via registry pattern
#..............................................................

"""
Notification Integration - Integration with Notification Module.

Abstract integration with notification module via registry pattern.
Allows notification module to register callback for authentication notifications.

Usage:
```python
from sopira_magic.apps.authentification.integration.notification import register_notification_integration

def notification_sender(notification_type, data):
    # Send email/SMS/push notification
    pass

register_notification_integration(notification_sender)
```
"""

import logging

from ..registry import register_notification_sender

logger = logging.getLogger(__name__)


def register_notification_integration(notification_callback):
    """Register notification integration callback.

    Args:
        notification_callback: Function that accepts (notification_type, data) and sends notifications

    Example:
        ```python
        def my_notification_sender(notification_type, data):
            if notification_type == 'login_notification':
                send_email(
                    to=settings.ADMIN_EMAIL,
                    subject='Login Notification',
                    template='login_notification',
                    context=data,
                )

        register_notification_integration(my_notification_sender)
        ```
    """
    register_notification_sender(notification_callback)
    logger.info("Notification integration registered")

