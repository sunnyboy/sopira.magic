#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/mystate/models.py
#   MyState Models - Saved state persistence
#   Database models for saved presets (not current state - that's LocalStorage)
#..............................................................

"""
   MyState Models - Saved State Persistence.

   Models for persisting saved state presets to database.
   Current state is handled by LocalStorage on frontend - these models
   are ONLY for saved/named presets that users want to persist.

   Models:

   1. SavedState (extends TimeStampedModel)
      - Saved preset for any scope (table, page, global)
      - Fields: user_id (UUID), scope_type, scope_key, preset_name, state_data
      - Cross-DB reference to User via UUID (not ForeignKey)
      - Indexed for fast lookup by user + scope

   2. SharedState (extends TimeStampedModel)
      - Sharing relationship between users for presets
      - Fields: source_preset (FK), shared_by_id, shared_with_id, can_edit
      - Enables preset sharing between users

   Database:
   - All models stored in STATE database
   - Routed via DatabaseRouter based on app_label 'mystate'

   Usage:
   ```python
   from sopira_magic.apps.mystate.models import SavedState
   
   # Create saved preset
   preset = SavedState.objects.using('state').create(
       user_id=user.id,
       scope_type='table',
       scope_key='companies',
       preset_name='My View',
       state_data={'pagination': {'pageSize': 25}, 'sorting': [...]}
   )
   ```

   Important:
   - NO HARDCODING: All state fields are defined in MYSTATE_CONFIG
   - state_data is extensible JSONField - schema defined in config
"""

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from sopira_magic.apps.core.models import TimeStampedModel


