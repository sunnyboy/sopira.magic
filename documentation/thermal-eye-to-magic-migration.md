---
name: thermal-eye-to-magic-migration
overview: Postupná migrácia Thermal Eye backendu a frontendu do projektu sopira.magic s jednotnou ConfigDriven & SSOT architektúrou a 1:1 zrkadlením štruktúry medzi BE a FE.
todos:
  - id: inventory-backend
    content: Urobiť inventúru backendu Thermal Eye (apps, modely, súbory) a zapísať ju do documentation/backend_docs/structure_thermal_eye.md.
    status: pending
  - id: inventory-frontend
    content: Urobiť inventúru frontend Thermal Eye UI (moduly, komponenty, hooks) a zapísať ju do documentation/frontend_docs/structure_thermal_eye_ui.md.
    status: pending
  - id: inventory-sopira-magic
    content: Zmapovať aktuálnu architektúru sopira.magic (BE/FE, existujúce m_* moduly: m_factory, m_tag, m_user, m_photo, m_video) a zapísať ju do architecture_docs/structure_sopira_magic.md.
    status: pending
  - id: model-path-map
    content: Pripraviť SSOT mapu modelov medzi Thermal Eye a sopira.magic v documentation/architecture_docs/model_path_map.md. Backend: sopira_magic/apps/m_*, Frontend: frontend/src/apps/*.
    status: pending
    dependencies:
      - inventory-backend
      - inventory-frontend
      - inventory-sopira-magic
  - id: configdriven-patterns
    content: Zdokumentovať existujúce ConfigDriven&SSOT vzory Thermal Eye a ich aplikáciu v sopira.magic v documentation/architecture_docs/configdriven_patterns.md.
    status: pending
    dependencies:
      - inventory-backend
      - inventory-frontend
  - id: target-architecture-doc
    content: Spísať cieľovú architektúru sopira.magic (BE+FE, 1:1 štruktúra, shared infra, konvencie pre hlavičky súborov) v documentation/architecture_docs/target_architecture_sopira_magic.md.
    status: pending
    dependencies:
      - model-path-map
      - configdriven-patterns
  - id: mytable-migrate
    content: Pripraviť detailný zoznam závislostí Thermal Eye `MyTable` a navrhnúť cieľovú štruktúru balíka `MyTable` v frontend/src/components/MyTable/ v sopira.magic.
    status: pending
    dependencies:
      - configdriven-patterns
      - target-architecture-doc
  - id: mytable-integrate-first-model
    content: Integrovať nový `MyTable` v sopira.magic pre jeden pilotný model (napr. `factory`) v frontend/src/apps/factory/ s plne ConfigDriven konfiguráciou.
    status: pending
    dependencies:
      - mytable-migrate
      - metadata-ssot-backend
      - metadata-ssot-frontend
  - id: metadata-ssot-backend
    content: Centralizovať modelové metadáta na backend strane (Thermal Eye → sopira.magic) v sopira_magic/config/model_metadata.py a napojiť na existujúce moduly.
    status: pending
    dependencies:
      - inventory-backend
      - configdriven-patterns
      - target-architecture-doc
  - id: metadata-ssot-frontend
    content: Vytvoriť frontend mirror modulu s metadátami v frontend/src/config/modelMetadata.ts (endpoints, ownership, ordering, filters) a napojiť na `MyTable` a formuláre.
    status: pending
    dependencies:
      - metadata-ssot-backend
      - inventory-frontend
      - target-architecture-doc
  - id: create-new-backend-modules
    content: Vytvoriť scaffold pre nové backend moduly: m_camera, m_carrier, m_driver, m_location, m_pit, m_pot, m_measurement, m_machine v sopira_magic/apps/ podľa existujúcich m_* modulov.
    status: pending
    dependencies:
      - target-architecture-doc
  - id: per-model-backend-migration
    content: Prejsť modely (factory, location, driver, carrier, pit, pot, machine, measurement, camera, user) a zmigrovať ich backend časti do sopira_magic/apps/m_<model>/ s napojením na SSOT. Nahradiť placeholdery v existujúcich moduloch (m_factory, m_tag, m_user, m_photo, m_video).
    status: pending
    dependencies:
      - metadata-ssot-backend
      - create-new-backend-modules
  - id: create-new-frontend-modules
    content: Vytvoriť scaffold pre nové frontend moduly: camera, carrier, driver, location, pit, pot, measurement, machine v frontend/src/apps/ podľa existujúcich modulov.
    status: pending
    dependencies:
      - target-architecture-doc
  - id: per-model-frontend-migration
    content: Pre tie isté modely vytvoriť/zosúladiť frontend moduly v frontend/src/apps/<model>/ v sopira.magic, používať `MyTable` a shared infra. Aktualizovať existujúce moduly (factory, tag, user, photo, video).
    status: pending
    dependencies:
      - mytable-integrate-first-model
      - metadata-ssot-frontend
      - per-model-backend-migration
      - create-new-frontend-modules
  - id: relation-module-ssot
    content: Pripraviť abstraktný relation modul (typy, interface, config) v sopira_magic/apps/relation/ a frontend/src/apps/relation/ bez konkrétnych tabuliek, pripravený na neskoršie doplnenie väzieb.
    status: pending
    dependencies:
      - metadata-ssot-backend
      - metadata-ssot-frontend
      - target-architecture-doc
  - id: cleanup-legacy
    content: Po úspešnej migrácii postupne odstrániť legacy kód a duplikované helpery z Thermal Eye.
    status: pending
    dependencies:
      - per-model-backend-migration
      - per-model-frontend-migration
      - relation-module-ssot
---

# Migrácia Thermal Eye → sopira.magic (ConfigDriven & SSOT)

## Cieľ

Migrácia komponentu `MyTable` a následne kompletnej aplikácie Thermal Eye (BE + FE) do projektu `sopira.magic` tak, aby:

- **architektúra bola striktne ConfigDriven & SSOT** (žiadny domain‑hardcode v generických vrstvách),
- **FE štruktúra adresárov bola 1:1 zrkadlom BE** (per‑model moduly),
- všetky väzby boli riešené cez **virtuálny relation modul**, nie priamo cez hardcoded tabuľky.

## Cieľová adresárová štruktúra (sopira.magic)

Základné root cesty:

- **sopira.magic root**: `/Users/sopira/sopira.magic/version_01`
- **Thermal Eye backend (zdroj)**: `/Users/sopira/www/thermal_eye`
- **Thermal Eye UI frontend (zdroj)**: `/Users/sopira/www/thermal_eye_ui`

### Backend (cieľ)

V projekte `sopira.magic` budeme backend organizovať takto:

- **backend root**: `/Users/sopira/sopira.magic/version_01/sopira_magic/apps/`
- **jadro/projekt**: `/Users/sopira/sopira.magic/version_01/sopira_magic/`
 - `settings.py`, `urls.py`, shared middleware, atď.
- **centrálne metadáta (SSOT)**: `/Users/sopira/sopira.magic/version_01/sopira_magic/config/` (alebo vhodné miesto podľa existujúcej štruktúry)
 - `model_metadata.py` – definícia VIEWS_MATRIX / model metadát,
 - prípadne ďalšie konfigy (permissions, ownership_hierarchy, default ordering,...).

#### Per‑model apps (1:1 s domain modelmi, všetky dátové modely s prefixom `m_`)

**Existujúce placeholdery/scaffold** (nahradiť placeholder skutočným kódom):

1. **m_factory** (`/Users/sopira/sopira.magic/version_01/sopira_magic/apps/m_factory/`)
   - `__init__.py`
   - `apps.py`
   - `admin.py`
   - `models.py` – Factory model definícia
   - `serializers.py` – Factory serializer
   - `views.py` / `viewsets.py` – Factory viewset
   - `filters.py` – Factory filter set
   - `urls.py` – Factory URL routing
   - `tests/` – test súbory
     - `__init__.py`
     - `test_models.py`
     - `test_serializers.py`
     - `test_views.py`
   - `migrations/` – Django migrations

2. **m_tag** (`/Users/sopira/sopira.magic/version_01/sopira_magic/apps/m_tag/`)
   - Rovnaká štruktúra ako m_factory

3. **m_user** (`/Users/sopira/sopira.magic/version_01/sopira_magic/apps/m_user/`)
   - Rovnaká štruktúra ako m_factory

4. **m_photo** (`/Users/sopira/sopira.magic/version_01/sopira_magic/apps/m_photo/`)
   - Rovnaká štruktúra ako m_factory

5. **m_video** (`/Users/sopira/sopira.magic/version_01/sopira_magic/apps/m_video/`)
   - Rovnaká štruktúra ako m_factory

**Nové moduly** (vytvoriť scaffold podľa existujúcich `m_*` modulov):

6. **m_camera** (`/Users/sopira/sopira.magic/version_01/sopira_magic/apps/m_camera/`)
   - `__init__.py`
   - `apps.py`
   - `admin.py`
   - `models.py` – Camera model definícia
   - `serializers.py` – Camera serializer
   - `views.py` / `viewsets.py` – Camera viewset
   - `filters.py` – Camera filter set
   - `urls.py` – Camera URL routing
   - `tests/` – test súbory
     - `__init__.py`
     - `test_models.py`
     - `test_serializers.py`
     - `test_views.py`
   - `migrations/` – Django migrations

7. **m_carrier** (`/Users/sopira/sopira.magic/version_01/sopira_magic/apps/m_carrier/`)
   - Rovnaká štruktúra ako m_camera

8. **m_driver** (`/Users/sopira/sopira.magic/version_01/sopira_magic/apps/m_driver/`)
   - Rovnaká štruktúra ako m_camera

9. **m_location** (`/Users/sopira/sopira.magic/version_01/sopira_magic/apps/m_location/`)
   - Rovnaká štruktúra ako m_camera

10. **m_pit** (`/Users/sopira/sopira.magic/version_01/sopira_magic/apps/m_pit/`)
    - Rovnaká štruktúra ako m_camera

11. **m_pot** (`/Users/sopira/sopira.magic/version_01/sopira_magic/apps/m_pot/`)
    - Rovnaká štruktúra ako m_camera

12. **m_measurement** (`/Users/sopira/sopira.magic/version_01/sopira_magic/apps/m_measurement/`)
    - Rovnaká štruktúra ako m_camera

13. **m_machine** (`/Users/sopira/sopira.magic/version_01/sopira_magic/apps/m_machine/`)
    - Rovnaká štruktúra ako m_camera

#### Cross‑cutting apps/moduly

- `/Users/sopira/sopira.magic/version_01/sopira_magic/apps/relation/` – abstraktný relation modul (SSOT definícia vzťahov, bez konkrétnych tabuliek v prvej fáze),
- `/Users/sopira/sopira.magic/version_01/sopira_magic/apps/security/` – security a permissions politika,
- `/Users/sopira/sopira.magic/version_01/sopira_magic/apps/state/` – snapshoty, table‑state (ak je na BE),
- `/Users/sopira/sopira.magic/version_01/sopira_magic/apps/scoping/` – scope/ownership logika,
- `/Users/sopira/sopira.magic/version_01/sopira_magic/apps/pdfviewer/` – generovanie reportov, PDF výstupy.

### Frontend (cieľ)

Frontend v `sopira.magic` bude zrkadliť backendovú štruktúru 1:1:

- **frontend root**: `/Users/sopira/sopira.magic/version_01/frontend`
- **konfigurácia, aliasy, bootstrapping**: `frontend/src/`
- **centrálne FE metadáta (mirror BE SSOT)**: `frontend/src/config/`
 - `modelMetadata.ts` (mirror backend `model_metadata.py`),
 - `api.ts` (BASE URL, common API nastavenia).
- **shared infra a UI**:
 - `frontend/src/components/MyTable/`
 - `MyTable.tsx` – orchestrátor (migrovaný z Thermal Eye UI),
 - `MyTableTypes.ts`, `MyTableHelpers.ts`, `useMyTableData.ts`, `MyTableToolbar.tsx`, prípadné ďalšie utility,
 - všetko generické a domain‑agnostické.
 - `frontend/src/components/ui_custom/` – shadcn/ui + custom tabla infra (importované z Thermal Eye UI),
 - `frontend/src/components/modals/` – `SaveStateModal`, `LoadStateModal`, `ShareFactoryModal`, `EditRecordModal`, `AddRecordModal`,
 - `frontend/src/components/TagEditor/` – editor tagov,
 - `frontend/src/shared/` – generické hooks a helpery (napr. `useApi`, `useErrorHandler`, `useTooltip`, `useSnapshot`, toast systém, atď.).
- **per‑model FE moduly (1:1 s BE)**: `frontend/src/apps/` (alebo `frontend/src/modules/` podľa existujúcej konvencie)

**Existujúce moduly** (aktualizovať/zosúladiť):

1. **m_factory** (`/Users/sopira/sopira.magic/version_01/frontend/src/apps/factory/`)
   - `FactoryListPage.tsx` – list view používajúci `MyTable` + ConfigDriven config
   - `FactoryDetailPage.tsx` – detail view pre factory
   - `FactoryForm.tsx` – CRUD formulár pre factory
   - `hooks/` – factory‑špecifické hooks
     - `useFactory.ts` – hook pre factory operácie
   - `types.ts` – TypeScript typy pre factory
   - `utils.ts` – factory‑špecifické utility funkcie

2. **m_tag** (`/Users/sopira/sopira.magic/version_01/frontend/src/apps/tag/`)
   - Rovnaká štruktúra ako factory

3. **m_user** (`/Users/sopira/sopira.magic/version_01/frontend/src/apps/user/`)
   - Rovnaká štruktúra ako factory

4. **m_photo** (`/Users/sopira/sopira.magic/version_01/frontend/src/apps/photo/`)
   - Rovnaká štruktúra ako factory

5. **m_video** (`/Users/sopira/sopira.magic/version_01/frontend/src/apps/video/`)
   - Rovnaká štruktúra ako factory

**Nové moduly** (vytvoriť):

6. **m_camera** (`/Users/sopira/sopira.magic/version_01/frontend/src/apps/camera/`)
   - `CameraListPage.tsx` – list view používajúci `MyTable` + ConfigDriven config
   - `CameraDetailPage.tsx` – detail view pre camera
   - `CameraForm.tsx` – CRUD formulár pre camera
   - `hooks/` – camera‑špecifické hooks
     - `useCamera.ts` – hook pre camera operácie
   - `types.ts` – TypeScript typy pre camera
   - `utils.ts` – camera‑špecifické utility funkcie

7. **m_carrier** (`/Users/sopira/sopira.magic/version_01/frontend/src/apps/carrier/`)
   - Rovnaká štruktúra ako camera

8. **m_driver** (`/Users/sopira/sopira.magic/version_01/frontend/src/apps/driver/`)
   - Rovnaká štruktúra ako camera

9. **m_location** (`/Users/sopira/sopira.magic/version_01/frontend/src/apps/location/`)
   - Rovnaká štruktúra ako camera

10. **m_pit** (`/Users/sopira/sopira.magic/version_01/frontend/src/apps/pit/`)
    - Rovnaká štruktúra ako camera

11. **m_pot** (`/Users/sopira/sopira.magic/version_01/frontend/src/apps/pot/`)
    - Rovnaká štruktúra ako camera

12. **m_measurement** (`/Users/sopira/sopira.magic/version_01/frontend/src/apps/measurement/`)
    - Rovnaká štruktúra ako camera

13. **m_machine** (`/Users/sopira/sopira.magic/version_01/frontend/src/apps/machine/`)
    - Rovnaká štruktúra ako camera

- **cross‑cutting FE moduly** (mirror backendových apps):
- `/Users/sopira/sopira.magic/version_01/frontend/src/apps/relation/` – FE časť abstraktného relation modulu (typy, configy, UI pre vzťahy – neskôr),
- `/Users/sopira/sopira.magic/version_01/frontend/src/apps/authentification/` – login, role, permissions UI,
- `/Users/sopira/sopira.magic/version_01/frontend/src/apps/state/` – globálny state management,
- `/Users/sopira/sopira.magic/version_01/frontend/src/apps/scoping/` – scope selector, hooky na scoping,
- `/Users/sopira/sopira.magic/version_01/frontend/src/apps/pdfviewer/` – zobrazenie PDF/reportov.

Táto adresárová štruktúra je **cieľový stav**, ktorému budú zodpovedať všetky migračné kroky nižšie.

---

## Konvencie pre súbory

Všetky súbory v projekte musia dodržiavať nasledujúcu konvenciu:

### Hlavička súboru

Každý súbor musí obsahovať hlavičku v tomto formáte:

```python
# /Users/sopira/sopira.magic/version_01/sopira_magic/apps/m_factory/models.py
# Factory model - core data model for factory entities
#
# <details>
# <summary>Detailed description</summary>
#
# This module contains the Factory model definition, including:
# - Field definitions (name, code, address, etc.)
# - Relationships to other models (locations, machines, etc.)
# - Custom methods and properties
# - Meta configuration (ordering, permissions, etc.)
#
# The model follows ConfigDriven & SSOT principles:
# - All metadata (endpoints, ownership, default ordering) is defined in sopira_magic/config/model_metadata.py
# - No hardcoded domain logic in the model itself
# </details>
```

### Formát hlavičky

Každý súbor musí začínať hlavičkou v tomto formáte:

1. **Prvý riadok**: Absolútna cesta k súboru + názov súboru
   - Príklad Python: `# /Users/sopira/sopira.magic/version_01/sopira_magic/apps/m_factory/models.py`
   - Príklad TypeScript: `// /Users/sopira/sopira.magic/version_01/frontend/src/apps/factory/FactoryListPage.tsx`

2. **Druhý riadok**: Stručný popis funkcie súboru (2-3 riadky)
   - Príklad: `# Factory model - core data model for factory entities`

3. **Tretí riadok**: Prázdny riadok

4. **Štvrtý riadok a ďalej**: Podrobný popis (kolapsovateľný v IDE)
   - Použiť HTML `<details>` a `<summary>` tagy pre kolapsovateľný obsah
   - Alebo komentáre v jazyku súboru (napr. `# <details>` v Python, `// <details>` v TypeScript)
   - Príklad:
     ```python
     # <details>
     # <summary>Detailed description</summary>
     #
     # This module contains the Factory model definition, including:
     # - Field definitions (name, code, address, etc.)
     # - Relationships to other models (locations, machines, etc.)
     # - Custom methods and properties
     # - Meta configuration (ordering, permissions, etc.)
     #
     # The model follows ConfigDriven & SSOT principles:
     # - All metadata (endpoints, ownership, default ordering) is defined in sopira_magic/config/model_metadata.py
     # - No hardcoded domain logic in the model itself
     # </details>
     ```

5. **Ďalšie popisy v kóde**: Tiež kolapsovateľné, priamo pri relevantných funkciách/triedach
   - Použiť rovnaký formát `<details>` / `<summary>` pre dlhšie komentáre pri funkciách/metódach

### Jazyk komentárov

- **Všetky popisy a komentáre v angličtine**
- Technické termíny môžu byť v angličtine (aj v slovenčine v komunikácii, ale v kóde anglicky)

### Príklady hlavičiek

**Python súbor (models.py)**:
```python
# /Users/sopira/sopira.magic/version_01/sopira_magic/apps/m_factory/models.py
# Factory model - core data model for factory entities
#
# <details>
# <summary>Detailed description</summary>
#
# This module contains the Factory model definition, including:
# - Field definitions (name, code, address, etc.)
# - Relationships to other models (locations, machines, etc.)
# - Custom methods and properties
# - Meta configuration (ordering, permissions, etc.)
#
# The model follows ConfigDriven & SSOT principles:
# - All metadata (endpoints, ownership, default ordering) is defined in sopira_magic/config/model_metadata.py
# - No hardcoded domain logic in the model itself
# </details>
```

**TypeScript súbor (MyTable.tsx)**:
```typescript
// /Users/sopira/sopira.magic/version_01/frontend/src/components/MyTable/MyTable.tsx
// MyTable - Generic, config-driven table component
//
// <details>
// <summary>Detailed description</summary>
//
// Single reusable table for all list views in the frontend.
// The component is fully driven by declarative configuration
// (MyTableConfig + MyTableColumnConfig) and is domain-agnostic.
//
// Responsibilities:
// - Render columns and rows based on configuration
// - Client-side sorting, global text filtering and pagination
// - Optional row selection with callbacks to the parent layer
//
// Non-responsibilities:
// - Data loading (handled by the caller)
// - Domain-specific rendering outside of the provided configuration
// </details>
```

**TypeScript súbor (FactoryListPage.tsx)**:
```typescript
// /Users/sopira/sopira.magic/version_01/frontend/src/apps/factory/FactoryListPage.tsx
// Factory list page - displays factory entities in a config-driven table
//
// <details>
// <summary>Detailed description</summary>
//
// This page component uses MyTable with ConfigDriven configuration.
// All table settings (columns, filters, sorting, pagination) are
// read from SSOT metadata (frontend/src/config/modelMetadata.ts).
//
// The page follows ConfigDriven & SSOT principles:
// - No hardcoded column definitions or filter configurations
// - All metadata comes from centralized SSOT source
// - Factory-specific UI logic only (if any) is kept minimal
// </details>
```

---

## Etapa 1 – Základná inventúra a mapovanie štruktúr (analýza + výstupy)

1. **Inventúra backendu Thermal Eye – strom modulov a modelov**

- Prejsť celý projekt `thermal_eye` a zostaviť prehľadovú mapu:
 - zoznam hlavných Django aplikácií (apps) a ich umiestnenie v `/Users/sopira/www/thermal_eye`,
 - zoznam modelov (factory, location, driver, carrier, pit, pot, machine, measurement, camera, user, …) s cestami k súborom `models.py`,
 - kde sú definované serializers, viewsety, filtersety, URL, permissions a signály.
- **Výstup (súbor)**: `/Users/sopira/sopira.magic/version_01/documentation/backend_docs/structure_thermal_eye.md` – strom adresárov a tabuľka *model → app → súbory*.

2. **Inventúra frontend Thermal Eye UI – moduly, komponenty, ConfigDriven/SSOT infra**

- Prejsť projekt `thermal_eye_ui` a identifikovať:
 - modulárne časti pre jednotlivé modely (views, forms, špecifické komponenty),
 - shared komponenty a hooky relevantné pre ConfigDriven/SSOT (napr. `MyTable`, `ui_custom/table/*`, `TagEditor`, `fkCacheService`, `useSnapshot`, `table-state-presets`, `modelMetadata`, `useApi`, `ScopeContext`, `AuthContext`, toast system),
 - všetky miesta, kde FE číta SSOT z backendu (model metadata, FK cache, scoping, security).
- **Výstup (súbor)**: `/Users/sopira/sopira.magic/version_01/documentation/frontend_docs/structure_thermal_eye_ui.md` – prehľad FE adresárov a tabuľka *model → FE modul → komponenty/hooky*.

3. **Inventúra existujúceho stavu v sopira.magic**

- Prejsť `sopira.magic/version_01` a zmapovať:
 - už existujúce moduly: `relation`, `security`, `state`, `scoping`, `pdfviewer`,
 - existujúce `m_*` moduly: `m_factory`, `m_tag`, `m_user`, `m_photo`, `m_video` (placeholdery/scaffold),
 - moduly, ktoré treba doplniť: `m_camera`, `m_carrier`, `m_driver`, `m_location`, `m_pit`, `m_pot`, `m_measurement`, `m_machine`,
 - aktuálnu BE štruktúru (apps pod `backend/apps/`),
 - aktuálnu FE štruktúru (moduly pod `frontend/src/modules/`, shared komponenty v `frontend/src/components/`).
- **Výstup (súbor)**: `/Users/sopira/sopira.magic/version_01/documentation/architecture_docs/structure_sopira_magic.md` – zhrnutie existujúcej architektúry a miest, kde už je ConfigDriven&SSOT aplikované.

4. **Mapovanie BE↔FE štruktúr (1:1 návrh)**

- Na základe inventúry pripraviť jednu SSOT tabuľku mapovania:
 - pre každý model (factory, location, driver, carrier, pit, pot, machine, measurement, camera, user) definovať:
 - `backend_app_path` v starej aplikácii (`/Users/sopira/www/thermal_eye/...`) a cieľový `backend_app_path` v sopira.magic (`/Users/sopira/sopira.magic/version_01/sopira_magic/apps/m_<model>/`),
 - `frontend_module_path` v starej aplikácii (`/Users/sopira/www/thermal_eye_ui/...`) a cieľový `frontend_module_path` v sopira.magic (`/Users/sopira/sopira.magic/version_01/frontend/src/apps/<model>/`),
 - väzbu na relation modul (len typovo, bez konkrétnych tabuliek).
- **Výstup (súbor)**: `/Users/sopira/sopira.magic/version_01/documentation/architecture_docs/model_path_map.md` – centrálna SSOT tabuľka.

5. **Analýza existujúceho ConfigDriven & SSOT patternu v Thermal Eye**

- Extrahovať a popísať:
 - ako je definovaný `VIEWS_MATRIX`/modelové metadáta v BE (`/Users/sopira/www/thermal_eye/...`),
 - ako FE tieto metadáta číta (`/Users/sopira/www/thermal_eye_ui/config/modelMetadata.*` a súvisiace moduly),
 - kde ešte existuje domain‑hardcode, ktorý sa v sopira.magic už nesmie zopakovať.
- **Výstup (súbor)**: `/Users/sopira/sopira.magic/version_01/documentation/architecture_docs/configdriven_patterns.md` – popis vzorov, ktoré budeme 1:1 aplikovať v sopira.magic.

6. **Návrh cieľovej architektúry pre sopira.magic (BE + FE)**

- Na základe predošlých bodov pripraviť krátky návrh:
 - BE: konvencie pre apps, umiestnenie modelov, kde bude centrálna definícia metadát (SSOT) – v `sopira_magic/config/` + per‑model `sopira_magic/apps/m_<model>/`,
 - FE: zrkadlová štruktúra adresárov k BE – v `frontend/src/apps/<model>/`,
 - shared infra: umiestnenie modulov `modelMetadata`, `fkCacheService`, `MyTable`, `state`, `security`, `scoping`, `relation` (abstraktný), podľa adresárov vyššie,
 - jasné pravidlá: čo smie byť hardcodnuté (lokálna UI logika v `modules/<model>`), čo musí byť v SSOT (modely, polia, väzby, endpointy, scoping, default sorting,... v `backend/config` + `frontend/src/config`).
- **Výstup (súbor)**: `/Users/sopira/sopira.magic/version_01/documentation/architecture_docs/target_architecture_sopira_magic.md` – referenčný dokument pre implementačné etapy.

---

## Etapa 2 – Migrácia `MyTable` do sopira.magic

1. **Analyzovať rozdiely medzi `MyTable` implementáciami**

- Už existujúci generický komponent v `sopira.magic`:
 - `/Users/sopira/sopira.magic/version_01/frontend/src/components/MyTable/MyTable.tsx`.
- Plne ConfigDriven & SSOT verzia v Thermal Eye UI:
 - `/Users/sopira/www/thermal_eye_ui/src/components/MyTable/MyTable.tsx`.

2. **Navrhnúť cieľový tvar `MyTable` v sopira.magic**

- Použiť **architektúru Thermal Eye `MyTable`** (ConfigDriven, metadata‑driven, fk cache, snapshoty, presets),
- zachovať typy a API tak, aby boli generické a domain‑agnostické (žiadne tvrdé väzby na konkrétny model).

3. **Identifikovať všetky závislosti `MyTable` a ich cieľové umiestnenie**

- Lokálne súbory:
 - z Thermal Eye UI (napr. `MyTableTypes.ts`, `MyTableHelpers.ts`, `useMyTableData.ts`) presunúť do:
 - `/Users/sopira/sopira.magic/version_01/frontend/src/components/MyTable/`.
- Shared infra:
 - `ui_custom/table/*` → `/Users/sopira/sopira.magic/version_01/frontend/src/components/ui_custom/table/`,
 - `TagEditor` → `/Users/sopira/sopira.magic/version_01/frontend/src/components/TagEditor/`,
 - modaly → `/Users/sopira/sopira.magic/version_01/frontend/src/components/modals/`.
- Hooks a helpery:
 - `useSnapshot`, `useErrorHandler`, `useTooltip`, `useRowSelection`, `useFilterState`, `useApi`, toast systém →
 - `/Users/sopira/sopira.magic/version_01/frontend/src/shared/hooks/` (alebo `frontend/src/hooks/` podľa existujúcej konvencie),
 - `/Users/sopira/sopira.magic/version_01/frontend/src/shared/utils/` – pre pomocné funkcie.
- Kontexty:
 - `ScopeContext`, `AuthContext` →
 - `/Users/sopira/sopira.magic/version_01/frontend/src/contexts/`.
- Configy:
 - `modelMetadata` (FE mirror) → `/Users/sopira/sopira.magic/version_01/frontend/src/config/modelMetadata.ts`,
 - `API_BASE` a CSRF utilita → `/Users/sopira/sopira.magic/version_01/frontend/src/config/api.ts` a `/Users/sopira/sopira.magic/version_01/frontend/src/utils/csrf.ts`.
- FK cache:
 - `fkCacheService` → `/Users/sopira/sopira.magic/version_01/frontend/src/services/fkCacheService.ts`.

4. **Navrhnúť cieľovú štruktúru balíka `MyTable` v sopira.magic**

V `sopira.magic`:

- Adresár: `/Users/sopira/sopira.magic/version_01/frontend/src/components/MyTable/`
- `MyTable.tsx` – hlavný orchestrátor (migrovaný Thermal Eye komponent, adaptovaný na nové aliasy),
- `MyTableTypes.ts` – typy a ConfigDriven rozhranie,
- `MyTableHelpers.ts` – helper funkcie (filter, sort, konverzie),
- `useMyTableData.ts` – hook pre server‑side fetchovanie (endpoint + query params),
- `MyTableToolbar.tsx` – toolbar/UI nad tabuľkou (ak je v Thermal Eye oddelený),
- prípadne ďalšie podkomponenty (`TableHeader`, `FilterPanel`, `ColumnsPanel`), ak sa v Thermal Eye nachádzajú v rámci MyTable balíka.

5. **Pripraviť plán úprav importov pri migrácii**

- Pre každý import v Thermal Eye verzii `MyTable` vytvoriť tabuľku „from → to" (s využitím cieľových adresárov vyššie).
- Zachovať **absolútne/alias importy** podľa `tsconfig.json`/bundlera v `sopira.magic` (v prípade potreby doplniť aliasy tak, aby ukazovali na uvedené adresáre).

6. **Naplánovať integráciu do existujúceho FE v sopira.magic**

- Vybrať **jednoduchý model** (napr. `factory`) a vytvoriť modul:
 - `/Users/sopira/sopira.magic/version_01/frontend/src/modules/m_factory/FactoryListPage.tsx` – ktorý použije nový `MyTable`.
- Pripraviť `MyTableConfig` pre tento model tak, aby:
 - stĺpce, filtre, ordering a endpointy boli čítané z **FE metadát** v `frontend/src/config/modelMetadata.ts`,
 - testovalo sa server‑side stránkovanie, sort, filtre a advanced search.

7. **Testovanie a prechod**

- Spustiť FE v sopira.magic a overiť:
 - funkčnosť stránkovania, sortovania, filtrov, selection, presets v `FactoryListPage`,
 - správnu integráciu scope a security (viditeľné len scoped dáta),
 - korektný zápis snapshotov a presets (kontrola podľa BE snapshot/state infra).
- Po overení **označiť starú jednoduchú verziu `MyTable` ako deprecated** (v `frontend/src/components/MyTable/`), ale zatiaľ ju neodstraňovať.

---

## Etapa 3 – Shared ConfigDriven & SSOT infra v sopira.magic

1. **Centralizovať modelové metadáta (SSOT)**

- Backend:
 - Preniesť/zosúladiť `VIEWS_MATRIX`/modelové metadáta do:
 - `/Users/sopira/sopira.magic/version_01/sopira_magic/config/model_metadata.py` (alebo rovnocenný modul podľa existujúcej štruktúry).
- Frontend:
 - Vytvoriť mirror modul:
 - `/Users/sopira/sopira.magic/version_01/frontend/src/config/modelMetadata.ts`.
- Oba moduly budú SSOT pre modely (factory, location, driver, carrier, pit, pot, machine, measurement, camera, user).

2. **FK cache & options infra**

- Backend endpoint(y) pre FK cache:
 - implementované v príslušnej app (napr. `backend/apps/relation/` alebo samostatná `fk_cache` app),
 - napojené na `sopira_magic/config/model_metadata.py`.
- Frontend:
 - `fkCacheService` v:
 - `/Users/sopira/sopira.magic/version_01/frontend/src/services/fkCacheService.ts`,
 - používaný v `MyTable` a ďalších komponentoch podľa ConfigDriven vzoru.

3. **Snapshot & table‑state infra**

- Backend:
 - ak existujú API pre snapshoty a table‑state (table presets), umiestniť ich do vhodnej app (napr. `backend/apps/state/`).
- Frontend:
 - hook `useSnapshot` a súvisiace utility v:
 - `/Users/sopira/sopira.magic/version_01/frontend/src/shared/hooks/useSnapshot.ts`,
 - komponenty `SaveStateModal`, `LoadStateModal` v `frontend/src/components/modals/`.

4. **Relation modul – zatiaľ bez konkrétnych tabuliek**

- Backend:
 - `backend/apps/relation/` – definícia typov a konfiguračných štruktúr pre vzťahy (bez konkrétnych modelových väzieb).
- Frontend:
 - `frontend/src/modules/relation/` – FE side mirror (typy, graf vzťahov, UI komponenty – neskôr),
 - zatiaľ len abstraktné rozhrania.

---

## Etapa 4 – Migrácia BE modulov (per‑model)

Pre každý model (factory, location, driver, carrier, pit, pot, machine, measurement, camera, user):

1. **Presunúť BE kód do sopira.magic**

 - Zdroj: `/Users/sopira/www/thermal_eye/...`
- Cieľ: `/Users/sopira/sopira.magic/version_01/sopira_magic/apps/m_<model>/`:
 - `models.py`, `serializers.py`, `views.py`/`viewsets.py`, `filters.py`, `urls.py`, `tests/`.
- Pre moduly, ktoré už existujú ako placeholdery (`m_factory`, `m_tag`, `m_user`, `m_photo`, `m_video`), nahradiť placeholder skutočným kódom.
- Pre moduly, ktoré treba vytvoriť (`m_camera`, `m_carrier`, `m_driver`, `m_location`, `m_pit`, `m_pot`, `m_measurement`, `m_machine`), vytvoriť nové adresáre so scaffold štruktúrou (podľa existujúcich `m_*` modulov).

2. **Očistiť od hardcodu a pripojiť na SSOT**

- Všetko, čo sa týka názvov tabuliek, endpointov, default ordering, ownership/scoping, filtrov, permissions,
sa bude čítať z `sopira_magic/config/model_metadata.py`.

3. **Napojenie na relation modul (virtuálne)**

- V tejto fáze len používať generické rozhrania `backend/apps/relation/`, bez pridávania konkrétnych definícií vzťahov.

4. **Dodržanie konvencií pre súbory**

- Všetky súbory musia mať hlavičku podľa konvencie (cesta, stručný popis, podrobný popis kolapsovateľný, všetko v angličtine).

5. **Testy**

- Spustiť pytest pre jednotlivé apps v `backend/apps/m_<model>/tests/`.

---

## Etapa 5 – Migrácia FE modulov (per‑model, 1:1 k BE)

Pre každý model (v rovnakom poradí ako BE):

1. **Vytvoriť/zosúladiť FE modul**

- Cieľové umiestnenie:
 - `/Users/sopira/sopira.magic/version_01/frontend/src/apps/<model>/`.
- Obsah modulov:
 - `*ListPage.tsx` (používajúci `MyTable` + ConfigDriven config),
 - `*DetailPage.tsx`, formuláre,
 - špecifické widgets, grafy, hooks.

2. **Používať výhradne ConfigDriven & SSOT**

- `MyTableConfig` generovať z `frontend/src/config/modelMetadata.ts`.
- Formuláre stavať cez generické field factory/schema (tiež z metadát), nie ručným vypisovaním polí.

3. **Znovu použiť shared moduly**

- Scoping: hooky a komponenty v `frontend/src/modules/scoping/` + `frontend/src/contexts/ScopeContext.tsx`.
- Security: `frontend/src/modules/security/` + `frontend/src/contexts/AuthContext.tsx`.
- State: `frontend/src/modules/state/` + shared hooks.

4. **Dodržanie konvencií pre súbory**

- Všetky súbory musia mať hlavičku podľa konvencie (cesta, stručný popis, podrobný popis kolapsovateľný, všetko v angličtine).

5. **Testy a regresné porovnanie**

- Overiť UX/flows oproti Thermal Eye UI.

---

## Etapa 6 – Cross‑cutting moduly a infra

1. **Security**

- BE: policies v `backend/apps/security/`,
- FE: UI a hooky v `frontend/src/modules/security/` + `frontend/src/contexts/AuthContext.tsx`.

2. **State management**

- Jednotný store/hooks v `frontend/src/modules/state/` alebo `frontend/src/shared/state/` (podľa existujúcej konvencie).

3. **Scoping**

 - BE: logika v `sopira_magic/apps/scoping/` a metadáta v `sopira_magic/config/model_metadata.py`,
- FE: komponenty/hooky v `frontend/src/modules/scoping/` + `ScopeContext`.

4. **PDF viewer & reporting**

- BE: generovanie reportov v `backend/apps/pdfviewer/`,
- FE: komponenty v `frontend/src/modules/pdfviewer/`.

---

## Etapa 7 – Postupný cut‑over a cleanup

1. **Paralelná prevádzka kým prebieha migrácia**

- Zachovať Thermal Eye (`/Users/sopira/www/thermal_eye*`) a sopira.magic paralelne, kým jednotlivé moduly nebudú v sopira.magic stabilné.

2. **Postupné vypínanie starých modulov**

- Po úspešnej migrácii modelu (BE + FE + testy) označiť starý modul v Thermal Eye za deprecated.

3. **Finálny cleanup**

- Odstrániť duplikované helpery, hooks a configy – ponechať iba SSOT verzie v `sopira.magic`.
- Skontrolovať, že žiadny generický komponent (najmä `MyTable`) neobsahuje domain‑hardcode (len odkazy na metadáta a configy).

---

## Hlavné TODO úlohy

- **inventory-backend**: Urobiť inventúru backendu Thermal Eye (apps, modely, súbory) a zapísať ju do `documentation/backend_docs/structure_thermal_eye.md` v `sopira.magic`.
- **inventory-frontend**: Urobiť inventúru frontend Thermal Eye UI (moduly, komponenty, hooks) a zapísať ju do `documentation/frontend_docs/structure_thermal_eye_ui.md` v `sopira.magic`.
- **inventory-sopira-magic**: Zmapovať aktuálnu architektúru sopira.magic (BE/FE, existujúce moduly) a zapísať ju do `documentation/architecture_docs/structure_sopira_magic.md`.
- **model-path-map**: Pripraviť SSOT mapu modelov medzi Thermal Eye a sopira.magic v `documentation/architecture_docs/model_path_map.md`.
- **configdriven-patterns**: Zdokumentovať existujúce ConfigDriven&SSOT vzory Thermal Eye a ich aplikáciu v sopira.magic v `documentation/architecture_docs/configdriven_patterns.md`.
- **target-architecture-doc**: Spísať cieľovú architektúru sopira.magic (BE+FE, 1:1 štruktúra, shared infra) v `documentation/architecture_docs/target_architecture_sopira_magic.md`.
- **mytable-migrate**: Pripraviť detailný zoznam závislostí Thermal Eye `MyTable` a navrhnúť cieľovú štruktúru balíka `MyTable` v `frontend/src/components/MyTable/` v sopira.magic.
- **mytable-integrate-first-model**: Integrovať nový `MyTable` v sopira.magic pre jeden pilotný model (napr. `factory`) v `frontend/src/modules/m_factory/` s plne ConfigDriven konfiguráciou.
- **metadata-ssot-backend**: Centralizovať modelové metadáta na backend strane (Thermal Eye → sopira.magic) v `sopira_magic/config/model_metadata.py` a napojiť na existujúce moduly.
- **metadata-ssot-frontend**: Vytvoriť frontend mirror modulu s metadátami v `frontend/src/config/modelMetadata.ts` (endpoints, ownership, ordering, filters) a napojiť na `MyTable` a formuláre.
- **per-model-backend-migration**: Prejsť modely (factory, location, driver, carrier, pit, pot, machine, measurement, camera, user) a zmigrovať ich backend časti do `sopira_magic/apps/m_<model>/` v sopira.magic s napojením na SSOT.
- **per-model-frontend-migration**: Pre tie isté modely vytvoriť/zosúladiť frontend moduly v `frontend/src/apps/<model>/` v sopira.magic, používať `MyTable` a shared infra.
- **relation-module-ssot**: Pripraviť abstraktný relation modul (typy, interface, config) v `sopira_magic/apps/relation/` a `frontend/src/apps/relation/` bez konkrétnych tabuliek, pripravený na neskoršie doplnenie väzieb.
- **cleanup-legacy**: Po úspešnej migrácii postupne odstrániť legacy kód a duplikované helpery z Thermal Eye, ponechať SSOT verzie v sopira.magic.

