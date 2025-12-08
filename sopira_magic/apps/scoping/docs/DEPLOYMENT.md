# Scoping Engine Deployment Guide

Best practices a troubleshooting pre produkčné nasadenie Scoping Engine.

## Best Practices

### 1. Validácia pri štarte

Vždy zapnite validáciu pravidiel pri štarte aplikácie:

```python
# settings.py
SCOPING_VALIDATE_ON_STARTUP = True
SCOPING_RAISE_ON_VALIDATION_ERRORS = False  # V dev, True v production
```

Toto zabráni runtime chybám spôsobeným neplatnými pravidlami.

### 2. Fallback stratégie

Zapnite fallback pre graceful degradation:

```python
# settings.py
SCOPING_FALLBACK_ENABLED = True
SCOPING_FALLBACK_LEVEL = 'engine'  # 'engine', 'simple', 'none'
```

Ak scoping engine zlyhá, aplikácia automaticky prepne na jednoduchší filter alebo unfiltered queryset.

### 3. Monitoring a metriky

Pravidelne monitorujte metriky výkonu:

```python
from apps.scoping.metrics import get_metrics, export_metrics

# Získaj metriky
metrics = get_metrics()

# Kontrola error rate
if metrics['error_rate'] > 0.01:  # Viac ako 1% chýb
    logger.warning(f"High error rate: {metrics['error_rate']:.2%}")

# Kontrola výkonu
for (table, role), avg_duration in metrics['avg_durations'].items():
    if avg_duration > 0.1:  # Viac ako 100ms
        logger.warning(f"Slow scoping for {table}/{role}: {avg_duration*1000:.2f}ms")
```

### 4. Thread-Safety

Registry je thread-safe, ale uistite sa, že callbacks sú tiež thread-safe:

```python
# ✅ Správne - thread-safe callback
def get_scope_values(scope_level, scope_owner, scope_type, request):
    # Použi request-level cache
    cache_key = f'scope_{scope_level}_{scope_owner.id}_{scope_type}'
    if hasattr(request, '_scope_cache'):
        if cache_key in request._scope_cache:
            return request._scope_cache[cache_key]
    
    values = compute_scope_values(...)
    
    if hasattr(request, '_scope_cache'):
        request._scope_cache[cache_key] = values
    
    return values
```

### 5. Caching

Používajte request-level cache pre scope values:

```python
def get_scope_values(scope_level, scope_owner, scope_type, request):
    if request is None:
        return compute_scope_values(...)
    
    # Request-level cache
    cache_key = f'scope_{scope_level}_{scope_owner.id}_{scope_type}'
    if not hasattr(request, '_scope_cache'):
        request._scope_cache = {}
    
    if cache_key in request._scope_cache:
        return request._scope_cache[cache_key]
    
    values = compute_scope_values(...)
    request._scope_cache[cache_key] = values
    return values
```

### 6. Registry Setup

Registrujte callbacks v `apps.py` alebo v `ready()` metóde:

```python
# measurement/apps.py
from django.apps import AppConfig

class MeasurementConfig(AppConfig):
    def ready(self):
        from apps.scoping.registry import register_scope_provider, register_role_provider
        from .api.scoping_adapter import get_scope_values, get_role
        
        register_scope_provider(get_scope_values)
        register_role_provider(get_role)
```

### 7. Export/Import pravidiel

Pravidelne exportujte pravidlá pre backup:

```bash
# Export
python manage.py scoping_export_rules --format json --output rules_backup.json

# Import (v prípade potreby)
python manage.py scoping_import_rules rules_backup.json
```

### 8. Logging

Nastavte vhodné logovacie úrovne:

```python
# settings.py
LOGGING = {
    'loggers': {
        'apps.scoping': {
            'level': 'INFO',  # V production
            # 'level': 'DEBUG',  # V development
        }
    }
}
```

## Monitoring

### Metriky

Scoping Engine automaticky zaznamenáva metriky:

