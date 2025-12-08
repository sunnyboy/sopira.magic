# Generator App - Universal Data Generator

## Overview

Generator app provides config-driven, universal data generation for any model. All generation logic is centralized in the generator app, following SSOT principles. **Auto-detects field types and adapts generated content accordingly.**

## Architecture

### Components

1. **GENERATOR_CONFIG** (`config.py`) - SSOT for generator definitions
2. **GeneratorConfig** (`models.py`) - Database storage for generator configs
3. **FieldGenerator** (`field_generators.py`) - Universal field value generators with auto-detection
4. **Datasets** (`datasets.py`) - Base datasets (business names, names, places, materials, etc.)
5. **GeneratorService** (`services.py`) - Universal data generation service
6. **Management Commands** (`management/commands/`) - CLI for data generation

## Field Type Auto-Detection

Generator automatically detects Django field types and adapts generated content:

- **CharField** → Random string
- **TextField** → Lorem Ipsum text
- **IntegerField** → Random integer (respects number_range, step)
- **DecimalField** → Random decimal (respects number_range, decimals, step)
- **BooleanField** → Random boolean
- **DateField** → Random date (respects date_range)
- **DateTimeField** → Random datetime (respects date_range)
- **TimeField** → Random time (respects time_range)
- **EmailField** → Email format
- **URLField** → URL format
- **UUIDField** → UUID
- **ForeignKey** → FK object (via `type: 'fk'`)

## Config Options

### Range Support

```python
'fields': {
    'price': {
        'number_range': {'min': 10.0, 'max': 1000.0},
        'decimals': 2,
        'step': 0.5,  # Generate values in 0.5 increments
    },
    'quantity': {
        'number_range': {'min': 1, 'max': 100},
        'step': 1,  # Integer step
    },
    'created_date': {
        'date_range': {
            'start': '2020-01-01',
            'end': '2024-12-31',
        },
    },
    'work_time': {
        'time_range': {
            'start': '08:00:00',
            'end': '17:00:00',
        },
    },
}
```

### Field Types

#### Template
```python
'code': {'type': 'template', 'template': 'COMP-{index:03d}'}
```

#### Copy from another field
```python
'human_id': {'type': 'copy', 'from': 'code'}
```

#### Lorem Ipsum
```python
'comment': {'type': 'lorem', 'words': 10}
```

#### Dataset (predefined values)
```python
'name': {'type': 'dataset', 'dataset': 'business_name'}
'first_name': {'type': 'dataset', 'dataset': 'first_name'}
'location': {'type': 'dataset', 'dataset': 'working_place'}
```

#### Random values
```python
'value': {
    'type': 'random',
    'field_type': 'integer',
    'number_range': {'min': 0, 'max': 100},
    'step': 5,
}
```

#### Static value
```python
'active': {'type': 'static', 'value': True}
```

#### Increment
```python
'order': {'type': 'increment', 'start': 1, 'step': 1}
```

## Available Datasets

### Business & Names
- `business_name` - Compound business name (3 words + company form)
- `first_name` - First name
- `last_name` - Last name
- `full_name` - Full name (first + last)

### Work & Resources
- `working_place` - Working place name
- `material` - Material name
- `resource` - Resource name
- `equipment` - Equipment name

### Contact Information
- `email` - Email address (supports first_name, last_name, domain params)
- `phone` / `phone_number` - Phone number (supports country param for format)
- `country` - Country name
- `city` - City name
- `street` - Street name
- `postal_code` / `zip` / `psc` - Postal code (supports country param for format)
- `address` / `full_address` - Full address string (supports country param, as_dict option)

## Dependency Management

Use `depends_on` to declare explicit dependencies between models:

```python
GENERATOR_CONFIG = {
    'user': {
        'model': 'user.User',
        'depends_on': [],  # No dependencies
    },
    'company': {
        'model': 'company.Company',
        'depends_on': ['user'],  # Generated after user
    },
    'factory': {
        'model': 'factory.Factory',
        'depends_on': ['company'],  # Generated after company
    },
    'location': {
        'model': 'location.Location',
        'depends_on': ['factory'],  # Generated after factory
    },
    'measurement': {
        'model': 'measurement.Measurement',
        'depends_on': ['factory', 'location', 'carrier', 'driver', 'pot'],
    },
}
```

The generator uses topological sort to ensure correct generation order.

