# Scoping Engine Configuration

Príručka pre konfiguráciu Scoping Engine.

## SCOPING_RULES_MATRIX

Hlavná konfiguračná matica pre všetky scoping pravidlá. Definuje pravidlá pre každú tabuľku a rolu.

### Štruktúra

```python
SCOPING_RULES_MATRIX: ScopingMatrix = {
    "table_name": {
        "role": [
            {
                "condition": "condition_name",
                "action": "action_name",
                "params": {
                    "scope_level": 1,
                    "scope_type": "accessible"
                },
                "when": {
                    "role": ["admin", "staff"],
                    "table": ["cameras", "machines"]
                }
            }
        ]
    }
}
```

### Conditions

- `has_scope` - Záznam má nastavený scope field (nie je NULL)
- `no_scope` - Záznam nemá nastavený scope field (je NULL)
- `is_owner` - Záznam patrí scope_owner (prvý field v ownership_hierarchy)
- `is_assigned` - Záznam je v accessible scope pre daný scope_level
- `is_selected` - Záznam je v selected scope pre daný scope_level

### Actions

- `include` - OR: Pridá záznamy do výsledku (ak spĺňajú condition)
- `exclude` - NOT: Odstráni záznamy z výsledku (ak spĺňajú condition)
- `filter_by` - AND: Filtruje len záznamy, ktoré spĺňajú condition
- `show_all` - Žiadne filtrovanie: Zobrazí všetky záznamy

### Params

- `scope_level` - Abstraktná úroveň scope (0, 1, 2...)
- `scope_type` - 'selected' alebo 'accessible'

### When Conditions

Voliteľné podmienky pre aplikovanie pravidla:

- `role` - List rolí, pre ktoré sa pravidlo aplikuje
- `table` - List tabuliek, pre ktoré sa pravidlo aplikuje
- `field` - Field name, pre ktorý sa pravidlo aplikuje

### Príklady

#### Factory-scoped tabuľka

```python
"cameras": {
    "superuser": [
        {
            "condition": "is_selected",
            "action": "filter_by",
            "params": {"scope_level": 1, "scope_type": "selected"}
        },
        {
            "condition": "no_scope",
            "action": "include"
        }
    ],
    "admin": [
        {
            "condition": "is_assigned",
            "action": "filter_by",
            "params": {"scope_level": 1, "scope_type": "accessible"}
        }
    ]
}
```

#### User-scoped tabuľka

```python
"user_preferences": {
    "superuser": [
        {
            "condition": "show_all",
            "action": "show_all"
        }
    ],
    "admin": [
        {
            "condition": "is_owner",
            "action": "filter_by"
        }
    ]
}
```

#### Hybrid scoping (factory + user)

```python
"measurements": {
    "superuser": [
        {
            "condition": "is_selected",
            "action": "filter_by",
            "params": {"scope_level": 1, "scope_type": "selected"}
        },
        {
            "condition": "is_owner",
            "action": "include"
        }
    ],
    "admin": [
        {
            "condition": "is_assigned",
            "action": "filter_by",
            "params": {"scope_level": 1, "scope_type": "accessible"}
        },
        {
            "condition": "is_owner",
            "action": "include"
        }
    ]
}
```

#### Pravidlo s 'when' podmienkami

```python
"cameras": {
    "admin": [
        {
            "condition": "is_assigned",
            "action": "filter_by",
            "params": {"scope_level": 1, "scope_type": "accessible"},
            "when": {
                "role": ["admin", "staff"],
                "table": ["cameras", "machines"]
            }
        }
    ]
}
```

## VIEWS_MATRIX Configuration

Konfigurácia v `VIEWS_MATRIX` definuje ownership hierarchiu a metadata.

### ownership_hierarchy

Definuje hierarchiu vlastníctva - zoznam field names v poradí od najnižšej úrovne (user) po najvyššiu (napr. location).

```python
"ownership_hierarchy": ["created_by", "factory_id", "location_id"]
```

Engine automaticky mapuje `scope_level` na field name:
- `scope_level: 0` → `created_by`
- `scope_level: 1` → `factory_id`
- `scope_level: 2` → `location_id`

### scope_level_metadata

Voliteľné metadata pre každý scope level (pre debugging a user-friendly názvy).

```python
"scope_level_metadata": {
    0: {"name": "User", "field": "created_by"},
    1: {"name": "Factory", "field": "factory_id"},
    2: {"name": "Location", "field": "location_id"}
}
```

Ak nie je definované, engine automaticky generuje metadata z `ownership_hierarchy`.

### Kompletný príklad

