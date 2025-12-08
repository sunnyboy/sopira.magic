# Sopira.magic - Inventúra aktuálnej architektúry

## Prehľad

Sopira.magic je **modular monolith** Django projekt s React frontendom, organizovaný ako **microservices-like Django apps** bežiace na jednej primárnej DB. Architektúra je **config-driven** a **SSOT (single source of truth)**.

**Cesta**: `/Users/sopira/sopira.magic/version_01`

## Backend architektúra

### Adresárová štruktúra

```
sopira_magic/
├── sopira_magic/              # Django project settings
│   ├── settings.py            # Main settings (35 apps registered)
│   ├── urls.py                # Root URL configuration
│   ├── wsgi.py / asgi.py      # WSGI/ASGI entry points
│   ├── security_config.py     # Security configuration (CORS, CSRF)
│   └── db_router.py          # Multi-database router
│
├── apps/                      # All Django apps (modular monolith)
│   ├── core/                  # Base models (TimeStampedModel, NamedWithCodeModel)
│   ├── shared/                # Shared utilities, mixins
│   ├── security/              # Security middleware, policies
│   │
│   ├── m_user/                # User management (m_* prefix = data models)
│   ├── authentification/       # Authentication (login, signup, 2FA)
│   │
│   ├── m_company/             # Company management
│   ├── m_factory/             # Factory management (placeholder)
│   ├── m_productionline/      # Production line management
│   ├── m_utility/             # Utility functions
│   ├── m_equipment/            # Equipment management
│   ├── m_resource/            # Resource management
│   ├── m_worker/              # Worker management
│   ├── m_material/            # Material management
│   ├── m_process/             # Business processes
│   ├── endpoint/              # External endpoints (cameras, sensors, IoT)
│   ├── dashboard/             # Dashboard configuration
│   │
│   ├── m_document/            # Document management
│   ├── m_video/               # Video gallery (placeholder)
│   ├── m_photo/               # Photo gallery (placeholder)
│   ├── m_tag/                 # Tag management (placeholder)
│   │
│   ├── search/                # Search functionality (Elasticsearch ready)
│   ├── notification/          # Notifications (email, SMS, push)
│   ├── reporting/             # Reports (PDF, CSV, Excel)
│   ├── analytics/             # Analytics
│   ├── alarm/                 # Alarm management
│   ├── audit/                 # Audit logging
│   ├── logging/               # Application logging
│   ├── file_storage/          # File storage (S3, Local, Azure)
│   ├── scheduler/             # Task scheduling
│   ├── caching/               # Caching layer
│   ├── state/                 # UI state persistence
│   ├── internationalization/  # i18n support
│   ├── impex/                 # Import/Export
│   ├── api/                   # API Gateway (config-driven)
│   ├── mobileapp/             # Mobile app configuration
│   │
│   ├── relation/               # Dynamic relation registry (config-driven, SSOT)
│   ├── generator/             # Data generation (SSOT, config-driven)
│   ├── pdfviewer/             # PDF viewer & reporting
│   └── scoping/               # Scoping engine (ownership hierarchy)
│
├── manage.py
├── requirements.txt
└── pytest.ini
```

### Django aplikácie (35 apps)

#### Core Apps
- **core** - Base models (TimeStampedModel, NamedWithCodeModel)
- **shared** - Shared utilities, mixins, decorators
- **security** - Security middleware, policies

#### User & Auth
- **m_user** - User management
- **authentification** - Authentication (login, signup, 2FA)

#### Business Logic (m_* prefix = data models)
- **m_company** - Company management
- **m_factory** - Factory management (placeholder/scaffold)
- **m_productionline** - Production line management
- **m_utility** - Utility functions
- **m_equipment** - Equipment management
- **m_resource** - Resource management
- **m_worker** - Worker management
- **m_material** - Material management
- **m_process** - Business processes
- **endpoint** - External endpoints (cameras, sensors, IoT)
- **dashboard** - Dashboard configuration

#### Media & Content
- **m_document** - Document management
- **m_video** - Video gallery (placeholder/scaffold)
- **m_photo** - Photo gallery (placeholder/scaffold)
- **m_tag** - Tag management (placeholder/scaffold)

