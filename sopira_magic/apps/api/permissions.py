"""
API permissions - ConfigDriven&SSOT access control helpers.

- IsSuperUserPermission: allow only authenticated superusers.
- AccessRightsPermission: consults accessrights matrix (SSOT) for view/action.
"""

from rest_framework.permissions import BasePermission, SAFE_METHODS

try:
    from sopira_magic.apps.accessrights.services import can_access
except Exception:  # pragma: no cover - fallback if module not installed yet
    can_access = None  # type: ignore


class IsSuperUserPermission(BasePermission):
    """Allow access only to authenticated superusers."""

    message = "Superuser privileges required."

    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        return bool(user and user.is_authenticated and user.is_superuser)


class AccessRightsPermission(BasePermission):
    """
    Permission backed by accessrights SSOT matrix.

    Maps HTTP method to action:
      SAFE_METHODS -> "view"
      POST -> "add"
      PUT/PATCH -> "edit"
      DELETE -> "delete"
    """

    def has_permission(self, request, view):
        if can_access is None:
            return True  # SSOT not available, do not block

        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return False

        view_name = getattr(view, "_view_name", None)
        if not view_name:
            return True

        if request.method in SAFE_METHODS:
            action = "view"
        elif request.method == "POST":
            action = "add"
        elif request.method in ("PUT", "PATCH"):
            action = "edit"
        elif request.method == "DELETE":
            action = "delete"
        else:
            action = "view"

        return can_access(view_name, action, user)  # type: ignore[arg-type]

