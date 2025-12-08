"""SSL check command - validate SSL certificate for a domain."""

import json

from django.core.management.base import BaseCommand

from sopira_magic.apps.security.validators.ssl import SslValidator


class Command(BaseCommand):
    help = "Check SSL certificate status for a given domain."

    def add_arguments(self, parser):
        parser.add_argument(
            "--domain",
            type=str,
            default=None,
            help="Domain to check (default: current hostname)",
        )
        parser.add_argument(
            "--json",
            action="store_true",
            help="Output result as JSON",
        )

    def handle(self, *args, **options):
        domain = options["domain"]
        json_output = options["json"]

        result = SslValidator.check_status(domain)

        if json_output:
            self.stdout.write(json.dumps(result, indent=2, sort_keys=True))
            return

        if result.get("valid", False):
            self.stdout.write(self.style.SUCCESS("SSL certificate is valid"))
        else:
            self.stdout.write(self.style.ERROR("SSL certificate is NOT valid"))

        for key, value in result.items():
            self.stdout.write(f"{key}: {value}")
