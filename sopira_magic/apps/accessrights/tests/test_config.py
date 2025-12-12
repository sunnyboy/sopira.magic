import importlib
from django.apps import apps
from django.test import SimpleTestCase

from sopira_magic.apps.accessrights.apps import AccessRightsConfig
from sopira_magic.apps.accessrights.config import ACCESS_MATRIX, DEFAULT_POLICY


class AccessRightsConfigTests(SimpleTestCase):
    def test_default_app_config_path(self):
        accessrights_mod = importlib.import_module("sopira_magic.apps.accessrights")
        assert accessrights_mod.default_app_config == (
            "sopira_magic.apps.accessrights.apps.AccessRightsConfig"
        )

    def test_app_config_metadata(self):
        app_config = apps.get_app_config("accessrights")
        assert isinstance(app_config, AccessRightsConfig)
        assert app_config.name == "sopira_magic.apps.accessrights"
        assert app_config.verbose_name == "Access Rights (ConfigDriven SSOT)"
        assert app_config.path.endswith("sopira_magic/apps/accessrights")

    def test_default_policy_contains_all_actions(self):
        expected_actions = {"view", "add", "edit", "delete", "export", "menu"}
        assert expected_actions == set(DEFAULT_POLICY.keys())
        for action, policy in DEFAULT_POLICY.items():
            assert set(policy.keys()) == {
                "superuser",
                "admin",
                "staff",
                "user",
                "anonymous",
            }

    def test_access_matrix_companies_sa_only(self):
        companies = ACCESS_MATRIX["companies"]
        for action, policy in companies.items():
            assert policy["superuser"] is True
            assert policy["admin"] is False
            assert policy["staff"] is False
            assert policy["user"] is False
            assert policy["anonymous"] is False




