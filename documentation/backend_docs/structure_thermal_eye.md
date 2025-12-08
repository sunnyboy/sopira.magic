# Thermal Eye Backend - Inventúra štruktúry

## Prehľad

Thermal Eye je Django aplikácia organizovaná ako **modular monolith** s jednou hlavnou aplikáciou `measurement` obsahujúcou všetky business modely, plus dva cross-cutting moduly pre scoping a table state.

**Zdrojová cesta**: `/Users/sopira/www/thermal_eye`

## Adresárová štruktúra

```
thermal_eye/
├── thermal_eye/              # Django project settings
│   ├── settings.py           # Hlavné nastavenia projektu
│   ├── urls.py               # Root URL konfigurácia
│   ├── wsgi.py / asgi.py     # WSGI/ASGI entry points
│   ├── middleware.py         # Custom middleware (AutoCorsMiddleware, CookieParsingMiddleware)
│   └── security_config.py    # Security konfigurácia (CORS, CSRF)
├── apps/                     # Cross-cutting moduly
│   ├── scoping/              # Abstraktný scoping engine
│   └── table_state/          # Abstraktný table state engine
├── measurement/              # Hlavná aplikácia (všetky business modely)
│   ├── models.py             # Všetky Django modely
│   ├── models_state.py       # TableStatePreset model
│   ├── admin.py              # Django admin konfigurácia
│   ├── urls.py               # App-level URLs
│   ├── api/                  # REST API vrstva
│   │   ├── views.py          # Hlavný viewset orchestrátor
│   │   ├── view_configs.py   # VIEWS_MATRIX - SSOT pre všetky viewsety
│   │   ├── serializers.py   # DRF serializers
│   │   ├── filters.py        # Django filters
│   │   ├── my_view.py        # Config-driven viewset factory
│   │   ├── my_urls.py        # Config-driven URL generator
│   │   ├── urls.py           # Auto-generated URLs
│   │   └── views/            # Custom view funkcie
│   │       ├── auth_views.py
│   │       ├── camera.py
│   │       ├── config.py
│   │       ├── dashboard.py
│   │       ├── dummy_data.py
│   │       ├── fk_cache.py
│   │       ├── metadata.py
│   │       ├── preferences.py
│   │       ├── streaming.py
│   │       ├── table_state.py
│   │       └── users.py
│   ├── signals.py            # Django signals
│   ├── signals_audit.py     # Audit logging signals
│   ├── signals_fk_cache.py  # FK cache rebuild signals
│   ├── signals_table_state.py # Table state signals
│   ├── middleware_api_logging.py # API logging middleware
│   ├── middleware_audit.py  # Audit context middleware
│   ├── migrations/           # Django migrations
│   ├── management/commands/ # Management commands
│   └── tests/                # Test súbory
├── manage.py
├── requirements.txt
└── pytest.ini
```

## Django aplikácie

### 1. `measurement` - Hlavná aplikácia

**Cesta**: `/Users/sopira/www/thermal_eye/measurement/`

Hlavná Django aplikácia obsahujúca všetky business modely a API logiku.

**INSTALLED_APPS konfigurácia**:
```python
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "django_filters",
    "apps.scoping",      # Musí byť pred measurement
    "apps.table_state",
    "measurement",
]
```

### 2. `apps.scoping` - Scoping Engine

**Cesta**: `/Users/sopira/www/thermal_eye/apps/scoping/`

Abstraktný modul pre scoping/ownership logiku. Poskytuje:
- ScopingEngine pre aplikovanie ownership pravidiel
- Registry pre scoping rules
- Middleware pre automatické scoping
- Presets pre scoping konfigurácie

**Kľúčové súbory**:
- `engine.py` - Hlavná scoping logika
- `registry.py` - Registry scoping rules
- `rules.py` - Definície scoping rules
- `middleware.py` - Scoping middleware

### 3. `apps.table_state` - Table State Engine

**Cesta**: `/Users/sopira/www/thermal_eye/apps/table_state/`

Abstraktný modul pre table state management (filtre, stĺpce, ordering, presets).

**Kľúčové súbory**:
- `models.py` - TableStatePreset model (importovaný do measurement)
- `engine.py` - Table state logika
- `viewsets.py` - Table state API endpoints