## Usage

### Via Management Commands

```bash
# Clear all data (keeps users)
python manage.py clear_all_data --keep-users

# Clear all data (including users)
python manage.py clear_all_data

# Preview what would be deleted
python manage.py clear_all_data --dry-run

# Generate seed data for all models (respects depends_on)
python manage.py generate_all_data

# Generate data for specific model
python manage.py generate_data factory --count 20

# Generate with specific user for relations
python manage.py generate_data company --user sopira

# Clear specific model data
python manage.py generate_data company --clear --keep 5
```

### Via Python Code

```python
from sopira_magic.apps.generator.services import GeneratorService

# Generate data for specific model
factories = GeneratorService.generate_data('factory', count=10)

# Generate seed data for all models (respects depends_on)
results = GeneratorService.generate_seed_data()
# Returns: {'user': 5, 'company': 3, 'factory': 6, ...}

# Clear data for specific model
deleted = GeneratorService.clear_data('factory', keep_count=0)
```

## Relationships

Generator supports two types of relationships:

### 1. Direct FK Fields (Hardcoded FK in model)

Use `type: 'fk'` in `fields` config for models with explicit ForeignKey fields:

```python
'factory': {
    'model': 'factory.Factory',
    'depends_on': ['company'],  # Explicit dependency declaration
    'fields': {
        'code': {'type': 'template', 'template': 'FAC-{index:03d}'},
        'name': {'type': 'template', 'template': 'Factory {index}'},
        # FK field - selects from existing Company objects
        'company': {
            'type': 'fk',
            'model': 'company.Company',
            'strategy': 'round_robin',  # or 'random'
            'nullable': False,  # optional, default False
            'filter': {'active': True},  # optional queryset filter
        },
    },
}
```

**FK Strategies:**
- `random` - Randomly selects from existing objects
- `round_robin` - Distributes evenly across objects (index % count)
- `from_context` - Uses value from generation context

### 2. Dynamic Relations (via RelationService)

Use `relations` config for flexible relationships managed by the `relation` app:

```python
'company': {
    'model': 'company.Company',
    'fields': {...},
'relations': {
    'user': {
            'type': 'random',  # or 'user', 'per_source'
        'model': 'user.User',
        'required': True,  # Create if doesn't exist
        },
    },
}
```

**Relation Types:**
- `random` - Assigns random existing object
- `user` - Uses provided user or first user
- `per_source` - Creates N objects per source (guaranteed coverage)

### Choosing Between FK and Relations

| Aspect | FK (`type: 'fk'`) | Relations (`relations`) |
|--------|-------------------|-------------------------|
| Use when | Model has explicit ForeignKey | Flexible/dynamic relationships |
| Storage | Direct FK in model | RelationInstance table |
| Performance | Faster (direct join) | Flexible but slower |
| Example | Factory → Company | User ↔ Company M2M |

**Both can coexist in the same config!**

## Current Generators

| Key | Model | Count | FK Dependencies |
|-----|-------|-------|-----------------|
| `user` | User | 5 | - |
| `company` | Company | 3 | - |
| `factory` | Factory | 6 | company |
| `location` | Location | 12 | factory |
| `carrier` | Carrier | 12 | factory |
| `driver` | Driver | 18 | factory |
| `pot` | Pot | 24 | factory |
| `pit` | Pit | 12 | factory, location? |
| `machine` | Machine | 6 | factory |
| `camera` | Camera | 12 | factory, location? |
| `measurement` | Measurement | 50 | factory, location, carrier, driver, pot, pit?, machine? |
| `photo` | Photo | 100 | measurement |
| `video` | Video | 50 | measurement |

## Benefits

- **Universal**: Works with any model
- **Auto-Detection**: Automatically detects field types and adapts
- **Config-Driven**: All configs in SSOT (GENERATOR_CONFIG)
- **Range Support**: date_range, time_range, number_range, decimals, step
- **Dataset Support**: Predefined datasets for common values
- **Field-Aware**: Auto-generates based on field types
- **FK Support**: Direct ForeignKey field generation with strategies
- **Relation-Aware**: Integrates with relation app for dynamic relations
- **Dependency-Aware**: Uses `depends_on` for correct generation order
- **Extensible**: Easy to add new field types and datasets
- **CLI Tools**: `generate_all_data`, `clear_all_data`, `generate_data` commands
