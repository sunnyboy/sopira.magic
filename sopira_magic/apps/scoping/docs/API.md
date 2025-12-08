# Scoping Engine API Reference

Kompletná API dokumentácia pre Scoping Engine.

## ScopingEngine

Hlavná trieda pre aplikovanie scoping pravidiel.

### `apply_rules`

Aplikuje scoping pravidlá na queryset.

```python
@classmethod
def apply_rules(
    cls,
    queryset: QuerySet,
    scope_owner: Any,
    table_name: str,
    config: Dict[str, Any],
    request=None,
    use_metrics: bool = True,
    use_fallback: bool = True,
) -> QuerySet
```

**Parametre:**
- `queryset` - Django QuerySet na filtrovanie
- `scope_owner` - Abstraktný objekt reprezentujúci vlastníka scope (napr. User)
- `table_name` - Názov tabuľky (napr. 'cameras', 'machines')
- `config` - ViewConfig z VIEWS_MATRIX
- `request` - Optional Django request object pre caching
- `use_metrics` - Ak True, zaznamená metriky (default: True)
- `use_fallback` - Ak True, použije fallback stratégie pri chybách (default: True)

**Returns:**
- Filtered QuerySet

**Príklad:**
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

### `get_scope_level_metadata`

Generuje metadata pre každý scope level pre debugging.

```python
@staticmethod
def get_scope_level_metadata(config: Dict[str, Any]) -> Dict[int, Dict[str, str]]
```

**Parametre:**
- `config` - ViewConfig z VIEWS_MATRIX

**Returns:**
- Dict mapujúci scope_level na metadata s user-friendly názvami

**Príklad:**
```python
metadata = ScopingEngine.get_scope_level_metadata(config)
# {0: {"name": "User", "field": "created_by"}, 1: {"name": "Factory", "field": "factory_id"}}
```

## Registry API

Thread-safe registry pre callbacks.

### `register_scope_provider`

Registruje callback funkciu pre získanie scope hodnôt.

```python
def register_scope_provider(
    callback: Callable[[int, Any, ScopeType, Optional[object]], List[str]]
)
```

**Parametre:**
- `callback` - Funkcia `(scope_level, scope_owner, scope_type, request) -> List[str]`

**Príklad:**
```python
from apps.scoping.registry import register_scope_provider

def get_scope_values(scope_level, scope_owner, scope_type, request):
    # Vráť zoznam hodnôt pre daný scope_level a scope_type
    if scope_level == 1:  # Factory level
        return ['factory-id-1', 'factory-id-2']
    return []

register_scope_provider(get_scope_values)
```

### `register_role_provider`

Registruje callback funkciu pre získanie role scope_owner.

```python
def register_role_provider(callback: Callable[[Any], str])
```

**Parametre:**
- `callback` - Funkcia `(scope_owner) -> str`

**Príklad:**
```python
from apps.scoping.registry import register_role_provider

def get_role(scope_owner):
    if scope_owner.is_superuser:
        return 'superuser'
    return scope_owner.role

register_role_provider(get_role)
```

### `get_scope_values`

Vráti zoznam hodnôt pre daný scope_level a scope_type.

```python
def get_scope_values(
    scope_level: int,
    scope_owner: Any,
    scope_type: ScopeType,
    request=None
) -> List[str]
```

**Parametre:**
- `scope_level` - Abstraktná úroveň scope (0, 1, 2...)
- `scope_owner` - Abstraktný objekt reprezentujúci vlastníka scope
- `scope_type` - 'selected' alebo 'accessible'
- `request` - Optional Django request object pre caching

**Returns:**
- List[str] - zoznam hodnôt (UUIDs/IDs)

### `get_scope_owner_role`

Vráti role scope_owner.

```python
def get_scope_owner_role(scope_owner: Any) -> str
```

**Parametre:**
- `scope_owner` - Abstraktný objekt reprezentujúci vlastníka scope

**Returns:**
- str - role ('superuser', 'admin', 'staff', 'editor', 'reader', 'adhoc')

### `is_registry_configured`

Kontroluje, či sú registry callbacks nakonfigurované.

```python
def is_registry_configured() -> bool
```

**Returns:**
- bool - True ak sú oba callbacks registrované

