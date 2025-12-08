"""Základné smoke testy pre security modul.

Tieto testy len overujú, že sa modul dá importovať a
že základná konfigurácia je konzistentná.
"""

from django.test import TestCase

from sopira_magic.apps.security.config import SECURITY_CONFIG_MATRIX
from sopira_magic.apps.security.types import EnvironmentType
from sopira_magic.apps.security.validation import validate_security_config


class SecurityConfigTests(TestCase):
    def test_all_environment_types_present(self):
        """Každý EnvironmentType má konfiguráciu v SECURITY_CONFIG_MATRIX."""

        for env in EnvironmentType:
            self.assertIn(env, SECURITY_CONFIG_MATRIX)

    def test_validation_returns_no_errors_for_default_matrix(self):
        errors = validate_security_config()
        self.assertIsInstance(errors, list)
        # V default stave by nemali byť kritické chyby
        self.assertEqual(errors, [])
