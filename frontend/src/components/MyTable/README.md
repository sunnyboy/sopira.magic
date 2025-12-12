# MyTable - Unified Table Component

**MyTable** je unifikovaný komponent pre všetky tabuľky v Thermal Eye aplikácii. Poskytuje konzistentné UI, funkcionalitu a správanie naprieč celou aplikáciou pomocou deklaratívnej konfigurácie.

## Výhody

✅ **DRY Principle** - Kód sa nepíše opakovane  
✅ **Konzistencia** - Všetky tabuľky vyzerajú a fungujú rovnako  
✅ **Rýchlosť** - Nová tabuľka za 10 minút namiesto hodín  
✅ **Maintainability** - Bug fix na jednom mieste  
✅ **Type-safe** - Plná TypeScript podpora  
✅ **Flexibilita** - Dá sa customizovať cez config  

## Rýchly štart

```tsx
import { MyTable } from '@/components/MyTable';
import type { MyTableConfig } from '@/components/MyTable';

interface MyRecord {
  id: string;
  name: string;
  created: string;
}

function MyTablePage() {
  const config: MyTableConfig<MyRecord> = {
    tableName: 'My Records',
    apiEndpoint: '/api/myrecords/',
    storageKey: 'myrecords',
    
    fields: [
      { key: 'id', header: 'ID', type: 'text', size: 80, editable: false },
      { key: 'name', header: 'Name', type: 'text', size: 200 },
      { key: 'created', header: 'Created', type: 'date', size: 180, editable: false },
    ],
  };
  
  return <MyTable config={config} />;
}
```

## Konfigurácia

### Základné nastavenia

```typescript
{
  // Identifikácia
  tableName: string;              // Názov tabuľky (zobrazí sa v header)
  apiEndpoint: string;            // API endpoint pre fetch (napr. '/api/logs/')
  storageKey: string;             // Kľúč pre persistence (filters, columns)
  
  // Stĺpce - FieldFactory konfigurácia
  fields: FieldConfig[];          // Pole field definícií
}
```

### Field Types (FieldFactory)

MyTable používa **FieldFactory** pre generovanie stĺpcov. Podporované typy:

#### Text Field
```typescript
{
  key: 'name',
  header: 'Name',
  type: 'text',
  size: 200,
  editable: true,
  multiline: false,
  maxLength: 100,
}
```

#### Number Field
```typescript
{
  key: 'count',
  header: 'Count',
  type: 'number',
  size: 100,
  editable: true,
  min: 0,
  max: 1000,
  decimals: 2,
  alignRight: true,
}
```

#### Date Field
```typescript
{
  key: 'created',
  header: 'Created',
  type: 'date',
  size: 180,
  editable: false,
  format: 'DD.MM.YYYY',
}
```

#### Select Field
```typescript
{
  key: 'status',
  header: 'Status',
  type: 'select',
  size: 120,
  options: [
    { value: 'active', label: 'Active' },
    { value: 'inactive', label: 'Inactive' },
  ],
}
```

#### Foreign Key Field
```typescript
{
  key: 'factory',
  header: 'Factory',
  type: 'fk',
  size: 150,
  labelField: 'factory_label',
  options: [
    { id: 'uuid-1', label: 'Factory A' },
    { id: 'uuid-2', label: 'Factory B' },
  ],
}
```

#### Tag Field
```typescript
{
  key: 'tags',
  header: 'Tags',
  type: 'tag',
  size: 250,
  suggestions: ['urgent', 'review', 'done'],
  maxNumberOfTags: 5,
}
```

### Visibility Controls

Každý UI element môže byť zapnutý/vypnutý:

