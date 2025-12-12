from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase

from sopira_magic.apps.accessrights.services import (
    can_access,
    can_view_menu,
    get_access_matrix_for_user,
)


class AccessRightsIntegrationTests(TestCase):
    def test_superuser_has_full_access(self):
        user = get_user_model().objects.create_superuser(
            username="super_sa",
            email="super@example.com",
            password="testpass123",
        )

        matrix = get_access_matrix_for_user(user, view_names={"companies": {}, "custom": {}})
        assert set(matrix.keys()) == {"companies", "custom"}
        for actions in matrix.values():
            assert all(actions.values())

    def test_staff_respects_matrix_and_default_policy(self):
        user = get_user_model().objects.create_user(
            username="staff_user",
            email="staff@example.com",
            password="testpass123",
            is_staff=True,
        )

        assert can_access("companies", "view", user) is False
        assert can_access("any_view", "export", user) is True

        matrix = get_access_matrix_for_user(user, view_names={"any_view": {}})
        assert matrix["any_view"] == {
            "view": True,
            "add": False,
            "edit": False,
            "delete": False,
            "export": True,
            "menu": True,
        }

    def test_regular_user_default_permissions(self):
        user = get_user_model().objects.create_user(
            username="regular_user",
            email="regular@example.com",
            password="testpass123",
        )

        assert can_view_menu("factories", user) is True
        assert can_access("factories", "add", user) is False

        matrix = get_access_matrix_for_user(user, view_names={"factories": {}})
        assert matrix["factories"]["view"] is True
        assert matrix["factories"]["export"] is False

    def test_anonymous_denied_everywhere(self):
        anon = AnonymousUser()
        assert can_access("companies", "view", anon) is False
        assert can_view_menu("companies", anon) is False

        matrix = get_access_matrix_for_user(anon, view_names={"companies": {}})
        assert all(value is False for value in matrix["companies"].values())