#### Services
- **search** - Search functionality (Elasticsearch ready)
- **notification** - Notifications (email, SMS, push)
- **reporting** - Reports (PDF, CSV, Excel)
- **analytics** - Analytics
- **alarm** - Alarm management
- **audit** - Audit logging
- **logging** - Application logging
- **file_storage** - File storage (S3, Local, Azure)
- **scheduler** - Task scheduling
- **caching** - Caching layer
- **state** - UI state persistence
- **internationalization** - i18n support
- **impex** - Import/Export
- **api** - API Gateway (config-driven)
- **mobileapp** - Mobile app configuration

#### SSOT & Config-driven
- **relation** - Dynamic relation registry (config-driven, SSOT)
- **generator** - Data generation (SSOT, config-driven)
- **pdfviewer** - PDF viewer & reporting
- **scoping** - Scoping engine (ownership hierarchy)

### Base modely

#### TimeStampedModel (core/models.py)
- `id` (UUID, primary key)
- `uuid` (UUID, unique, indexed)
- `created` (DateTime, auto_now_add, indexed)
- `updated` (DateTime, auto_now)
- `active` (Boolean, default=True, indexed) - soft delete flag
- `visible` (Boolean, default=True, indexed) - UI visibility flag

#### NamedWithCodeModel (core/models.py, extends TimeStampedModel)
- `human_id` (CharField, nullable, indexed)
- `code` (CharField, indexed)
- `name` (CharField, indexed)
- `comment` (TextField)
- `note` (TextField)
- Auto-generates `human_id` from `code` if not provided

### Existujúce m_* moduly (placeholdery/scaffold)

Tieto moduly existujú ako placeholdery/scaffold a treba ich nahradiť skutočným kódom z Thermal Eye:

1. **m_factory** (`sopira_magic/apps/m_factory/`)
   - Model: `Factory` (extends NamedWithCodeModel)
   - **Status**: Placeholder - potrebuje migráciu z Thermal Eye

2. **m_tag** (`sopira_magic/apps/m_tag/`)
   - **Status**: Placeholder - potrebuje migráciu z Thermal Eye

3. **m_user** (`sopira_magic/apps/m_user/`)
   - Model: `User` (extends Django User)
   - **Status**: Čiastočne implementované

4. **m_photo** (`sopira_magic/apps/m_photo/`)
   - **Status**: Placeholder - potrebuje migráciu z Thermal Eye

5. **m_video** (`sopira_magic/apps/m_video/`)
   - **Status**: Placeholder - potrebuje migráciu z Thermal Eye

### Moduly, ktoré treba vytvoriť

Tieto moduly neexistujú a treba ich vytvoriť podľa Thermal Eye:

1. **m_camera** - Camera management
2. **m_carrier** - Carrier management
3. **m_driver** - Driver management
4. **m_location** - Location management
5. **m_pit** - Pit management
6. **m_pot** - Pot management
7. **m_measurement** - Measurement management
8. **m_machine** - Machine management

### API Gateway (config-driven)

**Súbor**: `sopira_magic/apps/api/view_configs.py`

**VIEWS_MATRIX** - SSOT pre config-driven API viewsety:

```python
VIEWS_MATRIX: Dict[str, ViewConfig] = {
    "users": {
        "model": User,
        "serializer_read": UserListSerializer,
        "base_filters": {},
        "ownership_hierarchy": ["id"],
        "search_fields": ["username", "email", ...],
        "ordering_fields": [...],
        "default_ordering": ["username"],
    },
    "focusedviews": {
        "model": FocusedView,
        "serializer_read": FocusedViewSerializer,
        # ...
    },
}
```

**Status**: Čiastočne implementované (users, focusedviews). Potrebuje rozšírenie pre všetky modely.

### Relation Module (SSOT)

**Cesta**: `sopira_magic/apps/relation/`

**Účel**: Dynamic relation registry - všetky väzby medzi modelmi sú definované v konfigurácii, nie cez hardcoded ForeignKeys.

**Status**: Existuje, potrebuje rozšírenie pre Thermal Eye modely.

### Scoping Module

**Cesta**: `sopira_magic/apps/scoping/`

**Účel**: Scoping engine pre ownership hierarchy.

**Status**: Existuje (27 súborov), pravdepodobne z Thermal Eye.

### State Module

**Cesta**: `sopira_magic/apps/state/`

**Účel**: UI state persistence (table state, presets, snapshots).

**Status**: Existuje (9 súborov).

### Database Architecture

Multi-database PostgreSQL setup:

