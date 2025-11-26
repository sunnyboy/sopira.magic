#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/generator/management/commands/generate_data.py
#   Generate Data Command - Management command
#   CLI command for generating synthetic data
#..............................................................

"""
   Generate Data Command - Management Command.

   Django management command for generating synthetic data for models
   based on GENERATOR_CONFIG (SSOT). Supports generating data for specific
   models or all configured models with dependency resolution.

   This command is primarily for generating data for a specific model.
   For generating all seed data, prefer using `generate_all_data` command.

   Usage:
   ```bash
   # Generate data for specific model
   python manage.py generate_data user --count 100

   # Generate all seed data (respects dependencies)
   # Note: Prefer using 'generate_all_data' command for clarity
   python manage.py generate_data --seed
   python manage.py generate_all_data  # Recommended alternative

   # Generate with specific user for relations
   python manage.py generate_data company --user sopira
   ```

   Related Commands:
   - `generate_all_data`: Generate seed data for all models (recommended)
   - `clear_all_data`: Clear all business data before regenerating

   Arguments:
   - model_key: Model key from GENERATOR_CONFIG (optional, use --seed for all)
   - --count: Number of records to generate (overrides config)
   - --user: Username to use for relations (defaults to first user)
   - --seed: Generate seed data for all configured models (respects dependencies)
   - --clear: Clear existing data before generating (for specific model only)
   - --keep: Number of records to keep when clearing (default: 0 = delete all)
"""

from django.core.management.base import BaseCommand, CommandError
from sopira_magic.apps.generator.services import GeneratorService
from sopira_magic.apps.generator.config import get_all_generator_configs
from sopira_magic.apps.user.models import User


class Command(BaseCommand):
    help = 'Generate data for models based on GENERATOR_CONFIG'

    def add_arguments(self, parser):
        parser.add_argument(
            'model_key',
            nargs='?',
            type=str,
            help='Model key from GENERATOR_CONFIG (e.g., company, factory). If not provided, generates seed data for all models.',
        )
        parser.add_argument(
            '--count',
            type=int,
            help='Number of records to generate (overrides config count)',
        )
        parser.add_argument(
            '--user',
            type=str,
            help='Username to use for relations (defaults to first user)',
        )
        parser.add_argument(
            '--seed',
            action='store_true',
            help='Generate seed data for all configured models (respects dependencies)',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before generating',
        )
        parser.add_argument(
            '--keep',
            type=int,
            default=0,
            help='Number of records to keep when clearing (default: 0 = delete all)',
        )

    def handle(self, *args, **options):
        model_key = options.get('model_key')
        count = options.get('count')
        username = options.get('user')
        seed = options.get('seed')
        clear = options.get('clear')
        keep = options.get('keep')
        
        # Get user
        user = None
        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                raise CommandError(f"User '{username}' not found")
        else:
            user = User.objects.first()
            if user:
                self.stdout.write(self.style.WARNING(f"Using user: {user.username}"))
        
        # Clear data if requested
        if clear and model_key:
            configs = get_all_generator_configs()
            if model_key not in configs:
                raise CommandError(f"Model key '{model_key}' not found in GENERATOR_CONFIG")
            
            deleted_count = GeneratorService.clear_data(model_key, keep_count=keep)
            self.stdout.write(self.style.SUCCESS(f"Cleared {deleted_count} records from {model_key}"))
            return
        
        # Generate seed data for all models
        if seed or not model_key:
            self.stdout.write(self.style.SUCCESS('Generating seed data for all models...'))
            results = GeneratorService.generate_seed_data(user=user)
            
            self.stdout.write(self.style.SUCCESS('\nGeneration complete:'))
            for key, created_count in results.items():
                self.stdout.write(f"  {key}: {created_count} records created")
            return
        
        # Generate data for specific model
        configs = get_all_generator_configs()
        if model_key not in configs:
            available = ', '.join(configs.keys())
            raise CommandError(
                f"Model key '{model_key}' not found. Available: {available}"
            )
        
        self.stdout.write(self.style.SUCCESS(f'Generating data for {model_key}...'))
        
        try:
            created_objects = GeneratorService.generate_data(
                model_key, 
                count=count, 
                user=user
            )
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created {len(created_objects)} records')
            )
        except Exception as e:
            raise CommandError(f"Error generating data: {str(e)}")

