from types import SimpleNamespace
from django.test import SimpleTestCase

from sopira_magic.apps.accessrights import config
from sopira_magic.apps.accessrights.services import (
    _get_role,
    _get_policy,
    can_access,
    can_view_menu,
    get_access_matrix_for_user,
)


class AccessRightsServicesTests(SimpleTestCase):
    def _user(
        self,
        *,
        is_authenticated: bool = True,
        is_superuser: bool = False,
        is_admin: bool = False,
        is_staff: bool = False,
    ):
        return SimpleNamespace(
            is_authenticated=is_authenticated,
            is_superuser=is_superuser,
            is_admin=is_admin,
            is_staff=is_staff,
        )

    # _get_role
    def test_get_role_returns_anonymous_for_none(self):
        assert _get_role(None) == "anonymous"

    def test_get_role_returns_anonymous_when_not_authenticated(self):
        user = self._user(is_authenticated=False)
        assert _get_role(user) == "anonymous"

    def test_get_role_prioritizes_superuser(self):
        user = self._user(is_superuser=True, is_admin=True, is_staff=True)
        assert _get_role(user) == "superuser"

    def test_get_role_detects_admin_flag(self):
        user = self._user(is_admin=True)
        assert _get_role(user) == "admin"

    def test_get_role_detects_staff_flag(self):
        user = self._user(is_staff=True)
        assert _get_role(user) == "staff"

    def test_get_role_defaults_to_user(self):
        user = self._user()
        assert _get_role(user) == "user"

    # _get_policy
    def test_policy_uses_access_matrix_override(self):
        policy = _get_policy("companies", "view")
        assert policy["admin"] is False
        assert policy["superuser"] is True

    def test_policy_falls_back_to_default_for_unknown_view(self):
        policy = _get_policy("nonexistent", "add")
        assert policy == config.DEFAULT_POLICY["add"]

    def test_policy_falls_back_to_view_when_action_missing(self):
        policy = _get_policy("nonexistent", "custom")
        assert policy == config.DEFAULT_POLICY["view"]

    # can_access
    def test_can_access_superuser_short_circuit(self):
        user = self._user(is_superuser=True, is_authenticated=False)
        assert can_access("companies", "view", user) is True

    def test_can_access_denies_admin_for_sa_only_view(self):
        user = self._user(is_admin=True)
        assert can_access("companies", "delete", user) is False

    def test_can_access_allows_staff_export_on_default_policy(self):
        user = self._user(is_staff=True)
        assert can_access("factories", "export", user) is True

    def test_can_access_denies_anonymous_on_default_view(self):
        user = self._user(is_authenticated=False)
        assert can_access("factories", "view", user) is False

    # can_view_menu
    def test_can_view_menu_uses_menu_action(self):
        user = self._user()
        assert can_view_menu("any-menu", user) is True

    def test_can_view_menu_denies_anonymous(self):
        user = self._user(is_authenticated=False)
        assert can_view_menu("any-menu", user) is False

    # get_access_matrix_for_user
    def test_get_access_matrix_uses_access_matrix_when_names_missing(self):
        user = self._user()
        matrix = get_access_matrix_for_user(user, view_names={})
        assert "companies" in matrix
        # Regular user nemá prístup na SA-only view
        assert all(val is False for val in matrix["companies"].values())

    def test_get_access_matrix_for_superuser_allows_everything(self):
        user = self._user(is_superuser=True)
        matrix = get_access_matrix_for_user(user)
        assert "companies" in matrix
        assert all(matrix["companies"].values())

    def test_get_access_matrix_uses_default_policy_for_custom_names(self):
        user = self._user(is_staff=True)
        matrix = get_access_matrix_for_user(user, view_names={"custom": {}})
        assert matrix["custom"] == {
            "view": True,
            "add": False,
            "edit": False,
            "delete": False,
            "export": True,
            "menu": True,
        }




