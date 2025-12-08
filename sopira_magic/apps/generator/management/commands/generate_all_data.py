#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/generator/management/commands/generate_all_data.py
#   Generate All Data Command - Management command
#   CLI command for generating seed data for all configured models
#..............................................................

"""
   Generate All Data Command - Management Command.

   Django management command for generating seed data for all configured models
   based on GENERATOR_CONFIG (SSOT). This command respects dependencies and
   generates data in the correct order.

   This is a convenience command that wraps `generate_data --seed` for clarity.
   It's the recommended way to generate seed data for all models.

   Usage:
   ```bash
   # Generate seed data for all models
   python manage.py generate_all_data

   # Generate with specific user for relations
   python manage.py generate_all_data --user sopira
   ```

   Arguments:
   - --user: Username to use for relations (defaults to first user)

   Related Commands:
   - `clear_all_data`: Clear all business data before regenerating
   - `generate_data`: Generate data for a specific model

   Typical Workflow:
   ```bash
   # Clear all data and regenerate
   python manage.py clear_all_data --keep-users
   python manage.py generate_all_data

   # Or clear everything including users
   python manage.py clear_all_data
   python manage.py generate_all_data
   ```

   Note:
   This command generates data based on counts defined in GENERATOR_CONFIG.
   To generate a specific number of records for a single model, use:
   `python manage.py generate_data <model_key> --count <number>`
"""

from django.core.management.base import BaseCommand, CommandError
from sopira_magic.apps.generator.services import GeneratorService
from sopira_magic.apps.m_user.models import User


class Command(BaseCommand):
    help = 'Generate seed data for all configured models (respects dependencies)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            help='Username to use for relations (defaults to first user)',
        )

    def handle(self, *args, **options):
        username = options.get('user')
        
        # Get user
        user = None
        if username:
            try:
                user = User.objects.get(username=username)
                self.stdout.write(self.style.SUCCESS(f'Using user: {user.username}'))
            except User.DoesNotExist:
                raise CommandError(f"User '{username}' not found")
        else:
            user = User.objects.first()
            if user:
                self.stdout.write(self.style.WARNING(f'Using user: {user.username}'))
            else:
                self.stdout.write(self.style.WARNING('No users found. A new user will be created if "user" is in GENERATOR_CONFIG.'))
        
        # Generate seed data for all models
        self.stdout.write(self.style.SUCCESS('Generating seed data for all models...'))
        
        try:
            results = GeneratorService.generate_seed_data(user=user)
            
            self.stdout.write(self.style.SUCCESS('\nGeneration complete:'))
            total_created = 0
            for key, created_count in results.items():
                self.stdout.write(f'  ✓ {key}: {created_count} records created')
                total_created += created_count
            
            self.stdout.write(self.style.SUCCESS(f'\nTotal: {total_created} records created'))
        except Exception as e:
            raise CommandError(f"Error generating data: {str(e)}")

