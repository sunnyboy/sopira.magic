# Cieľová architektúra Sopira.magic (BE+FE, 1:1 štruktúra, Shared Infra)

## Prehľad

Tento dokument definuje **cieľovú architektúru** sopira.magic po migrácii z Thermal Eye. Architektúra je striktne **ConfigDriven & SSOT** s **1:1 zrkadlením štruktúry** medzi backendom a frontendom.

## Architektonické princípy

### 1. ConfigDriven & SSOT

- **Žiadny hardcode** v generických vrstvách
- **Deklaratívna konfigurácia** namiesto imperatívnej logiky
- **Single Source of Truth** pre všetky konfigurácie
- **Automatické generovanie** z konfigurácie

### 2. 1:1 Zrkadlenie BE ↔ FE

- **Per-model moduly**: Každý backend model má zodpovedajúci frontend modul
- **Rovnaké názvy**: Backend `m_factory` → Frontend `apps/factory`
- **Rovnaká štruktúra**: Backend `models.py`, `serializers.py`, `views.py` → Frontend `types.ts`, `hooks.ts`, `components.tsx`

### 3. Modular Monolith

- **Microservices-like apps**: Každý domain má vlastnú Django app
- **Shared infra**: Cross-cutting concerns v shared moduloch
- **Plugin systém**: Nové moduly sa pridávajú ako samostatné apps

## Backend architektúra

### Adresárová štruktúra

```
sopira_magic/
├── sopira_magic/              # Django project settings
│   ├── settings.py
│   ├── urls.py
│   ├── security_config.py
│   └── db_router.py
│
├── config/                    # SSOT konfigurácia (NOVÉ)
│   └── model_metadata.py     # Centrálny SSOT pre všetky modely
│
└── apps/                      # All Django apps
    ├── core/                  # Base models
    ├── shared/                # Shared utilities
    ├── security/              # Security middleware
    │
    ├── m_user/                # User management
    ├── authentification/      # Authentication
    │
    ├── m_factory/             # Factory (migrované z Thermal Eye)
    ├── m_location/            # Location (NOVÉ)
    ├── m_carrier/             # Carrier (NOVÉ)
    ├── m_driver/              # Driver (NOVÉ)
    ├── m_pot/                 # Pot (NOVÉ)
    ├── m_pit/                 # Pit (NOVÉ)
    ├── m_machine/             # Machine (NOVÉ)
    ├── m_camera/              # Camera (NOVÉ)
    ├── m_measurement/         # Measurement (NOVÉ)
    ├── m_tag/                 # Tag (migrované z Thermal Eye)
    ├── m_photo/               # Photo (migrované z Thermal Eye)
    ├── m_video/               # Video (migrované z Thermal Eye)
    │
    ├── api/                   # API Gateway (config-driven)
    │   ├── view_configs.py   # VIEWS_MATRIX (SSOT)
    │   ├── view_factory.py    # MyView factory
    │   ├── serializers.py     # MySerializer factory
    │   ├── models.py          # FKOptionsCache model
    │   └── views/
    │       ├── metadata.py    # Model metadata endpoint
    │       └── fk_cache.py    # FK cache endpoints
    │
    ├── relation/              # Dynamic relation registry (SSOT)
    ├── scoping/               # Scoping engine
    ├── state/                 # Table state persistence
    ├── generator/             # Data generation (SSOT)
    └── ... (ostatné apps)
```

### Per-Model App Štruktúra

Každý `m_*` modul má rovnakú štruktúru:

```
m_factory/
├── __init__.py
├── apps.py
├── admin.py
├── models.py              # Factory model (extends NamedWithCodeModel)
├── serializers.py         # Factory serializer (MySerializer.create_serializer())
├── views.py               # Factory viewset (MyView.create_viewset())
├── filters.py             # Factory filter set
├── urls.py                # Factory URL routing
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_serializers.py
│   └── test_views.py
└── migrations/
```

### SSOT Konfigurácia

#### 1. VIEWS_MATRIX (`api/view_configs.py`)

SSOT pre všetky API viewsety:

```python
VIEWS_MATRIX: Dict[str, ViewConfig] = {
    "factories": {
        "model": Factory,
        "serializer_read": None,  # Uses MySerializer.create_serializer()
        "serializer_write": None,
        "base_filters": {"active": True},
        "ownership_field": "id",
        "ownership_hierarchy": ["created_by", "id"],
        "scope_level_metadata": {
            0: {"name": "User", "field": "created_by"},
            1: {"name": "Factory", "field": "id"},
        },
        "search_fields": ["name", "code", "address"],
        "filter_class": FactoryFilter,
        "ordering_fields": "__all__",
        "default_ordering": ["name"],
        "soft_delete": True,
        "factory_scoped": True,
        "dynamic_search": True,
        "table_name": "factories",
        "fk_display_template": "{code}-{human_id}-{name}",
        "fk_fields": {
            "factory": "factories",
        },
        "before_create": auto_assign_factory_owner,
    },
    # ... všetky modely
}
```

