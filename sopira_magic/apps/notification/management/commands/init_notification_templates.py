#..............................................................
#   init_notification_templates.py
#   Management Command - Initialize notification templates from config
#..............................................................

"""
Initialize Notification Templates - Management Command.

Initializes NotificationTemplate objects from NOTIFICATION_CONFIG.
Creates or updates templates based on config (SSOT).

Usage:
    python manage.py init_notification_templates
    python manage.py init_notification_templates --force  # Overwrite existing
"""

from django.core.management.base import BaseCommand
from sopira_magic.apps.notification.models import NotificationTemplate
from sopira_magic.apps.notification.config import NOTIFICATION_CONFIG


class Command(BaseCommand):
    help = 'Initialize notification templates from NOTIFICATION_CONFIG'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update existing templates',
        )
    
    def handle(self, *args, **options):
        force = options.get('force', False)
        
        self.stdout.write(self.style.MIGRATE_HEADING('Initializing Notification Templates...'))
        
        notification_types = NOTIFICATION_CONFIG.get('notification_types', {})
        
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        for notif_type, config in notification_types.items():
            template_name = config.get('template_name', notif_type)
            template_source = config.get('template_source', 'database')
            subject_template = config.get('subject_template', '')
            variables = config.get('variables', [])
            scope_aware = config.get('scope_aware', False)
            enabled = config.get('enabled', True)
            
            # Check if template exists
            try:
                template = NotificationTemplate.objects.get(notification_type=notif_type)
                
                if force:
                    # Update existing
                    template.name = template_name
                    template.template_source = template_source
                    template.subject = subject_template
                    template.variables = variables
                    template.scope_aware = scope_aware
                    template.enabled = enabled
                    template.save()
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Updated: {notif_type}')
                    )
                    updated_count += 1
                else:
                    self.stdout.write(
                        self.style.WARNING(f'○ Skipped (exists): {notif_type}')
                    )
                    skipped_count += 1
            
            except NotificationTemplate.DoesNotExist:
                # Create new
                template = NotificationTemplate.objects.create(
                    name=template_name,
                    notification_type=notif_type,
                    template_source=template_source,
                    subject=subject_template,
                    variables=variables,
                    scope_aware=scope_aware,
                    enabled=enabled,
                    body=''  # Will be filled in admin or via another command
                )
                
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created: {notif_type}')
                )
                created_count += 1
        
        self.stdout.write(
            self.style.MIGRATE_LABEL(
                f'\n Summary: {created_count} created, {updated_count} updated, {skipped_count} skipped'
            )
        )
        
        if skipped_count > 0 and not force:
            self.stdout.write(
                self.style.WARNING(
                    'Use --force to update existing templates'
                )
            )