## Modely (measurement/models.py)

Všetky modely sú definované v jednom súbore `/Users/sopira/www/thermal_eye/measurement/models.py`.

### Abstraktné base modely

1. **TimeStampedModel** (abstract)
   - `id` (UUID, primary key)
   - `uuid` (UUID, unique, indexed)
   - `created` (DateTime, auto_now_add, indexed)
   - `updated` (DateTime, auto_now)
   - `active` (Boolean, default=True, indexed) - soft delete flag
   - `visible` (Boolean, default=True, indexed) - UI visibility flag

2. **NamedWithCodeModel** (abstract, extends TimeStampedModel)
   - `human_id` (CharField, nullable, indexed)
   - `code` (CharField, indexed)
   - `name` (CharField, indexed)
   - `comment` (TextField)
   - `note` (TextField)
   - `tags` (GenericRelation to TaggedItem)
   - Methods: `tag_names()`, `set_tags()`, `_get_factory_scope()`

3. **PhotoBase** (abstract, extends TimeStampedModel)
   - `image` (ImageField)
   - `title` (CharField)
   - `caption` (CharField)

### Tagovanie

4. **Tag** (extends TimeStampedModel)
   - `name` (CharField, indexed)
   - `slug` (SlugField, nullable, indexed)
   - `factory` (ForeignKey to Factory, nullable) - scope
   - `content_type` (ForeignKey to ContentType, nullable) - scope
   - Unique constraint: (name_lower, factory, content_type)

5. **TaggedItem** (extends TimeStampedModel)
   - `tag` (ForeignKey to Tag)
   - `content_type` (ForeignKey to ContentType)
   - `object_id` (UUIDField)
   - `content_object` (GenericForeignKey)
   - Unique constraint: (tag, content_type, object_id)

### Hlavné business entity

6. **Factory** (extends NamedWithCodeModel)
   - `address` (CharField)
   - `created_by` (ForeignKey to User)
   - Unique constraints: (created_by, code), (created_by, name), (human_id)

7. **Location** (extends NamedWithCodeModel)
   - `factory` (ForeignKey to Factory)
   - Unique constraints: (factory, code), (factory, name), (factory, human_id)

8. **Carrier** (extends NamedWithCodeModel)
   - `factory` (ForeignKey to Factory)
   - Unique constraints: (factory, code), (factory, name), (factory, human_id)

9. **Driver** (extends NamedWithCodeModel)
   - `factory` (ForeignKey to Factory)
   - `avatar` (ImageField, nullable)
   - Unique constraints: (factory, code), (factory, name), (factory, human_id)

10. **Pot** (extends NamedWithCodeModel)
    - `factory` (ForeignKey to Factory)
    - `knocks_max` (PositiveIntegerField, default=25, max=25)
    - `weight_nominal_kg` (DecimalField, nullable)
    - Unique constraints: (factory, code), (factory, name), (factory, human_id)

11. **Pit** (extends NamedWithCodeModel)
    - `factory` (ForeignKey to Factory)
    - `location` (ForeignKey to Location, nullable)
    - `capacity_tons` (DecimalField, nullable)
    - `is_active` (BooleanField, default=True)
    - Unique constraints: (factory, code), (factory, name), (factory, human_id)

12. **Machine** (extends NamedWithCodeModel)
    - `factory` (ForeignKey to Factory)
    - `machine_uuid` (UUIDField, unique, indexed)
    - `firmware_number` (CharField)
    - `config_hardware` (JSONField, nullable)
    - `config_software` (JSONField, nullable)
    - `machine_log` (JSONField, nullable)
    - `machine_state` (JSONField, nullable)
    - Unique constraints: (factory, code), (factory, name), (factory, human_id)

