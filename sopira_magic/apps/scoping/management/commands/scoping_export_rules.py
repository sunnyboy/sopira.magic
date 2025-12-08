#..............................................................
#   apps/scoping/management/commands/scoping_export_rules.py
#   Django management command pre export scoping pravidiel
#..............................................................

"""
Django management command pre export scoping pravidiel do JSON/YAML.
"""

from django.core.management.base import BaseCommand
from sopira_magic.apps.scoping.serialization import export_rules


class Command(BaseCommand):
    help = 'Export scoping rules to JSON or YAML file'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--format',
            type=str,
            default='json',
            choices=['json', 'yaml'],
            help='Output format (json or yaml)',
        )
        parser.add_argument(
            '--output',
            type=str,
            help='Output file path (if not provided, prints to stdout)',
        )
    
    def handle(self, *args, **options):
        format_type = options['format']
        output_file = options.get('output')
        
        try:
            result = export_rules(format=format_type, output_file=output_file)
            if output_file:
                self.stdout.write(self.style.SUCCESS(f'Rules exported to {output_file}'))
            else:
                self.stdout.write(result)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error exporting rules: {e}'))
            raise


