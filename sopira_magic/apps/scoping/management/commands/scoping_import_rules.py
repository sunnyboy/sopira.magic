#..............................................................
#   apps/scoping/management/commands/scoping_import_rules.py
#   Django management command pre import scoping pravidiel
#..............................................................

"""
Django management command pre import scoping pravidiel z JSON/YAML.
"""

from django.core.management.base import BaseCommand
from sopira_magic.apps.scoping.serialization import import_rules


class Command(BaseCommand):
    help = 'Import scoping rules from JSON or YAML file'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'input_file',
            type=str,
            help='Input file path',
        )
        parser.add_argument(
            '--no-validate',
            action='store_true',
            help='Skip validation of imported rules',
        )
        parser.add_argument(
            '--merge',
            action='store_true',
            help='Merge with existing rules instead of replacing',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Validate only, don\'t import',
        )
    
    def handle(self, *args, **options):
        input_file = options['input_file']
        validate = not options['no_validate']
        merge = options['merge']
        dry_run = options['dry_run']
        
        try:
            if dry_run:
                # Dry-run: len validuj bez importu
                self.stdout.write(self.style.WARNING(f'[DRY RUN] Validating rules from {input_file}'))
                result = import_rules(input_file, validate=validate, merge=False)
                
                if result['success']:
                    self.stdout.write(self.style.SUCCESS('✓ Validation passed'))
                    if result['version']:
                        self.stdout.write(f"Rules version: {result['version']}")
                    self.stdout.write(f"Would import {len(result['imported_rules'])} tables")
                else:
                    self.stdout.write(self.style.ERROR('Validation failed with errors:'))
                    for error in result['errors']:
                        self.stdout.write(self.style.ERROR(f'  - {error}'))
                    raise Exception('Validation failed')
            else:
                # Skutočný import
                result = import_rules(input_file, validate=validate, merge=merge)
                
                if result['success']:
                    self.stdout.write(self.style.SUCCESS(f'Rules imported from {input_file}'))
                    if result['version']:
                        self.stdout.write(f"Imported rules version: {result['version']}")
                else:
                    self.stdout.write(self.style.ERROR('Import failed with errors:'))
                    for error in result['errors']:
                        self.stdout.write(self.style.ERROR(f'  - {error}'))
                    raise Exception('Import failed')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error importing rules: {e}'))
            raise


