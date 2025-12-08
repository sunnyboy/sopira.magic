# Model Path Map - SSOT Mapa modelov Thermal Eye → Sopira.magic

## Prehľad

Tento dokument je **Single Source of Truth (SSOT)** pre mapovanie modelov medzi Thermal Eye a sopira.magic. Definuje presné cesty, kde sa nachádzajú modely v oboch projektoch a ako sa budú migrovať.

## Konvencie

- **Thermal Eye backend**: `/Users/sopira/www/thermal_eye`
- **Thermal Eye UI frontend**: `/Users/sopira/www/thermal_eye_ui`
- **Sopira.magic backend**: `/Users/sopira/sopira.magic/version_01/sopira_magic/apps/`
- **Sopira.magic frontend**: `/Users/sopira/sopira.magic/version_01/frontend/src/apps/`

## Mapovanie modelov

### 1. Factory

| Aspekt | Thermal Eye | Sopira.magic | Status |
|--------|-------------|--------------|--------|
| **Backend Model** | `measurement/models.py` → `Factory` | `m_factory/models.py` → `Factory` | ✅ Existuje (placeholder) |
| **Backend App** | `measurement` | `m_factory` | ✅ Existuje |
| **Backend Path** | `/Users/sopira/www/thermal_eye/measurement/models.py` | `/Users/sopira/sopira.magic/version_01/sopira_magic/apps/m_factory/models.py` | - |
| **Serializer** | `measurement/api/serializers.py` → `MySerializer` | `m_factory/serializers.py` (treba vytvoriť) | ❌ Chýba |
| **Viewset** | `measurement/api/my_view.py` → `MyViewSet` | `m_factory/views.py` (treba vytvoriť) | ❌ Chýba |
| **Filter** | `measurement/api/filters.py` → `FactoryFilter` | `m_factory/filters.py` (treba vytvoriť) | ❌ Chýba |
| **URLs** | `measurement/api/urls.py` → Auto-generated | `m_factory/urls.py` (treba vytvoriť) | ❌ Chýba |
| **VIEWS_MATRIX** | `measurement/api/view_configs.py` → `"factories"` | `api/view_configs.py` → `"factories"` (treba pridať) | ❌ Chýba |
| **Frontend Page** | `pages/FactoryTable.tsx` | `apps/factory/FactoryTable.tsx` (treba vytvoriť) | ❌ Chýba |
| **Frontend Config** | `pages/FactoryTable.tsx` → `MyTableConfig` | `apps/factory/factoryTableConfig.ts` (treba vytvoriť) | ❌ Chýba |
| **Frontend Route** | `/factories` | `/factories` | - |
| **Relation Module** | Hardcoded FK `created_by` | `relation/config.py` → `factory_user` | ❌ Chýba |

### 2. Location

| Aspekt | Thermal Eye | Sopira.magic | Status |
|--------|-------------|--------------|--------|
| **Backend Model** | `measurement/models.py` → `Location` | `m_location/models.py` → `Location` | ❌ Treba vytvoriť |
| **Backend App** | `measurement` | `m_location` | ❌ Treba vytvoriť |
| **Backend Path** | `/Users/sopira/www/thermal_eye/measurement/models.py` | `/Users/sopira/sopira.magic/version_01/sopira_magic/apps/m_location/models.py` | - |
| **Serializer** | `measurement/api/serializers.py` → `LookupSerializer` | `m_location/serializers.py` (treba vytvoriť) | ❌ Chýba |
| **Viewset** | `measurement/api/my_view.py` → `MyViewSet` | `m_location/views.py` (treba vytvoriť) | ❌ Chýba |
| **Filter** | - | `m_location/filters.py` (treba vytvoriť) | ❌ Chýba |
| **URLs** | `measurement/api/urls.py` → Auto-generated | `m_location/urls.py` (treba vytvoriť) | ❌ Chýba |
| **VIEWS_MATRIX** | `measurement/api/view_configs.py` → `"locations"` | `api/view_configs.py` → `"locations"` (treba pridať) | ❌ Chýba |
| **Frontend Page** | `pages/lookups/LocationsTable.tsx` | `apps/location/LocationsTable.tsx` (treba vytvoriť) | ❌ Chýba |
| **Frontend Config** | `pages/lookups/LocationsTable.tsx` → `MyTableConfig` | `apps/location/locationTableConfig.ts` (treba vytvoriť) | ❌ Chýba |
| **Frontend Route** | `/locations` | `/locations` | - |
| **Relation Module** | Hardcoded FK `factory` | `relation/config.py` → `location_factory` | ❌ Chýba |

