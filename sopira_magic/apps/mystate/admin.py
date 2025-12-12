#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/mystate/admin.py
#   MyState Admin - Django admin configuration
#   Admin interface for state management models
#..............................................................

"""
   MyState Admin - Django Admin Configuration.

   Admin interface for SavedState and SharedState models.
   Provides management interface for debugging and support.

   Admin Classes:
   - SavedStateAdmin: Manage saved presets
   - SharedStateAdmin: Manage sharing relationships
"""

from django.contrib import admin
from .models import SavedState, SharedState


@admin.register(SavedState)
class SavedStateAdmin(admin.ModelAdmin):
    """Admin configuration for SavedState model."""
    
    list_display = [
        'preset_name',
        'scope_type',
        'scope_key',
        'user_id',
        'is_default',
        'created',
        'updated',
    ]
    
    list_filter = [
        'scope_type',
        'is_default',
        'created',
    ]
    
    search_fields = [
        'preset_name',
        'scope_key',
        'description',
    ]
    
    readonly_fields = [
        'id',
        'uuid',
        'created',
        'updated',
    ]
    
    fieldsets = (
        ('Identification', {
            'fields': ('id', 'uuid', 'user_id')
        }),
        ('Scope', {
            'fields': ('scope_type', 'scope_key')
        }),
        ('Preset', {
            'fields': ('preset_name', 'description', 'is_default')
        }),
        ('State Data', {
            'fields': ('state_data',),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created', 'updated'),
            'classes': ('collapse',),
        }),
    )
    
    ordering = ['-updated']
    
    # Use STATE database
    using = 'state'
    
    def get_queryset(self, request):
        return super().get_queryset(request).using(self.using)
    
    def save_model(self, request, obj, form, change):
        obj.save(using=self.using)
    
    def delete_model(self, request, obj):
        obj.delete(using=self.using)


@admin.register(SharedState)
class SharedStateAdmin(admin.ModelAdmin):
    """Admin configuration for SharedState model."""
    
    list_display = [
        'source_preset',
        'shared_by_id',
        'shared_with_id',
        'can_edit',
        'created',
    ]
    
    list_filter = [
        'can_edit',
        'created',
    ]
    
    search_fields = [
        'source_preset__preset_name',
    ]
    
    readonly_fields = [
        'id',
        'uuid',
        'created',
        'updated',
    ]
    
    raw_id_fields = ['source_preset']
    
    ordering = ['-created']
    
    # Use STATE database
    using = 'state'
    
    def get_queryset(self, request):
        return super().get_queryset(request).using(self.using)
    
    def save_model(self, request, obj, form, change):
        obj.save(using=self.using)
    
    def delete_model(self, request, obj):
        obj.delete(using=self.using)
