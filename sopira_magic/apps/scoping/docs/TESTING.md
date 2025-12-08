# Testing Scoping Engine

Príručka pre testovanie Scoping Engine.

## Test Helpers

Scoping Engine poskytuje helper funkcie v `test_helpers.py` pre jednoduché testovanie.

### Mock Scope Owner

```python
from apps.scoping.test_helpers import create_mock_scope_owner

# Vytvor mock scope_owner
scope_owner = create_mock_scope_owner(role='admin', id='test-user-1')
```

### Mock Scope Provider

```python
from apps.scoping.test_helpers import create_mock_scope_provider

# Vytvor mock scope provider
scope_provider = create_mock_scope_provider({
    1: {  # scope_level 1 (Factory)
        'selected': ['factory-1', 'factory-2'],
        'accessible': ['factory-1', 'factory-2', 'factory-3']
    }
})
```

### Mock Role Provider

```python
from apps.scoping.test_helpers import create_mock_role_provider

# Vytvor mock role provider
role_provider = create_mock_role_provider({
    scope_owner1: 'admin',
    scope_owner2: 'reader'
})
```

### Mock Registry Context Manager

```python
from apps.scoping.test_helpers import with_mock_registry

# Použi mock registry v teste
with with_mock_registry(scope_provider, role_provider):
    # Test kód používajúci scoping engine
    queryset = ScopingEngine.apply_rules(...)
```

### Test Rule Creation

```python
from apps.scoping.test_helpers import create_test_rule

# Vytvor test pravidlo
rule = create_test_rule(
    condition='is_assigned',
    action='filter_by',
    scope_level=1,
    scope_type='accessible'
)
```

### Test Config Creation

```python
from apps.scoping.test_helpers import create_test_config

# Vytvor test ViewConfig
config = create_test_config(
    ownership_hierarchy=['created_by', 'factory_id'],
    scope_level_metadata={
        0: {'name': 'User', 'field': 'created_by'},
        1: {'name': 'Factory', 'field': 'factory_id'}
    }
)
```

### Assertion Helpers

```python
from apps.scoping.test_helpers import assert_scoping_result

# Over scoping výsledok
assert_scoping_result(
    queryset,
    expected_count=10,
    message="Should return 10 records"
)

# Alebo s rozsahom
assert_scoping_result(
    queryset,
    expected_min=5,
    expected_max=15,
    message="Should return 5-15 records"
)
```

## Unit Testy

### Základný test

```python
from django.test import TestCase
from apps.scoping.engine import ScopingEngine
from apps.scoping.test_helpers import (
    create_mock_scope_owner,
    create_mock_scope_provider,
    create_mock_role_provider,
    with_mock_registry,
    create_test_config,
    assert_scoping_result
)

class ScopingEngineTest(TestCase):
    def setUp(self):
        self.scope_owner = create_mock_scope_owner(role='admin')
        self.config = create_test_config(
            ownership_hierarchy=['created_by', 'factory_id']
        )
        
        # Vytvor mock providers
        self.scope_provider = create_mock_scope_provider({
            1: {
                'accessible': ['factory-1', 'factory-2']
            }
        })
        self.role_provider = create_mock_role_provider({
            self.scope_owner: 'admin'
        })
    
    def test_basic_scoping(self):
        # Vytvor test queryset
        queryset = MyModel.objects.all()
        
        # Aplikuj scoping s mock registry
        with with_mock_registry(self.scope_provider, self.role_provider):
            result = ScopingEngine.apply_rules(
                queryset,
                self.scope_owner,
                'mytable',
                self.config
            )
            
            # Over výsledok
            assert_scoping_result(
                result,
                expected_min=1,
                message="Should return at least 1 record"
            )
```

### Test s rôznymi rolami

