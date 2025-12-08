# Thermal Eye UI Frontend - Inventúra štruktúry

## Prehľad

Thermal Eye UI je React + TypeScript + Vite aplikácia s **ConfigDriven & SSOT architektúrou**. Používa jednotný `MyTable` komponent pre všetky tabuľky, ktorý je plne riadený deklaratívnou konfiguráciou.

**Zdrojová cesta**: `/Users/sopira/www/thermal_eye_ui`

## Adresárová štruktúra

```
thermal_eye_ui/
├── src/
│   ├── App.tsx                    # Main app component, routes
│   ├── main.jsx                   # Entry point
│   ├── index.css                  # Global styles
│   ├── vite-env.d.ts              # Vite type definitions
│   │
│   ├── config/                    # SSOT konfigurácia
│   │   ├── api.ts                 # API base URL, CSRF config
│   │   └── modelMetadata.ts       # Model metadata (mirror BE SSOT)
│   │
│   ├── contexts/                  # React contexts
│   │   ├── AuthContext.tsx        # Authentication state
│   │   ├── ScopeContext.tsx       # Factory scope (selected factories)
│   │   └── ThemeContext.tsx      # Theme management
│   │
│   ├── hooks/                     # Custom React hooks
│   │   ├── useApi.tsx             # API request hook
│   │   ├── useSnapshot.tsx        # Global state snapshot management
│   │   └── use-mobile.tsx        # Mobile detection
│   │
│   ├── services/                  # Service layer
│   │   └── fkCacheService.ts     # FK options cache service
│   │
│   ├── components/                # React components
│   │   ├── MyTable/               # Unified table component (ConfigDriven)
│   │   │   ├── MyTable.tsx        # Main orchestrator
│   │   │   ├── MyTableTypes.ts    # Type definitions & config interfaces
│   │   │   ├── MyTableHelpers.ts  # Helper functions
│   │   │   ├── useMyTableData.ts  # Data fetching hook
│   │   │   └── README.md
│   │   │
│   │   ├── modals/                # Modal dialogs
│   │   │   ├── AddRecordModal.tsx
│   │   │   ├── EditRecordModal.tsx
│   │   │   ├── SaveStateModal.tsx
│   │   │   ├── LoadStateModal.tsx
│   │   │   ├── ShareFactoryModal.tsx
│   │   │   ├── ExportModal.tsx
│   │   │   ├── ErrorModal.tsx
│   │   │   ├── ConfirmModal.tsx
│   │   │   ├── FactorySelectionModal.tsx
│   │   │   ├── UserSelectionModal.tsx
│   │   │   ├── FormModal.tsx
│   │   │   ├── RecallFilterModal.tsx
│   │   │   ├── SaveFilterModal.tsx
│   │   │   ├── BaseModal.tsx
│   │   │   └── TableModals.tsx
│   │   │
│   │   ├── ui/                    # shadcn/ui components
│   │   │   ├── table.tsx
│   │   │   ├── button.tsx
│   │   │   ├── input.tsx
│   │   │   ├── select.tsx
│   │   │   ├── dialog.tsx
│   │   │   ├── ... (50+ shadcn components)
│   │   │
│   │   ├── ui_custom/             # Custom UI components
│   │   │   ├── table/             # Table-specific components
│   │   │   │   ├── CustomTable.tsx
│   │   │   │   ├── TableHeader.tsx
│   │   │   │   ├── TableToolbar.tsx
│   │   │   │   ├── TableSearch.tsx
│   │   │   │   ├── FilterPanel.tsx
│   │   │   │   ├── ColumnsPanel.tsx
│   │   │   │   ├── fieldFactory.tsx  # Field renderer factory
│   │   │   │   ├── EditableCell.tsx
│   │   │   │   ├── ScopedFKCell.tsx
│   │   │   │   ├── ConditionalFKSelect.tsx
│   │   │   │   ├── ExpandedRowPanel.tsx
│   │   │   │   ├── GraphCells.tsx
│   │   │   │   ├── useFilterState.ts
│   │   │   │   ├── useRowSelection.ts
│   │   │   │   ├── useInlineEdit.ts
│   │   │   │   ├── useExport.ts
│   │   │   │   ├── useErrorHandler.ts
│   │   │   │   ├── useOptimisticField.ts
│   │   │   │   └── ... (30+ table hooks/components)
│   │   │   ├── button.tsx
│   │   │   ├── input.tsx
│   │   │   ├── select.tsx
│   │   │   └── ... (custom UI components)
│   │   │
│   │   ├── TagEditor.tsx         # Tag editor component
│   │   ├── Graph.tsx              # Graph/chart component
│   │   ├── NavBar.tsx             # Navigation bar
│   │   ├── PageHeader.tsx         # Page header component
│   │   └── PageFooter.tsx         # Page footer component
│   │
│   ├── pages/                     # Page components
│   │   ├── Home.tsx
│   │   ├── Login.tsx
│   │   ├── Dashboard.tsx          # Dashboard page
│   │   ├── FactoryTable.tsx      # Factory table page
│   │   ├── MeasurementsTable.tsx # Measurements table page
│   │   ├── Camera.tsx            # Camera page
│   │   ├── LogEntryTable.tsx     # Log entries table page
│   │   ├── UsersTable.tsx        # Users table page
│   │   ├── UserPreferences.tsx    # User preferences page
│   │   ├── Admin.tsx             # Admin page
│   │   ├── GenerateDummy.tsx     # Dummy data generator
│   │   ├── GenerateDummyPanel.tsx
│   │   ├── Contact.tsx
│   │   │
│   │   └── lookups/               # Lookup tables
│   │       ├── LocationsTable.tsx
│   │       ├── CarriersTable.tsx
│   │       ├── DriversTable.tsx
│   │       ├── PotsTable.tsx
│   │       ├── PitsTable.tsx
│   │       └── MachinesTable.tsx
│   │
│   ├── types/                     # TypeScript type definitions
│   │   ├── measurement.ts        # Measurement types
│   │   └── scoping.ts            # Scoping types
│   │
│   ├── schemas/                   # Zod validation schemas
│   │   ├── lookups.ts            # Lookup table schemas
│   │   └── validation.ts         # Validation schemas
│   │
│   ├── utils/                     # Utility functions
│   │   ├── csrf.ts               # CSRF token utilities
│   │   ├── date.ts               # Date utilities
│   │   ├── tableHelpers.ts      # Table helper functions
│   │   └── toastMessages.ts     # Toast message utilities
│   │
│   └── lib/                       # Library utilities
│       └── utils.ts              # General utilities (cn, etc.)
│
├── public/                        # Static assets
├── package.json                   # Dependencies
├── vite.config.js                 # Vite configuration
├── tailwind.config.js             # Tailwind CSS configuration
├── tsconfig.json                  # TypeScript configuration
└── README.md
```

