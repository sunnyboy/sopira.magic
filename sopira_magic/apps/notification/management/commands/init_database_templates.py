#..............................................................
#   init_database_templates.py
#   Management Command - Initialize database template content
#..............................................................

"""
Initialize Database Templates - Management Command.

Fills in body content for database templates (login, signup_admin, password_reset_confirm).

Usage:
    python manage.py init_database_templates
    python manage.py init_database_templates --force  # Overwrite existing
"""

from django.core.management.base import BaseCommand
from sopira_magic.apps.notification.models import NotificationTemplate


class Command(BaseCommand):
    help = 'Initialize database template content'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update existing template bodies',
        )
    
    def handle(self, *args, **options):
        force = options.get('force', False)
        
        self.stdout.write(self.style.MIGRATE_HEADING('Initializing Database Template Content...'))
        
        templates_content = {
            'login_notification': {
                'body': """🔐 Login Notification

A user has logged into Sopira Magic:

User Information:
- Username: {{ username }}
- Email: {{ email }}
- Role: {{ role }}

Login Details:
- Time: {{ timestamp }}
- IP Address: {{ ip_address }}
- User Agent: {{ user_agent }}

If this login was not authorized, please contact the user immediately.

---
This is an automated security notification from Sopira Magic.
""",
            },
            
            'signup_notification_admin': {
                'body': """👤 New User Registration

A new user has registered on Sopira Magic:

User Information:
- Username: {{ username }}
- Email: {{ email }}
- Role: {{ role }}

Registration Details:
- Time: {{ timestamp }}
- IP Address: {{ ip_address }}

Please review the new user account and configure appropriate access permissions.

---
This is an automated notification from Sopira Magic.
""",
            },
            
            'password_reset_confirm': {
                'body': """✅ Password Changed Successfully

Your Sopira Magic password has been changed successfully.

Account Information:
- Username: {{ username }}
- Email: {{ email }}

Change Details:
- Time: {{ timestamp }}
- IP Address: {{ ip_address }}

If you did not make this change, please contact support immediately.

---
This is an automated security notification from Sopira Magic.
""",
            },
        }
        
        updated_count = 0
        skipped_count = 0
        
        for notif_type, content in templates_content.items():
            try:
                template = NotificationTemplate.objects.get(notification_type=notif_type)
                
                if template.body and not force:
                    self.stdout.write(
                        self.style.WARNING(f'○ Skipped (has content): {notif_type}')
                    )
                    skipped_count += 1
                else:
                    template.body = content['body']
                    template.save()
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Updated: {notif_type}')
                    )
                    updated_count += 1
            
            except NotificationTemplate.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'✗ Not found: {notif_type}')
                )
        
        self.stdout.write(
            self.style.MIGRATE_LABEL(
                f'\nSummary: {updated_count} updated, {skipped_count} skipped'
            )
        )
        
        if skipped_count > 0 and not force:
            self.stdout.write(
                self.style.WARNING('Use --force to overwrite existing content')
            )