13. **Camera** (extends NamedWithCodeModel)
    - `factory` (ForeignKey to Factory, nullable)
    - `location` (ForeignKey to Location, nullable)
    - `manufacturer`, `manufacturer_name`, `camera_serie`, `camera_sn` (CharField)
    - `purchased_date`, `installed_date`, `fw_updated_date` (DateField, nullable)
    - `fw_number`, `installation_type` (CharField)
    - `ip` (GenericIPAddressField, nullable)
    - `port`, `http_port`, `rtsp_port` (PositiveIntegerField)
    - `port_type`, `protocol`, `channel`, `stream_type` (CharField)
    - `resolution`, `video_quality`, `bitrate`, `max_bitrate`, `video_encoding` (CharField)
    - `iframe_interval` (PositiveIntegerField, nullable)
    - `video_path`, `picture_path`, `path_prefix`, `path_suffix` (CharField)
    - `settings_payload` (JSONField)
    - `credential` (ForeignKey to ServiceCredential, nullable)
    - `environment` (ForeignKey to MicroserviceEnvironment, nullable)

14. **Measurement** (extends TimeStampedModel)
    - `tags` (GenericRelation to TaggedItem)
    - `dump_date` (DateField, indexed)
    - `dump_time` (TimeField, indexed)
    - `factory` (ForeignKey to Factory)
    - `location` (ForeignKey to Location)
    - `carrier` (ForeignKey to Carrier)
    - `driver` (ForeignKey to Driver)
    - `pot` (ForeignKey to Pot)
    - `pit` (ForeignKey to Pit, nullable)
    - `pit_number` (CharField)
    - `machine` (ForeignKey to Machine, nullable)
    - `pot_side` (CharField, choices: FRONT/BACK/NONE)
    - `pot_knocks` (PositiveIntegerField, 0-25)
    - `pot_knocks_measurement` (PositiveIntegerField, nullable, 0-25)
    - `pot_weight_kg` (DecimalField)
    - `roi_temp_max_c`, `roi_temp_mean_c`, `roi_temp_min_c` (DecimalField, nullable)
    - `roc_value_min_c`, `roc_value_max_c` (DecimalField, nullable)
    - `video_local_file` (FileField, nullable)
    - `photo_local_file` (FileField, nullable)
    - `graph_roc`, `graph_temp` (JSONField, nullable)
    - `comment`, `note` (TextField)
    - Default ordering: `-dump_date`, `-dump_time`, `-id`

### Foto modely

15. **FactoryPhoto** (extends PhotoBase)
    - `factory` (ForeignKey to Factory)

16. **DriverPhoto** (extends PhotoBase)
    - `driver` (ForeignKey to Driver)

17. **PotPhoto** (extends PhotoBase)
    - `pot` (ForeignKey to Pot)

18. **MeasurementPhoto** (extends PhotoBase)
    - `measurement` (ForeignKey to Measurement)

### Video a Photo URL modely

19. **MeasurementVideo** (extends TimeStampedModel)
    - `measurement` (ForeignKey to Measurement)
    - `url` (URLField)
    - `title` (CharField)
    - `order` (PositiveIntegerField, default=0)

20. **MeasurementPhotoURL** (extends TimeStampedModel)
    - `measurement` (ForeignKey to Measurement)
    - `url` (URLField)
    - `title` (CharField)
    - `order` (PositiveIntegerField, default=0)

### Konfiguračné modely

21. **FactoryPreference** (extends NamedWithCodeModel)
    - `factory` (OneToOneField to Factory)
    - `settings`, `workflows`, `templates`, `habits`, `customs`, `news` (JSONField)

22. **ServiceCredential** (extends NamedWithCodeModel)
    - `factory` (ForeignKey to Factory, nullable)
    - `scope` (CharField)
    - `username` (CharField)
    - `secret` (BinaryField) - encrypted
    - `secret_hint` (CharField)
    - `metadata` (JSONField)
    - Methods: `set_secret()`, `get_secret()` - XOR encryption

23. **MicroserviceEnvironment** (extends NamedWithCodeModel)
    - `environment_type` (CharField, choices: LOCAL/PRODUCTION/STAGING/CUSTOM)
    - `description` (TextField)
    - `base_url`, `stream_host` (CharField)
    - `stream_port`, `http_port`, `rtsp_port` (PositiveIntegerField)
    - `config` (JSONField)
    - `credential` (ForeignKey to ServiceCredential, nullable)

### Logging a workflow modely

