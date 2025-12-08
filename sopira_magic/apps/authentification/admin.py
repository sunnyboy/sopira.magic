#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/authentification/admin.py
#   Authentication Admin - Django admin configuration
#   Admin interface for authentication models
#..............................................................

"""
Authentication Admin - Django Admin Configuration.

Django admin interface configuration for authentication models.
Currently no models exist, but AUTH_CONFIG can be viewed here if needed.

Future: If authentication models are added (e.g., PasswordResetToken, TwoFactorSecret),
they will be registered here.
"""

from django.contrib import admin
from .config import AUTH_CONFIG

# Register authentication models here when they are created
# Example:
# from .models import PasswordResetToken, TwoFactorSecret
# @admin.register(PasswordResetToken)
# class PasswordResetTokenAdmin(admin.ModelAdmin):
#     list_display = ['user', 'token', 'created', 'expires_at']
#     list_filter = ['created', 'expires_at']
#     search_fields = ['user__username', 'user__email']

# For now, AUTH_CONFIG is read-only and managed via code
# No admin interface needed for configuration (it's SSOT in config.py)