#### 2. Model Metadata (`config/model_metadata.py`)

SSOT pre modelové metadáta (endpoints, ordering, ownership):

```python
# Automaticky generované z VIEWS_MATRIX
def get_model_metadata():
    """
    Return model metadata from VIEWS_MATRIX.
    Used by /api/models/metadata/ endpoint.
    """
    metadata = {}
    for view_name, config in VIEWS_MATRIX.items():
        model = config['model']
        metadata[view_name] = {
            "model": model.__name__,
            "singular": model._meta.verbose_name,
            "plural": model._meta.verbose_name_plural,
            "endpoint": f"/api/{view_name}/",
            "default_ordering": config.get('default_ordering', []),
            "ownership_field": config.get('ownership_field'),
        }
    return metadata
```

#### 3. Relation Registry (`relation/config.py`)

SSOT pre všetky väzby medzi modelmi:

```python
RELATION_REGISTRY = {
    "factory_user": {
        "source_model": "m_factory.Factory",
        "target_model": "m_user.User",
        "relation_type": "many_to_one",
        "field_name": "created_by",
    },
    "location_factory": {
        "source_model": "m_location.Location",
        "target_model": "m_factory.Factory",
        "relation_type": "many_to_one",
        "field_name": "factory",
    },
    # ... všetky väzby
}
```

### Config-Driven API

#### MyView Factory (`api/view_factory.py`)

```python
class MyView(ModelViewSet):
    """
    Universal ViewSet factory - generates viewsets from VIEWS_MATRIX.
    """
    
    @classmethod
    def create_viewset(cls, view_name: str) -> Type['MyView']:
        """
        Factory method to create configured ViewSet from VIEWS_MATRIX.
        """
        config = VIEWS_MATRIX.get(view_name)
        # ... dynamicky vytvorí viewset class
        return viewset_class

# Usage:
LocationViewSet = MyView.create_viewset("locations")
router.register('locations', LocationViewSet, basename='locations')
```

#### MySerializer Factory (`api/serializers.py`)

```python
class MySerializer(serializers.ModelSerializer):
    """
    Config-driven serializer factory - generates serializers from VIEWS_MATRIX.
    """
    
    @classmethod
    def create_serializer(cls, view_name: str, read_only: bool = False):
        """
        Factory method to create serializer from VIEWS_MATRIX config.
        """
        config = VIEWS_MATRIX.get(view_name)
        # ... dynamicky vytvorí serializer class
        return serializer_class
```

## Frontend architektúra

### Adresárová štruktúra

```
frontend/
├── src/
│   ├── App.tsx               # Root app, routes
│   ├── main.tsx              # Entry point
│   │
│   ├── config/               # SSOT konfigurácia
│   │   ├── api.ts            # API base URL, CSRF
│   │   └── modelMetadata.ts  # Model metadata (mirror BE SSOT)
│   │
│   ├── contexts/             # React contexts
│   │   ├── AuthContext.tsx   # Authentication state
│   │   ├── ScopeContext.tsx  # Factory scope
│   │   └── ThemeContext.tsx  # Theme
│   │
│   ├── hooks/                # Custom hooks
│   │   ├── useApi.tsx        # API request hook
│   │   └── useSnapshot.tsx   # State snapshot management
│   │
│   ├── services/             # Service layer
│   │   └── fkCacheService.ts # FK options cache service
│   │
│   ├── components/           # Shared components
│   │   ├── MyTable/          # Unified table component (ConfigDriven)
│   │   │   ├── MyTable.tsx
│   │   │   ├── MyTableTypes.ts
│   │   │   ├── MyTableHelpers.ts
│   │   │   └── useMyTableData.ts
│   │   │
│   │   ├── modals/           # Modal dialogs
│   │   │   ├── AddRecordModal.tsx
│   │   │   ├── EditRecordModal.tsx
│   │   │   ├── SaveStateModal.tsx
│   │   │   ├── LoadStateModal.tsx
│   │   │   └── ...
│   │   │
│   │   ├── ui/               # shadcn/ui components
│   │   │
│   │   └── ui_custom/        # Custom UI components
│   │       └── table/        # Table-specific components
│   │           ├── fieldFactory.tsx
│   │           ├── FilterPanel.tsx
│   │           ├── ColumnsPanel.tsx
│   │           └── ...
│   │
│   └── apps/                 # Per-model modules (1:1 k BE)
│       ├── factory/          # Factory module
│       │   ├── FactoryTable.tsx
│       │   ├── factoryTableConfig.ts
│       │   ├── components/
│       │   ├── hooks/
│       │   ├── types/
│       │   └── utils/
│       │
│       ├── location/         # Location module
│       ├── carrier/          # Carrier module
│       ├── driver/           # Driver module
│       ├── pot/              # Pot module
│       ├── pit/              # Pit module
│       ├── machine/          # Machine module
│       ├── camera/           # Camera module
│       ├── measurement/     # Measurement module
│       ├── tag/              # Tag module
│       ├── photo/            # Photo module
│       ├── video/            # Video module
│       └── ... (všetky modely)
```

