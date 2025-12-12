#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/mystate/__init__.py
#   MyState Module - UI state persistence and workspace management
#   New config-driven state management replacing legacy state module
#..............................................................

"""
   MyState Module - Modern UI State Persistence.

   A new config-driven state management system with:
   - Current state in LocalStorage (fast, no API calls)
   - Saved states in database (persistence, sharing)
   - Multi-scope support (table, page, global)
   - Extensible schema via MYSTATE_CONFIG

   Usage:
   ```python
   from sopira_magic.apps.mystate.models import SavedState
   ```
"""

default_app_config = 'sopira_magic.apps.mystate.apps.MyStateConfig'