```python
def test_different_roles(self):
    queryset = MyModel.objects.all()
    
    # Test pre admin
    admin_owner = create_mock_scope_owner(role='admin')
    admin_role_provider = create_mock_role_provider({admin_owner: 'admin'})
    
    with with_mock_registry(self.scope_provider, admin_role_provider):
        admin_result = ScopingEngine.apply_rules(
            queryset, admin_owner, 'mytable', self.config
        )
        assert_scoping_result(admin_result, expected_min=1)
    
    # Test pre reader
    reader_owner = create_mock_scope_owner(role='reader')
    reader_role_provider = create_mock_role_provider({reader_owner: 'reader'})
    
    with with_mock_registry(self.scope_provider, reader_role_provider):
        reader_result = ScopingEngine.apply_rules(
            queryset, reader_owner, 'mytable', self.config
        )
        # Reader môže mať iný počet záznamov
        assert_scoping_result(reader_result, expected_min=0)
```

### Test fallback stratégie

```python
from apps.scoping.fallback import apply_with_fallback, FALLBACK_SIMPLE

def test_fallback_on_error(self):
    queryset = MyModel.objects.all()
    
    # Vytvor provider, ktorý vyhodí chybu
    def failing_provider(*args):
        raise Exception("Provider failed")
    
    failing_role_provider = create_mock_role_provider({
        self.scope_owner: 'admin'
    })
    
    # Test fallback
    with with_mock_registry(failing_provider, failing_role_provider):
        result = apply_with_fallback(
            queryset,
            self.scope_owner,
            'mytable',
            self.config,
            fallback_level=FALLBACK_SIMPLE
        )
        
        # Fallback by mal vrátiť nejaké výsledky
        assert_scoping_result(result, expected_min=0)
```

## Integration Testy

### Test s reálnymi dátami

```python
class ScopingIntegrationTest(TestCase):
    def setUp(self):
        # Vytvor reálne test dáta
        self.factory1 = Factory.objects.create(name='Factory 1')
        self.factory2 = Factory.objects.create(name='Factory 2')
        
        self.user1 = User.objects.create(username='user1')
        self.user1.factories.add(self.factory1)
        
        self.user2 = User.objects.create(username='user2')
        self.user2.factories.add(self.factory2)
        
        # Vytvor objekty
        self.obj1 = MyModel.objects.create(
            factory=self.factory1,
            created_by=self.user1
        )
        self.obj2 = MyModel.objects.create(
            factory=self.factory2,
            created_by=self.user2
        )
    
    def test_scoping_with_real_data(self):
        queryset = MyModel.objects.all()
        config = VIEWS_MATRIX.get('mytable', {})
        
        # Aplikuj scoping pre user1
        result = ScopingEngine.apply_rules(
            queryset,
            self.user1,
            'mytable',
            config
        )
        
        # User1 by mal vidieť len obj1
        assert_scoping_result(result, expected_count=1)
        self.assertIn(self.obj1, result)
        self.assertNotIn(self.obj2, result)
```

### Test s rôznymi scope levels

```python
def test_multiple_scope_levels(self):
    # Vytvor hierarchiu: User -> Factory -> Location
    location1 = Location.objects.create(factory=self.factory1)
    location2 = Location.objects.create(factory=self.factory2)
    
    obj1 = MyModel.objects.create(
        factory=self.factory1,
        location=location1,
        created_by=self.user1
    )
    
    config = create_test_config(
        ownership_hierarchy=['created_by', 'factory_id', 'location_id']
    )
    
    queryset = MyModel.objects.all()
    
    # Test scoping na factory level
    result = ScopingEngine.apply_rules(
        queryset, self.user1, 'mytable', config
    )
    
    assert_scoping_result(result, expected_min=1)
```

## Performance Testy

### Test výkonu