24. **LogEntry** (extends NamedWithCodeModel)
    - `level` (CharField, choices: INFO/WARNING/ERROR/CRITICAL/DEBUG)
    - `action` (CharField)
    - `user` (ForeignKey to User, nullable)
    - `factory` (ForeignKey to Factory, nullable)
    - `camera` (ForeignKey to Camera, nullable)
    - `environment` (ForeignKey to MicroserviceEnvironment, nullable)
    - `target_model`, `target_identifier`, `outcome` (CharField)
    - `message` (TextField)
    - `metadata` (JSONField)
    - Default ordering: `-created`

25. **Action** (extends NamedWithCodeModel)
    - `action_type` (CharField, choices: TASK/ALERT/COMMAND/MAINTENANCE/OTHER)
    - `created_by`, `addressed_to`, `actor` (ForeignKey to User, nullable)
    - `factory` (ForeignKey to Factory, nullable)
    - `camera` (ForeignKey to Camera, nullable)
    - `environment` (ForeignKey to MicroserviceEnvironment, nullable)
    - `target_model`, `target_identifier`, `outcome` (CharField)
    - `message` (TextField)
    - `metadata` (JSONField)

26. **Workflow** (extends NamedWithCodeModel)
    - `workflow_type` (CharField, choices: AUTOMATION/SCHEDULE/APPROVAL/CHECKLIST/OTHER)
    - `created_by`, `addressed_to` (ForeignKey to User, nullable)
    - `actions_payload` (JSONField) - list of actions/commands
    - `repeat` (BooleanField)
    - `repeat_when` (CharField)
    - `result` (CharField)

### User preferences

27. **UserPreference** (extends TimeStampedModel)
    - `user` (OneToOneField to User)
    - `selected_factories` (JSONField) - list of UUIDs
    - `accessible_factories` (JSONField) - list of UUIDs
    - `seed_config` (JSONField)
    - `general_settings`, `custom_habits`, `special_preferences` (JSONField)
    - `role` (CharField, choices: SUPERUSER/ADMIN/STAFF/EDITOR/READER/ADHOC)
    - Methods: `is_adhoc()`, `is_reader()`, `is_editor()`, `is_staff_level()`, `is_admin()`, `is_superuser_role()`, `can_read()`, `can_edit()`, `can_export()`, `can_manage_factories()`, `can_manage_users()`, `can_generate_seeds()`, `sync_user_flags()`
    - Class methods: `user_can_read()`, `user_can_edit()`, `user_can_export()`, `user_can_manage_factories()`, `user_can_manage_users()`, `user_can_generate_seeds()`, `user_is_admin()`, `user_is_superuser()`, `role_for_user()`, `has_min_role()`

### Cache a state modely

28. **FKOptionsCache** (extends models.Model)
    - `field_name` (CharField) - FK field name (e.g., 'location', 'carrier')
    - `factory` (ForeignKey to Factory, nullable) - scope
    - `options` (JSONField) - cached FK options array
    - `last_updated` (DateTimeField, auto_now, indexed)
    - `record_count` (IntegerField)
    - Unique together: (field_name, factory)

29. **TableStatePreset** (imported from models_state.py)
    - Definovaný v `measurement/models_state.py`
    - Používa `apps.table_state` infra

## API vrstva (measurement/api/)

### Config-driven architektúra

**VIEWS_MATRIX** (`view_configs.py`) - SSOT pre všetky viewsety:

Definuje pre každý model:
- Model & serializers
- Query optimization (select_related, prefetch_related)
- Permissions & ownership
- Search & filter configuration
- Features (soft_delete, factory_scoped, dynamic_search)
- Ownership hierarchy (SSOT pre scoping)
- FK display templates
- Custom hooks

**Modely v VIEWS_MATRIX**:
- `locations` - Location
- `carriers` - Carrier
- `drivers` - Driver
- `pots` - Pot
- `pits` - Pit
- `factories` - Factory
- `cameras` - Camera
- `machines` - Machine
- `measurements` - Measurement
- `environments` - MicroserviceEnvironment
- `logs` - LogEntry

