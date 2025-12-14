#..............................................................
#   apps/scoping/config.py
#   Scoping Configuration - SSOT (CLEAN REWRITE)
#..............................................................

"""
Scoping Configuration - Single Source of Truth.

All scoping rules, levels, and feature flags in one place.
ConfigDriven & SSOT - no hardcoding anywhere else.
"""

import logging
from typing import Any, Dict, List, Literal, TypedDict

logger = logging.getLogger(__name__)

# =============================================================================
# TYPES
# =============================================================================

ScopeType = Literal['selected', 'accessible', 'all']
UserRole = Literal['superuser', 'admin', 'staff', 'editor', 'reader', 'adhoc']


class ScopingRule(TypedDict, total=False):
    condition: str  # 'is_assigned', 'is_owner', 'has_scope', 'no_scope', 'show_all'
    action: str     # 'filter_by', 'include', 'exclude'
    params: Dict[str, Any]  # e.g., {'scope_level': 1, 'scope_type': 'accessible'}


# =============================================================================
# FEATURE FLAGS
# =============================================================================

# Master switch
USE_SCOPING_ENGINE = True

# Per-table switches
USE_SCOPING_ENGINE_FOR_TABLES = {
    "users": True,
    "companies": True,
    "factories": True,
    "locations": True,
    "pits": True,
    "carriers": True,
    "drivers": True,
    "pots": True,
    "machines": True,
    "cameras": True,
    "measurements": True,
    "photos": True,
    "videos": True,
    "tags": True,
}

# =============================================================================
# SCOPE LEVELS - Conceptual hierarchy
# =============================================================================

SCOPE_LEVELS: Dict[int, Dict[str, Any]] = {
    0: {
        "name": "user",
        "description": "User ownership - individual user level",
        "model_path": "m_user.User",
        "field": "id",
        "comment": "Direct user ownership (e.g., user profiles, preferences)",
    },
    1: {
        "name": "company",
        "description": "Company membership - top organizational unit",
        "model_path": "m_company.Company",
        "field": "id",
        "comment": "User-Company relation tracked via RelationInstance (M2M)",
    },
    2: {
        "name": "factory",
        "description": "Factory scope - production unit",
        "model_path": "m_factory.Factory",
        "field": "id",
        "comment": "Factory belongs to Company (O2M). Most models are factory-scoped.",
    },
    3: {
        "name": "location",
        "description": "Location scope - physical location within factory",
        "model_path": "m_location.Location",
        "field": "id",
        "comment": "Location belongs to Factory (O2M). Used for spatial organization.",
    },
}

# =============================================================================
# SCOPING RULES MATRIX - SSOT for all scoping rules
# =============================================================================

SCOPING_RULES_MATRIX: Dict[str, Dict[UserRole, List[ScopingRule]]] = {
    "users": {
        "superuser": [],  # Superuser sees all users
        "admin": [
            {
                "condition": "is_owner",
                "action": "include"
            },
            {
                "condition": "is_assigned",
                "action": "include",
                "params": {"scope_level": 1, "scope_type": "accessible"}
            }
        ],  # Admin sees themselves + users from their companies
        "staff": [{"condition": "is_owner", "action": "filter_by"}],
        "editor": [{"condition": "is_owner", "action": "filter_by"}],
        "reader": [{"condition": "is_owner", "action": "filter_by"}],
        "adhoc": [{"condition": "is_owner", "action": "filter_by"}],
    },
    "companies": {
        "superuser": [],  # SA sees all companies
        "admin": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 1, "scope_type": "accessible"}
            }
        ],  # Admin sees only companies they created or were shared with
        "staff": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 1, "scope_type": "accessible"}
            }
        ],
        "editor": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 1, "scope_type": "accessible"}
            }
        ],
        "reader": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 1, "scope_type": "accessible"}
            }
        ],
        "adhoc": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 1, "scope_type": "accessible"}
            }
        ],
    },
    "factories": {
        "superuser": [],
        "admin": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 2, "scope_type": "accessible"}
            }
        ],
        "staff": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 2, "scope_type": "accessible"}
            }
        ],
        "editor": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 2, "scope_type": "accessible"}
            }
        ],
        "reader": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 2, "scope_type": "accessible"}
            }
        ],
        "adhoc": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 2, "scope_type": "accessible"}
            }
        ],
    },
    "locations": {
        "superuser": [],
        "admin": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 3, "scope_type": "accessible"}
            }
        ],
        "staff": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 3, "scope_type": "accessible"}
            }
        ],
        "editor": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 3, "scope_type": "accessible"}
            }
        ],
        "reader": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 3, "scope_type": "accessible"}
            }
        ],
        "adhoc": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 3, "scope_type": "accessible"}
            }
        ],
    },
    # Factory-scoped models (level 2)
    "carriers": {
        "superuser": [],
        "admin": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 2, "scope_type": "accessible"}
            }
        ],
    },
    "drivers": {
        "superuser": [],
        "admin": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 2, "scope_type": "accessible"}
            }
        ],
    },
    "pots": {
        "superuser": [],
        "admin": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 2, "scope_type": "accessible"}
            }
        ],
    },
    "machines": {
        "superuser": [],
        "admin": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 2, "scope_type": "accessible"}
            }
        ],
    },
    "cameras": {
        "superuser": [],
        "admin": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 2, "scope_type": "accessible"}
            }
        ],
    },
    "measurements": {
        "superuser": [],
        "admin": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 2, "scope_type": "accessible"}
            }
        ],
    },
    # Location-scoped models (level 3)
    "pits": {
        "superuser": [],
        "admin": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 3, "scope_type": "accessible"}
            }
        ],
    },
    # Measurement children
    "photos": {
        "superuser": [],
        "admin": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 2, "scope_type": "accessible"}
            }
        ],
    },
    "videos": {
        "superuser": [],
        "admin": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 2, "scope_type": "accessible"}
            }
        ],
    },
    # Tags (user-scoped for now)
    "tags": {
        "superuser": [],
        "admin": [
            {
                "condition": "is_assigned",
                "action": "filter_by",
                "params": {"scope_level": 0, "scope_type": "accessible"}
            }
        ],
    },
}