- **executions** - Počet vykonaní per table/role
- **avg_durations** - Priemerný čas spracovania
- **errors** - Počet chýb
- **cache_hit_rates** - Cache hit rate
- **error_rate** - Celková error rate

### Export metrík

```python
from apps.scoping.metrics import export_metrics

# Export do JSON
json_metrics = export_metrics(format='json')

# Export do textu (pre logy)
text_metrics = export_metrics(format='text')
print(text_metrics)
```

### Monitoring Endpoint (voliteľné)

Môžete vytvoriť API endpoint pre monitoring:

```python
from django.http import JsonResponse
from apps.scoping.metrics import get_metrics

def scoping_metrics_view(request):
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    metrics = get_metrics()
    return JsonResponse(metrics)
```

## Troubleshooting

### Pravidlá sa neaplikujú

**Príznaky:**
- Všetky záznamy sú viditeľné bez ohľadu na scoping
- Scoping engine sa nevolá

**Riešenie:**
1. Skontrolujte, či je `should_use_scoping_engine(table_name)` True
2. Skontrolujte feature flags v `rules.py`
3. Skontrolujte, či sú pravidlá definované v `SCOPING_RULES_MATRIX`
4. Skontrolujte logy pre debug správy

```python
# Debug
from apps.scoping.rules import should_use_scoping_engine, get_scoping_rules

print(f"Should use engine: {should_use_scoping_engine('mytable')}")
print(f"Rules: {get_scoping_rules('mytable', 'admin')}")
```

### Fallback sa aktivuje často

**Príznaky:**
- V logoch sa objavujú správy o fallback
- Error rate je vysoký

**Riešenie:**
1. Skontrolujte registry callbacks - musia byť registrované
2. Skontrolujte, či callbacks fungujú správne
3. Skontrolujte metriky pre konkrétne chyby

```python
# Debug registry
from apps.scoping.registry import is_registry_configured

print(f"Registry configured: {is_registry_configured()}")

# Test callbacks
from apps.scoping.registry import get_scope_values, get_scope_owner_role

try:
    values = get_scope_values(1, user, 'accessible', request)
    print(f"Scope values: {values}")
except Exception as e:
    print(f"Error: {e}")
```

### Validácia zlyháva

**Príznaky:**
- Aplikácia sa nespustí alebo vyhodí výnimku
- Validation errors v logoch

**Riešenie:**
1. Skontrolujte štruktúru pravidiel v `SCOPING_RULES_MATRIX`
2. Skontrolujte, či sú `scope_level` hodnoty platné pre `ownership_hierarchy`
3. Skontrolujte, či sú `condition` a `action` hodnoty platné

```python
# Debug validácie
from apps.scoping.validation import validate_all

result = validate_all(VIEWS_MATRIX)
if result['errors']:
    for error in result['errors']:
        print(f"Error: {error}")
```

### Pomalý výkon

**Príznaky:**
- Scoping trvá dlho
- Vysoký avg_duration v metrikách

**Riešenie:**
1. Použite request-level cache pre scope values
2. Optimalizujte registry callbacks
3. Skontrolujte, či nie sú zbytočné DB queries

```python
# Debug výkonu
from apps.scoping.metrics import get_metrics

metrics = get_metrics()
for (table, role), avg_duration in metrics['avg_durations'].items():
    if avg_duration > 0.1:
        print(f"Slow: {table}/{role} - {avg_duration*1000:.2f}ms")
```

### Thread-safety problémy

**Príznaky:**
- Nekonzistentné výsledky
- Race conditions

**Riešenie:**
1. Uistite sa, že registry callbacks sú thread-safe
2. Použite request-level cache namiesto globálneho cache
3. Skontrolujte, či nie sú shared mutable state v callbacks

### Scope values sa neaktualizujú

**Príznaky:**
- Staré hodnoty v scope
- Zmeny sa neprejavia

**Riešenie:**
1. Skontrolujte cache invalidation
2. Uistite sa, že request-level cache sa používa správne
3. Skontrolujte, či callbacks vracajú aktuálne hodnoty

