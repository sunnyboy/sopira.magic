"""Security test command - quick smoke test for security module."""

from django.core.management.base import BaseCommand

from sopira_magic.apps.security.engine import SecurityEngine
from sopira_magic.apps.security.validation import validate_security_config


class Command(BaseCommand):
    help = "Run quick smoke tests for security configuration and engine."

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("Running security smoke tests"))

        errors = validate_security_config()
        if errors:
            self.stdout.write(self.style.ERROR("Security config validation FAILED"))
            for err in errors:
                self.stdout.write(self.style.ERROR(f"  - {err}"))
            raise SystemExit(1)

        self.stdout.write(self.style.SUCCESS("Security config validation PASSED"))

        results = SecurityEngine.security_audit("quick")
        if not results.get("passed", False):
            self.stdout.write(self.style.ERROR("Quick security audit FAILED"))
            self.stdout.write(f"Summary: {results.get('summary')}")
            raise SystemExit(2)

        self.stdout.write(self.style.SUCCESS("Quick security audit PASSED"))
        self.stdout.write("All security smoke tests passed.")