**CUSTOM_ENDPOINTS** (`view_configs.py`) - Custom API endpoints:
- Authentication: `auth/login/`, `auth/logout/`, `auth/signup/`, `auth/check/`, `auth/csrf/`, `auth/forgot-password/`, `auth/reset-password/`
- User preferences: `user/preferences/`, `user/filters/`, `user/columns/`
- Table state: `table-state/sync-scope/`
- Factory sharing: `factories/share/`
- Configuration: `config/dummy/`, `factory-code-index/`
- Generation: `generate-dummy/`, `generate-dummy/stream/`, `generate-seeds/stream/`, `generate-seeds/auto/stream/`, `generate-measurements/stream/`, `generate-measurements/auto/stream/`, `generate-users/stream/`, `seed-config/`
- Tags: `tags/suggest/`
- Model metadata: `models/metadata/`
- FK cache: `fk-options-cache/`, `fk-options-cache/rebuild/`, `fk-options-cache/rebuild-scope/`
- Camera: `camera-streams/internal/`, `camera-streams/catalog/`, `camera-proxy/`
- Database operations: `clear-database/`, `delete-n-measurements/`, `delete-measurements-only/`, `delete-fk-entities/`, `sort-records/`

### Serializers (`serializers.py`)

- **LookupSerializer** - Pre FK dropdowns (Location, Carrier, Driver, Pot, Pit)
- **LookupWriteSerializer** - Pre zápis FK entít
- **MySerializer** - Config-driven serializer factory (používa VIEWS_MATRIX)
- **FactorySerializer**, **CameraSerializer**, **MachineSerializer**, **MeasurementSerializer**, **LogEntrySerializer** - Nahradené MySerializer

### Filters (`filters.py`)

- **FactoryFilter** - Pre Factory model
- **MeasurementFilter** - Pre Measurement model

### Views (`my_view.py`)

- **MyViewSet** - Config-driven viewset factory
- Automaticky generuje viewsety z VIEWS_MATRIX
- Integrácia so ScopingEngine
- Integrácia s table state
- Soft delete support
- Dynamic search support

### URLs (`my_urls.py`, `urls.py`)

- **MyUrls** - Config-driven URL generator
- Automaticky generuje URL patterns z VIEWS_MATRIX a CUSTOM_ENDPOINTS
- Všetky CRUD endpoints sú generované automaticky

## Signals

1. **signals.py** - Základné Django signals
2. **signals_audit.py** - Audit logging signals
3. **signals_fk_cache.py** - FK cache rebuild signals (automaticky rebuilduje FKOptionsCache)
4. **signals_table_state.py** - Table state signals

## Middleware

1. **middleware_api_logging.py** - APILoggingMiddleware
   - Loguje všetky API requesty (method, path, status code, response time)

2. **middleware_audit.py** - AuditContextMiddleware
   - Ukladá request context do thread-local storage pre audit logging
   - Musí byť AFTER AuthenticationMiddleware

## Management commands

**Cesta**: `/Users/sopira/www/thermal_eye/measurement/management/commands/`

- `cleanup_duplicate_snapshots.py` - Cleanup duplikátnych snapshotov
- `rebuild_fk_cache.py` - Rebuild FK cache
- `seed_cameras.py` - Seed kamier
- `seed_logentries.py` - Seed log entries

## Migrations

**Cesta**: `/Users/sopira/www/thermal_eye/measurement/migrations/`

- `0001_initial.py` - Počiatočná migrácia
- `0002_add_created_by_to_factory.py`
- `0003_action_camera_factorypreference_logentry_and_more.py`
- `0004_table_state_presets.py`
- `0005_columnstate.py`
- `0006_rename_logentry_actor_to_user.py`
- `0007_fix_factory_unique_constraints.py`
- `0008_add_accessible_factories.py`
- `0009_remove_columnstate.py`
- `0010_make_table_name_nullable.py`
- `0011_alter_measurement_pot_weight_kg_fkoptionscache.py`
- `0012_sync_existing_users_roles.py`
- `0013_add_unique_constraints_table_state_preset.py`

## Config-driven patterns

### VIEWS_MATRIX (SSOT)

Všetky API viewsety sú definované v `VIEWS_MATRIX` v `view_configs.py`. Každý model má konfiguráciu obsahujúcu:
- Model & serializers
- Query optimization
- Permissions & ownership
- Ownership hierarchy (pre scoping)
- Search & filter configuration
- Features (soft_delete, factory_scoped, dynamic_search)
- FK display templates
- Custom hooks