## Validation API

Validácia scoping pravidiel.

### `validate_scoping_rules_matrix`

Validuje celú SCOPING_RULES_MATRIX.

```python
def validate_scoping_rules_matrix() -> List[str]
```

**Returns:**
- List[str] - zoznam chybových hlásení (prázdny ak nie sú chyby)

### `validate_rule`

Validuje jedno scoping pravidlo.

```python
def validate_rule(
    rule: Dict[str, Any],
    table_name: str,
    role: str,
    rule_index: int = 0
) -> List[str]
```

**Returns:**
- List[str] - zoznam chybových hlásení

### `validate_all`

Kompletná validácia všetkých scoping pravidiel a konfigurácií.

```python
def validate_all(
    view_configs: Optional[Dict[str, Dict[str, Any]]] = None
) -> Dict[str, List[str]]
```

**Returns:**
- Dict s kľúčmi 'errors' a 'warnings'

### `validate_and_raise`

Validuje všetko a vyhodí výnimku pri chybách.

```python
def validate_and_raise(
    view_configs: Optional[Dict[str, Dict[str, Any]]] = None,
    raise_on_warnings: bool = False
)
```

**Raises:**
- `ScopingValidationError` - Ak sú chyby alebo (ak raise_on_warnings=True) warnings

## Metrics API

Monitoring a metriky pre scoping engine.

### `record_scoping_execution`

Zaznamená vykonanie scoping engine.

```python
def record_scoping_execution(
    table_name: str,
    role: str,
    duration: float,
    success: bool = True,
    cache_hit: bool = False
)
```

### `get_metrics`

Vráti aktuálne metriky.

```python
def get_metrics() -> Dict[str, Any]
```

**Returns:**
- Dict s metrikami:
  - `executions` - Dict[(table, role)] -> count
  - `avg_durations` - Dict[(table, role)] -> avg_duration
  - `errors` - Dict[(table, role)] -> error_count
  - `cache_hit_rates` - Dict[(table, role)] -> hit_rate (0-1)
  - `total_executions` - int
  - `total_errors` - int
  - `error_rate` - float
  - `uptime_seconds` - float
  - `start_time` - str (ISO format)

### `reset_metrics`

Resetuje všetky metriky.

```python
def reset_metrics()
```

### `export_metrics`

Exportuje metriky v zadanom formáte.

```python
def export_metrics(format: str = 'json') -> str
```

**Parametre:**
- `format` - 'json' alebo 'text'

**Returns:**
- String reprezentácia metrík

### `ScopingMetricsContext`

Context manager pre automatické zaznamenávanie metrík.

```python
with ScopingMetricsContext(table_name, role) as metrics:
    # Scoping operácie
    metrics.cache_hit = True  # Optional
    pass
```

## Fallback API

Fallback stratégie pre graceful degradation.

### `apply_with_fallback`

Aplikuje scoping s fallback stratégiou.

```python
def apply_with_fallback(
    queryset: QuerySet,
    scope_owner: Any,
    table_name: str,
    config: Dict[str, Any],
    request=None,
    fallback_level: Optional[str] = None,
    use_metrics: bool = True
) -> QuerySet
```

**Parametre:**
- `queryset` - Django QuerySet
- `scope_owner` - Abstraktný objekt reprezentujúci vlastníka scope
- `table_name` - Názov tabuľky
- `config` - ViewConfig z VIEWS_MATRIX
- `request` - Optional Django request object
- `fallback_level` - Optional fallback level override ('engine', 'simple', 'none')
- `use_metrics` - Ak True, zaznamená metriky

**Returns:**
- Filtered QuerySet

### `simple_fallback_filter`

Jednoduchý fallback filter - základné scoping bez pravidiel.

```python
def simple_fallback_filter(
    queryset: QuerySet,
    scope_owner: Any,
    config: Dict[str, Any]
) -> QuerySet
```

### `no_filter_fallback`

Fallback bez filtrovania - vráti unfiltered queryset.

```python
def no_filter_fallback(queryset: QuerySet) -> QuerySet
```

### `should_use_fallback`

Kontroluje, či by sa mal použiť fallback.

```python
def should_use_fallback() -> bool
```

