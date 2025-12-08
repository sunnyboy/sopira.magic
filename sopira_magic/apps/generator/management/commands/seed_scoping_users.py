#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/generator/management/commands/seed_scoping_users.py
#   Seed Scoping Users Command - Management command
#   Creates minimal users for testing scoping on /api/users/
#..............................................................

"""Seed Scoping Users Command.

This command creates a minimal set of users useful for testing the
scoping engine on the `/api/users/` endpoint:

- 1 SUPERADMIN user (role=SUPERADMIN)
- 1 ADMIN user (role=ADMIN)
- N regular users (role=READER by default)

It reuses the existing GeneratorService and GENERATOR_CONFIG for the
`user` model where appropriate, but ensures the required roles exist
with deterministic usernames.

Usage:
    python manage.py seed_scoping_users
    python manage.py seed_scoping_users --regular-count 5

The command is idempotent with respect to the two primary accounts:
- If `superadmin` already exists, it will not be recreated.
- If `admin` already exists, it will not be recreated.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from sopira_magic.apps.generator.services import GeneratorService


class Command(BaseCommand):
    help = "Seed minimal users for scoping tests (superadmin, admin, regular users)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--regular-count",
            type=int,
            default=5,
            help="Number of additional regular users to generate (default: 5)",
        )

    def handle(self, *args, **options):
        User = get_user_model()
        regular_count = options["regular_count"]

        # 1) Ensure SUPERADMIN user
        superadmin_username = "superadmin"
        superadmin, created_sa = User.objects.get_or_create(
            username=superadmin_username,
            defaults={
                "email": "superadmin@example.com",
                "role": User.UserRole.SUPERADMIN,
                "is_superuser": True,
                "is_staff": True,
                "is_active": True,
            },
        )
        if created_sa:
            superadmin.set_password("password123")
            superadmin.save()
            self.stdout.write(self.style.SUCCESS(f"Created SUPERADMIN user: {superadmin_username} / password123"))
        else:
            self.stdout.write(self.style.WARNING(f"SUPERADMIN user '{superadmin_username}' already exists"))

        # 2) Ensure ADMIN user
        admin_username = "admin"
        admin_user, created_admin = User.objects.get_or_create(
            username=admin_username,
            defaults={
                "email": "admin@example.com",
                "role": User.UserRole.ADMIN,
                "is_superuser": False,
                "is_staff": True,
                "is_active": True,
            },
        )
        if created_admin:
            admin_user.set_password("password123")
            admin_user.save()
            self.stdout.write(self.style.SUCCESS(f"Created ADMIN user: {admin_username} / password123"))
        else:
            self.stdout.write(self.style.WARNING(f"ADMIN user '{admin_username}' already exists"))

        # 3) Generate additional regular users via generator service
        if regular_count > 0:
            self.stdout.write(self.style.SUCCESS(f"Generating {regular_count} regular users via GeneratorService..."))
            users = GeneratorService.generate_data("user", count=regular_count, user=superadmin)
            self.stdout.write(self.style.SUCCESS(f"Generated {len(users)} regular users"))
        else:
            self.stdout.write(self.style.WARNING("No regular users requested (regular-count=0)"))

        self.stdout.write(self.style.SUCCESS("Seed scoping users completed."))
