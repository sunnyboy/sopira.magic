#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/state/models.py
#   State Models - UI state persistence and workspace management
#   Uses STATE database for UI state and user preferences
#..............................................................

"""
   State Models - UI State Persistence and Workspace Management.

   Models for persisting UI state and workspace configurations.
   Stored in STATE database (separate from business data).

   Models:

   1. TableState (extends TimeStampedModel)
      - Persists UI table state (columns, filters, sorting, pagination)
      - Fields: user, table_name, component, state_data (JSON), is_active
      - Indexed on: user, table_name, is_active
      - Allows multiple saved states per user per table

   2. SavedWorkspace (extends TimeStampedModel)
      - Saved workspace configurations
      - Fields: user, name, description, workspace_data (JSON), is_default
      - Indexed on: user, is_default
      - Allows users to save and restore workspace layouts

   3. EnvironmentState (extends TimeStampedModel)
      - Environment state and settings per user
      - Fields: user, environment_name, environment_data (JSON), is_active
      - Unique constraint: user + environment_name
      - Stores user-specific environment configurations

   Database:
   - All models stored in STATE database (not PRIMARY)
   - Routed via DatabaseRouter based on app_label

   Usage:
   ```python
   from sopira_magic.apps.state.models import TableState, SavedWorkspace
   state = TableState.objects.using('state').create(user_id=user.id, table_name='companies', state_data={...})
   ```
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from sopira_magic.apps.core.models import TimeStampedModel
from sopira_magic.apps.m_user.models import User


class TableState(TimeStampedModel):
    """UI table state persistence."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="table_states"
    )
    table_name = models.CharField(max_length=255, db_index=True)
    component = models.CharField(max_length=255, blank=True, default="")
    state_data = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    
    class Meta:
        verbose_name = _("Table State")
        verbose_name_plural = _("Table States")
        indexes = [
            models.Index(fields=['user', 'table_name', 'is_active']),
        ]


class SavedWorkspace(TimeStampedModel):
    """Saved workspace configuration."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="saved_workspaces"
    )
    name = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True, default="")
    workspace_data = models.JSONField(default=dict, blank=True)
    is_default = models.BooleanField(default=False, db_index=True)
    
    class Meta:
        verbose_name = _("Saved Workspace")
        verbose_name_plural = _("Saved Workspaces")
        indexes = [
            models.Index(fields=['user', 'is_default']),
        ]


class EnvironmentState(TimeStampedModel):
    """Environment state tied to user."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="environment_states"
    )
    environment_name = models.CharField(max_length=255, db_index=True)
    environment_data = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    
    class Meta:
        verbose_name = _("Environment State")
        verbose_name_plural = _("Environment States")
        indexes = [
            models.Index(fields=['user', 'environment_name', 'is_active']),
        ]
        unique_together = [['user', 'environment_name']]