### Per-Model Frontend Štruktúra

Každý frontend modul má rovnakú štruktúru:

```
apps/factory/
├── FactoryTable.tsx          # Main page component
├── factoryTableConfig.ts     # MyTableConfig (SSOT)
├── components/
│   └── index.ts
├── hooks/
│   └── index.ts
├── types/
│   └── index.ts
├── utils/
│   └── index.ts
└── index.ts                  # Module exports
```

### Config-Driven Frontend

#### MyTable Component (`components/MyTable/MyTable.tsx`)

```typescript
interface MyTableConfig<T> {
  tableName: string;
  apiEndpoint: string;  // Alebo z modelMetadata
  fieldsMatrix: Record<string, FieldConfig>;
  filtersConfig?: FiltersConfig;
  actionsConfig?: ActionsConfig;
  toolbarVisibility?: TableToolbarVisibility;
  // ... ďalšie konfigurácie
}

export function MyTable<T>({ config }: { config: MyTableConfig<T> }) {
  // Automaticky používa:
  // - modelMetadata.ts pre endpoints
  // - fkCacheService.ts pre FK options
  // - useSnapshot.ts pre state persistence
  // - ScopeContext pre scoping
  // - AuthContext pre permissions
}
```

#### Fields Matrix (`factoryTableConfig.ts`)

```typescript
export const factoryTableConfig: MyTableConfig<Factory> = {
  tableName: 'Factories',
  apiEndpoint: '/api/factories/',  // Alebo z modelMetadata
  fieldsMatrix: {
    code: {
      type: 'text',
      header: 'Code',
      size: 150,
      order: 60,
      isInColumnPanel: true,
      defaultVisible: true,
      isInFilterPanel: true,
      filterType: 'text',
      editableInEditModal: true,
      editableInline: true,
      sortable: true,
    },
    factory: {
      type: 'fk',
      header: 'Factory',
      fkField: 'factory',
      // ...
    },
  },
  // ... ďalšie konfigurácie
};
```

### SSOT Frontend

#### Model Metadata (`config/modelMetadata.ts`)

```typescript
export interface ModelMeta {
  model: string;
  singular: string;
  plural: string;
  endpoint: string;
  default_ordering?: string[];
  ownership_field?: string | null;
}

export async function loadModelMetadata(): Promise<Record<string, ModelMeta>> {
  const response = await fetch('/api/models/metadata/');
  return await response.json();
}

export function getModelEndpoint(fieldName: string): string {
  const metadata = getCachedMetadata();
  return metadata[fieldName.toLowerCase()]?.endpoint || '';
}
```

#### FK Cache Service (`services/fkCacheService.ts`)

```typescript
export async function loadFKOptionsFromCache(
  field: string,
  factoryIds: string[] = []  // DEPRECATED: Backend handles scoping
): Promise<FKOption[]> {
  const url = `/api/fk-options-cache/?field=${field}`;
  const response = await fetch(url, { credentials: 'include' });
  return await response.json();
}
```

## Shared Infra

### Backend Shared

1. **Core Models** (`apps/core/models.py`)
   - `TimeStampedModel` - Base model
   - `NamedWithCodeModel` - Named model

2. **API Gateway** (`apps/api/`)
   - `VIEWS_MATRIX` - SSOT pre viewsety
   - `MyView` - ViewSet factory
   - `MySerializer` - Serializer factory
   - `FKOptionsCache` - FK cache model

3. **Scoping Engine** (`apps/scoping/`)
   - Ownership hierarchy
   - Automatic scoping application

4. **State Module** (`apps/state/`)
   - Table state persistence
   - Presets and snapshots

5. **Relation Module** (`apps/relation/`)
   - Dynamic relation registry
   - Config-driven relations

### Frontend Shared

1. **MyTable Component** (`components/MyTable/`)
   - Unified table component
   - Config-driven rendering

2. **Field Factory** (`components/ui_custom/table/fieldFactory.tsx`)
   - Generic field renderer
   - Type-based rendering

