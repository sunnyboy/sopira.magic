#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/user/models.py
#   User Models - Extended Django User model
#   User management with roles and preferences
#..............................................................

"""
   User Models - Extended Django User Model.

   Custom user model extending Django's AbstractUser with additional fields
   and user preferences management.

   Models:

   1. User (extends AbstractUser)
      - Additional fields: phone, address, role, date_of_birth, photo_url
      - User roles: SUPERADMIN, ADMIN, STAFF, EDITOR, READER, ADHOC
      - Default role: READER
      - Custom authentication via AUTH_USER_MODEL setting

   2. UserPreference (extends TimeStampedModel)
      - One-to-one relationship with User
      - JSON fields: settings, preferences
      - Stores user-specific UI preferences and application settings

   Usage:
   ```python
   from sopira_magic.apps.user.models import User, UserPreference
   user = User.objects.create_user(username='test', email='test@example.com')
   preference = UserPreference.objects.create(user=user, settings={'theme': 'dark'})
   ```
"""

import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from sopira_magic.apps.core.models import TimeStampedModel


class User(AbstractUser):
    """Extended User model with UUID primary key."""
    # Override AbstractUser.id (BigAutoField) with UUIDField for consistency
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    class UserRole(models.TextChoices):
        SUPERADMIN = 'superadmin', _('SuperAdmin')
        ADMIN = 'admin', _('Admin')
        STAFF = 'staff', _('Staff')
        EDITOR = 'editor', _('Editor')
        READER = 'reader', _('Reader')
        ADHOC = 'adhoc', _('AdHoc')
    
    phone = models.CharField(max_length=50, blank=True, default="")
    address = models.TextField(blank=True, default="")
    role = models.CharField(
        max_length=16,
        choices=UserRole.choices,
        default=UserRole.READER,
        help_text=_('Authorization level for the user'),
    )
    date_of_birth = models.DateField(null=True, blank=True)
    photo_url = models.URLField(blank=True, default="")
    
    def save(self, *args, **kwargs):
        """
        Override save to protect SA user (sopira) from deactivation.
        
        This is a fallback protection in case someone bypasses the API
        (e.g., Django admin, shell, direct SQL).
        """
        # Protection: SA user 'sopira' must always remain active
        if self.username == 'sopira' and not self.is_active:
            self.is_active = True
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(
                f"[SA Protection - Model] Auto-reverted 'sopira' is_active to True. "
                f"SA user cannot be deactivated."
            )
        
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")


class UserPreference(TimeStampedModel):
    """User preferences and settings."""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="preferences"
    )
    settings = models.JSONField(default=dict, blank=True)
    preferences = models.JSONField(default=dict, blank=True)
    
    class Meta:
        verbose_name = _("User Preference")
        verbose_name_plural = _("User Preferences")
