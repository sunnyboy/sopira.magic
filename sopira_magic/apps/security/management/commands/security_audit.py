"""Security audit command - ConfigDriven security CLI tool."""

from django.core.management.base import BaseCommand

from sopira_magic.apps.security.engine import SecurityEngine
from sopira_magic.apps.security.utils import SecurityUtils


class Command(BaseCommand):
    help = "Run comprehensive security audit (ConfigDriven & SSOT)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--check",
            type=str,
            default="quick",
            choices=["quick", "full", "ssl", "headers", "cors", "config"],
            help="Type of audit to run",
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Show detailed results",
        )
        parser.add_argument(
            "--fix",
            action="store_true",
            help="(Reserved) Attempt to fix issues automatically",
        )

    def handle(self, *args, **options):
        check_type = options["check"]
        verbose = options["verbose"]
        fix_mode = options["fix"]

        self.stdout.write(
            self.style.MIGRATE_HEADING(
                f"Running {check_type.upper()} Security Audit (ConfigDriven & SSOT)"
            )
        )
        self.stdout.write("=" * 70)

        results = SecurityEngine.security_audit(check_type)

        if results.get("passed", False):
            self.stdout.write(self.style.SUCCESS("Security Audit PASSED"))
        else:
            self.stdout.write(self.style.ERROR("Security Audit FAILED"))

        self.stdout.write(f"\nSummary: {results.get('summary', 'Unknown')}")
        self.stdout.write(f"Timestamp: {results.get('timestamp')}")

        checks = results.get("checks", {})
        for check_name, check_results in checks.items():
            self.stdout.write("\n" + "-" * 50)
            self.stdout.write(f"{check_name.upper()} check")
            self.stdout.write("-" * 50)

            if check_results.get("passed", False):
                self.stdout.write(
                    self.style.SUCCESS(check_results.get("message", "PASSED"))
                )
            else:
                self.stdout.write(
                    self.style.ERROR(check_results.get("message", "FAILED"))
                )

            for warning in check_results.get("warnings", []):
                self.stdout.write(self.style.WARNING(f"Warning: {warning}"))

            for error in check_results.get("errors", []):
                self.stdout.write(self.style.ERROR(f"Error: {error}"))

            if verbose and check_results.get("details"):
                self.stdout.write("Details:")
                for key, value in check_results["details"].items():
                    self.stdout.write(f"  {key}: {value}")

        if fix_mode and not results.get("passed", False):
            self.stdout.write("\nFix mode is not implemented yet. Please fix issues manually.")

        report = SecurityUtils.generate_security_report(results)
        self.stdout.write("\n" + "=" * 70)
        self.stdout.write(report)
