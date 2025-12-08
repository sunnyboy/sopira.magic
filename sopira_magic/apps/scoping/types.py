#..............................................................
#   apps/scoping/types.py
#   Scoping Engine Type Definitions
#..............................................................

"""
Scoping Engine Type Definitions.

Python TypedDict definitions synchronized with TypeScript interface in scoping.ts.
These types define the structure of scoping rules used across the application.

SSOT: This file defines the structure of scoping rules used across the application.
"""

from typing import TypedDict, List, Dict, Any, Optional, Literal

# Type aliases for better readability
UserRole = Literal['superuser', 'admin', 'staff', 'editor', 'reader', 'adhoc']
ScopingCondition = Literal['has_scope', 'no_scope', 'is_owner', 'is_assigned', 'is_selected']
ScopingAction = Literal['include', 'exclude', 'filter_by', 'show_all']
ScopeType = Literal['selected', 'accessible']


class ScopingRuleWhen(TypedDict, total=False):
    """Optional conditions for when a rule applies."""
    role: Optional[List[UserRole]]      # Roles this rule applies to
    table: Optional[List[str]]          # Tables this rule applies to
    field: Optional[str]                # Field this rule applies to


class ScopingRule(TypedDict, total=False):
    """Scoping rule - defines a condition and action to apply."""
    condition: ScopingCondition          # Condition to evaluate
    action: ScopingAction                # Action to apply when condition is met
    params: Optional[Dict[str, Any]]     # Optional parameters (e.g., {scope_level: 1, scope_type: 'selected'})
    when: Optional[ScopingRuleWhen]     # Optional conditions for when this rule applies


class TableScopingConfig(TypedDict, total=False):
    """Scoping configuration for a single table."""
    table_name: str                      # Table name (e.g., 'cameras', 'machines')
    factory_field: str                   # Factory foreign key field name (e.g., 'factory_id', 'created_by')
    rules: List[ScopingRule]             # List of scoping rules for this table
    default_action: Optional[ScopingAction]  # Default action if no rules match


# Scoping matrix type - SSOT for all scoping rules
# Structure: Dict[table_name, Dict[role, List[ScopingRule]]]
ScopingMatrix = Dict[str, Dict[str, List[ScopingRule]]]

