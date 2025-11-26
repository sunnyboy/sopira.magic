#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/relation/admin.py
#   Relation Admin - Django admin configuration
#   Admin interface for RelationRegistry and RelationInstance
#..............................................................

"""
   Relation Admin - Django Admin Configuration.

   Django admin interface configuration for relation models.
   Provides management interface for relation registry and instances.

   Admin Classes:

   1. RelationRegistryAdmin
      - Displays: source_model, target_model, relation_type, field_name, active, created
      - Filters: relation_type, source_model, target_model, active
      - Search: source_model, target_model, field_name, related_name
      - Read-only: created, updated

   2. RelationInstanceAdmin
      - Displays: relation, source_object, target_object, created
      - Filters: relation, created
      - Search: relation source_model, relation target_model
      - Read-only: created, updated

   3. RelationInstanceInline
      - GenericTabularInline for RelationInstance
      - Allows inline editing of relation instances
"""

from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from .models import RelationRegistry, RelationInstance


@admin.register(RelationRegistry)
class RelationRegistryAdmin(admin.ModelAdmin):
    """RelationRegistry admin configuration."""
    list_display = ['source_model', 'target_model', 'relation_type', 'field_name', 'active', 'created']
    list_filter = ['relation_type', 'source_model', 'target_model', 'active']
    search_fields = ['source_model', 'target_model', 'field_name', 'related_name']
    readonly_fields = ['created', 'updated']


class RelationInstanceInline(GenericTabularInline):
    """Inline admin for RelationInstance."""
    model = RelationInstance
    extra = 0
    ct_field = 'source_content_type'
    ct_fk_field = 'source_object_id'


@admin.register(RelationInstance)
class RelationInstanceAdmin(admin.ModelAdmin):
    """RelationInstance admin configuration."""
    list_display = ['relation', 'source_object', 'target_object', 'created']
    list_filter = ['relation', 'created']
    search_fields = ['relation__source_model', 'relation__target_model']
    readonly_fields = ['created', 'updated']