## Tech stack

- **Framework**: React 18.3.1
- **Build tool**: Vite 7.1.2
- **Language**: TypeScript
- **Styling**: Tailwind CSS 3.4.18
- **UI Components**: shadcn/ui (Radix UI primitives)
- **Table**: TanStack Table 8.21.3
- **Forms**: React Hook Form 7.65.0 + Zod 4.1.12
- **Routing**: React Router DOM 7.9.1
- **State**: React Context API
- **HTTP**: Fetch API (via useApi hook)
- **Notifications**: Sonner 2.0.7
- **Charts**: Recharts 2.15.4
- **Date**: date-fns 4.1.0
- **Export**: xlsx 0.18.5

## ConfigDriven & SSOT architektúra

### 1. Model Metadata (SSOT)

**Súbor**: `src/config/modelMetadata.ts`

**Účel**: Mirror backend `VIEWS_MATRIX` - SSOT pre modelové metadáta

**Funkcie**:
- `loadModelMetadata()` - Načíta metadáta z `/api/models/metadata/`
- `getModelEndpoint(fieldName)` - Vráti API endpoint pre model (napr. `'factory'` → `'/api/factories/'`)
- `getModelPlural(fieldName)` - Vráti plural názov (napr. `'factory'` → `'Factories'`)
- `getModelSingular(fieldName)` - Vráti singular názov
- `getDefaultOrdering(fieldName)` - Vráti default ordering z VIEWS_MATRIX
- `getOwnershipField(fieldName)` - Vráti ownership field z VIEWS_MATRIX

