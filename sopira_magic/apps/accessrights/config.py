"""
ConfigDriven AccessRights SSOT.

Matrix definuje, ktoré roly môžu vidieť/robiť akcie na jednotlivých view_name
a ktoré menu položky sú viditeľné.
"""

from typing import Dict, Literal

Role = Literal["superuser", "admin", "staff", "user", "anonymous"]
Action = Literal["view", "add", "edit", "delete", "export", "menu"]

# Default fallback policy (non-SA)
DEFAULT_POLICY: Dict[Action, Dict[Role, bool]] = {
    "view": {
        "superuser": True,
        "admin": True,
        "staff": True,
        "user": True,
        "anonymous": False,
    },
    "add": {
        "superuser": True,
        "admin": True,
        "staff": False,
        "user": False,
        "anonymous": False,
    },
    "edit": {
        "superuser": True,
        "admin": True,
        "staff": False,
        "user": False,
        "anonymous": False,
    },
    "delete": {
        "superuser": True,
        "admin": True,
        "staff": False,
        "user": False,
        "anonymous": False,
    },
    "export": {
        "superuser": True,
        "admin": True,
        "staff": True,
        "user": False,
        "anonymous": False,
    },
    "menu": {
        "superuser": True,
        "admin": True,
        "staff": True,
        "user": True,
        "anonymous": False,
    },
}

# Access matrix per view/menu key.
# Pridávame len výnimky; inak platí DEFAULT_POLICY.
ACCESS_MATRIX: Dict[str, Dict[Action, Dict[Role, bool]]] = {
    # Companies sú SA-only (všetky akcie + menu).
    "companies": {
        "view": {
            "superuser": True,
            "admin": False,
            "staff": False,
            "user": False,
            "anonymous": False,
        },
        "add": {
            "superuser": True,
            "admin": False,
            "staff": False,
            "user": False,
            "anonymous": False,
        },
        "edit": {
            "superuser": True,
            "admin": False,
            "staff": False,
            "user": False,
            "anonymous": False,
        },
        "delete": {
            "superuser": True,
            "admin": False,
            "staff": False,
            "user": False,
            "anonymous": False,
        },
        "export": {
            "superuser": True,
            "admin": False,
            "staff": False,
            "user": False,
            "anonymous": False,
        },
        "menu": {
            "superuser": True,
            "admin": False,
            "staff": False,
            "user": False,
            "anonymous": False,
        },
    },
}