```typescript
{
  // Page Header
  pageHeader: {
    visible: true,
    title: 'Custom Title',      // default: tableName
    subtitle: 'Subtitle text',
    buildNumber: true,
  },
  
  // Page Footer
  pageFooter: {
    visible: true,
  },
  
  // TableHeader elementy
  headerVisibility: {
    title: true,          // Table title
    stats: true,          // Selected/Visible/Total counts
    pagination: true,     // Pagination controls
    pageSize: true,       // Page size select
    search: true,         // Global search input
    toolbar: true,        // Toolbar buttons
  },
  
  // TableToolbar buttons
  toolbarVisibility: {
    filters: true,        // Filters panel toggle
    columns: true,        // Columns panel toggle
    compact: false,       // Compact/Expand mode toggle
    add: true,            // Add new record button
    csv: true,            // CSV export
    xlsx: true,           // XLSX export
    pdf: false,           // PDF export
    reset: true,          // Reset all filters/state
    save: false,          // Save changes (bulk edit)
    editAll: false,       // Edit all mode
    delete: false,        // Delete selected (shows when selectedCount > 0)
  },
}
```

### Features

```typescript
{
  // Filters
  filters: {
    fields: ['name', 'created', 'status'],  // Filterable fields
    persistence: true,                       // Save filters to DB
  },
  
  // Columns panel
  columns: {
    enabled: true,
    persistence: true,  // Save column state to DB
  },
  
  // Actions column
  actions: {
    edit: true,
    delete: true,
    customActions: [
      {
        label: 'Archive',
        icon: <ArchiveIcon />,
        onClick: (row) => archiveRecord(row),
        variant: 'solid',
      },
    ],
  },
  
  // Inline edit
  inlineEdit: {
    enabled: true,
    allowedFields: ['name', 'status'],  // Optional: limit editable fields
  },
  
  // Export
  export: {
    csv: true,
    xlsx: true,
    pdf: false,
  },
  
  // Row selection
  rowSelection: {
    enabled: true,
    mode: 'multiple',  // or 'single'
  },
  
  // Pagination
  pagination: {
    defaultPageSize: 5,
    pageSizeOptions: [5, 10, 25, 50, 100, 250, 500],
  },
  
  // Empty state
  emptyState: {
    text: 'No records found.',
    icon: <EmptyIcon />,
  },
}
```

### Callbacks

```typescript
{
  callbacks: {
    onAdd: () => openAddModal(),
    onEdit: (record) => openEditModal(record),
    onDelete: async (records) => {
      await deleteRecords(records);
    },
    onSave: async (records) => {
      await saveChanges(records);
    },
    onEditAll: () => enableEditAllMode(),
    onExportCSV: () => exportToCSV(),
    onExportXLSX: () => exportToXLSX(),
    onExportPDF: () => exportToPDF(),
    onRefresh: () => refetchData(),
  },
}
```

## Príklady

### Read-only Log Table

```typescript
const config: MyTableConfig<LogEntry> = {
  tableName: 'Log Entries',
  apiEndpoint: '/api/logs/',
  storageKey: 'logentry',
  
  fields: [
    { key: 'id', header: 'ID', type: 'text', size: 80, editable: false },
    { key: 'timestamp', header: 'Timestamp', type: 'date', size: 180, editable: false },
    { key: 'level', header: 'Level', type: 'select', size: 100, editable: false, options: [...] },
    { key: 'message', header: 'Message', type: 'text', size: 400, editable: false },
  ],
  
  toolbarVisibility: {
    add: false,     // Cannot add logs manually
    editAll: false,
    save: false,
  },
  
  actions: {
    edit: false,    // Logs are immutable
    delete: true,   // Allow cleanup
  },
  
  inlineEdit: {
    enabled: false,
  },
};
```

### Editable User Table

```typescript
const config: MyTableConfig<User> = {
  tableName: 'Users',
  apiEndpoint: '/api/users/',
  storageKey: 'users',
  
  fields: [
    { key: 'id', header: 'ID', type: 'text', size: 80, editable: false },
    { key: 'username', header: 'Username', type: 'text', size: 150 },
    { key: 'email', header: 'Email', type: 'text', size: 200 },
    { key: 'is_active', header: 'Active', type: 'select', size: 100, options: [...] },
    { key: 'role', header: 'Role', type: 'select', size: 120, options: [...] },
  ],
  
  toolbarVisibility: {
    add: true,
    editAll: true,
    save: true,
  },
  
  actions: {
    edit: true,
    delete: true,
  },
  
  inlineEdit: {
    enabled: true,
  },
  
  callbacks: {
    onAdd: () => openAddUserModal(),
    onEdit: (user) => openEditUserModal(user),
    onDelete: async (users) => {
      await deleteUsers(users.map(u => u.id));
    },
  },
};
```