## Decorators API

Decorators pre automatické aplikovanie scoping.

### `@apply_scoping`

Decorator pre automatické aplikovanie scoping na view funkciu.

```python
@apply_scoping(table_name: str, config: Optional[Dict[str, Any]] = None, use_fallback: bool = True)
```

**Príklad:**
```python
from apps.scoping.decorators import apply_scoping

@apply_scoping('locations')
def my_view(request):
    queryset = Location.objects.all()
    # Scoping je automaticky aplikovaný
    return queryset
```

### `@scoping_context`

Decorator pre pridanie scoping kontextu do response.

```python
@scoping_context(table_name: str)
```

**Príklad:**
```python
from apps.scoping.decorators import scoping_context

@scoping_context('locations')
def my_view(request):
    # Response bude obsahovať scoping kontext
    return Response(...)
```

## Presets API

Preddefinované konfigurácie pre bežné scoping patterny.

### `get_factory_scoped_preset`

Vráti factory-scoped preset pravidiel.

```python
def get_factory_scoped_preset() -> Dict[str, List[ScopingRule]]
```

### `get_user_scoped_preset`

Vráti user-scoped preset pravidiel.

```python
def get_user_scoped_preset() -> Dict[str, List[ScopingRule]]
```

### `get_global_preset`

Vráti global preset pravidiel (žiadne scoping).

```python
def get_global_preset() -> Dict[str, List[ScopingRule]]
```

### `get_hybrid_preset`

Vráti hybrid preset pravidiel (kombinácia factory a user scoping).

```python
def get_hybrid_preset() -> Dict[str, List[ScopingRule]]
```

### `create_custom_preset`

Vytvorí custom preset podľa zadaných parametrov.

```python
def create_custom_preset(
    scope_levels: List[int],
    roles: List[UserRole],
    base_preset: Optional[str] = None
) -> Dict[str, List[ScopingRule]]
```

## Serialization API

Export/Import scoping pravidiel.

### `export_rules`

Exportuje scoping pravidlá do súboru alebo stringu.

```python
def export_rules(
    format: str = 'json',
    output_file: Optional[str] = None
) -> str
```

**Parametre:**
- `format` - 'json' alebo 'yaml'
- `output_file` - Optional cesta k výstupnému súboru (ak None, vráti string)

**Returns:**
- str - serializované pravidlá (ak output_file je None)

### `import_rules`

Importuje scoping pravidlá zo súboru.

```python
def import_rules(
    input_file: str,
    validate: bool = True,
    merge: bool = False
) -> Dict[str, Any]
```

**Returns:**
- Dict s výsledkom importu:
  - `success` - bool
  - `imported_rules` - Dict s importovanými pravidlami
  - `errors` - List[str] s chybami
  - `version` - str verzia importovaných pravidiel

### `get_rules_version`

Vráti verziu pravidiel (hash).

```python
def get_rules_version() -> str
```

**Returns:**
- str - SHA256 hash pravidiel (prvých 16 znakov)

### `validate_imported_rules`

Validuje importované pravidlá.

```python
def validate_imported_rules(rules: Dict[str, Any]) -> list
```

**Returns:**
- List[str] - zoznam chybových hlásení

## Management Commands

### `scoping_export_rules`

Exportuje scoping pravidlá do JSON/YAML.

```bash
python manage.py scoping_export_rules --format json --output rules.json
```

### `scoping_import_rules`

Importuje scoping pravidlá z JSON/YAML.

```bash
python manage.py scoping_import_rules rules.json --merge
```

## Middleware

### `ScopingMiddleware`

Django middleware pre automatické aplikovanie scoping.

**Settings:**
- `SCOPING_MIDDLEWARE_ENABLED` - enable/disable middleware
- `SCOPING_MIDDLEWARE_TABLES` - zoznam tabuliek pre automatické scoping

### `ScopingViewSetMixin`

Mixin pre ViewSet pre automatické aplikovanie scoping.

```python
from apps.scoping.middleware import ScopingViewSetMixin

class MyViewSet(ScopingViewSetMixin, ModelViewSet):
    queryset = Location.objects.all()
    # Scoping je automaticky aplikovaný v get_queryset
```

