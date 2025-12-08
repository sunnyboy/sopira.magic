# Scoping Engine

Config-driven rule engine pre aplikovanie scoping pravidiel na Django querysets.

## Úvod

Scoping Engine je abstraktný systém pre automatické filtrovanie dát na základe pravidiel definovaných v konfiguračnej matici. Systém je úplne abstraktný - pracuje s úrovňami scope (`scope_level`) namiesto konkrétnych názvov fieldov, čo umožňuje flexibilné a znovupoužiteľné scoping pravidlá.

## Filozofia

- **Abstraktné úrovne scope** - Engine pracuje s `scope_level` (0, 1, 2...), nie s konkrétnymi názvami fieldov
- **Config-driven** - Všetky pravidlá sú definované v `SCOPING_RULES_MATRIX` (SSOT)
- **Thread-safe** - Registry operácie sú chránené lockmi pre produkčné nasadenie
- **Fallback stratégie** - Graceful degradation pri chybách
- **Monitoring** - Automatické zaznamenávanie metrík výkonu
- **Backward compatible** - Všetky nové funkcie sú voliteľné

## Základné koncepty

### Scope Level

`scope_level` je abstraktná úroveň v ownership hierarchii. Napríklad:
- `scope_level: 0` = User (prvý field v `ownership_hierarchy`)
- `scope_level: 1` = Factory (druhý field v `ownership_hierarchy`)
- `scope_level: 2` = Location (tretí field v `ownership_hierarchy`)

Engine automaticky mapuje `scope_level` na skutočný field name z `ownership_hierarchy` v `VIEWS_MATRIX`.

### Ownership Hierarchy

Definuje hierarchiu vlastníctva v `VIEWS_MATRIX`:

```python
"ownership_hierarchy": ["created_by", "factory_id", "location_id"]
```

Toto určuje, ktoré fields sa používajú pre jednotlivé úrovne scope.

### Scoping Rules

Pravidlá sú definované v `SCOPING_RULES_MATRIX`:

```python
{
    "condition": "is_assigned",
    "action": "filter_by",
    "params": {"scope_level": 1, "scope_type": "accessible"}
}
```

## Quick Start

### 1. Registrácia callbacks

Pred použitím scoping engine musíte registrovať callbacks:

```python
from apps.scoping.registry import register_scope_provider, register_role_provider

def get_scope_values(scope_level, scope_owner, scope_type, request):
    # Vráť zoznam hodnôt pre daný scope_level a scope_type
    return ['id1', 'id2', 'id3']

def get_role(scope_owner):
    # Vráť role scope_owner
    return 'admin'

register_scope_provider(get_scope_values)
register_role_provider(get_role)
```

### 2. Použitie v view

```python
from apps.scoping.engine import ScopingEngine
from measurement.api.view_configs import VIEWS_MATRIX

def my_view(request):
    queryset = MyModel.objects.all()
    config = VIEWS_MATRIX.get('mytable', {})
    
    # Aplikuj scoping
    queryset = ScopingEngine.apply_rules(
        queryset,
        request.user,
        'mytable',
        config,
        request=request
    )
    
    return queryset
```

### 3. Použitie decoratoru

```python
from apps.scoping.decorators import apply_scoping

@apply_scoping('mytable')
def my_view(request):
    queryset = MyModel.objects.all()
    # Scoping je automaticky aplikovaný
    return queryset
```

## Komponenty

- **engine.py** - Hlavný scoping engine
- **rules.py** - Definícia pravidiel (SCOPING_RULES_MATRIX)
- **registry.py** - Thread-safe registry pre callbacks
- **validation.py** - Validácia pravidiel pri štarte
- **metrics.py** - Monitoring a metriky
- **fallback.py** - Fallback stratégie
- **decorators.py** - Decorators pre automatické scoping
- **presets.py** - Preddefinované konfigurácie
- **serialization.py** - Export/Import pravidiel
- **middleware.py** - Django middleware pre automatické scoping
- **test_helpers.py** - Helper funkcie pre testovanie

## Dokumentácia

- [API Reference](docs/API.md) - Kompletná API dokumentácia
- [Configuration](docs/CONFIGURATION.md) - Konfigurácia a príklady
- [Testing](docs/TESTING.md) - Ako testovať scoping engine
- [Deployment](docs/DEPLOYMENT.md) - Best practices a troubleshooting

## Príklady

### Základné použitie

```python
from apps.scoping.engine import ScopingEngine

queryset = ScopingEngine.apply_rules(
    queryset=MyModel.objects.all(),
    scope_owner=request.user,
    table_name='mytable',
    config=VIEWS_MATRIX.get('mytable', {}),
    request=request
)
```

### Použitie presetov

```python
from apps.scoping.presets import get_factory_scoped_preset

preset = get_factory_scoped_preset()
# Použi preset v SCOPING_RULES_MATRIX
```

### Export/Import pravidiel

```bash
# Export
python manage.py scoping_export_rules --format json --output rules.json

# Import
python manage.py scoping_import_rules rules.json
```

### Monitoring

```python
from apps.scoping.metrics import get_metrics, export_metrics

# Získaj metriky
metrics = get_metrics()

# Export do JSON
json_metrics = export_metrics(format='json')
```

## Settings

```python
# settings.py

# Fallback stratégie
SCOPING_FALLBACK_ENABLED = True
SCOPING_FALLBACK_LEVEL = 'engine'  # 'engine', 'simple', 'none'

# Middleware
SCOPING_MIDDLEWARE_ENABLED = False
SCOPING_MIDDLEWARE_TABLES = ['cameras', 'machines']

# Validácia
SCOPING_VALIDATE_ON_STARTUP = True
SCOPING_RAISE_ON_VALIDATION_ERRORS = False
```

## Podpora

Pre otázky a problémy pozri [Deployment Guide](docs/DEPLOYMENT.md) alebo kontaktujte vývojový tím.

