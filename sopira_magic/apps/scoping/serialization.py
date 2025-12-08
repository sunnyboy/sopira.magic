#..............................................................
#   apps/scoping/serialization.py
#   Export/Import scoping pravidiel
#..............................................................

"""
Export/Import scoping pravidiel do JSON/YAML.

Umožňuje serializáciu a deserializáciu scoping pravidiel do JSON/YAML.
Uľahčuje versioning, migrácie medzi prostrediami a backup konfigurácie.
"""

import json
import hashlib
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from .rules import SCOPING_RULES_MATRIX
from .validation import validate_scoping_rules_matrix

logger = logging.getLogger(__name__)


def get_rules_version() -> str:
    """
    Vráti verziu pravidiel (hash).
    
    Používa sa pre sledovanie zmien v pravidlách.
    
    Returns:
        str - SHA256 hash pravidiel
    """
    rules_json = json.dumps(SCOPING_RULES_MATRIX, sort_keys=True, default=str)
    return hashlib.sha256(rules_json.encode()).hexdigest()[:16]


def export_rules(format: str = 'json', output_file: Optional[str] = None) -> str:
    """
    Exportuje scoping pravidlá do súboru alebo stringu.
    
    Args:
        format: 'json' alebo 'yaml'
        output_file: Optional cesta k výstupnému súboru (ak None, vráti string)
        
    Returns:
        str - serializované pravidlá (ak output_file je None)
    """
    # Pridaj metadata
    export_data = {
        'version': get_rules_version(),
        'rules': SCOPING_RULES_MATRIX,
        'exported_at': str(logging.Formatter().formatTime(logging.LogRecord(
            name='', level=0, pathname='', lineno=0, msg='', args=(), exc_info=None
        ))),
    }
    
    if format == 'json':
        content = json.dumps(export_data, indent=2, default=str)
    elif format == 'yaml':
        try:
            import yaml
            content = yaml.dump(export_data, default_flow_style=False, allow_unicode=True)
        except ImportError:
            raise ImportError("PyYAML is required for YAML export. Install with: pip install pyyaml")
    else:
        raise ValueError(f"Unknown format: {format}. Must be 'json' or 'yaml'")
    
    if output_file:
        Path(output_file).write_text(content, encoding='utf-8')
        logger.info(f"Exported scoping rules to {output_file}")
        return f"Rules exported to {output_file}"
    
    return content


def validate_imported_rules(rules: Dict[str, Any]) -> list:
    """
    Validuje importované pravidlá.
    
    Args:
        rules: Dict s pravidlami (štruktúra ako SCOPING_RULES_MATRIX)
        
    Returns:
        List[str] - zoznam chybových hlásení (prázdny ak nie sú chyby)
    """
    errors = []
    
    if not isinstance(rules, dict):
        errors.append("Rules must be a dict")
        return errors
    
    # Validuj každú tabuľku
    for table_name, table_rules in rules.items():
        if not isinstance(table_rules, dict):
            errors.append(f"Table '{table_name}': rules must be a dict")
            continue
        
        for role, role_rules in table_rules.items():
            if not isinstance(role_rules, list):
                errors.append(f"Table '{table_name}'/Role '{role}': rules must be a list")
                continue
            
            for i, rule in enumerate(role_rules):
                if not isinstance(rule, dict):
                    errors.append(f"Table '{table_name}'/Role '{role}'[{i}]: rule must be a dict")
                    continue
                
                # Základná validácia
                if 'condition' not in rule:
                    errors.append(f"Table '{table_name}'/Role '{role}'[{i}]: missing 'condition'")
                if 'action' not in rule:
                    errors.append(f"Table '{table_name}'/Role '{role}'[{i}]: missing 'action'")
    
    return errors


def import_rules(input_file: str, validate: bool = True, merge: bool = False) -> Dict[str, Any]:
    """
    Importuje scoping pravidlá zo súboru.
    
    Args:
        input_file: Cesta k vstupnému súboru
        validate: Ak True, validuje importované pravidlá
        merge: Ak True, zlúči s existujúcimi pravidlami (inak prepíše)
        
    Returns:
        Dict s výsledkom importu:
        - success: bool
        - imported_rules: Dict s importovanými pravidlami
        - errors: List[str] s chybami
        - version: str verzia importovaných pravidiel
    """
    path = Path(input_file)
    if not path.exists():
        return {
            'success': False,
            'errors': [f"File not found: {input_file}"],
            'imported_rules': {},
            'version': None,
        }
    
    content = path.read_text(encoding='utf-8')
    
    # Detekuj formát podľa prípony
    if path.suffix.lower() in ['.yaml', '.yml']:
        try:
            import yaml
            data = yaml.safe_load(content)
        except ImportError:
            return {
                'success': False,
                'errors': ["PyYAML is required for YAML import. Install with: pip install pyyaml"],
                'imported_rules': {},
                'version': None,
            }
    else:
        data = json.loads(content)
    
    # Extrahuj pravidlá (môžu byť v 'rules' kľúči alebo priamo)
    if 'rules' in data:
        imported_rules = data['rules']
        version = data.get('version')
    else:
        imported_rules = data
        version = None
    
    errors = []
    
    # Validácia
    if validate:
        validation_errors = validate_imported_rules(imported_rules)
        errors.extend(validation_errors)
    
    if errors:
        return {
            'success': False,
            'errors': errors,
            'imported_rules': imported_rules,
            'version': version,
        }
    
    # Import do SCOPING_RULES_MATRIX
    if merge:
        # Merge s existujúcimi pravidlami
        SCOPING_RULES_MATRIX.update(imported_rules)
        logger.info(f"Merged scoping rules from {input_file}")
    else:
        # Prepíš existujúce pravidlá
        SCOPING_RULES_MATRIX.clear()
        SCOPING_RULES_MATRIX.update(imported_rules)
        logger.info(f"Imported scoping rules from {input_file}")
    
    return {
        'success': True,
        'errors': [],
        'imported_rules': imported_rules,
        'version': version,
    }