**Použitie**: 
- `MyTable` automaticky používa metadáta pre FK endpoints
- Všetky tabuľky čítajú endpoints z metadát, nie hardcode

### 2. MyTable Component (ConfigDriven)

**Súbor**: `src/components/MyTable/MyTable.tsx`

**Účel**: Jednotný, ConfigDriven komponent pre všetky tabuľky

**Konfigurácia** (`MyTableConfig`):
- `tableName` - Názov tabuľky (pre state persistence)
- `apiEndpoint` - API endpoint (z modelMetadata)
- `fieldsMatrix` - Deklaratívna konfigurácia polí (typy, headers, visibility, filters, editability)
- `filtersConfig` - Konfigurácia filtrov
- `actionsConfig` - Konfigurácia actions (edit, delete, expand, custom)
- `toolbarVisibility` - Visibility flags pre toolbar buttons
- `headerVisibility` - Visibility flags pre header elements
- `pageHeaderConfig` - Konfigurácia page header
- `pageFooterConfig` - Konfigurácia page footer
- `quickCreateConfig` - Konfigurácia quick create panel
- `inlineEditConfig` - Konfigurácia inline edit

**Features**:
- Server-side pagination, sorting, filtering
- Client-side global text search
- Column visibility management
- Filter panel (text, select, date range, checkbox, tag autocomplete)
- Columns panel (reorder, resize, visibility)
- Inline edit
- CRUD modals (Add, Edit)
- Export (CSV, XLSX, PDF)
- State persistence (presets, snapshots)
- FK dropdowns (z FK cache)
- Tag editor
- Row selection
- Expanded rows (detail view)
- Graph cells (ROC, TEMP)
- Error handling
- Optimistic updates

**Závislosti**:
- `useMyTableData` - Data fetching hook
- `useSnapshot` - State snapshot management
- `useScope` - Factory scope context
- `useAuth` - Authentication context
- `fkCacheService` - FK options cache
- `modelMetadata` - Model metadata SSOT

### 3. Field Factory (ConfigDriven)

**Súbor**: `src/components/ui_custom/table/fieldFactory.tsx`

**Účel**: Generický field renderer - renderuje polia podľa typu z `fieldsMatrix`

**Podporované typy**:
- `text` - Text input
- `number` - Number input
- `date` - Date picker
- `time` - Time picker
- `datetime` - DateTime picker
- `select` - Select dropdown
- `fk` - Foreign key dropdown (z FK cache)
- `checkbox` - Checkbox
- `textarea` - Textarea
- `tag` - Tag editor
- `graph` - Graph cell (ROC, TEMP)
- `image` - Image display
- `video` - Video display

**Použitie**: `MyTable` automaticky používa fieldFactory pre renderovanie polí v tabuľke a modáloch

### 4. FK Cache Service (SSOT)

**Súbor**: `src/services/fkCacheService.ts`

**Účel**: Načítanie FK options z backend cache (`/api/fk-options-cache/`)

**Funkcie**:
- `loadFKOptionsFromCache(field, factoryIds)` - Načíta FK options pre field
- `loadMultipleFKOptionsFromCache(fields, factoryIds)` - Načíta viacero fields paralelne

**Poznámka**: Backend automaticky aplikuje scope na základe `selected_factories` z Dashboard. Frontend neposiela `factory_ids[]` - backend to rieši automaticky.

## Contexts (Global State)

### 1. AuthContext

**Súbor**: `src/contexts/AuthContext.tsx`

**Účel**: Správa authentication state