```python
import time
from apps.scoping.metrics import get_metrics, reset_metrics

class ScopingPerformanceTest(TestCase):
    def setUp(self):
        # Vytvor veľké množstvo dát
        for i in range(1000):
            MyModel.objects.create(...)
    
    def test_scoping_performance(self):
        reset_metrics()
        
        queryset = MyModel.objects.all()
        config = VIEWS_MATRIX.get('mytable', {})
        
        start_time = time.time()
        
        for _ in range(100):
            ScopingEngine.apply_rules(
                queryset,
                self.user1,
                'mytable',
                config
            )
        
        duration = time.time() - start_time
        
        # Over, že výkon je prijateľný
        self.assertLess(duration, 1.0, "Scoping should be fast")
        
        # Skontroluj metriky
        metrics = get_metrics()
        self.assertEqual(metrics['total_executions'], 100)
```

## Thread-Safety Testy

### Test súbežného prístupu

```python
import threading
from apps.scoping.registry import register_scope_provider, register_role_provider

class ScopingThreadSafetyTest(TestCase):
    def test_concurrent_access(self):
        results = []
        errors = []
        
        def worker(worker_id):
            try:
                scope_owner = create_mock_scope_owner(id=f'user-{worker_id}')
                queryset = MyModel.objects.all()
                config = create_test_config(['created_by', 'factory_id'])
                
                result = ScopingEngine.apply_rules(
                    queryset, scope_owner, 'mytable', config
                )
                results.append(len(result))
            except Exception as e:
                errors.append(e)
        
        # Spusti viac workerov súbežne
        threads = []
        for i in range(10):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Počkaj na dokončenie
        for thread in threads:
            thread.join()
        
        # Over, že neboli žiadne chyby
        self.assertEqual(len(errors), 0, f"Errors: {errors}")
        self.assertEqual(len(results), 10)
```

## Best Practices

### 1. Používajte test helpers

Namiesto manuálneho vytvárania mock objektov použite helpers:

```python
# ❌ Zlé
mock_owner = Mock()
mock_owner.role = 'admin'

# ✅ Správne
mock_owner = create_mock_scope_owner(role='admin')
```

### 2. Izolujte testy

Každý test by mal byť nezávislý:

```python
def setUp(self):
    # Vytvor čisté test dáta pre každý test
    self.scope_owner = create_mock_scope_owner()
    self.config = create_test_config(['created_by', 'factory_id'])
```

### 3. Testujte edge cases

Testujte aj hraničné prípady:

```python
def test_empty_queryset(self):
    queryset = MyModel.objects.none()
    result = ScopingEngine.apply_rules(...)
    assert_scoping_result(result, expected_count=0)

def test_no_rules(self):
    # Test, keď nie sú definované pravidlá
    pass

def test_invalid_scope_level(self):
    # Test, keď scope_level je mimo rozsahu
    pass
```

### 4. Používajte assertion helpers

Namiesto manuálnych assertov použite helpers:

```python
# ❌ Zlé
self.assertEqual(queryset.count(), 10)

# ✅ Správne
assert_scoping_result(queryset, expected_count=10)
```

### 5. Testujte metriky

Overte, že metriky sa zaznamenávajú správne:

```python
from apps.scoping.metrics import reset_metrics, get_metrics

def test_metrics_recording(self):
    reset_metrics()
    
    ScopingEngine.apply_rules(...)
    
    metrics = get_metrics()
    self.assertEqual(metrics['total_executions'], 1)
```

## Debugging

### Zapnutie debug logov

```python
import logging

logging.getLogger('apps.scoping').setLevel(logging.DEBUG)
```

### Kontrola metrík

```python
from apps.scoping.metrics import get_metrics, export_metrics

# Získaj metriky
metrics = get_metrics()
print(f"Executions: {metrics['total_executions']}")
print(f"Errors: {metrics['total_errors']}")
print(f"Error rate: {metrics['error_rate']:.2%}")

# Export do textu
print(export_metrics(format='text'))
```

### Validácia pravidiel

```python
from apps.scoping.validation import validate_all

result = validate_all(VIEWS_MATRIX)
if result['errors']:
    print("Validation errors:")
    for error in result['errors']:
        print(f"  - {error}")
```

