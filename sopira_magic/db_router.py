#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/db_router.py
#   Database Router - Multi-database routing
#   Routes models to appropriate databases based on app_label
#..............................................................

"""
Database Router - Multi-Database Routing.

   Custom Django database router that directs models to specific databases
   based on their app_label, implementing the multi-database architecture.

   Database Mapping:
   - state app → state database (UI state, user preferences)
   - logging, audit apps → logging database (logs, audit trails)
   - All other apps → default database (PRIMARY - business data)

   Router Methods:
   - db_for_read(): Suggests database for read operations
   - db_for_write(): Suggests database for write operations
   - allow_relation(): Allows relations only within same database
   - allow_migrate(): Ensures migrations go to correct database

   Usage:
   Configured in settings.py:
   DATABASE_ROUTERS = ['sopira_magic.db_router.DatabaseRouter']
"""


class DatabaseRouter:
    """
    Router for multiple databases:
    - default: Primary database (business data)
    - state: UI state and user preferences
    - logging: Application logs and audit trails
    """
    
    # Apps that use STATE database
    state_apps = ['state']
    
    # Apps that use LOGGING database
    logging_apps = ['logging', 'audit']
    
    def db_for_read(self, model, **hints):
        """Suggest which database should be used for read operations."""
        if model._meta.app_label in self.state_apps:
            return 'state'
        if model._meta.app_label in self.logging_apps:
            return 'logging'
        return 'default'
    
    def db_for_write(self, model, **hints):
        """Suggest which database should be used for write operations."""
        if model._meta.app_label in self.state_apps:
            return 'state'
        if model._meta.app_label in self.logging_apps:
            return 'logging'
        return 'default'
    
    def allow_relation(self, obj1, obj2, **hints):
        """Allow relations if models are in the same database."""
        db_set = {'default', 'state', 'logging'}
        if obj1._state.db in db_set and obj2._state.db in db_set:
            return obj1._state.db == obj2._state.db
        return None
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Ensure that apps only appear in their designated database."""
        if app_label in self.state_apps:
            return db == 'state'
        if app_label in self.logging_apps:
            return db == 'logging'
        # All other apps go to default database
        if db == 'default':
            return True
        # Prevent migrations to state/logging for other apps
        return False

