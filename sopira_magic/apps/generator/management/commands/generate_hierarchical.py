#..............................................................
#   management/commands/generate_hierarchical.py
#   Generate data hierarchically - N records per parent
#..............................................................

"""
Hierarchical Data Generator - Generate N records per parent.

This command generates data in a hierarchical manner, where each model
creates N records per parent record, respecting FK relationships.

Example hierarchy (with count_per_parent values):
- 10 users
- 3 companies per user → 30 companies total
- 5 factories per company → 150 factories total  
- 5 locations per factory → 750 locations total
- 10 cameras per factory → 1500 cameras total
- 50 measurements per factory → 7500 measurements total
- 1 photo per measurement → 7500 photos total
- 1 video per measurement → 7500 videos total
- 3 tags per record → assigned dynamically

Usage:
    python manage.py generate_hierarchical
    python manage.py generate_hierarchical --dry-run
"""

from django.core.management.base import BaseCommand
from sopira_magic.apps.generator.config import get_all_generator_configs
from sopira_magic.apps.generator.services import GeneratorService
from sopira_magic.apps.m_user.models import User


class Command(BaseCommand):
    help = 'Generate data hierarchically (N per parent) with FK relationships'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be generated without actually creating records',
        )
        parser.add_argument(
            '--user',
            type=str,
            help='Username for M2M relations (default: first user)',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        username = options.get('user')
        
        # Get user for M2M relations
        user = None
        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"User '{username}' not found"))
                return
        else:
            user = User.objects.first()
        
        if not user:
            self.stdout.write(self.style.ERROR("No users found. Create at least one user first."))
            return
        
        self.stdout.write(self.style.SUCCESS(f"Using user: {user.username}\n"))
        
        # Get all generator configs
        configs = get_all_generator_configs()
        
        # Calculate hierarchical counts
        hierarchical_plan = self._calculate_hierarchical_counts(configs)
        
        # Display plan
        self.stdout.write(self.style.SUCCESS("=" * 70))
        self.stdout.write(self.style.SUCCESS("HIERARCHICAL GENERATION PLAN"))
        self.stdout.write(self.style.SUCCESS("=" * 70))
        
        total_records = 0
        for model_key, plan in hierarchical_plan.items():
            count = plan['total_count']
            total_records += count
            
            if plan.get('count_per_parent'):
                parent_key = plan.get('parent_key', 'N/A')
                parent_count = plan.get('parent_count', 0)
                per_parent = plan['count_per_parent']
                
                self.stdout.write(
                    f"  {model_key:20s}: {count:6d} records "
                    f"({per_parent} per {parent_key}, {parent_count} parents)"
                )
            else:
                self.stdout.write(f"  {model_key:20s}: {count:6d} records (top-level)")
        
        self.stdout.write(self.style.SUCCESS("=" * 70))
        self.stdout.write(self.style.SUCCESS(f"TOTAL: {total_records} records"))
        self.stdout.write(self.style.SUCCESS("=" * 70))
        
        if dry_run:
            self.stdout.write(self.style.WARNING("\n[DRY RUN] No data will be generated."))
            return
        
        # Confirm
        self.stdout.write(self.style.WARNING(f"\nThis will create {total_records} records."))
        confirm = input("Continue? [y/N]: ")
        if confirm.lower() != 'y':
            self.stdout.write(self.style.ERROR("Cancelled."))
            return
        
        # Generate data hierarchically
        self.stdout.write(self.style.SUCCESS("\n" + "=" * 70))
        self.stdout.write(self.style.SUCCESS("GENERATING DATA"))
        self.stdout.write(self.style.SUCCESS("=" * 70 + "\n"))
        
        results = {}
        
        for model_key, plan in hierarchical_plan.items():
            config = configs[model_key]
            count = plan['total_count']
            
            self.stdout.write(f"Generating {model_key}... ", ending='')
            
            try:
                # Temporarily override count in config for this generation
                original_count = config.get('count')
                config['count'] = count
                
                created = GeneratorService.generate_data(model_key, count=count, user=user)
                results[model_key] = len(created)
                
                # Restore original count
                config['count'] = original_count
                
                self.stdout.write(self.style.SUCCESS(f"✓ {len(created)} created"))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"✗ FAILED: {e}"))
                results[model_key] = 0
        
        # Summary
        self.stdout.write(self.style.SUCCESS("\n" + "=" * 70))
        self.stdout.write(self.style.SUCCESS("GENERATION COMPLETE"))
        self.stdout.write(self.style.SUCCESS("=" * 70))
        
        for key, created_count in results.items():
            self.stdout.write(f"  {key:20s}: {created_count:6d} created")
        
        total_created = sum(results.values())
        self.stdout.write(self.style.SUCCESS("=" * 70))
        self.stdout.write(self.style.SUCCESS(f"TOTAL: {total_created} records created"))
        self.stdout.write(self.style.SUCCESS("=" * 70))

    def _calculate_hierarchical_counts(self, configs):
        """
        Calculate total counts for hierarchical generation.
        
        For each model with count_per_parent, multiply by parent count.
        Top-level models (no parents) use their count directly.
        
        Returns:
            Dict[model_key, {total_count, count_per_parent, parent_key, parent_count}]
        """
        plan = {}
        created_counts = {}
        
        # Build dependency graph for topological order
        dependencies = {}
        for key, config in configs.items():
            dependencies[key] = config.get('depends_on', [])
        
        # Topological sort
        sorted_keys = self._topological_sort(dependencies)
        
        # Calculate counts in dependency order
        for model_key in sorted_keys:
            config = configs[model_key]
            count_per_parent = config.get('count_per_parent')
            base_count = config.get('count', 0)
            depends_on = config.get('depends_on', [])
            
            if not count_per_parent:
                # Top-level model - use base count
                total_count = base_count
                plan[model_key] = {
                    'total_count': total_count,
                    'count_per_parent': None,
                    'parent_key': None,
                    'parent_count': None,
                }
            else:
                # Find primary parent (first dependency with FK field)
                parent_key = self._find_primary_parent(config, depends_on)
                if not parent_key or parent_key not in created_counts:
                    # No parent or parent not yet created - use base count as fallback
                    total_count = base_count
                    parent_count = 0
                else:
                    parent_count = created_counts[parent_key]
                    total_count = count_per_parent * parent_count
                
                plan[model_key] = {
                    'total_count': total_count,
                    'count_per_parent': count_per_parent,
                    'parent_key': parent_key,
                    'parent_count': parent_count,
                }
            
            # Store count for child calculations
            created_counts[model_key] = plan[model_key]['total_count']
        
        return plan

    def _find_primary_parent(self, config, depends_on):
        """
        Find primary parent model (first FK field in config).
        
        For example, factory has FK to company, so primary parent is 'company'.
        For pit, location is optional but factory is required, so factory is primary.
        """
        fields = config.get('fields', {})
        
        # Look for NON-nullable FK fields first (primary parent)
        for field_name, field_config in fields.items():
            if isinstance(field_config, dict) and field_config.get('type') == 'fk':
                # Skip nullable FK (optional relations)
                if field_config.get('nullable', False):
                    continue
                
                # Extract model key from FK model path
                fk_model = field_config.get('model', '')
                # Convert "company.Company" -> "company"
                model_key = fk_model.split('.')[0].lower()
                
                if model_key in depends_on:
                    return model_key
        
        # Fallback: use first dependency
        return depends_on[0] if depends_on else None

    def _topological_sort(self, dependencies):
        """
        Topological sort of models based on dependencies.
        
        Returns list of model keys in generation order.
        """
        from collections import deque
        
        # Calculate in-degrees
        in_degree = {key: 0 for key in dependencies}
        for key, deps in dependencies.items():
            for dep in deps:
                if dep in in_degree:
                    in_degree[dep] += 1
        
        # Queue for models with no dependencies
        queue = deque([key for key, degree in in_degree.items() if degree == 0])
        sorted_keys = []
        
        while queue:
            key = queue.popleft()
            sorted_keys.append(key)
            
            # Reduce in-degree for dependents
            for other_key, deps in dependencies.items():
                if key in deps:
                    in_degree[other_key] -= 1
                    if in_degree[other_key] == 0:
                        queue.append(other_key)
        
        # Check for cycles
        if len(sorted_keys) != len(dependencies):
            # Cycle detected - return keys in original order
            return list(dependencies.keys())
        
        return sorted_keys

