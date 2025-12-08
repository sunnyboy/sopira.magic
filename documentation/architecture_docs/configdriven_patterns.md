# ConfigDriven & SSOT Patterns - Thermal Eye → Sopira.magic

## Prehľad

Tento dokument popisuje **ConfigDriven & SSOT vzory** používané v Thermal Eye a ako ich aplikovať v sopira.magic. Všetky vzory sú založené na princípe **Single Source of Truth (SSOT)** a **deklaratívnej konfigurácii** namiesto hardcoded logiky.

## 1. VIEWS_MATRIX Pattern (Backend SSOT)

### Thermal Eye implementácia

**Súbor**: `/Users/sopira/www/thermal_eye/measurement/api/view_configs.py`

**Účel**: SSOT pre všetky API viewsety - deklaratívna konfigurácia namiesto hardcoded viewset logiky.

**Struktúra**:
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
    # ... ďalšie modely
}
```

**Kľúčové vlastnosti**:
- **Model & Serializers**: Definované v konfigurácii
- **Query optimization**: `select_related`, `prefetch_related`
- **Permissions & Ownership**: `ownership_field`, `ownership_hierarchy`, `scope_level_metadata`
- **Search & Filters**: `search_fields`, `filter_class`, `ordering_fields`, `default_ordering`
- **Features**: `soft_delete`, `factory_scoped`, `dynamic_search`
- **FK Display Templates**: SSOT pre FK label rendering
- **Custom Hooks**: `before_create`, `after_create`, `before_update`, `after_update`
- **Table State**: `table_name` pre dynamic search fields

**Použitie**:
```python
# Auto-generate viewsets from config
LocationViewSet = MyView.create_viewset("locations")
CarrierViewSet = MyView.create_viewset("carriers")
MeasurementViewSet = MyView.create_viewset("measurements")

# Register with router
router.register('locations', LocationViewSet, basename='locations')
```

### Aplikácia v sopira.magic

**Cieľový súbor**: `/Users/sopira/sopira.magic/version_01/sopira_magic/apps/api/view_configs.py`

**Status**: Čiastočne existuje (len `users`, `focusedviews`). Potrebuje rozšírenie pre všetky modely.

**Akcia**:
1. Rozšíriť `VIEWS_MATRIX` o všetky modely z Thermal Eye
2. Implementovať `MyView.create_viewset()` factory method
3. Migrovať všetky konfigurácie z Thermal Eye

## 2. MySerializer Pattern (Config-Driven Serializers)

### Thermal Eye implementácia

**Súbor**: `/Users/sopira/www/thermal_eye/measurement/api/serializers.py`

**Účel**: Config-driven serializer factory - automaticky generuje serializers z VIEWS_MATRIX.

**Struktúra**:
```python
class MySerializer(serializers.ModelSerializer):
    """
    Config-driven serializer factory.
    Automatically generates serializer fields from VIEWS_MATRIX config.
    """
    
    @classmethod
    def create_serializer(cls, view_name: str, read_only: bool = False):
        """
        Factory method to create serializer from VIEWS_MATRIX config.
        
        Features:
        - Auto-generates fields from model
        - FK display labels (from fk_display_template)
        - Computed fields (from computed_fields config)
        - Exclude fields (from exclude_fields config)
        - Read-only fields (from read_only_fields config)
        """
        config = VIEWS_MATRIX.get(view_name)
        if not config:
            raise ValueError(f"View config '{view_name}' not found in VIEWS_MATRIX")
        
        model = config['model']
        serializer_class = type(
            f"{model.__name__}Serializer",
            (cls,),
            {
                'Meta': type('Meta', (), {
                    'model': model,
                    'fields': '__all__',
                    # ... config-driven Meta options
                })
            }
        )
        
        # Add FK display fields
        # Add computed fields
        # Apply exclude_fields, read_only_fields
        
        return serializer_class
```

**Kľúčové vlastnosti**:
- **Auto-generation**: Automaticky generuje serializers z VIEWS_MATRIX
- **FK Display Labels**: Generuje `*_display_label` fields z `fk_display_template`
- **Computed Fields**: Podporuje computed fields z konfigurácie
- **Field Exclusion**: Podporuje `exclude_fields`, `read_only_fields`

**Použitie**:
```python
# In VIEWS_MATRIX:
"factories": {
    "serializer_read": None,  # Uses MySerializer.create_serializer()
    "serializer_write": None,
    "fk_display_template": "{code}-{human_id}-{name}",
    "computed_fields": {
        "created_by_username": "created_by.username",
    },
    "exclude_fields": ["secret"],
    "read_only_fields": ["uuid", "created"],
}

