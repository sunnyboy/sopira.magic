#!/usr/bin/env python
#..............................................................
#   ~/sopira.magic/version_01/manage.py
#   Django Management Script - Command-line utility
#   Django's command-line utility for administrative tasks
#..............................................................

"""
   Django Management Script - Command-Line Utility.

   Django's command-line utility for administrative tasks.
   Entry point for Django management commands.

   Usage:
   ```bash
   python manage.py runserver
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py generate_data user --count 100
   python manage.py init_relations
   ```

   Sets Django settings module: sopira_magic.settings
"""

import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sopira_magic.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
