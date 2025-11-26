# Relation App - Dynamic Relation Configuration

## Overview

Relation app provides config-driven, dynamic relation management between models. Models remain universal without hardcoded ForeignKey fields. All relations are defined in configuration and managed through the relation service.

## Architecture

### Components

1. **RELATION_CONFIG** (`config.py`) - SSOT for relation definitions
2. **RelationRegistry** (`models.py`) - Database storage for relations
3. **RelationInstance** (`models.py`) - Actual relation instances between objects
4. **RelationService** (`services.py`) - Dynamic query building and relation management
5. **Helpers** (`helpers.py`) - Convenience functions for common operations

## Usage

### Defining Relations

Relations are defined in `config.py`:

```python
RELATION_CONFIG = {
    'user_company': {
        'source': 'user.User',
        'target': 'company.Company',
        'type': 'ForeignKey',
        'field_name': 'user',
        'related_name': 'companies',
        'on_delete': 'PROTECT',
    },
}
```

### Initializing Relations

Run management command to populate RelationRegistry from config:

```bash
python manage.py init_relations
```

### Creating Relations

```python
from sopira_magic.apps.relation.helpers import create_user_company

user = User.objects.get(...)
company = Company.objects.create(...)

# Create relation
create_user_company(user, company)
```

### Querying Related Objects

```python
from sopira_magic.apps.relation.helpers import get_user_companies

user = User.objects.get(...)
companies = get_user_companies(user)  # Returns QuerySet of Company objects
```

### Building Queries

```python
from sopira_magic.apps.relation.helpers import query_companies_by_user

companies = query_companies_by_user(user_id)
```

## Current Relations

- `user_company`: User O2M Company
- `company_factory`: Company O2M Factory
- `factory_productionline`: Factory O2M ProductionLine

## Benefits

- **Universal Models**: No hardcoded ForeignKey fields
- **Config-Driven**: All relations defined in SSOT config
- **Dynamic Queries**: Build queries based on relation config
- **Scalable**: Add new relations without modifying models
- **Flexible**: Support for FK, M2M, O2O relation types

