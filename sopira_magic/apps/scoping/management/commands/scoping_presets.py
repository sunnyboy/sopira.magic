#..............................................................
#   apps/scoping/management/commands/scoping_presets.py
#   Django management command pre prácu s presetmi scoping pravidiel
#..............................................................

"""
Django management command pre prácu s presetmi scoping pravidiel.
"""

import json
from django.core.management.base import BaseCommand, CommandError
from sopira_magic.apps.scoping.presets import (
    get_factory_scoped_preset,
    get_user_scoped_preset,
    get_global_preset,
    get_hybrid_preset,
)
from sopira_magic.apps.scoping.rules import SCOPING_RULES_MATRIX
from sopira_magic.apps.scoping.serialization import export_rules


class Command(BaseCommand):
    help = 'Manage scoping rule presets'
    
    PRESETS = {
        'factory': get_factory_scoped_preset,
        'user': get_user_scoped_preset,
        'global': get_global_preset,
        'hybrid': get_hybrid_preset,
    }
    
    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # list command
        list_parser = subparsers.add_parser('list', help='List available presets')
        list_parser.add_argument(
            '--format',
            type=str,
            default='text',
            choices=['text', 'json'],
            help='Output format',
        )
        
        # show command
        show_parser = subparsers.add_parser('show', help='Show preset rules')
        show_parser.add_argument(
            'preset_name',
            type=str,
            help='Preset name (factory, user, global, hybrid)',
        )
        show_parser.add_argument(
            '--format',
            type=str,
            default='text',
            choices=['text', 'json', 'yaml'],
            help='Output format',
        )
        show_parser.add_argument(
            '--output',
            type=str,
            help='Output file path (if not provided, prints to stdout)',
        )
        
        # apply command
        apply_parser = subparsers.add_parser('apply', help='Apply preset to table')
        apply_parser.add_argument(
            'preset_name',
            type=str,
            help='Preset name (factory, user, global, hybrid)',
        )
        apply_parser.add_argument(
            'table_name',
            type=str,
            help='Table name to apply preset to',
        )
        apply_parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Validate only, don\'t apply',
        )
    
    def handle(self, *args, **options):
        command = options.get('command')
        
        if not command:
            self.stdout.write(self.style.ERROR('Please specify a command. Use --help for available commands.'))
            raise CommandError('No command specified')
        
        if command == 'list':
            self.handle_list(**options)
        elif command == 'show':
            self.handle_show(**options)
        elif command == 'apply':
            self.handle_apply(**options)
        else:
            raise CommandError(f'Unknown command: {command}')
    
    def handle_list(self, **options):
        """List available presets."""
        format_type = options['format']
        
        preset_names = list(self.PRESETS.keys())
        
        if format_type == 'json':
            output = {
                'presets': preset_names,
                'count': len(preset_names),
            }
            self.stdout.write(json.dumps(output, indent=2))
        else:
            self.stdout.write('Available presets:')
            for preset_name in preset_names:
                self.stdout.write(f'  - {preset_name}')
            self.stdout.write(f'\nTotal: {len(preset_names)} presets')
    
    def handle_show(self, **options):
        """Show preset rules."""
        preset_name = options['preset_name']
        format_type = options['format']
        output_file = options.get('output')
        
        if preset_name not in self.PRESETS:
            raise CommandError(
                f'Unknown preset: {preset_name}. Available: {", ".join(self.PRESETS.keys())}'
            )
        
        preset_func = self.PRESETS[preset_name]
        preset_rules = preset_func()
        
        if format_type == 'json':
            content = json.dumps(preset_rules, indent=2, default=str)
        elif format_type == 'yaml':
            try:
                import yaml
                content = yaml.dump(preset_rules, default_flow_style=False, allow_unicode=True)
            except ImportError:
                raise CommandError('PyYAML is required for YAML export. Install with: pip install pyyaml')
        else:
            # Textový formát
            lines = [f'Preset: {preset_name}', '=' * 80]
            for role, rules in preset_rules.items():
                lines.append(f'\nRole: {role}')
                lines.append('-' * 80)
                for i, rule in enumerate(rules):
                    lines.append(f'  Rule {i + 1}:')
                    lines.append(f'    Condition: {rule.get("condition")}')
                    lines.append(f'    Action: {rule.get("action")}')
                    if 'params' in rule:
                        lines.append(f'    Params: {rule["params"]}')
                    if 'when' in rule:
                        lines.append(f'    When: {rule["when"]}')
            content = '\n'.join(lines)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            self.stdout.write(self.style.SUCCESS(f'Preset exported to {output_file}'))
        else:
            self.stdout.write(content)
    
    def handle_apply(self, **options):
        """Apply preset to table."""
        preset_name = options['preset_name']
        table_name = options['table_name']
        dry_run = options['dry_run']
        
        if preset_name not in self.PRESETS:
            raise CommandError(
                f'Unknown preset: {preset_name}. Available: {", ".join(self.PRESETS.keys())}'
            )
        
        preset_func = self.PRESETS[preset_name]
        preset_rules = preset_func()
        
        if dry_run:
            self.stdout.write(self.style.WARNING(f'[DRY RUN] Would apply preset "{preset_name}" to table "{table_name}"'))
            self.stdout.write(f'Rules that would be applied:')
            for role, rules in preset_rules.items():
                self.stdout.write(f'  {role}: {len(rules)} rules')
            self.stdout.write(self.style.SUCCESS('✓ Validation passed (dry-run)'))
            return
        
        # Aplikuj preset na tabuľku
        if table_name not in SCOPING_RULES_MATRIX:
            SCOPING_RULES_MATRIX[table_name] = {}
        
        # Prepíš pravidlá pre tabuľku presetom
        SCOPING_RULES_MATRIX[table_name] = preset_rules.copy()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'✓ Preset "{preset_name}" applied to table "{table_name}"'
            )
        )
        self.stdout.write(f'Applied rules for {len(preset_rules)} roles')