**State**:
- `user` - Current user object
- `isAuthenticated` - Boolean flag
- `isLoading` - Loading state
- `csrfToken` - CSRF token

**Methods**:
- `login(username, password)` - Login
- `logout()` - Logout
- `signup(...)` - Signup
- `forgotPassword(email)` - Password reset
- `checkAuth()` - Check authentication status

**User object obsahuje**:
- `id`, `username`, `email`
- `role` - SSOT role (SUPERUSER/ADMIN/STAFF/EDITOR/READER/ADHOC)
- `can_read`, `can_edit`, `can_export`, `can_manage_factories`, `can_manage_users`, `can_generate_seeds`
- `is_admin`, `is_superuser_role`

### 2. ScopeContext

**Súbor**: `src/contexts/ScopeContext.tsx`

**Účel**: Správa factory scope (selected factories)

**State**:
- `selectedFactories` - Array of factory UUIDs

**Methods**:
- `setSelectedFactories(ids)` - Set selected factories
- `clearScope()` - Clear scope
- `toggleFactory(id)` - Toggle factory selection
- `rebuildFKCache()` - Rebuild FK cache for current scope
- `updateTableState(removedFactoryIds?)` - Update table state after scope change

**SSOT**: `selected_factories` z `UserPreference` v databáze (primary source). localStorage je len fallback.

### 3. ThemeContext

**Súbor**: `src/contexts/ThemeContext.tsx`

**Účel**: Správa theme (light/dark)

## Hooks

### 1. useApi

**Súbor**: `src/hooks/useApi.tsx`

**Účel**: Wrapper pre fetch API s CSRF token handling

**Features**:
- Automatické pridanie CSRF tokenu
- Error handling
- Loading state management

### 2. useSnapshot

**Súbor**: `src/hooks/useSnapshot.tsx`

**Účel**: Global state snapshot management

**State**:
- `snapshot` - Current snapshot (`__current__` preset)
- `isLoading` - Loading state
- `error` - Error state

**Methods**:
- `updateTable(tableName, partialState)` - Update table state
- `updateGlobal(partialState)` - Update global state
- `getTableState(tableName)` - Get table state
- `refresh()` - Refresh from server

**SSOT**: `TableStatePreset` s `preset_name='__current__'` v databáze

## Pages (Per-Model Modules)

### Main Tables

1. **FactoryTable.tsx** (`/factories`)
   - Factory management
   - Share factory access (Admin/SA only)
   - Uses `MyTable` s Factory config

2. **MeasurementsTable.tsx** (`/measurements`)
   - Measurement management
   - Graph cells (ROC, TEMP)
   - Uses `MyTable` s Measurement config

3. **Camera.tsx** (`/camera`)
   - Camera management
   - Uses `MyTable` s Camera config

4. **LogEntryTable.tsx** (`/logs`)
   - Log entries (Admin only)
   - Uses `MyTable` s LogEntry config

5. **UsersTable.tsx** (`/users`)
   - User management (Admin only)
   - Uses `MyTable` s User config

### Lookup Tables

6. **LocationsTable.tsx** (`/locations`)
   - Location lookup table
   - Uses `MyTable` s Location config

7. **CarriersTable.tsx** (`/carriers`)
   - Carrier lookup table
   - Uses `MyTable` s Carrier config

8. **DriversTable.tsx** (`/drivers`)
   - Driver lookup table
   - Uses `MyTable` s Driver config

9. **PotsTable.tsx** (`/pots`)
   - Pot lookup table
   - Uses `MyTable` s Pot config

10. **PitsTable.tsx** (`/pits`)
    - Pit lookup table
    - Uses `MyTable` s Pit config

11. **MachinesTable.tsx** (`/machines`)
    - Machine lookup table
    - Uses `MyTable` s Machine config

### Other Pages

12. **Dashboard.tsx** (`/dashboard`)
    - Dashboard page
    - Factory selection (scope management)

13. **UserPreferences.tsx** (`/user-preferences`)
    - User preferences management

