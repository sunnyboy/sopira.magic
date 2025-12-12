#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/mystate/config.py
#   MyState Config - SSOT for state management
#   Single source of truth for all state fields and scope definitions
#..............................................................

"""
   MyState Config - SSOT for State Management.

   Single source of truth for all state management configurations.
   Defines scope types, tracked state fields, and their defaults.

   Configuration Structure:
   - scopes: Defines scope types (table, page, global) and their tracked states
   - state_fields: All available state fields with types and defaults
   - debounce: Timing configuration for state persistence

   Adding New State Fields:
   1. Add field definition to state_fields dict
   2. Add field name to appropriate scope's tracked_states list
   3. Frontend will automatically pick up the new field

   Usage:
   ```python
   from sopira_magic.apps.mystate.config import MYSTATE_CONFIG, get_scope_config

   # Get config for table scope
   table_config = get_scope_config('table')

   # Get default value for pagination
   default = get_state_field_default('pagination')
   ```

   Important:
   - NO HARDCODING: All state fields must be defined here
   - This config is the SSOT for both backend validation and frontend types
"""

from typing import Dict, List, Any, Optional


# =============================================================================
# SCOPE_HIERARCHY - Hierarchical scope definitions (SSOT)
# =============================================================================
# Defines parent-child relationships and state fields for each scope type.
# This hierarchy enables:
# - Cascading state save/load (parent saves children state)
# - Scoped presets (each level has own preset list)
# - State status line (shows active preset per element)

SCOPE_HIERARCHY: Dict[str, Dict[str, Any]] = {
    # =========================================================================
    # TOP LEVEL SCOPES
    # =========================================================================
    "user": {
        "parent": None,
        "children": ["application"],
        "state_fields": [
            "theme", "language", "sidebarCollapsed", 
            "notificationsEnabled", "compactMode"
        ],
        "description": "User-level global preferences",
    },
    "application": {
        "parent": "user",
        "children": ["page"],
        "state_fields": [
            "selectedFactory", "colorScheme", "lastVisitedPage"
        ],
        "description": "Application-wide state",
    },
    "page": {
        "parent": "application",
        "children": ["table", "pdfviewer", "texteditor", "formgenerator"],
        "state_fields": [
            "layout", "widgets", "collapsed", "activeTab", 
            "panelSizes", "expandedSections", "scrollPosition"
        ],
        "description": "Per-page UI state",
    },
    
    # =========================================================================
    # PAGE ELEMENTS
    # =========================================================================
    "table": {
        "parent": "page",
        "children": ["table_columns", "table_filters"],
        "state_fields": [
            "sorting", "pagination", "scrollPosition", "expandedRows",
            "rowSelection", "highlightedRowId", "searchValue", "focusedField"
        ],
        "description": "Table component state (MyTable)",
    },
    "pdfviewer": {
        "parent": "page",
        "children": [],
        "state_fields": [
            "zoom", "currentPage", "scrollPosition", "rotation"
        ],
        "description": "PDF viewer component state",
    },
    "texteditor": {
        "parent": "page",
        "children": [],
        "state_fields": [
            "cursorPosition", "selection", "scrollPosition", "wordWrap"
        ],
        "description": "Text editor component state",
    },
    "formgenerator": {
        "parent": "page",
        "children": [],
        "state_fields": [
            "formData", "validationState", "activeSection", "expandedFields"
        ],
        "description": "Form generator component state",
    },
    
    # =========================================================================
    # TABLE SUB-ELEMENTS
    # =========================================================================
    "table_columns": {
        "parent": "table",
        "children": [],
        "state_fields": [
            "columnVisibility", "columnOrder", "columnSizing"
        ],
        "description": "Table columns panel state",
    },
    "table_filters": {
        "parent": "table",
        "children": [],
        "state_fields": [
            "columnFilters", "globalFilter"
        ],
        "description": "Table filters panel state",
    },
}


# =============================================================================
# MYSTATE_CONFIG - Single Source of Truth for state management
# =============================================================================

