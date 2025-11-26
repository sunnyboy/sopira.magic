#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/equipment/admin.py
#   Equipment Admin - Django admin configuration
#   Admin interface for Equipment model
#..............................................................

"""
   Equipment Admin - Django Admin Configuration.

   Django admin interface configuration for Equipment model.
   Extends NamedWithCodeModelAdmin with equipment-specific fields.

   Admin Classes:

   EquipmentAdmin (extends NamedWithCodeModelAdmin)
   - Displays: code, name, equipment_type, brand, model, active, visible
   - Filters: equipment_type, brand, active, visible
   - Search: code, name, brand, model, serial_number
"""

from django.contrib import admin
from sopira_magic.apps.core.admin import NamedWithCodeModelAdmin
from .models import Equipment


@admin.register(Equipment)
class EquipmentAdmin(NamedWithCodeModelAdmin):
    """Equipment admin configuration."""
    list_display = ['code', 'name', 'equipment_type', 'brand', 'model', 'active', 'visible']
    list_filter = ['equipment_type', 'brand', 'active', 'visible']
    search_fields = ['code', 'name', 'brand', 'model', 'serial_number']
