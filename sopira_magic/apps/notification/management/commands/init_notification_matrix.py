#..............................................................
#   init_notification_matrix.py
#   Management Command - Initialize notification matrix from config
#..............................................................

"""
Initialize Notification Matrix - Management Command.

Initializes NotificationMatrix entries based on NOTIFICATION_CONFIG.
Creates default matrix entries for each notification type.

Usage:
    python manage.py init_notification_matrix
    python manage.py init_notification_matrix --force  # Overwrite existing
"""

from django.core.management.base import BaseCommand
from sopira_magic.apps.notification.models import NotificationMatrix
from sopira_magic.apps.notification.config import NOTIFICATION_CONFIG


class Command(BaseCommand):
    help = 'Initialize notification matrix from NOTIFICATION_CONFIG'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force recreate matrix entries',
        )
    
    def handle(self, *args, **options):
        force = options.get('force', False)
        
        self.stdout.write(self.style.MIGRATE_HEADING('Initializing Notification Matrix...'))
        
        notification_types = NOTIFICATION_CONFIG.get('notification_types', {})
        
        created_count = 0
        skipped_count = 0
        
        for notif_type, config in notification_types.items():
            default_recipients = config.get('default_recipients', [])
            scope_aware = config.get('scope_aware', False)
            
            for recipient_type in default_recipients:
                # Check if matrix entry exists
                existing = NotificationMatrix.objects.filter(
                    notification_type=notif_type,
                    recipient_type=recipient_type
                ).first()
                
                if existing and not force:
                    self.stdout.write(
                        self.style.WARNING(
                            f'○ Skipped (exists): {notif_type} → {recipient_type}'
                        )
                    )
                    skipped_count += 1
                    continue
                
                if existing and force:
                    # Delete and recreate
                    existing.delete()
                
                # Create matrix entry
                NotificationMatrix.objects.create(
                    notification_type=notif_type,
                    recipient_type=recipient_type,
                    recipient_identifier='',
                    scope_pattern='same_scope' if scope_aware else '',
                    conditions={},
                    enabled=True
                )
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Created: {notif_type} → {recipient_type}'
                    )
                )
                created_count += 1
        
        self.stdout.write(
            self.style.MIGRATE_LABEL(
                f'\n Summary: {created_count} created, {skipped_count} skipped'
            )
        )
        
        if skipped_count > 0 and not force:
            self.stdout.write(
                self.style.WARNING(
                    'Use --force to recreate existing matrix entries'
                )
            )