# Auto-generated serializer includes:
# - All model fields
# - factory_display_label (from template)
# - created_by_username (computed)
# - Excludes: secret
# - Read-only: uuid, created
```

### Aplikácia v sopira.magic

**Cieľový súbor**: `/Users/sopira/sopira.magic/version_01/sopira_magic/apps/api/serializers.py`

**Status**: Neexistuje. Potrebuje vytvoriť.

**Akcia**:
1. Vytvoriť `MySerializer` factory class
2. Implementovať `create_serializer()` method
3. Podporovať FK display templates, computed fields, exclude fields

## 3. MyView Pattern (Config-Driven Viewsets)

### Thermal Eye implementácia

**Súbor**: `/Users/sopira/www/thermal_eye/measurement/api/my_view.py`

**Účel**: Universal ViewSet factory - automaticky generuje viewsety z VIEWS_MATRIX.

**Struktúra**:
```python
class MyView(ModelViewSet):
    """
    Universal ViewSet that configures itself from VIEWS_MATRIX.
    
    Features:
    - Auto-configured from VIEWS_MATRIX
    - Composable mixins (DynamicSearch, FactoryOwnership, SoftDelete)
    - Custom hooks (before_create, after_create, etc.)
    - Query optimization (select_related, prefetch_related)
    - Permission handling
    - Scoping integration (ScopingEngine)
    - Table state integration (TableStateEngine)
    """
    
    @classmethod
    def create_viewset(cls, view_name: str) -> Type['MyView']:
        """
        Factory method to create configured ViewSet from VIEWS_MATRIX.
        
        Dynamically builds ViewSet class with:
        - Appropriate mixins based on config
        - Model and serializer configuration
        - Search and filter backends
        - Query optimization
        """
        config = VIEWS_MATRIX.get(view_name)
        if not config:
            raise ValueError(f"View config '{view_name}' not found")
        
        # Build mixins list based on config
        mixins = []
        if config.get('dynamic_search'):
            mixins.append(DynamicSearchFieldsMixin)
        if config.get('factory_scoped'):
            mixins.append(FactoryOwnershipMixin)
        if config.get('soft_delete'):
            mixins.append(SoftDeleteMixin)
        
        # Create ViewSet class dynamically
        viewset_class = type(
            f"{config['model'].__name__}ViewSet",
            tuple([*mixins, cls]),
            {
                'queryset': config['model'].objects.all(),
                'serializer_class': MySerializer.create_serializer(view_name),
                # ... config-driven attributes
            }
        )
        
        return viewset_class
```

**Kľúčové vlastnosti**:
- **Auto-configuration**: Automaticky konfiguruje viewset z VIEWS_MATRIX
- **Composable Mixins**: Dynamicky pridáva mixiny podľa konfigurácie
- **Query Optimization**: Automaticky aplikuje `select_related`, `prefetch_related`
- **Scoping Integration**: Integrácia so ScopingEngine
- **Table State Integration**: Integrácia s TableStateEngine
- **Custom Hooks**: Podporuje `before_create`, `after_create`, etc.

**Použitie**:
```python
# Auto-generate viewsets
LocationViewSet = MyView.create_viewset("locations")
CarrierViewSet = MyView.create_viewset("carriers")

