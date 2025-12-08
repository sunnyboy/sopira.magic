#..............................................................
#   apps/scoping/rules.py
#   Scoping Rules Matrix - SSOT for all scoping rules
#..............................................................

"""
Scoping Rules Matrix - Single Source of Truth.

This file defines all scoping rules for all tables and roles.
Rules are evaluated by ScopingEngine and applied to querysets.

Structure:
    SCOPING_RULES_MATRIX[table_name][role] = List[ScopingRule]

Migration Strategy:
    - Start with empty structure (fallback to old system)
    - Migrate tables one by one (cameras first as pilot)
    - Feature flags control which tables use new system
"""

from typing import Dict, List
from .types import ScopingMatrix, ScopingRule

# =============================================================================
# SCOPING RULES MATRIX - SSOT
# =============================================================================

SCOPING_RULES_MATRIX: ScopingMatrix = {
    # =========================================================================
    # USERS - Basic scoping for sopira.magic
    #   - SUPERADMIN + ADMIN: see all users (no extra filter)
    #   - others: see only themselves (id == request.user.id)
    #
    # Roles here are abstract scoping roles; we map from User.role in
    # a registry callback (see register_role_provider in project code).
    # =========================================================================
    "users": {
        # SUPERUSER and ADMIN have no scoping rules; they effectively
        # see all users because no additional filters are applied.
        "superuser": [],
        "admin": [],
        # All non-admin roles see only themselves via is_owner condition
        "staff": [
            {
                "condition": "is_owner",
                "action": "filter_by",
            },
        ],
        "editor": [
            {
                "condition": "is_owner",
                "action": "filter_by",
            },
        ],
        "reader": [
            {
                "condition": "is_owner",
                "action": "filter_by",
            },
        ],
        "adhoc": [
            {
                "condition": "is_owner",
                "action": "filter_by",
            },
        ],
    },

    # =========================================================================
    # CAMERAS - Pilot implementation
    # =========================================================================
    "cameras": {
        "superuser": [
            {
                "condition": "is_selected",
                "action": "filter_by",
                "params": {"scope_level": 1, "scope_type": "selected"},
            },
            {
                "condition": "no_scope",
                "action": "include",
            },
        ],
        "admin": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 1, "scope_type": "accessible"},
            },
        ],
        "staff": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 1, "scope_type": "accessible"},
            },
        ],
        "editor": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 1, "scope_type": "accessible"},
            },
        ],
        "reader": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 1, "scope_type": "accessible"},
            },
        ],
        "adhoc": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 1, "scope_type": "accessible"},
            },
        ],
    },
    
    # =========================================================================
    # OTHER TABLES - All migrated to abstract scope_level
    # =========================================================================
    
    # Factories - special case (uses scope_level: 1 = id, because active_scope contains factory IDs)
    "factories": {
        "superuser": [
            {
                "condition": "is_selected",
                "action": "filter_by",
                "params": {"scope_level": 1, "scope_type": "selected"},
            },
            {
                "condition": "no_scope",  # Works abstractly - becomes id__isnull=True when scope_level=1
                "action": "include",
            },
        ],
        "admin": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 1, "scope_type": "accessible"},
            },
        ],
        "staff": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 1, "scope_type": "accessible"},
            },
        ],
        "editor": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 1, "scope_type": "accessible"},
            },
        ],
        "reader": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 1, "scope_type": "accessible"},
            },
        ],
        "adhoc": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 1, "scope_type": "accessible"},
            },
        ],
    },
    
    # Machines - factory_scoped=True (scope_level: 1 = factory_id)
    "machines": {
        "superuser": [
            {
                "condition": "is_selected",
                "action": "filter_by",
                "params": {"scope_level": 1, "scope_type": "selected"},
            },
            {
                "condition": "no_scope",
                "action": "include",
            },
        ],
        "admin": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 1, "scope_type": "accessible"},
            },
        ],
        "staff": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 1, "scope_type": "accessible"},
            },
        ],
        "editor": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 1, "scope_type": "accessible"},
            },
        ],
        "reader": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 1, "scope_type": "accessible"},
            },
        ],
        "adhoc": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 1, "scope_type": "accessible"},
            },
        ],
    },
    
    # Measurements - factory_scoped=True (scope_level: 1 = factory_id)
    "measurements": {
        "superuser": [
            {
                "condition": "is_selected",
                "action": "filter_by",
                "params": {"scope_level": 1, "scope_type": "selected"},
            },
            {
                "condition": "no_scope",
                "action": "include",
            },
        ],
        "admin": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 1, "scope_type": "accessible"},
            },
        ],
        "staff": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 1, "scope_type": "accessible"},
            },
        ],
        "editor": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 1, "scope_type": "accessible"},
            },
        ],
        "reader": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 1, "scope_type": "accessible"},
            },
        ],
        "adhoc": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 1, "scope_type": "accessible"},
            },
        ],
    },
    
    # Locations - factory_scoped=True (scope_level: 1 = factory_id)
    "locations": {
        "superuser": [
            {
                "condition": "is_selected",
                "action": "filter_by",
                "params": {"scope_level": 1, "scope_type": "selected"},
            },
            {
                "condition": "no_scope",
                "action": "include",
            },
        ],
        "admin": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 1, "scope_type": "accessible"},
            },
        ],
        "staff": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 1, "scope_type": "accessible"},
            },
        ],
        "editor": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 1, "scope_type": "accessible"},
            },
        ],
        "reader": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 1, "scope_type": "accessible"},
            },
        ],
        "adhoc": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 1, "scope_type": "accessible"},
            },
        ],
    },
    
    # Carriers - factory_scoped=True (scope_level: 1 = factory_id)
    "carriers": {
        "superuser": [
            {
                "condition": "is_selected",
                "action": "filter_by",
                "params": {"scope_level": 1, "scope_type": "selected"},
            },
            {
                "condition": "no_scope",
                "action": "include",
            },
        ],
        "admin": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 1, "scope_type": "accessible"},
            },
        ],
        "staff": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 1, "scope_type": "accessible"},
            },
        ],
        "editor": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 1, "scope_type": "accessible"},
            },
        ],
        "reader": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 1, "scope_type": "accessible"},
            },
        ],
        "adhoc": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 1, "scope_type": "accessible"},
            },
        ],
    },
    
    # Drivers - factory_scoped=True (scope_level: 1 = factory_id)
    "drivers": {
        "superuser": [
            {
                "condition": "is_selected",
                "action": "filter_by",
                "params": {"scope_level": 1, "scope_type": "selected"},
            },
            {
                "condition": "no_scope",
                "action": "include",
            },
        ],
        "admin": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 1, "scope_type": "accessible"},
            },
        ],
        "staff": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 1, "scope_type": "accessible"},
            },
        ],
        "editor": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 1, "scope_type": "accessible"},
            },
        ],
        "reader": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 1, "scope_type": "accessible"},
            },
        ],
        "adhoc": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 1, "scope_type": "accessible"},
            },
        ],
    },
    
    # Pots - factory_scoped=True (scope_level: 1 = factory_id)
    "pots": {
        "superuser": [
            {
                "condition": "is_selected",
                "action": "filter_by",
                "params": {"scope_level": 1, "scope_type": "selected"},
            },
            {
                "condition": "no_scope",
                "action": "include",
            },
        ],
        "admin": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 1, "scope_type": "accessible"},
            },
        ],
        "staff": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 1, "scope_type": "accessible"},
            },
        ],
        "editor": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 1, "scope_type": "accessible"},
            },
        ],
        "reader": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 1, "scope_type": "accessible"},
            },
        ],
        "adhoc": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 1, "scope_type": "accessible"},
            },
        ],
    },
    
    # Pits - factory_scoped=True (scope_level: 1 = factory_id)
    "pits": {
        "superuser": [
            {
                "condition": "is_selected",
                "action": "filter_by",
                "params": {"scope_level": 1, "scope_type": "selected"},
            },
            {
                "condition": "no_scope",
                "action": "include",
            },
        ],
        "admin": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 1, "scope_type": "accessible"},
            },
        ],
        "staff": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 1, "scope_type": "accessible"},
            },
        ],
        "editor": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 1, "scope_type": "accessible"},
            },
        ],
        "reader": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 1, "scope_type": "accessible"},
            },
        ],
        "adhoc": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 1, "scope_type": "accessible"},
            },
        ],
    },
    
    # Logs - factory_scoped=True (scope_level: 1 = factory_id)
    "logs": {
        "superuser": [
            {
                "condition": "is_selected",
                "action": "filter_by",
                "params": {"scope_level": 1, "scope_type": "selected"},
            },
            {
                "condition": "no_scope",
                "action": "include",
            },
        ],
        "admin": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 1, "scope_type": "accessible"},
            },
        ],
        "staff": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 1, "scope_type": "accessible"},
            },
        ],
        "editor": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 1, "scope_type": "accessible"},
            },
        ],
        "reader": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 1, "scope_type": "accessible"},
            },
        ],
        "adhoc": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 1, "scope_type": "accessible"},
            },
        ],
    },
    
    # Environments - factory_scoped=False (global entity)
    "environments": {},
}