### 3. Carrier

| Aspekt | Thermal Eye | Sopira.magic | Status |
|--------|-------------|--------------|--------|
| **Backend Model** | `measurement/models.py` → `Carrier` | `m_carrier/models.py` → `Carrier` | ❌ Treba vytvoriť |
| **Backend App** | `measurement` | `m_carrier` | ❌ Treba vytvoriť |
| **Backend Path** | `/Users/sopira/www/thermal_eye/measurement/models.py` | `/Users/sopira/sopira.magic/version_01/sopira_magic/apps/m_carrier/models.py` | - |
| **Serializer** | `measurement/api/serializers.py` → `LookupSerializer` | `m_carrier/serializers.py` (treba vytvoriť) | ❌ Chýba |
| **Viewset** | `measurement/api/my_view.py` → `MyViewSet` | `m_carrier/views.py` (treba vytvoriť) | ❌ Chýba |
| **Filter** | - | `m_carrier/filters.py` (treba vytvoriť) | ❌ Chýba |
| **URLs** | `measurement/api/urls.py` → Auto-generated | `m_carrier/urls.py` (treba vytvoriť) | ❌ Chýba |
| **VIEWS_MATRIX** | `measurement/api/view_configs.py` → `"carriers"` | `api/view_configs.py` → `"carriers"` (treba pridať) | ❌ Chýba |
| **Frontend Page** | `pages/lookups/CarriersTable.tsx` | `apps/carrier/CarriersTable.tsx` (treba vytvoriť) | ❌ Chýba |
| **Frontend Config** | `pages/lookups/CarriersTable.tsx` → `MyTableConfig` | `apps/carrier/carrierTableConfig.ts` (treba vytvoriť) | ❌ Chýba |
| **Frontend Route** | `/carriers` | `/carriers` | - |
| **Relation Module** | Hardcoded FK `factory` | `relation/config.py` → `carrier_factory` | ❌ Chýba |

### 4. Driver

| Aspekt | Thermal Eye | Sopira.magic | Status |
|--------|-------------|--------------|--------|
| **Backend Model** | `measurement/models.py` → `Driver` | `m_driver/models.py` → `Driver` | ❌ Treba vytvoriť |
| **Backend App** | `measurement` | `m_driver` | ❌ Treba vytvoriť |
| **Backend Path** | `/Users/sopira/www/thermal_eye/measurement/models.py` | `/Users/sopira/sopira.magic/version_01/sopira_magic/apps/m_driver/models.py` | - |
| **Serializer** | `measurement/api/serializers.py` → `LookupSerializer` | `m_driver/serializers.py` (treba vytvoriť) | ❌ Chýba |
| **Viewset** | `measurement/api/my_view.py` → `MyViewSet` | `m_driver/views.py` (treba vytvoriť) | ❌ Chýba |
| **Filter** | - | `m_driver/filters.py` (treba vytvoriť) | ❌ Chýba |
| **URLs** | `measurement/api/urls.py` → Auto-generated | `m_driver/urls.py` (treba vytvoriť) | ❌ Chýba |
| **VIEWS_MATRIX** | `measurement/api/view_configs.py` → `"drivers"` | `api/view_configs.py` → `"drivers"` (treba pridať) | ❌ Chýba |
| **Frontend Page** | `pages/lookups/DriversTable.tsx` | `apps/driver/DriversTable.tsx` (treba vytvoriť) | ❌ Chýba |
| **Frontend Config** | `pages/lookups/DriversTable.tsx` → `MyTableConfig` | `apps/driver/driverTableConfig.ts` (treba vytvoriť) | ❌ Chýba |
| **Frontend Route** | `/drivers` | `/drivers` | - |
| **Relation Module** | Hardcoded FK `factory` | `relation/config.py` → `driver_factory` | ❌ Chýba |

### 5. Pot

