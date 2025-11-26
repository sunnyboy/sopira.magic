#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/generator/management/commands/verify_relations.py
#   Verify Relations Command - Management command
#   CLI command for verifying relation integrity
#..............................................................

"""
   Verify Relations Command - Management Command.

   Django management command for verifying relation integrity.
   Checks if RelationRegistry is initialized, RelationInstance records exist,
   and relations are properly created between objects.

   Usage:
   ```bash
   # Verify all relations
   python manage.py verify_relations

   # Verify specific relation
   python manage.py verify_relations --relation user_company
   ```

   Arguments:
   - --relation: Specific relation key to verify (optional)
"""

from django.core.management.base import BaseCommand
from sopira_magic.apps.relation.models import RelationRegistry, RelationInstance
from sopira_magic.apps.relation.config import RELATION_CONFIG
from django.contrib.contenttypes.models import ContentType
from django.apps import apps


class Command(BaseCommand):
    help = 'Verify relation integrity and report statistics'

    def add_arguments(self, parser):
        parser.add_argument(
            '--relation',
            type=str,
            help='Specific relation key to verify (e.g., user_company)',
        )

    def handle(self, *args, **options):
        relation_key = options.get('relation')
        
        self.stdout.write(self.style.SUCCESS('\n=== Relation Verification Report ===\n'))
        
        # 1. Check RelationRegistry
        self.stdout.write(self.style.WARNING('1. Checking RelationRegistry...'))
        registry_count = RelationRegistry.objects.count()
        expected_count = len(RELATION_CONFIG)
        
        if registry_count == expected_count:
            self.stdout.write(self.style.SUCCESS(f'   ✓ RelationRegistry: {registry_count}/{expected_count} entries'))
        else:
            self.stdout.write(self.style.ERROR(
                f'   ✗ RelationRegistry: {registry_count}/{expected_count} entries (MISSING!)'
            ))
            self.stdout.write(self.style.WARNING('   → Run: python manage.py init_relations'))
        
        # List all relations
        for key, config in RELATION_CONFIG.items():
            if relation_key and key != relation_key:
                continue
            
            registry = RelationRegistry.objects.filter(
                source_model=config['source'],
                target_model=config['target'],
                relation_type=config['type']
            ).first()
            
            if registry:
                self.stdout.write(f'   ✓ {key}: {config["source"]} -> {config["target"]}')
            else:
                self.stdout.write(self.style.ERROR(
                    f'   ✗ {key}: {config["source"]} -> {config["target"]} (NOT FOUND)'
                ))
        
        # 2. Check RelationInstance records
        self.stdout.write(self.style.WARNING('\n2. Checking RelationInstance records...'))
        instance_count = RelationInstance.objects.count()
        self.stdout.write(f'   Total RelationInstance records: {instance_count}')
        
        if instance_count == 0:
            self.stdout.write(self.style.WARNING('   → No relations created yet. Generate data first.'))
        
        # 3. Check relations per model
        self.stdout.write(self.style.WARNING('\n3. Checking relations per model...'))
        
        for key, config in RELATION_CONFIG.items():
            if relation_key and key != relation_key:
                continue
            
            registry = RelationRegistry.objects.filter(
                source_model=config['source'],
                target_model=config['target'],
                relation_type=config['type']
            ).first()
            
            if not registry:
                continue
            
            # Count instances for this relation
            instance_count = RelationInstance.objects.filter(relation=registry).count()
            
            # Get source and target models
            try:
                source_app, source_model_name = config['source'].split('.')
                target_app, target_model_name = config['target'].split('.')
                
                source_model = apps.get_model(source_app, source_model_name)
                target_model = apps.get_model(target_app, target_model_name)
                
                source_count = source_model.objects.count()
                target_count = target_model.objects.count()
                
                # Calculate expected relations (approximate)
                expected_relations = min(source_count, target_count)
                
                self.stdout.write(f'\n   Relation: {key}')
                self.stdout.write(f'   Source ({config["source"]}): {source_count} objects')
                self.stdout.write(f'   Target ({config["target"]}): {target_count} objects')
                self.stdout.write(f'   Relations created: {instance_count}')
                
                if instance_count == 0 and expected_relations > 0:
                    self.stdout.write(self.style.WARNING(
                        f'   → Expected ~{expected_relations} relations, but none created!'
                    ))
                elif instance_count > 0:
                    coverage = (instance_count / expected_relations * 100) if expected_relations > 0 else 0
                    self.stdout.write(self.style.SUCCESS(
                        f'   ✓ Coverage: {coverage:.1f}% ({instance_count}/{expected_relations})'
                    ))
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'   ✗ Error checking {key}: {str(e)}'))
        
        # 4. Sample relations
        if instance_count > 0:
            self.stdout.write(self.style.WARNING('\n4. Sample relations (first 5):'))
            for instance in RelationInstance.objects.select_related('relation')[:5]:
                self.stdout.write(
                    f'   {instance.relation.source_model} ({instance.source_object_id}) -> '
                    f'{instance.relation.target_model} ({instance.target_object_id})'
                )
        
        self.stdout.write(self.style.SUCCESS('\n=== Verification Complete ===\n'))

