#..............................................................
#   apps/scoping/management/commands/scoping_validate_rules.py
#   Django management command pre validáciu scoping pravidiel
#..............................................................

"""
Django management command pre validáciu scoping pravidiel.
"""

import json
from django.core.management.base import BaseCommand
from sopira_magic.apps.scoping.validation import validate_all, validate_and_raise, ScopingValidationError


class Command(BaseCommand):
    help = 'Validate scoping rules and configuration'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--raise-on-errors',
            action='store_true',
            help='Raise exception if validation errors are found',
        )
        parser.add_argument(
            '--include-warnings',
            action='store_true',
            help='Include warnings in output (default: only errors)',
        )
        parser.add_argument(
            '--format',
            type=str,
            default='text',
            choices=['text', 'json'],
            help='Output format (text or json)',
        )
    
    def handle(self, *args, **options):
        raise_on_errors = options['raise_on_errors']
        include_warnings = options['include_warnings']
        format_type = options['format']
        
        # Skús získať VIEWS_MATRIX pre kompletnú validáciu
        view_configs = None
        try:
            from sopira_magic.apps.api.view_configs import VIEWS_MATRIX
            view_configs = VIEWS_MATRIX
        except ImportError:
            self.stdout.write(
                self.style.WARNING('VIEWS_MATRIX not available, skipping scope_level validation')
            )
        
        try:
            if raise_on_errors:
                # Validuj a vyhoď výnimku pri chybách
                try:
                    validate_and_raise(view_configs, raise_on_warnings=False)
                    result = {'errors': [], 'warnings': []}
                except ScopingValidationError as e:
                    # Ak chceme warnings, musíme zavolať validate_all
                    result = validate_all(view_configs)
                    if format_type == 'json':
                        self.stdout.write(json.dumps(result, indent=2))
                    else:
                        self.stdout.write(self.style.ERROR(str(e)))
                    raise
            else:
                # Validuj bez vyhodenia výnimky
                result = validate_all(view_configs)
            
            # Výstup výsledkov
            if format_type == 'json':
                output = {
                    'errors': result['errors'],
                    'warnings': result['warnings'] if include_warnings else [],
                    'error_count': len(result['errors']),
                    'warning_count': len(result['warnings']),
                }
                self.stdout.write(json.dumps(output, indent=2))
            else:
                # Textový výstup
                if result['errors']:
                    self.stdout.write(self.style.ERROR(f"Validation found {len(result['errors'])} errors:"))
                    for error in result['errors']:
                        self.stdout.write(self.style.ERROR(f"  - {error}"))
                else:
                    self.stdout.write(self.style.SUCCESS("✓ No validation errors found"))
                
                if include_warnings and result['warnings']:
                    self.stdout.write(self.style.WARNING(f"\nValidation found {len(result['warnings'])} warnings:"))
                    for warning in result['warnings']:
                        self.stdout.write(self.style.WARNING(f"  - {warning}"))
                elif include_warnings:
                    self.stdout.write(self.style.SUCCESS("✓ No warnings found"))
            
            # Exit code: 0 ak žiadne chyby, 1 ak sú chyby
            if result['errors']:
                raise SystemExit(1)
                
        except ScopingValidationError as e:
            if format_type == 'json':
                self.stdout.write(json.dumps({
                    'errors': [str(e)],
                    'warnings': [],
                    'error_count': 1,
                    'warning_count': 0,
                }, indent=2))
            else:
                self.stdout.write(self.style.ERROR(f"Validation error: {e}"))
            raise SystemExit(1)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error during validation: {e}'))
            raise