| Aspekt | Thermal Eye | Sopira.magic | Status |
|--------|-------------|--------------|--------|
| **Backend Model** | `measurement/models.py` → `Pot` | `m_pot/models.py` → `Pot` | ❌ Treba vytvoriť |
| **Backend App** | `measurement` | `m_pot` | ❌ Treba vytvoriť |
| **Backend Path** | `/Users/sopira/www/thermal_eye/measurement/models.py` | `/Users/sopira/sopira.magic/version_01/sopira_magic/apps/m_pot/models.py` | - |
| **Serializer** | `measurement/api/serializers.py` → `LookupSerializer` | `m_pot/serializers.py` (treba vytvoriť) | ❌ Chýba |
| **Viewset** | `measurement/api/my_view.py` → `MyViewSet` | `m_pot/views.py` (treba vytvoriť) | ❌ Chýba |
| **Filter** | - | `m_pot/filters.py` (treba vytvoriť) | ❌ Chýba |
| **URLs** | `measurement/api/urls.py` → Auto-generated | `m_pot/urls.py` (treba vytvoriť) | ❌ Chýba |
| **VIEWS_MATRIX** | `measurement/api/view_configs.py` → `"pots"` | `api/view_configs.py` → `"pots"` (treba pridať) | ❌ Chýba |
| **Frontend Page** | `pages/lookups/PotsTable.tsx` | `apps/pot/PotsTable.tsx` (treba vytvoriť) | ❌ Chýba |
| **Frontend Config** | `pages/lookups/PotsTable.tsx` → `MyTableConfig` | `apps/pot/potTableConfig.ts` (treba vytvoriť) | ❌ Chýba |
| **Frontend Route** | `/pots` | `/pots` | - |
| **Relation Module** | Hardcoded FK `factory` | `relation/config.py` → `pot_factory` | ❌ Chýba |

### 6. Pit

| Aspekt | Thermal Eye | Sopira.magic | Status |
|--------|-------------|--------------|--------|
| **Backend Model** | `measurement/models.py` → `Pit` | `m_pit/models.py` → `Pit` | ❌ Treba vytvoriť |
| **Backend App** | `measurement` | `m_pit` | ❌ Treba vytvoriť |
| **Backend Path** | `/Users/sopira/www/thermal_eye/measurement/models.py` | `/Users/sopira/sopira.magic/version_01/sopira_magic/apps/m_pit/models.py` | - |
| **Serializer** | `measurement/api/serializers.py` → `LookupSerializer` | `m_pit/serializers.py` (treba vytvoriť) | ❌ Chýba |
| **Viewset** | `measurement/api/my_view.py` → `MyViewSet` | `m_pit/views.py` (treba vytvoriť) | ❌ Chýba |
| **Filter** | - | `m_pit/filters.py` (treba vytvoriť) | ❌ Chýba |
| **URLs** | `measurement/api/urls.py` → Auto-generated | `m_pit/urls.py` (treba vytvoriť) | ❌ Chýba |
| **VIEWS_MATRIX** | `measurement/api/view_configs.py` → `"pits"` | `api/view_configs.py` → `"pits"` (treba pridať) | ❌ Chýba |
| **Frontend Page** | `pages/lookups/PitsTable.tsx` | `apps/pit/PitsTable.tsx` (treba vytvoriť) | ❌ Chýba |
| **Frontend Config** | `pages/lookups/PitsTable.tsx` → `MyTableConfig` | `apps/pit/pitTableConfig.ts` (treba vytvoriť) | ❌ Chýba |
| **Frontend Route** | `/pits` | `/pits` | - |
| **Relation Module** | Hardcoded FK `factory`, `location` | `relation/config.py` → `pit_factory`, `pit_location` | ❌ Chýba |

### 7. Machine

| Aspekt | Thermal Eye | Sopira.magic | Status |
|--------|-------------|--------------|--------|
| **Backend Model** | `measurement/models.py` → `Machine` | `m_machine/models.py` → `Machine` | ❌ Treba vytvoriť |
| **Backend App** | `measurement` | `m_machine` | ❌ Treba vytvoriť |
| **Backend Path** | `/Users/sopira/www/thermal_eye/measurement/models.py` | `/Users/sopira/sopira.magic/version_01/sopira_magic/apps/m_machine/models.py` | - |
| **Serializer** | `measurement/api/serializers.py` → `MySerializer` | `m_machine/serializers.py` (treba vytvoriť) | ❌ Chýba |
| **Viewset** | `measurement/api/my_view.py` → `MyViewSet` | `m_machine/views.py` (treba vytvoriť) | ❌ Chýba |
| **Filter** | - | `m_machine/filters.py` (treba vytvoriť) | ❌ Chýba |
| **URLs** | `measurement/api/urls.py` → Auto-generated | `m_machine/urls.py` (treba vytvoriť) | ❌ Chýba |
| **VIEWS_MATRIX** | `measurement/api/view_configs.py` → `"machines"` | `api/view_configs.py` → `"machines"` (treba pridať) | ❌ Chýba |
| **Frontend Page** | `pages/lookups/MachinesTable.tsx` | `apps/machine/MachinesTable.tsx` (treba vytvoriť) | ❌ Chýba |
| **Frontend Config** | `pages/lookups/MachinesTable.tsx` → `MyTableConfig` | `apps/machine/machineTableConfig.ts` (treba vytvoriť) | ❌ Chýba |
| **Frontend Route** | `/machines` | `/machines` | - |
| **Relation Module** | Hardcoded FK `factory` | `relation/config.py` → `machine_factory` | ❌ Chýba |