### Scoping Engine

- Používa `apps.scoping.ScopingEngine`
- Ownership hierarchy je definovaná v VIEWS_MATRIX (`ownership_hierarchy`, `scope_level_metadata`)
- Automaticky aplikuje scoping pravidlá na základe user preferences (`selected_factories`, `accessible_factories`)

### Table State

- Používa `apps.table_state` infra
- TableStatePreset model pre ukladanie presetov
- Dynamic search fields z table state

### FK Cache

- FKOptionsCache model pre caching FK options
- Automaticky rebuilduje cez signals (`signals_fk_cache.py`)
- Endpointy: `/api/fk-options-cache/`, `/api/fk-options-cache/rebuild/`, `/api/fk-options-cache/rebuild-scope/`

## Mapovanie model → app → súbory

| Model | App | models.py | Serializer | Viewset | Filter | URLs |
|-------|-----|-----------|------------|---------|--------|------|
| Factory | measurement | ✅ | MySerializer | MyViewSet | FactoryFilter | Auto-generated |
| Location | measurement | ✅ | LookupSerializer | MyViewSet | - | Auto-generated |
| Carrier | measurement | ✅ | LookupSerializer | MyViewSet | - | Auto-generated |
| Driver | measurement | ✅ | LookupSerializer | MyViewSet | - | Auto-generated |
| Pot | measurement | ✅ | LookupSerializer | MyViewSet | - | Auto-generated |
| Pit | measurement | ✅ | LookupSerializer | MyViewSet | - | Auto-generated |
| Machine | measurement | ✅ | MySerializer | MyViewSet | - | Auto-generated |
| Camera | measurement | ✅ | MySerializer | MyViewSet | - | Auto-generated |
| Measurement | measurement | ✅ | MySerializer | MyViewSet | MeasurementFilter | Auto-generated |
| MicroserviceEnvironment | measurement | ✅ | LookupSerializer | MyViewSet | - | Auto-generated |
| LogEntry | measurement | ✅ | MySerializer | MyViewSet | - | Auto-generated |
| Tag | measurement | ✅ | - | - | - | - |
| TaggedItem | measurement | ✅ | - | - | - | - |
| FactoryPhoto | measurement | ✅ | - | - | - | - |
| DriverPhoto | measurement | ✅ | - | - | - | - |
| PotPhoto | measurement | ✅ | - | - | - | - |
| MeasurementPhoto | measurement | ✅ | - | - | - | - |
| MeasurementVideo | measurement | ✅ | - | - | - | - |
| MeasurementPhotoURL | measurement | ✅ | - | - | - | - |
| FactoryPreference | measurement | ✅ | - | - | - | - |
| ServiceCredential | measurement | ✅ | - | - | - | - |
| Action | measurement | ✅ | - | - | - | - |
| Workflow | measurement | ✅ | - | - | - | - |
| UserPreference | measurement | ✅ | - | - | - | - |
| FKOptionsCache | measurement | ✅ | - | - | - | - |
| TableStatePreset | measurement | ✅ (models_state.py) | - | TableStateViewSet | - | Auto-generated |

## Dôležité poznámky

1. **Všetky modely v jednej aplikácii**: Thermal Eye má všetky modely v `measurement` aplikácii, nie v separátnych apps.

2. **Config-driven architektúra**: VIEWS_MATRIX je SSOT pre všetky API viewsety. Všetko je generované automaticky.

3. **Scoping Engine**: Používa abstraktný `apps.scoping` modul s ownership hierarchy definovanou v VIEWS_MATRIX.

4. **Table State**: Používa abstraktný `apps.table_state` modul pre ukladanie presetov a state.

5. **FK Cache**: Automaticky rebuilduje cez signals pri zmene FK entít.

6. **Soft Delete**: Väčšina modelov používa `active=False` namiesto hard delete (okrem Measurement, LogEntry, Action, Workflow).

7. **Permissions**: Používa UserPreference.role ako SSOT pre permissions (nie Django flags).

8. **Ownership Hierarchy**: Definovaná v VIEWS_MATRIX pre každý model. Používa sa ScopingEngine pre automatické filtrovanie.

