"""
ConfigDriven AccessRights SSOT.

Matrix definuje, ktoré roly môžu vidieť/robiť akcie na jednotlivých view_name
a ktoré menu položky sú viditeľné.
"""

from typing import Dict, Literal, Any

# Role types - MUST match User.UserRole from m_user.models
Role = Literal["superuser", "admin", "staff", "editor", "reader", "adhoc", "anonymous"]
Action = Literal["view", "add", "edit", "delete", "export", "menu"]

# Default fallback policy
DEFAULT_POLICY: Dict[Action, Dict[Role, bool]] = {
    "view": {
        "superuser": True,
        "admin": True,
        "staff": True,
        "editor": True,
        "reader": True,
        "adhoc": False,
        "anonymous": False,
    },
    "add": {
        "superuser": True,
        "admin": True,
        "staff": False,
        "editor": False,
        "reader": False,
        "adhoc": False,
        "anonymous": False,
    },
    "edit": {
        "superuser": True,
        "admin": True,
        "staff": False,
        "editor": True,
        "reader": False,
        "adhoc": False,
        "anonymous": False,
    },
    "delete": {
        "superuser": True,
        "admin": True,
        "staff": False,
        "editor": False,
        "reader": False,
        "adhoc": False,
        "anonymous": False,
    },
    "export": {
        "superuser": True,
        "admin": True,
        "staff": True,
        "editor": False,
        "reader": False,
        "adhoc": False,
        "anonymous": False,
    },
    "menu": {
        "superuser": True,
        "admin": True,
        "staff": True,
        "editor": True,
        "reader": True,
        "adhoc": False,
        "anonymous": False,
    },
}

# Access matrix per view/menu key.
# Pridávame len výnimky; inak platí DEFAULT_POLICY.
ACCESS_MATRIX: Dict[str, Dict[Action, Dict[Role, bool]]] = {
    # Companies - Admin can see menu and view/manage their own companies via scoping
    "companies": {
        "view": {
            "superuser": True,
            "admin": True,  # ✅ Admin can view companies (scoped)
            "staff": False,
            "user": False,
            "anonymous": False,
        },
        "add": {
            "superuser": True,
            "admin": True,  # ✅ Admin can add companies
            "staff": False,
            "user": False,
            "anonymous": False,
        },
        "edit": {
            "superuser": True,
            "admin": True,  # ✅ Admin can edit companies
            "staff": False,
            "user": False,
            "anonymous": False,
        },
        "delete": {
            "superuser": True,
            "admin": True,  # ✅ Admin can delete companies
            "staff": False,
            "user": False,
            "anonymous": False,
        },
        "export": {
            "superuser": True,
            "admin": True,  # ✅ Admin can export companies
            "staff": False,
            "user": False,
            "anonymous": False,
        },
        "menu": {
            "superuser": True,
            "admin": True,  # ✅ Admin can see companies menu item
            "staff": False,
            "editor": False,
            "reader": False,
            "adhoc": False,
            "anonymous": False,
        },
    },
}

# =============================================================================
# MENU DEPENDENCIES - ConfigDriven SSOT for hierarchical menu visibility
# =============================================================================

MENU_DEPENDENCIES: Dict[str, Dict[str, Any]] = {
    # Level 1: Requires companies
    "factories": {
        "requires": "has_companies",
        "empty_message": "Create a company first to access factories.",
    },
    
    # Level 2: Requires factories
    "measurements": {
        "requires": "has_factories",
        "empty_message": "Create a factory first to access measurements.",
    },
    "locations": {
        "requires": "has_factories",
        "empty_message": "Create a factory first to access locations.",
    },
    "carriers": {
        "requires": "has_factories",
        "empty_message": "Create a factory first to access carriers.",
    },
    "drivers": {
        "requires": "has_factories",
        "empty_message": "Create a factory first to access drivers.",
    },
    "pits": {
        "requires": "has_factories",
        "empty_message": "Create a factory first to access pits.",
    },
    "pots": {
        "requires": "has_factories",
        "empty_message": "Create a factory first to access pots.",
    },
    "cameras": {
        "requires": "has_factories",
        "empty_message": "Create a factory first to access cameras.",
    },
    "machines": {
        "requires": "has_factories",
        "empty_message": "Create a factory first to access machines.",
    },
    
    # No dependencies (always visible if access rights allow)
    "dashboard": {},
    "companies": {},
    "users": {},
}

# Empty state messages (SSOT)
EMPTY_STATE_MESSAGES: Dict[str, str] = {
    "no_companies": "Create your first company to start using the platform.",
    "no_factories": "Create your first factory to access production features.",
}

