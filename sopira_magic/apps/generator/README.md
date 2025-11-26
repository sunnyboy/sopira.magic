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
6. **Management Command** (`management/commands/generate_data.py`) - CLI for data generation

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

## Usage

### Via Management Command

```bash
# Generate seed data for all models
python manage.py generate_data --seed

# Generate data for specific model
python manage.py generate_data company --count 20

# Generate with user
python manage.py generate_data company --user sopira

# Clear existing data
python manage.py generate_data company --clear --keep 5
```

### Via Python Code

```python
from sopira_magic.apps.generator.services import GeneratorService

# Generate data for specific model
companies = GeneratorService.generate_data('company', count=10)

# Generate seed data for all models (respects dependencies)
results = GeneratorService.generate_seed_data()
```

## Relations

Relations are handled via relation app:

```python
'relations': {
    'user': {
        'type': 'random',  # or 'user'
        'model': 'user.User',
        'required': True,  # Create if doesn't exist
    },
}
```

## Current Generators

- `company`: Company model generator (uses business_name dataset)
- `factory`: Factory model generator  
- `productionline`: ProductionLine model generator

## Benefits

- **Universal**: Works with any model
- **Auto-Detection**: Automatically detects field types and adapts
- **Config-Driven**: All configs in SSOT
- **Range Support**: date_range, time_range, number_range, decimals, step
- **Dataset Support**: Predefined datasets for common values
- **Field-Aware**: Auto-generates based on field types
- **Relation-Aware**: Integrates with relation app
- **Dependency-Aware**: Generates in correct order
- **Extensible**: Easy to add new field types and datasets