class SavedState(TimeStampedModel):
    """
    Saved state preset for any scope (table, page, global).
    
    This model stores named presets that users explicitly save.
    Current/live state is NOT stored here - it's in LocalStorage.
    
    Attributes:
        user_id: UUID reference to User (cross-DB, not ForeignKey)
        scope_type: Type of scope ('table', 'page', 'global')
        scope_key: Specific scope identifier (e.g., 'companies', 'dashboard')
        preset_name: User-defined name for this preset
        description: Optional description
        state_data: JSON containing the actual state (extensible schema)
        is_default: Whether this is the default preset for this scope
    """
    
    # Cross-DB reference to User (UUID instead of ForeignKey)
    # This avoids cross-database FK issues with multi-DB setup
    user_id = models.UUIDField(
        db_index=True,
        help_text=_("UUID of the user who owns this preset")
    )
    
    # Scope identification
    scope_type = models.CharField(
        max_length=32,
        db_index=True,
        help_text=_("Type of scope: 'table', 'page', or 'global'")
    )
    scope_key = models.CharField(
        max_length=128,
        db_index=True,
        help_text=_("Scope identifier, e.g., 'companies', 'dashboard', 'global'")
    )
    
    # Preset metadata
    preset_name = models.CharField(
        max_length=255,
        help_text=_("User-defined name for this preset")
    )
    description = models.TextField(
        blank=True,
        default="",
        help_text=_("Optional description of this preset")
    )
    
    # State data - extensible JSON schema defined in MYSTATE_CONFIG
    # Contains only this scope's own state fields (not children)
    state_data = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("JSON containing this scope's own state data")
    )
    
    # Children state - hierarchical snapshot of all child scopes
    # Structure: { "child_scope_type": { "preset_name": str|None, "preset_id": uuid|None, "state_data": {...} }, ... }
    # - preset_name/preset_id: Reference to named preset (if child has active preset)
    # - state_data: Raw state data (always included for full restore capability)
    children_state = models.JSONField(
        default=dict,
        blank=True,
        help_text=_(
            "Hierarchical snapshot of child scopes. "
            "Structure: {scope_type: {preset_name, preset_id, state_data}}"
        )
    )
    
    # Default flag - only one default per user+scope_type+scope_key
    is_default = models.BooleanField(
        default=False,
        db_index=True,
        help_text=_("Is this the default preset for this scope?")
    )
    
    class Meta:
        db_table = 'mystate_savedstate'
        verbose_name = _("Saved State")
        verbose_name_plural = _("Saved States")
        
        # Unique constraint: one preset name per user per scope
        unique_together = ['user_id', 'scope_type', 'scope_key', 'preset_name']
        
        indexes = [
            models.Index(fields=['user_id', 'scope_type', 'scope_key']),
            models.Index(fields=['user_id', 'is_default']),
            models.Index(fields=['scope_type', 'scope_key']),
        ]
        
        ordering = ['-updated', 'preset_name']
    
    def __str__(self):
        return f"{self.scope_type}:{self.scope_key} - {self.preset_name}"
    
    def save(self, *args, **kwargs):
        """Ensure only one default preset per user+scope."""
        if self.is_default:
            # Unset other defaults for this user+scope
            SavedState.objects.using('state').filter(
                user_id=self.user_id,
                scope_type=self.scope_type,
                scope_key=self.scope_key,
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        
        super().save(*args, **kwargs)
    
    # =========================================================================
    # CHILDREN STATE HELPER METHODS
    # =========================================================================
    
    def get_child_state(self, child_scope_type: str) -> dict:
        """
        Get state data for a specific child scope.
        
        Args:
            child_scope_type: Type of child scope (e.g., 'table_columns')
            
        Returns:
            Child state dict with keys: preset_name, preset_id, state_data
            Returns empty dict if child not found
        """
        return self.children_state.get(child_scope_type, {})
    
    def set_child_state(
        self, 
        child_scope_type: str, 
        state_data: dict,
        preset_name: str = None,
        preset_id: str = None
    ) -> None:
        """
        Set state data for a specific child scope.
        
        Args:
            child_scope_type: Type of child scope
            state_data: Raw state data for the child
            preset_name: Name of active preset (if child has named preset)
            preset_id: UUID of active preset (if child has named preset)
        """
        if self.children_state is None:
            self.children_state = {}
        
        self.children_state[child_scope_type] = {
            "preset_name": preset_name,
            "preset_id": str(preset_id) if preset_id else None,
            "state_data": state_data,
        }
    
    def get_full_state(self, include_children: bool = True) -> dict:
        """
        Get complete state including this scope and optionally children.
        
        Args:
            include_children: Whether to include children state
            
        Returns:
            Dict with own state_data and optionally children_state
        """
        result = {
            "state_data": self.state_data or {},
        }
        if include_children and self.children_state:
            result["children_state"] = self.children_state
        return result
    
    def has_children(self) -> bool:
        """Check if this preset has any children state."""
        return bool(self.children_state)
    
    def get_child_preset_names(self) -> dict:
        """
        Get mapping of child scope types to their active preset names.
        
        Returns:
            Dict like {'table_columns': 'my-columns', 'table_filters': None}
        """
        if not self.children_state:
            return {}
        
        return {
            scope_type: child.get("preset_name")
            for scope_type, child in self.children_state.items()
        }


class SharedState(TimeStampedModel):
    """
    Sharing relationship for state presets between users.
    
    Enables users to share their saved presets with other users.
    The shared_with user can load the preset, and optionally edit it
    if can_edit is True.
    
    Attributes:
        source_preset: The preset being shared
        shared_by_id: UUID of user who shared it
        shared_with_id: UUID of user it's shared with
        can_edit: Whether the recipient can modify the preset
    """
    
    # Reference to the source preset (same DB, so FK is OK)
    source_preset = models.ForeignKey(
        SavedState,
        on_delete=models.CASCADE,
        related_name='shares',
        help_text=_("The preset being shared")
    )
    
    # Cross-DB references to Users (UUIDs)
    shared_by_id = models.UUIDField(
        db_index=True,
        help_text=_("UUID of user who shared this preset")
    )
    shared_with_id = models.UUIDField(
        db_index=True,
        help_text=_("UUID of user this preset is shared with")
    )
    
    # Permission level
    can_edit = models.BooleanField(
        default=False,
        help_text=_("Can the recipient edit this preset?")
    )
    
    class Meta:
        db_table = 'mystate_sharedstate'
        verbose_name = _("Shared State")
        verbose_name_plural = _("Shared States")
        
        # One share per preset per recipient
        unique_together = ['source_preset', 'shared_with_id']
        
        indexes = [
            models.Index(fields=['shared_with_id']),
            models.Index(fields=['shared_by_id']),
        ]
        
        ordering = ['-created']
    
    def __str__(self):
        return f"{self.source_preset.preset_name} → {self.shared_with_id}"