### 8. Camera

| Aspekt | Thermal Eye | Sopira.magic | Status |
|--------|-------------|--------------|--------|
| **Backend Model** | `measurement/models.py` → `Camera` | `m_camera/models.py` → `Camera` | ❌ Treba vytvoriť |
| **Backend App** | `measurement` | `m_camera` | ❌ Treba vytvoriť |
| **Backend Path** | `/Users/sopira/www/thermal_eye/measurement/models.py` | `/Users/sopira/sopira.magic/version_01/sopira_magic/apps/m_camera/models.py` | - |
| **Serializer** | `measurement/api/serializers.py` → `MySerializer` | `m_camera/serializers.py` (treba vytvoriť) | ❌ Chýba |
| **Viewset** | `measurement/api/my_view.py` → `MyViewSet` | `m_camera/views.py` (treba vytvoriť) | ❌ Chýba |
| **Filter** | - | `m_camera/filters.py` (treba vytvoriť) | ❌ Chýba |
| **URLs** | `measurement/api/urls.py` → Auto-generated | `m_camera/urls.py` (treba vytvoriť) | ❌ Chýba |
| **VIEWS_MATRIX** | `measurement/api/view_configs.py` → `"cameras"` | `api/view_configs.py` → `"cameras"` (treba pridať) | ❌ Chýba |
| **Frontend Page** | `pages/Camera.tsx` | `apps/camera/Camera.tsx` (treba vytvoriť) | ❌ Chýba |
| **Frontend Config** | `pages/Camera.tsx` → `MyTableConfig` | `apps/camera/cameraTableConfig.ts` (treba vytvoriť) | ❌ Chýba |
| **Frontend Route** | `/camera` | `/camera` | - |
| **Relation Module** | Hardcoded FK `factory`, `location`, `credential`, `environment` | `relation/config.py` → `camera_factory`, `camera_location`, `camera_credential`, `camera_environment` | ❌ Chýba |

### 9. Measurement

| Aspekt | Thermal Eye | Sopira.magic | Status |
|--------|-------------|--------------|--------|
| **Backend Model** | `measurement/models.py` → `Measurement` | `m_measurement/models.py` → `Measurement` | ❌ Treba vytvoriť |
| **Backend App** | `measurement` | `m_measurement` | ❌ Treba vytvoriť |
| **Backend Path** | `/Users/sopira/www/thermal_eye/measurement/models.py` | `/Users/sopira/sopira.magic/version_01/sopira_magic/apps/m_measurement/models.py` | - |
| **Serializer** | `measurement/api/serializers.py` → `MySerializer` | `m_measurement/serializers.py` (treba vytvoriť) | ❌ Chýba |
| **Viewset** | `measurement/api/my_view.py` → `MyViewSet` | `m_measurement/views.py` (treba vytvoriť) | ❌ Chýba |
| **Filter** | `measurement/api/filters.py` → `MeasurementFilter` | `m_measurement/filters.py` (treba vytvoriť) | ❌ Chýba |
| **URLs** | `measurement/api/urls.py` → Auto-generated | `m_measurement/urls.py` (treba vytvoriť) | ❌ Chýba |
| **VIEWS_MATRIX** | `measurement/api/view_configs.py` → `"measurements"` | `api/view_configs.py` → `"measurements"` (treba pridať) | ❌ Chýba |
| **Frontend Page** | `pages/MeasurementsTable.tsx` | `apps/measurement/MeasurementsTable.tsx` (treba vytvoriť) | ❌ Chýba |
| **Frontend Config** | `pages/MeasurementsTable.tsx` → `MyTableConfig` | `apps/measurement/measurementTableConfig.ts` (treba vytvoriť) | ❌ Chýba |
| **Frontend Route** | `/measurements` | `/measurements` | - |
| **Relation Module** | Hardcoded FK `factory`, `location`, `carrier`, `driver`, `pot`, `pit`, `machine` | `relation/config.py` → `measurement_factory`, `measurement_location`, etc. | ❌ Chýba |