# Register with router
router.register('locations', LocationViewSet, basename='locations')
router.register('carriers', CarrierViewSet, basename='carriers')
```

### Aplikácia v sopira.magic

**Cieľový súbor**: `/Users/sopira/sopira.magic/version_01/sopira_magic/apps/api/view_factory.py`

**Status**: Neexistuje. Potrebuje vytvoriť.

**Akcia**:
1. Vytvoriť `MyView` factory class
2. Implementovať `create_viewset()` method
3. Implementovať mixiny (DynamicSearch, FactoryOwnership, SoftDelete)
4. Integrovať so ScopingEngine a TableStateEngine

## 4. Scoping Engine Pattern (SSOT Ownership)

### Thermal Eye implementácia

**Súbor**: `/Users/sopira/www/thermal_eye/apps/scoping/engine.py`

**Účel**: SSOT pre ownership/scoping logiku - automaticky aplikuje scoping pravidlá na základe ownership hierarchy.

**Struktúra**:
```python
class ScopingEngine:
    """
    Scoping engine - applies ownership rules based on ownership hierarchy.
    
    SSOT: Ownership hierarchy is defined in VIEWS_MATRIX (ownership_hierarchy, scope_level_metadata).
    """
    
    @staticmethod
    def apply_rules(queryset: QuerySet, user, view_name: str, config: ViewConfig, request=None) -> QuerySet:
        """
        Apply scoping rules to queryset based on ownership hierarchy.
        
        Ownership hierarchy example:
        ["created_by", "factory_id"] means:
        - Level 0: User (created_by)
        - Level 1: Factory (factory_id)
        
        Scoping logic:
        1. Get user's accessible factories from UserPreference.accessible_factories
        2. Get user's selected factories from UserPreference.selected_factories (Dashboard)
        3. Apply filters based on ownership hierarchy
        """
        ownership_hierarchy = config.get('ownership_hierarchy', [])
        scope_level_metadata = config.get('scope_level_metadata', {})
        
        # Get user's scope
        accessible_factories = get_user_accessible_factories(user)
        selected_factories = get_user_selected_factories(user)  # Dashboard selection
        
        # Apply scoping based on hierarchy
        if ownership_hierarchy:
            # Level 0: User scope
            if ownership_hierarchy[0] == "created_by":
                queryset = queryset.filter(created_by=user)
            
            # Level 1: Factory scope
            if len(ownership_hierarchy) > 1 and ownership_hierarchy[1] == "factory_id":
                if selected_factories:
                    queryset = queryset.filter(factory_id__in=selected_factories)
                elif accessible_factories:
                    queryset = queryset.filter(factory_id__in=accessible_factories)
        
        return queryset
```

**Kľúčové vlastnosti**:
- **SSOT**: Ownership hierarchy je definovaná v VIEWS_MATRIX
- **Automatic Application**: Automaticky aplikuje scoping pravidlá
- **Dashboard Integration**: Používa `selected_factories` z Dashboard ako SSOT
- **Multi-level Scoping**: Podporuje viacúrovňové scoping (User → Factory → Location)

**Použitie**:
```python
# In VIEWS_MATRIX:
"locations": {
    "ownership_hierarchy": ["created_by", "factory_id"],
    "scope_level_metadata": {
        0: {"name": "User", "field": "created_by"},
        1: {"name": "Factory", "field": "factory_id"},
    },
}