## Architektúra

MyTable je **orchestrátor** - skladá hotové shadcn komponenty:

```
MyTable
├── PageHeader
├── TableCard
│   ├── TableHeader
│   │   ├── TableSearch
│   │   └── TableToolbar
│   ├── FilterPanel (conditional)
│   ├── ColumnsPanel (conditional)
│   └── TableWrapper
│       └── <table> (TanStack Table)
└── PageFooter
```

### Použité komponenty

- **Data fetching**: `useMyTableData` hook
- **Columns**: `FieldFactory` (createTableColumns)
- **Table logic**: TanStack Table v8
- **UI**: shadcn custom components (TableCard, TableHeader, FilterPanel, atď.)
- **State**: useColumnState, useFilterState, useRowSelection
- **Persistence**: Backend API (/api/user/filters/, /api/user/columns/)

## Persistence

MyTable automaticky ukladá:

- **Filter presets** - do DB cez `/api/user/filters/`
- **Column state** - do DB cez `/api/user/columns/`
- Uložené preset-y sú dostupné naprieč sessions

## Rozšírenia

### Custom Filter Functions

```typescript
{
  customFilterFns: {
    myCustomFilter: (row, columnId, filterValue) => {
      return row.getValue(columnId) === filterValue;
    },
  },
}
```

### Custom Columns

Ak FieldFactory nestačí, môžeš pridať vlastné stĺpce:

```typescript
{
  customColumns: [
    {
      id: 'custom',
      header: 'Custom',
      cell: (info) => <CustomCell data={info.row.original} />,
    },
  ],
}
```

### Custom Toolbar Buttons

```typescript
{
  customToolbarButtons: (
    <>
      <Button onClick={handleCustomAction}>
        <CustomIcon size={16} />
        Custom
      </Button>
    </>
  ),
}
```

## Debug Mode

Pre ladenie zapni debug mode:

```typescript
{
  debug: true,  // Zobrazí debug panel s state info
}
```

## Migration Guide

### Zo starej tabuľky na MyTable

1. **Identifikuj data type** - vytvor TypeScript interface
2. **Definuj fields** - použij FieldConfig array
3. **Nastav visibility** - vypni nepotrebné UI elementy
4. **Implementuj callbacks** - onAdd, onEdit, onDelete, atď.
5. **Testuj** - over funkcionalitu v prehliadači

**Príklad: Z MeasurementsTable na MyTable**

Pred (cca 1200 riadkov):
```tsx
// MeasurementsTable.tsx - 1200+ lines of code
```

Po (cca 300 riadkov):
```tsx
// MeasurementsTable.tsx - just config!
const config: MyTableConfig<Measurement> = { ... };
return <MyTable config={config} />;
```

## Limitácie

- **FieldFactory typy** - Ak potrebuješ custom field type, musíš použiť `customColumns`
- **Complex forms** - Quick create s vlastným formulárom ešte nie je podporovaný
- **Graph columns** - Zatiaľ nie je implementované (použij customColumns)

## TODO

- [ ] Dynamic filter rendering (podľa filters.fields)
- [ ] Quick create panel integration
- [ ] Graph column type support
- [ ] PDF export implementation
- [ ] Edit all mode implementation
- [ ] Compact/Expand view toggle

## Príspevky

Pri úprave MyTable:

1. Aktualizuj `MyTableTypes.ts` - pridaj nové config options
2. Implementuj v `MyTable.tsx` - pridaj logiku
3. Aktualizuj `README.md` - dokumentuj zmeny
4. Otestuj na pilotnom príklade - napr. LogEntryTable

## Viac informácií

- [table-standards.md](../../../table-standards.md) - Design guidelines pre tabuľky
- [FieldFactory](../ui_custom/table/fieldFactory.tsx) - Field config reference
- [tableImports](../ui_custom/table/tableImports.ts) - Centralizované importy