### 10. User

| Aspekt | Thermal Eye | Sopira.magic | Status |
|--------|-------------|--------------|--------|
| **Backend Model** | Django `User` + `UserPreference` | `m_user/models.py` → `User` (extends Django User) | ✅ Existuje (čiastočne) |
| **Backend App** | `measurement` (UserPreference) | `m_user` | ✅ Existuje |
| **Backend Path** | `/Users/sopira/www/thermal_eye/measurement/models.py` → `UserPreference` | `/Users/sopira/sopira.magic/version_01/sopira_magic/apps/m_user/models.py` | - |
| **Serializer** | `measurement/api/serializers.py` → `MySerializer` | `m_user/serializers.py` (treba vytvoriť) | ❌ Chýba |
| **Viewset** | `measurement/api/my_view.py` → `MyViewSet` | `m_user/views.py` (treba vytvoriť) | ❌ Chýba |
| **Filter** | - | `m_user/filters.py` (treba vytvoriť) | ❌ Chýba |
| **URLs** | `measurement/api/urls.py` → Auto-generated | `m_user/urls.py` (treba vytvoriť) | ❌ Chýba |
| **VIEWS_MATRIX** | `measurement/api/view_configs.py` → `"users"` | `api/view_configs.py` → `"users"` | ✅ Existuje |
| **Frontend Page** | `pages/UsersTable.tsx` | `apps/user/UsersPage.tsx` | ✅ Existuje (čiastočne) |
| **Frontend Config** | `pages/UsersTable.tsx` → `MyTableConfig` | `apps/user/userTableConfig.ts` | ✅ Existuje |
| **Frontend Route** | `/users` | `/users` | ✅ Existuje |
| **Relation Module** | Hardcoded FK `created_by` | `relation/config.py` → `user_*` | ❌ Chýba |

### 11. Tag

| Aspekt | Thermal Eye | Sopira.magic | Status |
|--------|-------------|--------------|--------|
| **Backend Model** | `measurement/models.py` → `Tag`, `TaggedItem` | `m_tag/models.py` → `Tag`, `TaggedItem` | ✅ Existuje (placeholder) |
| **Backend App** | `measurement` | `m_tag` | ✅ Existuje |
| **Backend Path** | `/Users/sopira/www/thermal_eye/measurement/models.py` | `/Users/sopira/sopira.magic/version_01/sopira_magic/apps/m_tag/models.py` | - |
| **Serializer** | - | `m_tag/serializers.py` (treba vytvoriť) | ❌ Chýba |
| **Viewset** | - | `m_tag/views.py` (treba vytvoriť) | ❌ Chýba |
| **Filter** | - | `m_tag/filters.py` (treba vytvoriť) | ❌ Chýba |
| **URLs** | - | `m_tag/urls.py` (treba vytvoriť) | ❌ Chýba |
| **VIEWS_MATRIX** | - | `api/view_configs.py` → `"tags"` (treba pridať) | ❌ Chýba |
| **Frontend Page** | - | `apps/tag/TagTable.tsx` (treba vytvoriť) | ❌ Chýba |
| **Frontend Config** | - | `apps/tag/tagTableConfig.ts` (treba vytvoriť) | ❌ Chýba |
| **Frontend Route** | - | `/tags` | - |
| **Relation Module** | GenericRelation `TaggedItem` | `relation/config.py` → `tag_*` (generic) | ❌ Chýba |

### 12. Photo

