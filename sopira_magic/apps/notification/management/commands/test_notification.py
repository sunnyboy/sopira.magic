#..............................................................
#   test_notification.py
#   Management Command - Test notification sending
#..............................................................

"""
Test Notification - Management Command.

Tests notification sending with sample data.
Useful for debugging and verifying email configuration.

Usage:
    python manage.py test_notification login_notification
    python manage.py test_notification signup_notification_user --email test@example.com
    python manage.py test_notification --list  # List all notification types
"""

from django.core.management.base import BaseCommand, CommandError
from sopira_magic.apps.notification.engine import NotificationEngine
from sopira_magic.apps.notification.config import get_all_notification_types
from datetime import datetime


class Command(BaseCommand):
    help = 'Test notification sending with sample data'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'notification_type',
            nargs='?',
            type=str,
            help='Notification type to test',
        )
        parser.add_argument(
            '--email',
            type=str,
            help='Override recipient email',
        )
        parser.add_argument(
            '--list',
            action='store_true',
            help='List all available notification types',
        )
        parser.add_argument(
            '--preview',
            action='store_true',
            help='Preview only (don\'t send)',
        )
    
    def handle(self, *args, **options):
        # List mode
        if options.get('list'):
            self.stdout.write(self.style.MIGRATE_HEADING('Available Notification Types:'))
            for notif_type in get_all_notification_types():
                self.stdout.write(f'  • {notif_type}')
            return
        
        # Test mode
        notification_type = options.get('notification_type')
        if not notification_type:
            raise CommandError('Please provide notification_type or use --list')
        
        self.stdout.write(
            self.style.MIGRATE_HEADING(f'Testing Notification: {notification_type}')
        )
        
        # Create sample context
        from sopira_magic.apps.m_user.models import User
        
        try:
            sample_user = User.objects.first()
        except:
            sample_user = None
        
        sample_context = {
            'user': sample_user,
            'username': 'test_user',
            'email': options.get('email') or 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'ip_address': '192.168.1.1',
            'user_agent': 'Mozilla/5.0 (Test)',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'role': 'ADMIN',
            'login_url': 'http://localhost:3000/login',
            'reset_url': 'http://localhost:3000/reset-password/test-token-123',
            'uid': 'test-uid-123',
            'token': 'test-token-456',
            'token_expiry': '24 hours',
        }
        
        # Preview mode
        if options.get('preview'):
            self.stdout.write(self.style.WARNING('📋 Preview Mode (not sending)'))
            
            try:
                preview = NotificationEngine.preview_notification(
                    notification_type=notification_type,
                    sample_context=sample_context
                )
                
                if preview.get('error'):
                    self.stdout.write(
                        self.style.ERROR(f'❌ Preview failed: {preview["error"]}')
                    )
                    return
                
                self.stdout.write(self.style.SUCCESS(f'\n✓ Enabled: {preview.get("enabled")}'))
                self.stdout.write(self.style.SUCCESS(f'✓ Recipients: {preview.get("recipients", [])}'))
                self.stdout.write(self.style.SUCCESS(f'✓ Subject: {preview.get("subject")}'))
                self.stdout.write(self.style.MIGRATE_LABEL(f'\nBody preview (first 200 chars):'))
                body = preview.get('body', '')
                self.stdout.write(body[:200] + '...' if len(body) > 200 else body)
            
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Preview failed: {e}')
                )
            
            return
        
        # Send mode
        self.stdout.write(self.style.WARNING('📤 Sending Test Notification...'))
        
        try:
            result = NotificationEngine.send_notification(
                notification_type=notification_type,
                context=sample_context
            )
            
            if result['success']:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'\n✅ Success! Sent to {result["sent_count"]} recipients'
                    )
                )
                self.stdout.write(f'   Recipients: {result["recipients"]}')
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f'\n❌ Failed! {result["failed_count"]} failures'
                    )
                )
                if result['errors']:
                    self.stdout.write('   Errors:')
                    for error in result['errors']:
                        self.stdout.write(f'     • {error}')
            
            if result['failed_count'] > 0:
                self.stdout.write(
                    self.style.WARNING(
                        f'\n⚠️  Partial success: {result["sent_count"]} sent, {result["failed_count"]} failed'
                    )
                )
        
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'\n❌ Test failed: {e}')
            )
            import traceback
            self.stdout.write(traceback.format_exc())

