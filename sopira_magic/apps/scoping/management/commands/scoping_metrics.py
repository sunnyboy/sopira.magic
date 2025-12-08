#..............................................................
#   apps/scoping/management/commands/scoping_metrics.py
#   Django management command pre zobrazenie metrík scoping engine
#..............................................................

"""
Django management command pre zobrazenie metrík scoping engine.
"""

import json
from django.core.management.base import BaseCommand
from sopira_magic.apps.scoping.metrics import get_metrics, reset_metrics, export_metrics


class Command(BaseCommand):
    help = 'Display scoping engine metrics'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--format',
            type=str,
            default='text',
            choices=['text', 'json'],
            help='Output format (text or json)',
        )
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset metrics after displaying',
        )
    
    def handle(self, *args, **options):
        format_type = options['format']
        reset = options['reset']
        
        try:
            # Získaj metriky
            metrics = get_metrics()
            
            # Výstup metrík
            if format_type == 'json':
                self.stdout.write(json.dumps(metrics, indent=2, default=str))
            else:
                # Použi export_metrics pre textový formát
                output = export_metrics(format='text')
                self.stdout.write(output)
            
            # Reset ak je požadovaný
            if reset:
                reset_metrics()
                self.stdout.write(self.style.SUCCESS('\n✓ Metrics reset'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error retrieving metrics: {e}'))
            raise