```python
VIEWS_MATRIX = {
    "cameras": {
        "table_name": "cameras",
        "ownership_hierarchy": ["created_by", "factory_id"],
        "scope_level_metadata": {
            0: {"name": "User", "field": "created_by"},
            1: {"name": "Factory", "field": "factory_id"}
        },
        # ... ďalšie konfigurácie
    }
}
```

## Settings Configuration

### Fallback Settings

```python
# settings.py

# Povoliť/zakázať fallback stratégie
SCOPING_FALLBACK_ENABLED = True

# Fallback úroveň: 'engine', 'simple', 'none'
SCOPING_FALLBACK_LEVEL = 'engine'
```

### Middleware Settings

```python
# Povoliť/zakázať middleware
SCOPING_MIDDLEWARE_ENABLED = False

# Zoznam tabuliek pre automatické scoping
SCOPING_MIDDLEWARE_TABLES = ['cameras', 'machines', 'measurements']
```

### Validation Settings

```python
# Validovať pravidlá pri štarte aplikácie
SCOPING_VALIDATE_ON_STARTUP = True

# Vyhodiť výnimku pri validation errors (nie len warnings)
SCOPING_RAISE_ON_VALIDATION_ERRORS = False
```

## Použitie Presetov

Presety poskytujú preddefinované konfigurácie pre bežné scoping patterny.

### Factory-scoped Preset

```python
from apps.scoping.presets import get_factory_scoped_preset

preset = get_factory_scoped_preset()
# Použi preset v SCOPING_RULES_MATRIX
SCOPING_RULES_MATRIX['mytable'] = preset
```

### User-scoped Preset

```python
from apps.scoping.presets import get_user_scoped_preset

preset = get_user_scoped_preset()
SCOPING_RULES_MATRIX['mytable'] = preset
```

### Hybrid Preset

```python
from apps.scoping.presets import get_hybrid_preset

preset = get_hybrid_preset()
SCOPING_RULES_MATRIX['mytable'] = preset
```

### Custom Preset

```python
from apps.scoping.presets import create_custom_preset

preset = create_custom_preset(
    scope_levels=[0, 1],  # User a Factory
    roles=['admin', 'staff', 'editor'],
    base_preset='hybrid'
)
SCOPING_RULES_MATRIX['mytable'] = preset
```

## Best Practices

### 1. Používajte abstraktné scope_level

Namiesto hardcode field names používajte `scope_level`:

```python
# ❌ Zlé
"params": {"field": "factory_id"}

# ✅ Správne
"params": {"scope_level": 1}
```

### 2. Definujte ownership_hierarchy

Vždy definujte `ownership_hierarchy` v `VIEWS_MATRIX`:

```python
"ownership_hierarchy": ["created_by", "factory_id", "location_id"]
```

### 3. Používajte presety pre bežné patterny

Namiesto manuálneho definovania pravidiel použite presety:

```python
from apps.scoping.presets import get_factory_scoped_preset

SCOPING_RULES_MATRIX['mytable'] = get_factory_scoped_preset()
```

### 4. Validujte pravidlá pri štarte

Zapnite validáciu v settings:

```python
SCOPING_VALIDATE_ON_STARTUP = True
```

### 5. Používajte fallback pre produkciu

Zapnite fallback pre graceful degradation:

```python
SCOPING_FALLBACK_ENABLED = True
SCOPING_FALLBACK_LEVEL = 'engine'
```

### 6. Monitorujte metriky

Pravidelne kontrolujte metriky výkonu:

```python
from apps.scoping.metrics import get_metrics

metrics = get_metrics()
print(f"Total executions: {metrics['total_executions']}")
print(f"Error rate: {metrics['error_rate']:.2%}")
```

## Troubleshooting

### Pravidlá sa neaplikujú

1. Skontrolujte, či je `should_use_scoping_engine(table_name)` True
2. Skontrolujte, či sú pravidlá definované v `SCOPING_RULES_MATRIX`
3. Skontrolujte, či je registry nakonfigurovaný
4. Skontrolujte logy pre chybové hlásenia

### Fallback sa aktivuje často

1. Skontrolujte, či registry callbacks fungujú správne
2. Skontrolujte metriky pre error rate
3. Skontrolujte logy pre konkrétne chyby

### Validácia zlyháva

1. Skontrolujte štruktúru pravidiel v `SCOPING_RULES_MATRIX`
2. Skontrolujte, či sú `scope_level` hodnoty platné pre `ownership_hierarchy`
3. Skontrolujte, či sú `condition` a `action` hodnoty platné