MYSTATE_CONFIG: Dict[str, Any] = {
    # =========================================================================
    # SCOPE DEFINITIONS
    # =========================================================================
    # Each scope type defines which state fields are tracked for that scope
    
    "scopes": {
        # Table scope - per-table UI state (MyTable component)
        "table": {
            "key_pattern": "table_{key}",  # LocalStorage key pattern
            "description": "Per-table UI state (columns, filters, sorting, etc.)",
            "tracked_states": [
                "pagination",
                "sorting",
                "columnFilters",
                "globalFilter",
                "columnVisibility",
                "columnOrder",
                "columnSizing",
                "rowSelection",
                "scrollPosition",
                "expandedRows",
                "searchValue",
                "focusedField",
                "filterPanelState",
                "columnPanelState",
                "highlightedRowId",
            ],
        },
        
        # Page scope - per-page UI state (dashboard, settings, etc.)
        "page": {
            "key_pattern": "page_{key}",
            "description": "Per-page UI state (layout, widgets, tabs, etc.)",
            "tracked_states": [
                "layout",
                "widgets",
                "collapsed",
                "activeTab",
                "scrollPosition",
                "focusedField",
                "panelSizes",
                "expandedSections",
            ],
        },
        
        # Global scope - application-wide state
        "global": {
            "key_pattern": "global",
            "description": "Application-wide UI state (theme, language, sidebar, etc.)",
            "tracked_states": [
                "theme",
                "language",
                "sidebarCollapsed",
                "selectedFactory",
                "colorScheme",
                "notificationsEnabled",
                "compactMode",
                "lastVisitedPage",
            ],
        },
    },
    
    # =========================================================================
    # STATE FIELD DEFINITIONS
    # =========================================================================
    # All available state fields with their types and default values
    # Add new fields here to make them available across the system
    
    "state_fields": {
        # ----- Table state fields -----
        "pagination": {
            "type": "object",
            "default": {"pageSize": 10, "pageIndex": 0},
            "description": "Table pagination state",
        },
        "sorting": {
            "type": "array",
            "default": [],
            "description": "Table sorting configuration [{id: string, desc: boolean}]",
        },
        "columnFilters": {
            "type": "array",
            "default": [],
            "description": "Column filter values [{id: string, value: any}]",
        },
        "globalFilter": {
            "type": "string",
            "default": "",
            "description": "Global search/filter value",
        },
        "columnVisibility": {
            "type": "object",
            "default": {},
            "description": "Column visibility map {columnId: boolean}",
        },
        "columnOrder": {
            "type": "array",
            "default": [],
            "description": "Column order array [columnId, ...]",
        },
        "columnSizing": {
            "type": "object",
            "default": {},
            "description": "Column width map {columnId: number}",
        },
        "rowSelection": {
            "type": "object",
            "default": {},
            "description": "Selected rows map {rowId: boolean}",
        },
        "expandedRows": {
            "type": "array",
            "default": [],
            "description": "Expanded row IDs [rowId, ...]",
        },
        "searchValue": {
            "type": "string",
            "default": "",
            "description": "Search input value",
        },
        "focusedField": {
            "type": "string",
            "default": None,
            "description": "Currently focused field/cell ID",
        },
        "filterPanelState": {
            "type": "object",
            "default": {"isOpen": False, "activePresetId": None},
            "description": "Filter panel state",
        },
        "columnPanelState": {
            "type": "object",
            "default": {"isOpen": False, "activePresetId": None},
            "description": "Column panel state",
        },
        "highlightedRowId": {
            "type": "string",
            "default": None,
            "description": "Currently highlighted row ID",
        },
        
        # ----- Shared state fields (used by multiple scopes) -----
        "scrollPosition": {
            "type": "object",
            "default": {"x": 0, "y": 0},
            "description": "Scroll position {x: number, y: number}",
        },
        
        # ----- Page state fields -----
        "layout": {
            "type": "object",
            "default": {},
            "description": "Page layout configuration",
        },
        "widgets": {
            "type": "array",
            "default": [],
            "description": "Dashboard widget configuration",
        },
        "collapsed": {
            "type": "object",
            "default": {},
            "description": "Collapsed sections map {sectionId: boolean}",
        },
        "activeTab": {
            "type": "string",
            "default": None,
            "description": "Currently active tab ID",
        },
        "panelSizes": {
            "type": "object",
            "default": {},
            "description": "Resizable panel sizes {panelId: number}",
        },
        "expandedSections": {
            "type": "array",
            "default": [],
            "description": "Expanded section IDs [sectionId, ...]",
        },
        
        # ----- Global state fields -----
        "theme": {
            "type": "string",
            "default": "dark",
            "description": "UI theme: 'light' or 'dark'",
        },
        "language": {
            "type": "string",
            "default": "sk",
            "description": "UI language code",
        },
        "sidebarCollapsed": {
            "type": "boolean",
            "default": False,
            "description": "Is sidebar collapsed?",
        },
        "selectedFactory": {
            "type": "string",
            "default": None,
            "description": "Currently selected factory UUID",
        },
        "colorScheme": {
            "type": "string",
            "default": "blue",
            "description": "Color scheme name",
        },
        "notificationsEnabled": {
            "type": "boolean",
            "default": True,
            "description": "Are notifications enabled?",
        },
        "compactMode": {
            "type": "boolean",
            "default": False,
            "description": "Use compact UI mode?",
        },
        "lastVisitedPage": {
            "type": "string",
            "default": None,
            "description": "Last visited page path",
        },
    },
    
    # =========================================================================
    # DEBOUNCE CONFIGURATION
    # =========================================================================
    # Timing for debounced state persistence to LocalStorage
    
    "debounce": {
        "default": 100,      # ms - default debounce for most state changes
        "scroll": 300,       # ms - longer debounce for scroll position
        "resize": 200,       # ms - debounce for column resizing
        "search": 300,       # ms - debounce for search input
    },
    
    # =========================================================================
    # LOCALSTORAGE CONFIGURATION
    # =========================================================================
    
    "localStorage_prefix": "mystate_",  # Prefix for all LocalStorage keys
    "localStorage_version": 1,          # Version for migration support
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_scope_config(scope_type: str) -> Optional[Dict[str, Any]]:
    """
    Get configuration for a specific scope type.
    
    Args:
        scope_type: Type of scope ('table', 'page', 'global')
        
    Returns:
        Scope configuration dict or None if not found
    """
    return MYSTATE_CONFIG["scopes"].get(scope_type)


def get_scope_types() -> List[str]:
    """Get all available scope types from SCOPE_HIERARCHY."""
    return list(SCOPE_HIERARCHY.keys())


def get_tracked_states(scope_type: str) -> List[str]:
    """
    Get list of tracked state fields for a scope type.
    
    Args:
        scope_type: Type of scope
        
    Returns:
        List of state field names
    """
    scope_config = get_scope_config(scope_type)
    if scope_config:
        return scope_config.get("tracked_states", [])
    return []


def get_state_field_config(field_name: str) -> Optional[Dict[str, Any]]:
    """
    Get configuration for a specific state field.
    
    Args:
        field_name: Name of the state field
        
    Returns:
        Field configuration dict or None if not found
    """
    return MYSTATE_CONFIG["state_fields"].get(field_name)


def get_state_field_default(field_name: str) -> Any:
    """
    Get default value for a state field.
    
    Args:
        field_name: Name of the state field
        
    Returns:
        Default value for the field
    """
    field_config = get_state_field_config(field_name)
    if field_config:
        return field_config.get("default")
    return None


def get_default_state_for_scope(scope_type: str) -> Dict[str, Any]:
    """
    Get default state object for a scope type.
    
    Args:
        scope_type: Type of scope
        
    Returns:
        Dict with default values for all tracked states
    """
    tracked_states = get_tracked_states(scope_type)
    return {
        field: get_state_field_default(field)
        for field in tracked_states
    }


def get_debounce_ms(state_type: str = "default") -> int:
    """
    Get debounce timing for a state type.
    
    Args:
        state_type: Type of state ('default', 'scroll', 'resize', 'search')
        
    Returns:
        Debounce time in milliseconds
    """
    return MYSTATE_CONFIG["debounce"].get(state_type, MYSTATE_CONFIG["debounce"]["default"])


def get_localstorage_key(scope_type: str, scope_key: str) -> str:
    """
    Generate LocalStorage key for a scope.
    
    Args:
        scope_type: Type of scope
        scope_key: Specific scope key
        
    Returns:
        Full LocalStorage key string
    """
    prefix = MYSTATE_CONFIG["localStorage_prefix"]
    scope_config = get_scope_config(scope_type)
    if scope_config:
        pattern = scope_config.get("key_pattern", "{scope_type}_{key}")
        key = pattern.format(key=scope_key)
        return f"{prefix}{key}"
    return f"{prefix}{scope_type}_{scope_key}"


def validate_scope_type(scope_type: str) -> bool:
    """Check if scope type is valid (exists in SCOPE_HIERARCHY)."""
    return scope_type in SCOPE_HIERARCHY


def validate_state_field(field_name: str) -> bool:
    """Check if state field is defined."""
    return field_name in MYSTATE_CONFIG["state_fields"]


# =============================================================================
# SCOPE_HIERARCHY HELPER FUNCTIONS
# =============================================================================

def get_scope_hierarchy_config(scope_type: str) -> Optional[Dict[str, Any]]:
    """
    Get hierarchy configuration for a scope type.
    
    Args:
        scope_type: Type of scope (e.g., 'table', 'table_columns')
        
    Returns:
        Scope hierarchy config dict or None if not found
    """
    return SCOPE_HIERARCHY.get(scope_type)


def get_parent_scope(scope_type: str) -> Optional[str]:
    """
    Get parent scope type for a given scope.
    
    Args:
        scope_type: Type of scope
        
    Returns:
        Parent scope type or None if no parent (top level)
        
    Example:
        get_parent_scope('table_columns') -> 'table'
        get_parent_scope('table') -> 'page'
        get_parent_scope('user') -> None
    """
    config = get_scope_hierarchy_config(scope_type)
    if config:
        return config.get("parent")
    return None


def get_child_scopes(scope_type: str) -> List[str]:
    """
    Get child scope types for a given scope.
    
    Args:
        scope_type: Type of scope
        
    Returns:
        List of child scope types (empty list if no children)
        
    Example:
        get_child_scopes('table') -> ['table_columns', 'table_filters']
        get_child_scopes('table_columns') -> []
    """
    config = get_scope_hierarchy_config(scope_type)
    if config:
        return config.get("children", [])
    return []


def get_scope_state_fields(scope_type: str) -> List[str]:
    """
    Get state fields that belong to a specific scope (own fields only, not children).
    
    Args:
        scope_type: Type of scope
        
    Returns:
        List of state field names for this scope
        
    Example:
        get_scope_state_fields('table_columns') -> ['columnVisibility', 'columnOrder', 'columnSizing']
    """
    config = get_scope_hierarchy_config(scope_type)
    if config:
        return config.get("state_fields", [])
    return []


def get_all_scope_state_fields(scope_type: str, include_children: bool = True) -> List[str]:
    """
    Get all state fields for a scope, optionally including children's fields.
    
    Args:
        scope_type: Type of scope
        include_children: Whether to include children's state fields
        
    Returns:
        List of all state field names
        
    Example:
        get_all_scope_state_fields('table', include_children=True) 
        -> ['sorting', 'pagination', ..., 'columnVisibility', 'columnOrder', ..., 'columnFilters', 'globalFilter']
    """
    fields = get_scope_state_fields(scope_type).copy()
    
    if include_children:
        for child_scope in get_child_scopes(scope_type):
            fields.extend(get_all_scope_state_fields(child_scope, include_children=True))
    
    return fields


def get_scope_ancestors(scope_type: str) -> List[str]:
    """
    Get all ancestor scope types (from immediate parent to root).
    
    Args:
        scope_type: Type of scope
        
    Returns:
        List of ancestor scope types (closest first)
        
    Example:
        get_scope_ancestors('table_columns') -> ['table', 'page', 'application', 'user']
    """
    ancestors = []
    current = get_parent_scope(scope_type)
    while current:
        ancestors.append(current)
        current = get_parent_scope(current)
    return ancestors


def get_scope_descendants(scope_type: str) -> List[str]:
    """
    Get all descendant scope types (recursively).
    
    Args:
        scope_type: Type of scope
        
    Returns:
        List of all descendant scope types
        
    Example:
        get_scope_descendants('table') -> ['table_columns', 'table_filters']
        get_scope_descendants('page') -> ['table', 'table_columns', 'table_filters', 'pdfviewer', ...]
    """
    descendants = []
    for child in get_child_scopes(scope_type):
        descendants.append(child)
        descendants.extend(get_scope_descendants(child))
    return descendants


def is_ancestor_of(ancestor_scope: str, descendant_scope: str) -> bool:
    """
    Check if one scope is an ancestor of another.
    
    Args:
        ancestor_scope: Potential ancestor scope type
        descendant_scope: Potential descendant scope type
        
    Returns:
        True if ancestor_scope is an ancestor of descendant_scope
    """
    return ancestor_scope in get_scope_ancestors(descendant_scope)


def get_scope_depth(scope_type: str) -> int:
    """
    Get the depth of a scope in the hierarchy (0 = root).
    
    Args:
        scope_type: Type of scope
        
    Returns:
        Depth level (0 for 'user', 1 for 'application', etc.)
    """
    return len(get_scope_ancestors(scope_type))
