#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/user/admin.py
#   User Admin - Django admin configuration
#   Admin interface for User and UserPreference models
#..............................................................

"""
   User Admin - Django Admin Configuration.

   Django admin interface configuration for User and UserPreference models.
   Extends Django's default UserAdmin with custom fields and filters.

   Admin Classes:

   1. UserAdmin (extends BaseUserAdmin)
      - Displays: username, email, first_name, last_name, role, photo_url, is_staff, is_active
      - Filters: role, is_staff, is_superuser, is_active
      - Search: username, email, first_name, last_name
      - Additional fieldsets: phone, address, role, date_of_birth, photo_url

   2. UserPreferenceAdmin
      - Displays: user, created, updated
      - Search: user username, user email
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, UserPreference


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """User admin configuration."""
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'photo_url', 'is_staff', 'is_active']
    list_filter = ['role', 'is_staff', 'is_superuser', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        (_('Additional Info'), {'fields': ('phone', 'address', 'role', 'date_of_birth', 'photo_url')}),
    )


@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    """UserPreference admin configuration."""
    list_display = ['user', 'created', 'updated']
    search_fields = ['user__username', 'user__email']