# =============================================================================
# FEATURE FLAGS - Control which tables use new scoping engine
# =============================================================================

# Global flag to enable/disable scoping engine
USE_SCOPING_ENGINE = True

# Per-table flags for gradual migration
USE_SCOPING_ENGINE_FOR_CAMERAS = True  # Pilot - enabled
USE_SCOPING_ENGINE_FOR_MACHINES = True
USE_SCOPING_ENGINE_FOR_MEASUREMENTS = True
USE_SCOPING_ENGINE_FOR_FACTORIES = True
USE_SCOPING_ENGINE_FOR_LOCATIONS = True
USE_SCOPING_ENGINE_FOR_CARRIERS = True
USE_SCOPING_ENGINE_FOR_DRIVERS = True
USE_SCOPING_ENGINE_FOR_POTS = True
USE_SCOPING_ENGINE_FOR_PITS = True
USE_SCOPING_ENGINE_FOR_LOGS = True
USE_SCOPING_ENGINE_FOR_ENVIRONMENTS = True  # Global entity, but flag can be True


def should_use_scoping_engine(table_name: str) -> bool:
    """
    Check if scoping engine should be used for a given table.
    
    Args:
        table_name: Table name (e.g., 'cameras', 'machines')
        
    Returns:
        True if scoping engine should be used, False to use old system
    """
    if not USE_SCOPING_ENGINE:
        return False
    
    # Check per-table flags
    flag_map = {
        "cameras": USE_SCOPING_ENGINE_FOR_CAMERAS,
        "machines": USE_SCOPING_ENGINE_FOR_MACHINES,
        "measurements": USE_SCOPING_ENGINE_FOR_MEASUREMENTS,
        "factories": USE_SCOPING_ENGINE_FOR_FACTORIES,
        "locations": USE_SCOPING_ENGINE_FOR_LOCATIONS,
        "carriers": USE_SCOPING_ENGINE_FOR_CARRIERS,
        "drivers": USE_SCOPING_ENGINE_FOR_DRIVERS,
        "pots": USE_SCOPING_ENGINE_FOR_POTS,
        "pits": USE_SCOPING_ENGINE_FOR_PITS,
        "logs": USE_SCOPING_ENGINE_FOR_LOGS,
        "environments": USE_SCOPING_ENGINE_FOR_ENVIRONMENTS,
    }
    
    return flag_map.get(table_name, False)


def get_scoping_rules(table_name: str, role: str) -> List[ScopingRule]:
    """
    Get scoping rules for a table and role.
    
    Args:
        table_name: Table name (e.g., 'cameras', 'machines')
        role: User role (e.g., 'superuser', 'admin')
        
    Returns:
        List of scoping rules, or empty list if not defined
    """
    table_rules = SCOPING_RULES_MATRIX.get(table_name, {})
    return table_rules.get(role, [])