14. **Admin.tsx** (`/admin`)
    - Admin page (Admin only)

15. **GenerateDummy.tsx** (`/generate-dummy`)
    - Dummy data generator (Superuser only)

16. **Login.tsx** (`/login`)
    - Login page

17. **Home.tsx** (`/`)
    - Home page

18. **Contact.tsx** (`/contact`)
    - Contact page

## Mapovanie Model → FE Modul → Komponenty

| Model | Page Component | Route | MyTable Config | Features |
|-------|---------------|-------|----------------|----------|
| Factory | FactoryTable.tsx | `/factories` | Factory config | Share factory, CRUD |
| Location | LocationsTable.tsx | `/locations` | Location config | Lookup table |
| Carrier | CarriersTable.tsx | `/carriers` | Carrier config | Lookup table |
| Driver | DriversTable.tsx | `/drivers` | Driver config | Lookup table |
| Pot | PotsTable.tsx | `/pots` | Pot config | Lookup table |
| Pit | PitsTable.tsx | `/pits` | Pit config | Lookup table |
| Machine | MachinesTable.tsx | `/machines` | Machine config | Lookup table |
| Camera | Camera.tsx | `/camera` | Camera config | CRUD |
| Measurement | MeasurementsTable.tsx | `/measurements` | Measurement config | Graph cells, CRUD |
| LogEntry | LogEntryTable.tsx | `/logs` | LogEntry config | Read-only (Admin) |
| User | UsersTable.tsx | `/users` | User config | CRUD (Admin) |

## ConfigDriven Patterns

### 1. Fields Matrix Pattern

Každá tabuľka definuje `fieldsMatrix` v `MyTableConfig`:

```typescript
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
    resizable: true,
  },
  // ...
}
```

**Výhody**:
- Deklaratívna konfigurácia (žiadny hardcode)
- Jednotný formát pre všetky tabuľky
- Automatické generovanie UI (filtre, stĺpce, modaly)

### 2. Model Metadata Pattern

Všetky endpoints a metadáta sa čítajú z `modelMetadata.ts` (SSOT):

```typescript
const endpoint = getModelEndpoint('factory'); // → '/api/factories/'
const plural = getModelPlural('factory'); // → 'Factories'
const ordering = getDefaultOrdering('factory'); // → ['name']
```

**Výhody**:
- Žiadny hardcode endpoints
- Automatická synchronizácia s backendom
- Jednoduchá údržba

### 3. FK Cache Pattern

Všetky FK dropdowny používajú `fkCacheService`:

```typescript
const options = await loadFKOptionsFromCache('location');
```

**Výhody**:
- Rýchle načítanie (cache)
- Automatické scoping (backend)
- Jednotný formát

### 4. State Persistence Pattern

Všetky tabuľky používajú `useSnapshot` pre state persistence:

```typescript
const { updateTable, getTableState } = useSnapshot();
updateTable('factories', { pagination: { pageIndex: 0 } });
const state = getTableState('factories');
```

**Výhody**:
- Automatická synchronizácia s backendom
- Presets a snapshots
- Cross-tab synchronization

## Dôležité poznámky

1. **Všetky tabuľky používajú MyTable**: Jednotný komponent, ConfigDriven konfigurácia

2. **Žiadny hardcode**: Všetky endpoints, metadáta, FK options sa čítajú z SSOT

3. **Scoping**: Automaticky aplikované cez ScopeContext a backend ScopingEngine

4. **Permissions**: SSOT z UserPreference.role (nie Django flags)

5. **State Persistence**: Všetky tabuľky používajú TableStatePreset v databáze

6. **FK Cache**: Automaticky rebuilduje pri zmene scope alebo FK entít

7. **Field Factory**: Generický renderer pre všetky typy polí

8. **Modals**: Všetky CRUD operácie cez modaly (AddRecordModal, EditRecordModal)

9. **Export**: CSV, XLSX, PDF export cez useExport hook

10. **Error Handling**: Centralizované cez useErrorHandler hook

