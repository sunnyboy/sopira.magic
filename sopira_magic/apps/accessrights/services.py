"""
AccessRights services - single source of truth for role/action matrix.
"""

from typing import Dict
from django.contrib.auth import get_user_model
from .config import ACCESS_MATRIX, DEFAULT_POLICY, Role, Action

User = get_user_model()


def _get_role(user) -> Role:
    if not user or not getattr(user, "is_authenticated", False):
        return "anonymous"
    if getattr(user, "is_superuser", False):
        return "superuser"
    if getattr(user, "is_admin", False):
        return "admin"
    if getattr(user, "is_staff", False):
        return "staff"
    return "user"


def _get_policy(view_name: str, action: Action) -> Dict[Role, bool]:
    view_cfg = ACCESS_MATRIX.get(view_name, {})
    if action in view_cfg:
        return view_cfg[action]
    return DEFAULT_POLICY.get(action, DEFAULT_POLICY["view"])


def can_access(view_name: str, action: Action, user) -> bool:
    # Superuser hard-allow
    if getattr(user, "is_superuser", False):
        return True
    role = _get_role(user)
    policy = _get_policy(view_name, action)
    return bool(policy.get(role, False))


def can_view_menu(menu_key: str, user) -> bool:
    # Menu uses action "menu"
    return can_access(menu_key, "menu", user)


def get_access_matrix_for_user(user, view_names: Dict[str, Dict] | None = None) -> Dict[str, Dict[str, bool]]:
    """
    Vypočíta actions pre daného usera na základe matice a default policy.

    Args:
        user: Django user
        view_names: optional mapping of view_name -> any (napr. VIEWS_MATRIX keys)
    Returns:
        dict {view_name: {view/add/edit/delete/export/menu: bool}}
    """
    actions = ["view", "add", "edit", "delete", "export", "menu"]
    result: Dict[str, Dict[str, bool]] = {}

    names = list(view_names.keys()) if view_names else list(ACCESS_MATRIX.keys())
    # Ak nie sú žiadne view_names ani ACCESS_MATRIX, vráť prázdno
    if not names:
        return result

    for name in names:
        result[name] = {}
        for action in actions:
            result[name][action] = can_access(name, action, user)
    return result