## Migration Guide

### Migrácia z starého systému

1. **Definujte ownership_hierarchy** v `VIEWS_MATRIX`:

```python
"ownership_hierarchy": ["created_by", "factory_id"]
```

2. **Definujte pravidlá** v `SCOPING_RULES_MATRIX`:

```python
"mytable": {
    "admin": [
        {
            "condition": "is_assigned",
            "action": "filter_by",
            "params": {"scope_level": 1, "scope_type": "accessible"}
        }
    ]
}
```

3. **Registrujte callbacks**:

```python
from apps.scoping.registry import register_scope_provider, register_role_provider

register_scope_provider(get_scope_values)
register_role_provider(get_role)
```

4. **Zapnite feature flag**:

```python
# rules.py
USE_SCOPING_ENGINE_FOR_MYTABLE = True
```

5. **Testujte** v development prostredí

6. **Monitorujte** metriky po nasadení

### Postupná migrácia

1. Začnite s jednou tabuľkou (pilot)
2. Monitorujte metriky a chyby
3. Postupne migrujte ďalšie tabuľky
4. Po úspešnej migrácii všetkých tabuliek odstráňte starý systém

## Performance Optimalizácia

### 1. Request-Level Cache

Vždy používajte request-level cache pre scope values:

```python
def get_scope_values(scope_level, scope_owner, scope_type, request):
    if request is None:
        return compute_scope_values(...)
    
    cache_key = f'scope_{scope_level}_{scope_owner.id}_{scope_type}'
    if not hasattr(request, '_scope_cache'):
        request._scope_cache = {}
    
    if cache_key in request._scope_cache:
        return request._scope_cache[cache_key]
    
    values = compute_scope_values(...)
    request._scope_cache[cache_key] = values
    return values
```

### 2. Optimalizácia DB Queries

Optimalizujte registry callbacks:

```python
# ✅ Správne - batch query
def get_scope_values(scope_level, scope_owner, scope_type, request):
    # Načítaj všetky hodnoty naraz
    all_values = get_all_accessible_values(scope_owner, scope_level)
    return filter_by_type(all_values, scope_type)

# ❌ Zlé - N+1 queries
def get_scope_values(scope_level, scope_owner, scope_type, request):
    values = []
    for item in get_items(scope_owner):
        if check_access(item, scope_type):
            values.append(item.id)
    return values
```

### 3. Indexy v databáze

Uistite sa, že máte indexy na scope fields:

```python
# models.py
class MyModel(models.Model):
    factory = models.ForeignKey(Factory, db_index=True)
    created_by = models.ForeignKey(User, db_index=True)
```

## Security Considerations

### 1. Validácia pravidiel

Vždy validujte pravidlá pri štarte:

```python
SCOPING_VALIDATE_ON_STARTUP = True
SCOPING_RAISE_ON_VALIDATION_ERRORS = True  # V production
```

### 2. Registry Callbacks

Uistite sa, že registry callbacks správne kontrolujú oprávnenia:

```python
def get_scope_values(scope_level, scope_owner, scope_type, request):
    # Vždy kontroluj oprávnenia
    if not has_permission(scope_owner, scope_level):
        return []
    
    return compute_scope_values(...)
```

### 3. Fallback Security

Fallback bez filtrovania (`FALLBACK_NONE`) by mal byť používaný len pre superuser:

```python
def no_filter_fallback(queryset):
    # V production by mal byť používaný len pre superuser
    logger.warning("Using no-filter fallback")
    return queryset
```

## Checklist pre Deployment

- [ ] Registry callbacks sú registrované
- [ ] Validácia pravidiel je zapnutá
- [ ] Fallback stratégie sú nakonfigurované
- [ ] Monitoring je nastavený
- [ ] Logging je nakonfigurovaný
- [ ] Request-level cache je implementovaný
- [ ] DB indexy sú vytvorené
- [ ] Testy prechádzajú
- [ ] Dokumentácia je aktualizovaná
- [ ] Backup pravidiel je vytvorený

