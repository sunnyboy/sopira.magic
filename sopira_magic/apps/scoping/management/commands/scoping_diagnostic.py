#..............................................................
#   apps/scoping/management/commands/scoping_diagnostic.py
#   Django management command pre diagnostiku scoping engine
#..............................................................

"""
Django management command pre diagnostiku scoping engine.
Kontroluje registry konfiguráciu, settings, pravidlá a VIEWS_MATRIX kompatibilitu.
"""

import json
from django.core.management.base import BaseCommand
from django.conf import settings
from sopira_magic.apps.scoping import registry
from sopira_magic.apps.scoping.rules import SCOPING_RULES_MATRIX
from sopira_magic.apps.scoping.validation import validate_all


class Command(BaseCommand):
    help = 'Run diagnostic checks on scoping engine configuration'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--format',
            type=str,
            default='text',
            choices=['text', 'json'],
            help='Output format (text or json)',
        )
        parser.add_argument(
            '--check',
            type=str,
            action='append',
            choices=['registry', 'settings', 'rules', 'compatibility', 'all'],
            help='Specific checks to run (default: all)',
        )
    
    def handle(self, *args, **options):
        format_type = options['format']
        checks = options.get('check') or ['all']
        
        if 'all' in checks:
            checks = ['registry', 'settings', 'rules', 'compatibility']
        
        results = {}
        
        if 'registry' in checks:
            results['registry'] = self.check_registry()
        
        if 'settings' in checks:
            results['settings'] = self.check_settings()
        
        if 'rules' in checks:
            results['rules'] = self.check_rules()
        
        if 'compatibility' in checks:
            results['compatibility'] = self.check_compatibility()
        
        # Výstup výsledkov
        if format_type == 'json':
            self.stdout.write(json.dumps(results, indent=2, default=str))
        else:
            self.print_text_results(results)
    
    def check_registry(self):
        """Kontrola registry konfigurácie."""
        is_configured = registry.is_registry_configured()
        
        return {
            'configured': is_configured,
            'status': 'OK' if is_configured else 'NOT CONFIGURED',
            'message': (
                'Registry callbacks are configured' if is_configured
                else 'Registry callbacks are not configured. Call register_scope_provider() and register_role_provider()'
            ),
        }
    
    def check_settings(self):
        """Kontrola Django settings."""
        settings_checks = {}
        
        # SCOPING_VALIDATE_ON_STARTUP
        validate_on_startup = getattr(settings, 'SCOPING_VALIDATE_ON_STARTUP', True)
        settings_checks['SCOPING_VALIDATE_ON_STARTUP'] = {
            'value': validate_on_startup,
            'default': True,
            'status': 'OK',
        }
        
        # SCOPING_RAISE_ON_VALIDATION_ERRORS
        raise_on_errors = getattr(settings, 'SCOPING_RAISE_ON_VALIDATION_ERRORS', False)
        settings_checks['SCOPING_RAISE_ON_VALIDATION_ERRORS'] = {
            'value': raise_on_errors,
            'default': False,
            'status': 'OK',
        }
        
        # SCOPING_FALLBACK_ENABLED
        fallback_enabled = getattr(settings, 'SCOPING_FALLBACK_ENABLED', True)
        settings_checks['SCOPING_FALLBACK_ENABLED'] = {
            'value': fallback_enabled,
            'default': True,
            'status': 'OK',
        }
        
        # SCOPING_MIDDLEWARE_ENABLED
        middleware_enabled = getattr(settings, 'SCOPING_MIDDLEWARE_ENABLED', False)
        settings_checks['SCOPING_MIDDLEWARE_ENABLED'] = {
            'value': middleware_enabled,
            'default': False,
            'status': 'OK',
        }
        
        return {
            'status': 'OK',
            'settings': settings_checks,
        }
    
    def check_rules(self):
        """Kontrola scoping pravidiel."""
        rule_count = sum(
            len(rules) for table_rules in SCOPING_RULES_MATRIX.values()
            for rules in table_rules.values()
        )
        table_count = len(SCOPING_RULES_MATRIX)
        
        # Validácia pravidiel
        validation_result = validate_all()
        
        return {
            'table_count': table_count,
            'rule_count': rule_count,
            'validation': {
                'errors': len(validation_result['errors']),
                'warnings': len(validation_result['warnings']),
                'status': 'OK' if not validation_result['errors'] else 'ERRORS',
            },
            'tables': list(SCOPING_RULES_MATRIX.keys()),
        }
    
    def check_compatibility(self):
        """Kontrola kompatibility medzi pravidlami a VIEWS_MATRIX."""
        try:
            from sopira_magic.apps.api.view_configs import VIEWS_MATRIX
        except ImportError:
            return {
                'status': 'SKIP',
                'message': 'VIEWS_MATRIX not available',
            }
        
        issues = []
        compatible_tables = []
        
        # Kontrola každého pravidla voči VIEWS_MATRIX
        for table_name, table_rules in SCOPING_RULES_MATRIX.items():
            config = VIEWS_MATRIX.get(table_name)
            
            if not config:
                issues.append(f"Table '{table_name}': No config in VIEWS_MATRIX")
                continue
            
            # Kontrola scope_level voči ownership_hierarchy
            ownership_hierarchy = config.get('ownership_hierarchy', [])
            max_level = len(ownership_hierarchy) - 1
            
            for role, rules in table_rules.items():
                for i, rule in enumerate(rules):
                    params = rule.get('params', {})
                    scope_level = params.get('scope_level')
                    
                    if scope_level is not None and scope_level > max_level:
                        issues.append(
                            f"Table '{table_name}'/Role '{role}'[{i}]: "
                            f"scope_level {scope_level} exceeds ownership_hierarchy length ({len(ownership_hierarchy)})"
                        )
            
            if not issues or not any(issue.startswith(f"Table '{table_name}'") for issue in issues):
                compatible_tables.append(table_name)
        
        return {
            'status': 'OK' if not issues else 'ISSUES',
            'compatible_tables': compatible_tables,
            'issues': issues,
            'issue_count': len(issues),
        }
    
    def print_text_results(self, results):
        """Vytlačí textové výsledky diagnostiky."""
        self.stdout.write('Scoping Engine Diagnostic Report')
        self.stdout.write('=' * 80)
        self.stdout.write('')
        
        # Registry
        if 'registry' in results:
            registry_result = results['registry']
            self.stdout.write('Registry Configuration:')
            self.stdout.write(f"  Status: {self.style.SUCCESS(registry_result['status']) if registry_result['configured'] else self.style.ERROR(registry_result['status'])}")
            self.stdout.write(f"  {registry_result['message']}")
            self.stdout.write('')
        
        # Settings
        if 'settings' in results:
            settings_result = results['settings']
            self.stdout.write('Settings Configuration:')
            for setting_name, setting_info in settings_result['settings'].items():
                value = setting_info['value']
                default = setting_info['default']
                status_icon = '✓' if value == default else '⚠'
                self.stdout.write(f"  {status_icon} {setting_name}: {value} (default: {default})")
            self.stdout.write('')
        
        # Rules
        if 'rules' in results:
            rules_result = results['rules']
            self.stdout.write('Rules Configuration:')
            self.stdout.write(f"  Tables: {rules_result['table_count']}")
            self.stdout.write(f"  Total Rules: {rules_result['rule_count']}")
            validation = rules_result['validation']
            if validation['errors'] > 0:
                self.stdout.write(f"  Validation: {self.style.ERROR(f'{validation['errors']} errors, {validation['warnings']} warnings')}")
            elif validation['warnings'] > 0:
                self.stdout.write(f"  Validation: {self.style.WARNING(f'{validation['warnings']} warnings')}")
            else:
                self.stdout.write(f"  Validation: {self.style.SUCCESS('OK')}")
            self.stdout.write('')
        
        # Compatibility
        if 'compatibility' in results:
            compat_result = results['compatibility']
            self.stdout.write('VIEWS_MATRIX Compatibility:')
            if compat_result['status'] == 'SKIP':
                self.stdout.write(f"  {self.style.WARNING(compat_result['message'])}")
            elif compat_result['status'] == 'OK':
                self.stdout.write(f"  Status: {self.style.SUCCESS('OK')}")
                self.stdout.write(f"  Compatible Tables: {len(compat_result['compatible_tables'])}")
            else:
                self.stdout.write(f"  Status: {self.style.ERROR('ISSUES FOUND')}")
                self.stdout.write(f"  Issues: {compat_result['issue_count']}")
                for issue in compat_result['issues']:
                    self.stdout.write(f"    - {issue}")
            self.stdout.write('')
        
        # Summary
        self.stdout.write('Summary:')
        all_ok = all(
            (r.get('status') == 'OK' or r.get('configured', False))
            for r in results.values()
            if isinstance(r, dict) and 'status' in r
        )
        
        if all_ok:
            self.stdout.write(self.style.SUCCESS('  ✓ All checks passed'))
        else:
            self.stdout.write(self.style.WARNING('  ⚠ Some issues found (see details above)'))