1. **PRIMARY DATABASE** (`default`)
   - Business data storage
   - Tables: user_*, company_*, factory_*, equipment_*, measurement_*, etc.
   - Environment Variable: `PRIMARY_DATABASE_URL` or `DATABASE_URL`

2. **STATE DATABASE** (`state`)
   - UI state a environment state viazaný na usera
   - Tables: table_state, saved_workspace, environment_state
   - Environment Variable: `STATE_DATABASE_URL`
   - Apps: `state`

3. **LOGGING DATABASE** (`logging`)
   - Application logs a audit trails
   - Tables: system_log, audit_log, performance_log
   - Environment Variable: `LOGGING_DATABASE_URL`
   - Apps: `logging`, `audit`

**Database Router**: `sopira_magic.db_router.DatabaseRouter`
- Routes models to appropriate database based on app_label
- Prevents cross-database relations
- Ensures migrations go to correct database

## Frontend architektúra

### Adresárová štruktúra

```
frontend/
├── src/
│   ├── App.tsx                # Root app component (minimal - len users, pdfviewer routes)
│   ├── main.tsx               # Entry point
│   ├── index.css              # Global styles
│   │
│   ├── apps/                  # Per-model modules (1:1 k BE)
│   │   ├── user/              # User module
│   │   │   ├── UsersPage.tsx  # User table page
│   │   │   ├── userTableConfig.ts
│   │   │   ├── components/
│   │   │   ├── hooks/
│   │   │   ├── types/
│   │   │   └── utils/
│   │   │
│   │   ├── pdfviewer/         # PDF viewer module (implementovaný)
│   │   │   ├── PdfViewerPage.tsx
│   │   │   ├── AnnotationToolbar.tsx
│   │   │   ├── api.ts
│   │   │   ├── hooks/
│   │   │   └── types.ts
│   │   │
│   │   ├── factory/           # Factory module (scaffold)
│   │   ├── tag/               # Tag module (scaffold)
│   │   ├── photo/             # Photo module (scaffold)
│   │   ├── video/             # Video module (scaffold)
│   │   ├── company/           # Company module (scaffold)
│   │   ├── ... (35 modulov - všetky majú rovnakú štruktúru)
│   │
│   ├── components/            # Shared components
│   │   ├── MyTable/           # Unified table component (ConfigDriven)
│   │   │   ├── MyTable.tsx    # Main orchestrator
│   │   │   ├── MyTableTypes.ts
│   │   │   ├── MyTableHelpers.ts
│   │   │   └── MyTableToolbar.tsx
│   │   │
│   │   ├── PdfViewer/         # PDF viewer component
│   │   ├── ui/                # shadcn/ui components
│   │   └── shared/            # Shared components
│   │
│   ├── config/                # SSOT konfigurácia
│   │   └── (modelMetadata.ts - zatiaľ neexistuje)
│   │
│   ├── contexts/              # React contexts
│   │   └── (AuthContext, ScopeContext - zatiaľ neexistujú)
│   │
│   ├── hooks/                 # Custom hooks
│   │   └── (useApi, useSnapshot - zatiaľ neexistujú)
│   │
│   ├── services/              # Service layer
│   │   └── (fkCacheService - zatiaľ neexistuje)
│   │
│   └── lib/                   # Library utilities
│       └── utils.ts
│
├── package.json
├── vite.config.ts
├── tailwind.config.js
└── tsconfig.json
```

### Frontend moduly (per-model, 1:1 k BE)

Všetky moduly majú rovnakú štruktúru:
- `components/` - React components
- `hooks/` - Custom hooks
- `types/` - TypeScript types
- `utils/` - Utility functions
- `index.ts` - Module exports

**Existujúce moduly** (scaffold):
- `user/` - Čiastočne implementované (UsersPage.tsx)
- `pdfviewer/` - Implementovaný
- `factory/`, `tag/`, `photo/`, `video/`, `company/`, ... (35 modulov) - Scaffold

**Moduly, ktoré treba vytvoriť**:
- `camera/`, `carrier/`, `driver/`, `location/`, `pit/`, `pot/`, `measurement/`, `machine/`

### MyTable Component

**Súbor**: `frontend/src/components/MyTable/MyTable.tsx`

**Status**: Existuje, ale je jednoduchší ako Thermal Eye verzia. Potrebuje migráciu z Thermal Eye pre plnú ConfigDriven funkcionalitu.