| Aspekt | Thermal Eye | Sopira.magic | Status |
|--------|-------------|--------------|--------|
| **Backend Model** | `measurement/models.py` → `FactoryPhoto`, `DriverPhoto`, `PotPhoto`, `MeasurementPhoto` | `m_photo/models.py` → `Photo` (generic) | ✅ Existuje (placeholder) |
| **Backend App** | `measurement` | `m_photo` | ✅ Existuje |
| **Backend Path** | `/Users/sopira/www/thermal_eye/measurement/models.py` | `/Users/sopira/sopira.magic/version_01/sopira_magic/apps/m_photo/models.py` | - |
| **Serializer** | - | `m_photo/serializers.py` (treba vytvoriť) | ❌ Chýba |
| **Viewset** | - | `m_photo/views.py` (treba vytvoriť) | ❌ Chýba |
| **Filter** | - | `m_photo/filters.py` (treba vytvoriť) | ❌ Chýba |
| **URLs** | - | `m_photo/urls.py` (treba vytvoriť) | ❌ Chýba |
| **VIEWS_MATRIX** | - | `api/view_configs.py` → `"photos"` (treba pridať) | ❌ Chýba |
| **Frontend Page** | - | `apps/photo/PhotoTable.tsx` (treba vytvoriť) | ❌ Chýba |
| **Frontend Config** | - | `apps/photo/photoTableConfig.ts` (treba vytvoriť) | ❌ Chýba |
| **Frontend Route** | - | `/photos` | - |
| **Relation Module** | Hardcoded FK `factory`, `driver`, `pot`, `measurement` | `relation/config.py` → `photo_factory`, `photo_driver`, etc. | ❌ Chýba |

### 13. Video

| Aspekt | Thermal Eye | Sopira.magic | Status |
|--------|-------------|--------------|--------|
| **Backend Model** | `measurement/models.py` → `MeasurementVideo`, `MeasurementPhotoURL` | `m_video/models.py` → `Video` (generic) | ✅ Existuje (placeholder) |
| **Backend App** | `measurement` | `m_video` | ✅ Existuje |
| **Backend Path** | `/Users/sopira/www/thermal_eye/measurement/models.py` | `/Users/sopira/sopira.magic/version_01/sopira_magic/apps/m_video/models.py` | - |
| **Serializer** | - | `m_video/serializers.py` (treba vytvoriť) | ❌ Chýba |
| **Viewset** | - | `m_video/views.py` (treba vytvoriť) | ❌ Chýba |
| **Filter** | - | `m_video/filters.py` (treba vytvoriť) | ❌ Chýba |
| **URLs** | - | `m_video/urls.py` (treba vytvoriť) | ❌ Chýba |
| **VIEWS_MATRIX** | - | `api/view_configs.py` → `"videos"` (treba pridať) | ❌ Chýba |
| **Frontend Page** | - | `apps/video/VideoTable.tsx` (treba vytvoriť) | ❌ Chýba |
| **Frontend Config** | - | `apps/video/videoTableConfig.ts` (treba vytvoriť) | ❌ Chýba |
| **Frontend Route** | - | `/videos` | - |
| **Relation Module** | Hardcoded FK `measurement` | `relation/config.py` → `video_measurement` | ❌ Chýba |

## Cross-cutting moduly

### Scoping

| Aspekt | Thermal Eye | Sopira.magic | Status |
|--------|-------------|--------------|--------|
| **Backend** | `apps/scoping/` | `apps/scoping/` | ✅ Existuje |
| **Frontend** | `contexts/ScopeContext.tsx` | `contexts/ScopeContext.tsx` (treba vytvoriť) | ❌ Chýba |

### Table State

| Aspekt | Thermal Eye | Sopira.magic | Status |
|--------|-------------|--------------|--------|
| **Backend** | `apps/table_state/` | `apps/state/` | ✅ Existuje |
| **Frontend** | `hooks/useSnapshot.tsx` | `hooks/useSnapshot.tsx` (treba vytvoriť) | ❌ Chýba |

### FK Cache

| Aspekt | Thermal Eye | Sopira.magic | Status |
|--------|-------------|--------------|--------|
| **Backend Model** | `measurement/models.py` → `FKOptionsCache` | `api/models.py` → `FKOptionsCache` (treba vytvoriť) | ❌ Chýba |
| **Backend Endpoint** | `measurement/api/views/fk_cache.py` | `api/views/fk_cache.py` (treba vytvoriť) | ❌ Chýba |
| **Frontend Service** | `services/fkCacheService.ts` | `services/fkCacheService.ts` (treba vytvoriť) | ❌ Chýba |

### Model Metadata (SSOT)