3. **Modals** (`components/modals/`)
   - AddRecordModal
   - EditRecordModal
   - SaveStateModal
   - LoadStateModal
   - ShareFactoryModal

4. **Contexts** (`contexts/`)
   - AuthContext - Authentication
   - ScopeContext - Factory scope
   - ThemeContext - Theme

5. **Hooks** (`hooks/`)
   - useApi - API requests
   - useSnapshot - State management

6. **Services** (`services/`)
   - fkCacheService - FK options

## Konvencie

### Súborové hlavičky

Každý súbor musí mať hlavičku v tomto formáte:

```python
# /Users/sopira/sopira.magic/version_01/sopira_magic/apps/m_factory/models.py
# Factory model - core data model for factory entities
#
# <details>
# <summary>Detailed description</summary>
#
# This module contains the Factory model definition, including:
# - Field definitions (name, code, address, etc.)
# - Relationships to other models (via relation module)
# - Custom methods and properties
# - Meta configuration (ordering, permissions, etc.)
#
# The model follows ConfigDriven & SSOT principles:
# - All metadata (endpoints, ownership, default ordering) is defined in sopira_magic/config/model_metadata.py
# - All relations are defined in sopira_magic/apps/relation/config.py
# - No hardcoded domain logic in the model itself
# </details>
```

### Naming Conventions

- **Backend apps**: `m_*` prefix pre data models (m_factory, m_location, etc.)
- **Frontend apps**: Bez prefixu (factory, location, etc.)
- **Models**: PascalCase (Factory, Location, Carrier)
- **Viewsets**: `{Model}ViewSet` (FactoryViewSet, LocationViewSet)
- **Serializers**: `{Model}Serializer` (FactorySerializer, LocationSerializer)
- **Frontend pages**: `{Model}Table.tsx` (FactoryTable.tsx, LocationTable.tsx)
- **Frontend configs**: `{model}TableConfig.ts` (factoryTableConfig.ts, locationTableConfig.ts)

### Hardcode Rules

**ČO SMIE BYŤ HARDCODED**:
- Lokálna UI logika v `apps/{model}/` moduloch
- Domain-specific business logic v `apps/m_{model}/` moduloch

**ČO MUSÍ BYŤ V SSOT**:
- Modely, polia, väzby → `config/model_metadata.py`, `relation/config.py`
- Endpointy, ordering, ownership → `VIEWS_MATRIX`
- FK options → `FKOptionsCache`
- Table state → `TableStatePreset`
- Scoping rules → `ScopingEngine` + `VIEWS_MATRIX.ownership_hierarchy`
- Field konfigurácia → `fieldsMatrix` v frontend config

## Migračný plán

### Etapa 1: Backend SSOT Infra
1. Vytvoriť `config/model_metadata.py`
2. Rozšíriť `api/view_configs.py` VIEWS_MATRIX
3. Implementovať `MyView` factory
4. Implementovať `MySerializer` factory
5. Vytvoriť `FKOptionsCache` model a endpoints

### Etapa 2: Backend Moduly
1. Vytvoriť nové apps (m_location, m_carrier, etc.)
2. Migrovať modely z Thermal Eye
3. Vytvoriť serializers, viewsets, filters, URLs
4. Pridať do VIEWS_MATRIX

### Etapa 3: Frontend SSOT Infra
1. Migrovať `MyTable` z Thermal Eye
2. Vytvoriť `config/modelMetadata.ts`
3. Vytvoriť `contexts/AuthContext.tsx`
4. Vytvoriť `contexts/ScopeContext.tsx`
5. Vytvoriť `hooks/useSnapshot.tsx`
6. Vytvoriť `services/fkCacheService.ts`
7. Migrovať modals a ui_custom components

### Etapa 4: Frontend Moduly
1. Vytvoriť frontend moduly pre každý model
2. Migrovať page komponenty z Thermal Eye UI
3. Vytvoriť MyTableConfig pre každý model
4. Pridať routes do App.tsx

### Etapa 5: Relation Module
1. Rozšíriť `relation/config.py` o všetky väzby
2. Nahradiť hardcoded ForeignKeys cez relation modul

## Zhrnutie

Cieľová architektúra sopira.magic je:

1. **ConfigDriven**: Všetko je riadené deklaratívnou konfiguráciou
2. **SSOT**: Single Source of Truth pre všetky konfigurácie
3. **1:1 Zrkadlenie**: Backend a frontend majú rovnakú štruktúru
4. **Modular Monolith**: Microservices-like apps v jednom projekte
5. **Žiadny Hardcode**: Žiadna domain-specific logika v generických vrstvách
6. **Automatické Generovanie**: Viewsety, serializers, UI sa generujú z konfigurácie

