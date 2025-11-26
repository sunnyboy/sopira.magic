#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/relation/management/commands/init_relations.py
#   Init Relations Command - Management command
#   CLI command for initializing relation registry
#..............................................................

"""
   Init Relations Command - Management Command.

   Django management command for initializing RelationRegistry from
   RELATION_CONFIG (SSOT). Creates or updates RelationRegistry entries
   based on configuration.

   Usage:
   ```bash
   # Initialize relations from config
   python manage.py init_relations

   # Dry run (show what would be created)
   python manage.py init_relations --dry-run
   ```

   Arguments:
   - --dry-run: Show what would be created without actually creating

   Process:
   1. Reads RELATION_CONFIG from relation/config.py
   2. Creates or updates RelationRegistry entries
   3. Reports created/updated counts
"""

from django.core.management.base import BaseCommand
from sopira_magic.apps.relation.config import RELATION_CONFIG
from sopira_magic.apps.relation.models import RelationRegistry


class Command(BaseCommand):
    help = 'Initialize RelationRegistry from RELATION_CONFIG'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without actually creating',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        created_count = 0
        updated_count = 0
        
        for relation_key, config in RELATION_CONFIG.items():
            relation, created = RelationRegistry.objects.get_or_create(
                source_model=config['source'],
                target_model=config['target'],
                relation_type=config['type'],
                defaults={
                    'field_name': config.get('field_name', ''),
                    'related_name': config.get('related_name', ''),
                    'on_delete': config.get('on_delete', 'PROTECT'),
                    'config': config,
                }
            )
            
            if not created:
                # Update existing relation
                relation.field_name = config.get('field_name', '')
                relation.related_name = config.get('related_name', '')
                relation.on_delete = config.get('on_delete', 'PROTECT')
                relation.config = config
                
                if not dry_run:
                    relation.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Updated: {relation_key} ({relation.source_model} -> {relation.target_model})')
                )
            else:
                if not dry_run:
                    pass  # Already created by get_or_create
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created: {relation_key} ({relation.source_model} -> {relation.target_model})')
                )
        
        self.stdout.write(self.style.SUCCESS(
            f'\nSummary: {created_count} created, {updated_count} updated'
        ))