| Aspekt | Thermal Eye | Sopira.magic | Status |
|--------|-------------|--------------|--------|
| **Backend** | `measurement/api/view_configs.py` → `VIEWS_MATRIX` | `sopira_magic/config/model_metadata.py` (treba vytvoriť) | ❌ Chýba |
| **Backend Endpoint** | `measurement/api/views/metadata.py` → `model_metadata_view` | `api/views/metadata.py` (treba vytvoriť) | ❌ Chýba |
| **Frontend** | `config/modelMetadata.ts` | `config/modelMetadata.ts` (treba vytvoriť) | ❌ Chýba |

## Zhrnutie

### Backend moduly - Status

| Model | App | Model | Serializer | Viewset | Filter | URLs | VIEWS_MATRIX |
|-------|-----|-------|------------|---------|--------|------|--------------|
| Factory | ✅ | ✅ (placeholder) | ❌ | ❌ | ❌ | ❌ | ❌ |
| Location | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Carrier | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Driver | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Pot | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Pit | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Machine | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Camera | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Measurement | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| User | ✅ | ✅ (čiastočne) | ❌ | ❌ | ❌ | ❌ | ✅ |
| Tag | ✅ | ✅ (placeholder) | ❌ | ❌ | ❌ | ❌ | ❌ |
| Photo | ✅ | ✅ (placeholder) | ❌ | ❌ | ❌ | ❌ | ❌ |
| Video | ✅ | ✅ (placeholder) | ❌ | ❌ | ❌ | ❌ | ❌ |

### Frontend moduly - Status

| Model | Page Component | Config | Route |
|-------|---------------|--------|-------|
| Factory | ❌ | ❌ | ❌ |
| Location | ❌ | ❌ | ❌ |
| Carrier | ❌ | ❌ | ❌ |
| Driver | ❌ | ❌ | ❌ |
| Pot | ❌ | ❌ | ❌ |
| Pit | ❌ | ❌ | ❌ |
| Machine | ❌ | ❌ | ❌ |
| Camera | ❌ | ❌ | ❌ |
| Measurement | ❌ | ❌ | ❌ |
| User | ✅ | ✅ | ✅ |
| Tag | ❌ | ❌ | ❌ |
| Photo | ❌ | ❌ | ❌ |
| Video | ❌ | ❌ | ❌ |

### Cross-cutting infra - Status

| Komponent | Backend | Frontend |
|-----------|---------|----------|
| Scoping | ✅ | ❌ |
| Table State | ✅ | ❌ |
| FK Cache | ❌ | ❌ |
| Model Metadata | ❌ | ❌ |
| MyTable (plne ConfigDriven) | N/A | ❌ |
| AuthContext | N/A | ❌ |
| ScopeContext | N/A | ❌ |
| useSnapshot | N/A | ❌ |
| fkCacheService | N/A | ❌ |

## Migračný plán

### Fáza 1: Backend moduly (per-model)
1. Vytvoriť nové apps: `m_location`, `m_carrier`, `m_driver`, `m_pit`, `m_pot`, `m_machine`, `m_camera`, `m_measurement`
2. Migrovať modely z Thermal Eye do sopira.magic
3. Vytvoriť serializers, viewsets, filters, URLs pre každý model
4. Pridať do VIEWS_MATRIX v `api/view_configs.py`
5. Nahradiť placeholdery v existujúcich moduloch (`m_factory`, `m_tag`, `m_user`, `m_photo`, `m_video`)

### Fáza 2: Frontend moduly (per-model, 1:1 k BE)
1. Vytvoriť frontend moduly v `frontend/src/apps/` pre každý model
2. Migrovať page komponenty z Thermal Eye UI
3. Vytvoriť MyTableConfig pre každý model
4. Pridať routes do `App.tsx`

### Fáza 3: Cross-cutting infra
1. Migrovať `MyTable` z Thermal Eye UI (plne ConfigDriven verzia)
2. Migrovať `config/modelMetadata.ts`
3. Migrovať `contexts/AuthContext.tsx`
4. Migrovať `contexts/ScopeContext.tsx`
5. Migrovať `hooks/useSnapshot.tsx`
6. Migrovať `services/fkCacheService.ts`
7. Migrovať `components/modals/`
8. Migrovať `components/ui_custom/table/`
9. Vytvoriť FK cache backend (`FKOptionsCache` model, endpoints)
10. Vytvoriť model metadata backend (`model_metadata.py`, endpoint)

### Fáza 4: Relation modul
1. Rozšíriť `relation/config.py` o všetky väzby z Thermal Eye
2. Nahradiť hardcoded ForeignKeys v modeloch cez relation modul