**Rozdiely oproti Thermal Eye**:
- Chýba integrácia s modelMetadata
- Chýba FK cache service
- Chýba useSnapshot hook
- Chýba ScopeContext
- Chýba AuthContext
- Chýba fieldFactory
- Chýba filter panel, columns panel
- Chýba state persistence

## ConfigDriven & SSOT status

### Backend

✅ **Existuje**:
- `core.models` - Base models (TimeStampedModel, NamedWithCodeModel)
- `api.view_configs` - VIEWS_MATRIX (čiastočne)
- `relation` - Relation registry (SSOT)
- `scoping` - Scoping engine
- `state` - State persistence
- `generator` - Data generation (SSOT)

❌ **Chýba**:
- Centrálny `model_metadata.py` (SSOT pre všetky modely)
- VIEWS_MATRIX pre všetky modely (len users, focusedviews)
- FK cache infra
- Table state presets (existuje state app, ale nie presets)

### Frontend

✅ **Existuje**:
- `MyTable` komponent (základná verzia)
- Per-model moduly (scaffold štruktúra)

❌ **Chýba**:
- `config/modelMetadata.ts` (SSOT mirror BE)
- `contexts/AuthContext.tsx`
- `contexts/ScopeContext.tsx`
- `hooks/useApi.tsx`
- `hooks/useSnapshot.tsx`
- `services/fkCacheService.ts`
- Field factory
- Filter panel, columns panel
- State persistence integrácia
- Modals (AddRecordModal, EditRecordModal, SaveStateModal, etc.)

## Mapovanie Thermal Eye → Sopira.magic

### Backend

| Thermal Eye | Sopira.magic | Status |
|------------|--------------|--------|
| `measurement` app (všetky modely) | `m_*` apps (separátne) | Potrebuje migráciu |
| `apps.scoping` | `apps.scoping` | ✅ Existuje |
| `apps.table_state` | `apps.state` | ✅ Existuje |
| `VIEWS_MATRIX` (view_configs.py) | `api.view_configs.VIEWS_MATRIX` | ❌ Čiastočne |
| `FKOptionsCache` model | - | ❌ Chýba |
| `model_metadata.py` (SSOT) | - | ❌ Chýba |

### Frontend

| Thermal Eye | Sopira.magic | Status |
|------------|--------------|--------|
| `MyTable` (plne ConfigDriven) | `MyTable` (základná verzia) | ❌ Potrebuje migráciu |
| `config/modelMetadata.ts` | - | ❌ Chýba |
| `contexts/ScopeContext.tsx` | - | ❌ Chýba |
| `contexts/AuthContext.tsx` | - | ❌ Chýba |
| `hooks/useSnapshot.tsx` | - | ❌ Chýba |
| `services/fkCacheService.ts` | - | ❌ Chýba |
| `components/modals/` | - | ❌ Chýba |
| `components/ui_custom/table/` | - | ❌ Chýba |
| Per-model pages | Per-model apps (scaffold) | ❌ Potrebuje migráciu |

## Dôležité poznámky

1. **Modular monolith**: Sopira.magic je organizovaný ako modular monolith s microservices-like Django apps.

2. **m_* prefix**: Všetky dátové modely majú prefix `m_` (m_factory, m_user, m_tag, etc.).

3. **Placeholdery**: Väčšina m_* modulov sú placeholdery/scaffold a potrebujú migráciu z Thermal Eye.

4. **Config-driven**: Architektúra je config-driven, ale nie všetko je ešte implementované.

5. **SSOT**: SSOT princípy sú aplikované v relation, scoping, generator moduloch, ale chýba centrálny model_metadata.py.

6. **Frontend**: Frontend má základnú štruktúru, ale chýba väčšina ConfigDriven infra z Thermal Eye.

7. **1:1 štruktúra**: Frontend `apps/` zrkadlí backend `apps/` štruktúru (1:1), ale väčšina modulov je len scaffold.

8. **Multi-database**: Podporuje multi-database architektúru (PRIMARY, STATE, LOGGING).

9. **Thermal Eye migrácia**: Väčšina funkcionality z Thermal Eye ešte nie je zmigrovaná do sopira.magic.

10. **API Gateway**: API Gateway existuje s VIEWS_MATRIX, ale len pre users a focusedviews. Potrebuje rozšírenie pre všetky modely.