# ScopingEngine automatically applies:
# - Level 0: Filter by created_by=user
# - Level 1: Filter by factory_id in selected_factories
```

### Aplikácia v sopira.magic

**Cieľový súbor**: `/Users/sopira/sopira.magic/version_01/sopira_magic/apps/scoping/engine.py`

**Status**: Existuje (27 súborov). Pravdepodobne už z Thermal Eye.

**Akcia**:
1. Overiť, že ScopingEngine je kompatibilný s Thermal Eye verziou
2. Integrovať s VIEWS_MATRIX v sopira.magic
3. Zabezpečiť, že ownership hierarchy je definovaná v VIEWS_MATRIX

## 5. Model Metadata Pattern (SSOT Frontend Mirror)

### Thermal Eye implementácia

**Backend**: `/Users/sopira/www/thermal_eye/measurement/api/views/metadata.py`

**Účel**: SSOT endpoint pre modelové metadáta - frontend mirror backend VIEWS_MATRIX.

**Struktúra**:
```python
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def model_metadata_view(request):
    """
    Return model metadata from VIEWS_MATRIX.
    
    Frontend uses this as SSOT for:
    - Endpoints (plural names)
    - Default ordering
    - Ownership fields
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
    return Response(metadata)
```

**Frontend**: `/Users/sopira/www/thermal_eye_ui/src/config/modelMetadata.ts`

**Účel**: Frontend mirror backend metadát - SSOT pre frontend.

**Struktúra**:
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
  const metadata = await response.json();
  return metadata;
}

export function getModelEndpoint(fieldName: string): string {
  const metadata = getCachedMetadata();
  return metadata[fieldName.toLowerCase()]?.endpoint || '';
}
```

**Kľúčové vlastnosti**:
- **SSOT**: Backend VIEWS_MATRIX je SSOT, frontend je mirror
- **Automatic Sync**: Frontend automaticky načíta metadáta z backendu
- **No Hardcode**: Frontend nepoužíva hardcoded endpoints, všetko z metadát

**Použitie**:
```typescript
// Load once on app init
await loadModelMetadata();

// Use in MyTable
const endpoint = getModelEndpoint('factory'); // → '/api/factories/'
const ordering = getDefaultOrdering('factory'); // → ['name']
```

### Aplikácia v sopira.magic

**Backend**: `/Users/sopira/sopira.magic/version_01/sopira_magic/config/model_metadata.py` (treba vytvoriť)

**Frontend**: `/Users/sopira/sopira.magic/version_01/frontend/src/config/modelMetadata.ts` (treba vytvoriť)

**Akcia**:
1. Vytvoriť backend endpoint `/api/models/metadata/`
2. Vytvoriť frontend `modelMetadata.ts` mirror
3. Integrovať s VIEWS_MATRIX v sopira.magic

## 6. FK Cache Pattern (SSOT FK Options)

### Thermal Eye implementácia

**Backend Model**: `/Users/sopira/www/thermal_eye/measurement/models.py` → `FKOptionsCache`

**Účel**: Cache pre FK dropdown options - SSOT pre FK options.

**Struktúra**:
```python
class FKOptionsCache(models.Model):
    """
    Cache for FK dropdown options (for fast FE loading).
    Automatically rebuilt when related models change via signals.
    """
    field_name = models.CharField(max_length=50)  # e.g., 'location', 'carrier'
    factory = models.ForeignKey('Factory', on_delete=models.CASCADE, null=True)  # Scope
    options = models.JSONField(default=list)  # Cached FK options
    last_updated = models.DateTimeField(auto_now=True)
    record_count = models.IntegerField(default=0)
    
    class Meta:
        unique_together = [('field_name', 'factory')]
```

**Backend Endpoint**: `/Users/sopira/www/thermal_eye/measurement/api/views/fk_cache.py`

**Účel**: Endpoint pre načítanie FK options z cache.

**Frontend Service**: `/Users/sopira/www/thermal_eye_ui/src/services/fkCacheService.ts`

**Účel**: Frontend service pre načítanie FK options.

**Kľúčové vlastnosti**:
- **SSOT**: FKOptionsCache je SSOT pre FK options
- **Automatic Rebuild**: Automaticky rebuilduje cez signals pri zmene FK entít
- **Scoping**: Automaticky aplikuje scope na základe `selected_factories`
- **Fast Loading**: Cache umožňuje rýchle načítanie FK options

**Použitie**:
```typescript
// Frontend
const options = await loadFKOptionsFromCache('location');
// Backend automatically applies scope based on selected_factories
```

### Aplikácia v sopira.magic

**Backend**: `/Users/sopira/sopira.magic/version_01/sopira_magic/apps/api/models.py` (treba vytvoriť FKOptionsCache)

**Frontend**: `/Users/sopira/sopira.magic/version_01/frontend/src/services/fkCacheService.ts` (treba vytvoriť)

**Akcia**:
1. Vytvoriť `FKOptionsCache` model
2. Vytvoriť signals pre automatický rebuild
3. Vytvoriť backend endpoint `/api/fk-options-cache/`
4. Vytvoriť frontend `fkCacheService.ts`

## 7. MyTable Pattern (Frontend ConfigDriven)

### Thermal Eye implementácia

**Súbor**: `/Users/sopira/www/thermal_eye_ui/src/components/MyTable/MyTable.tsx`

**Účel**: Config-driven table component - jednotný komponent pre všetky tabuľky.

**Struktúra**:
```typescript
interface MyTableConfig<T> {
  tableName: string;
  apiEndpoint: string;
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

**Kľúčové vlastnosti**:
- **Config-Driven**: Všetko je riadené konfiguráciou, nie hardcode
- **SSOT Integration**: Používa modelMetadata, fkCacheService, useSnapshot
- **Field Factory**: Automaticky renderuje polia podľa typu z fieldsMatrix
- **State Persistence**: Automaticky ukladá/načítava state z backendu
- **Scoping**: Automaticky aplikuje scoping na základe ScopeContext

**Použitie**:
```typescript
const config: MyTableConfig<Factory> = {
  tableName: 'Factories',
  apiEndpoint: '/api/factories/',  // Alebo z modelMetadata
  fieldsMatrix: {
    code: { type: 'text', header: 'Code', ... },
    name: { type: 'text', header: 'Name', ... },
    factory: { type: 'fk', header: 'Factory', fkField: 'factory', ... },
  },
};

<MyTable config={config} />
```

### Aplikácia v sopira.magic

**Cieľový súbor**: `/Users/sopira/sopira.magic/version_01/frontend/src/components/MyTable/MyTable.tsx`

**Status**: Existuje, ale je jednoduchší ako Thermal Eye verzia.

**Akcia**:
1. Migrovať plnú ConfigDriven verziu z Thermal Eye
2. Integrovať s modelMetadata, fkCacheService, useSnapshot
3. Pridať fieldFactory, filter panel, columns panel
4. Pridať state persistence integráciu

## 8. Fields Matrix Pattern (Frontend SSOT)

### Thermal Eye implementácia

**Účel**: SSOT pre field konfiguráciu - deklaratívna konfigurácia polí namiesto hardcode.

**Struktúra**:
```typescript
interface FieldConfig {
  type: 'text' | 'number' | 'date' | 'fk' | 'select' | 'checkbox' | ...;
  header: string;
  size?: number;
  order?: number;
  isInColumnPanel?: boolean;
  defaultVisible?: boolean;
  isInFilterPanel?: boolean;
  filterType?: 'text' | 'select' | 'date' | 'checkbox' | ...;
  editableInEditModal?: boolean;
  editableInline?: boolean;
  editableInAddModal?: boolean;
  sortable?: boolean;
  resizable?: boolean;
  fkField?: string;  // For FK fields
  // ... ďalšie vlastnosti
}

const fieldsMatrix: Record<string, FieldConfig> = {
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
};
```

**Kľúčové vlastnosti**:
- **SSOT**: FieldsMatrix je SSOT pre field konfiguráciu
- **Deklaratívna**: Všetko je deklarované, nie hardcoded
- **Automatic UI**: Automaticky generuje UI (stĺpce, filtre, modaly) z konfigurácie

### Aplikácia v sopira.magic

**Akcia**: Použiť rovnaký pattern ako v Thermal Eye.

## 9. Table State Pattern (SSOT State Persistence)

### Thermal Eye implementácia

**Backend**: `/Users/sopira/www/thermal_eye/apps/table_state/models.py` → `TableStatePreset`

**Účel**: SSOT pre table state persistence - ukladá stavy tabuliek (filtre, stĺpce, ordering, pagination).

**Frontend**: `/Users/sopira/www/thermal_eye_ui/src/hooks/useSnapshot.tsx`

**Účel**: Frontend hook pre state management.

**Kľúčové vlastnosti**:
- **SSOT**: TableStatePreset v databáze je SSOT
- **Automatic Sync**: Automatická synchronizácia s backendom
- **Presets**: Podporuje presets (uložené stavy)
- **Snapshots**: Podporuje snapshots (`__current__` preset)

### Aplikácia v sopira.magic

**Backend**: `/Users/sopira/sopira.magic/version_01/sopira_magic/apps/state/models.py` (existuje)

**Frontend**: `/Users/sopira/sopira.magic/version_01/frontend/src/hooks/useSnapshot.tsx` (treba vytvoriť)

**Akcia**:
1. Overiť, že state app je kompatibilný
2. Vytvoriť frontend `useSnapshot.tsx` hook
3. Integrovať s MyTable

## 10. Relation Module Pattern (SSOT Relations)

### Thermal Eye implementácia

**Status**: Thermal Eye používa hardcoded ForeignKeys. Sopira.magic má relation modul pre config-driven relations.

**Cieľ**: Použiť relation modul namiesto hardcoded ForeignKeys.

**Struktúra**:
```python
# Sopira.magic relation/config.py
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
    # ... ďalšie väzby
}
```

**Kľúčové vlastnosti**:
- **SSOT**: Relation registry je SSOT pre všetky väzby
- **No Hardcode**: Žiadne hardcoded ForeignKeys v modeloch
- **Config-Driven**: Všetky väzby sú definované v konfigurácii

### Aplikácia v sopira.magic

**Akcia**: Rozšíriť relation modul o všetky väzby z Thermal Eye.

## Zhrnutie - ConfigDriven & SSOT Princípy

### Backend SSOT

1. **VIEWS_MATRIX** - SSOT pre všetky API viewsety
2. **Model Metadata** - SSOT pre modelové metadáta (endpoints, ordering, ownership)
3. **FK Cache** - SSOT pre FK options
4. **Scoping Engine** - SSOT pre ownership/scoping logiku
5. **Table State** - SSOT pre table state persistence
6. **Relation Registry** - SSOT pre všetky väzby medzi modelmi

### Frontend SSOT

1. **modelMetadata.ts** - Mirror backend metadát
2. **fieldsMatrix** - SSOT pre field konfiguráciu
3. **fkCacheService** - SSOT pre FK options
4. **useSnapshot** - SSOT pre state management
5. **ScopeContext** - SSOT pre factory scope
6. **AuthContext** - SSOT pre authentication state

### ConfigDriven Princípy

1. **Deklaratívna konfigurácia** namiesto hardcoded logiky
2. **Automatické generovanie** z konfigurácie
3. **Žiadny domain hardcode** v generických vrstvách
4. **Single Source of Truth** pre všetky konfigurácie
5. **Composable mixins** namiesto dedičnosti
6. **Factory patterns** pre dynamické vytváranie tried

