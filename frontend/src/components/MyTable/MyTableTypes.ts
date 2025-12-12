/*........................................................
//*       www/thermal_eye_ui/src/components/MyTable/MyTableTypes.ts
//*       Type definitions for unified MyTable component
//*       
//*       Purpose: Deklaratívna konfigurácia pre všetky tabuľky
//*       Features: Konfigurovateľné UI elementy, actions, exports, filters
//*........................................................

import type { ColumnDef } from '@tanstack/react-table';
import type { FieldConfig } from '@/components/ui_custom/table/fieldFactory';
import type { ReactNode } from 'react';

/**
 * Visibility flags pre TableHeader elementy
 */
export interface TableHeaderVisibility {
  /** Zobrazit title (default: true) */
  title?: boolean;
  /** Zobrazit stats (Selected/Visible/Total) (default: true) */
  stats?: boolean;
  /** Zobrazit pagination controls (default: true) */
  pagination?: boolean;
  /** Zobrazit page size select (default: true) */
  pageSize?: boolean;
  /** Zobrazit search input (default: true) */
  search?: boolean;
  /** Zobrazit toolbar (default: true) */
  toolbar?: boolean;
}

/**
 * Visibility flags pre TableToolbar buttons
 */
export interface TableToolbarVisibility {
  /** Zobrazit Filters toggle button (default: true) */
  filters?: boolean;
  /** Zobrazit Columns toggle button (default: true) */
  columns?: boolean;
  /** Zobrazit Compact/Expand toggle button (default: false) */
  compact?: boolean;
  /** Zobrazit Add button (default: true) */
  add?: boolean;
  /** Zobrazit CSV export button (default: true) */
  csv?: boolean;
  /** Zobrazit XLSX export button (default: true) */
  xlsx?: boolean;
  /** Zobrazit PDF export button (default: false) */
  pdf?: boolean;
  /** Zobrazit Reset button (default: true) */
  reset?: boolean;
  /** Zobrazit Save button (condition: saveCount > 0) (default: false) */
  save?: boolean;
  /** Zobrazit Share button (condition: shareCount > 0, Admin/SA only) (default: false) */
  share?: boolean;
  /** Zobrazit Edit All button (default: false) */
  editAll?: boolean;
  /** Zobrazit Delete button (condition: deleteCount > 0) (default: false) */
  delete?: boolean;
}

/**
 * Konfigurácia page header
 */
export interface PageHeaderConfig {
  /** Zobrazit page header (default: true) */
  visible?: boolean;
  /** Title (default: tableName) */
  title?: string;
  /** Subtitle text (default: undefined) */
  subtitle?: string;
  /** Zobrazit build number (default: false) */
  buildNumber?: boolean;
}

/**
 * Konfigurácia page footer
 */
export interface PageFooterConfig {
  /** Zobrazit page footer (default: true) */
  visible?: boolean;
}

/**
 * Konfigurácia pre Actions column
 */
export interface ActionsConfig<T = any> {
  /** Povolit edit action (default: true) */
  edit?: boolean;
  /** Povolit delete action (default: true) */
  delete?: boolean;
  /** Povolit expand action - rozbalí riadok pre zobrazenie detailov (default: false) */
  expand?: boolean;
  /** Povolit inline share action button v riadku (default: false) */
  inlineShare?: boolean;
  /** Custom action buttons */
  customActions?: Array<{
    label: string;
    icon?: ReactNode;
    onClick: (row: T) => void;
    variant?: 'default' | 'danger' | 'solid' | 'ghost';
  }>;
}

/**
 * Konfigurácia pre Quick Create/Edit
 */
export interface QuickCreateConfig<T = any> {
  /** Enable quick create panel (default: false) */
  enabled?: boolean;
  /** Form schema (zod) */
  schema?: any;
  /** Form fields component */
  FormFields?: React.ComponentType<any>;
  /** Default values generator */
  getDefaults?: () => any;
  /** Transform data before submit */
  transformForApi?: (data: any) => any;
  /** On success callback */
  onSuccess?: (newRecord: T) => void;
}

/**
 * Konfigurácia pre Inline Edit
 */
export interface InlineEditConfig {
  /** Enable inline edit (default: true) */
  enabled?: boolean;
  /** Fields that can be edited inline (default: all editable fields) */
  allowedFields?: string[];
}

/**
 * Konfigurácia pre Filters
 * 
 * Umožňuje deklaratívne nastaviť ktoré polia sú filtrovateľné.
 * fields môže byť buď array string[] alebo objekt Record<string, boolean>
 * 
 * @example
 * // Simple array (všetky true):
 * fields: ['name', 'level', 'created']
 * 
 * @example
 * // Detailná kontrola (DATA:KEY štruktúra):
 * fields: {
 *   name: true,
 *   level: true,
 *   created: false,  // disabled
 * }
 */
export interface FiltersConfig {
  /** 
   * Filter field keys - môže byť array alebo objekt
   * - string[]: všetky uvedené polia budú filtrovateľné
   * - Record<string, boolean>: KEY=true znamená zobrazit filter, KEY=false znamená skryt
   */
  fields?: string[] | Record<string, boolean>;
  /** Custom filter components (pre pokročilé custom filtry) */
  customFilters?: ReactNode;
  /** Enable filter persistence - ukladá filtre do DB (default: true) */
  persistence?: boolean;
}

/**
 * Konfigurácia pre Columns panel
 * 
 * Umožňuje nastaviť ktoré columns sú v ColumnsPanel a ich default viditeľnosť.
 * 
 * @example
 * // Detailná kontrola (KEY:[isInList, defaultVisibility] štruktúra):
 * columns: {
 *   fields: {
 *     id: [true, false],        // V ColumnsPanel, ale defaultne skryté
 *     created: [false, false],  // Nie je v ColumnsPanel vôbec
 *     level: [true, true],      // V ColumnsPanel a defaultne zobrazené
 *   }
 * }
 */
export interface ColumnsConfig {
  /** Enable columns panel - umožní užívateľovi meniť viditeľnosť columns (default: true) */
  enabled?: boolean;
  /** Enable column persistence - ukladá column state do DB (default: true) */
  persistence?: boolean;
  /** 
   * Column configuration (KEY:[isInList, defaultVisibility] štruktúra)
   * - [true, true]   = pole JE v ColumnsPanel a JE defaultne zobrazené
   * - [true, false]  = pole JE v ColumnsPanel ale NIE JE defaultne zobrazené
   * - [false, false] = pole NIE JE v ColumnsPanel vôbec (užívateľ ho nemôže meniť)
   * - [false, true]  = pole NIE JE v ColumnsPanel ale JE zobrazené (always visible)
   */
  fields?: Record<string, [boolean, boolean]>;
  /** Default column order (zľava doprava) */
  defaultOrder?: string[];
}

/**
 * Konfigurácia pre Export
 */
export interface ExportConfig {
  /** CSV export enabled (default: true) */
  csv?: boolean;
  /** XLSX export enabled (default: true) */
  xlsx?: boolean;
  /** PDF export enabled (default: false) */
  pdf?: boolean;
  /** CSV filename generator */
  csvFilename?: () => string;
  /** XLSX filename generator */
  xlsxFilename?: () => string;
  /** PDF filename generator */
  pdfFilename?: () => string;
}

/**
 * Konfigurácia pre Row Selection
 * 
 * Umožňuje výber riadkov pomocou checkboxov.
 */
export interface RowSelectionConfig {
  /** Enable row selection - zobrazí selection checkbox column (default: true) */
  enabled?: boolean;
  /** 
   * Selection mode:
   * - 'single': len jeden riadok môže byť selected
   * - 'multiple': viacero riadkov môže byť selected (default)
   */
  mode?: 'single' | 'multiple';
  /** Enable persistence - ukladá selected rows do localStorage/sessionStorage (default: false) */
  persistence?: boolean;
}

/**
 * Konfigurácia pre MultiLine režim
 * 
 * Určuje ako sa zobrazujú bunky s textom.
 */
export interface MultiLineConfig {
  /**
   * Default multiline mode:
   * - false: kompaktný režim - text je skrátený na 1 riadok (default)
   * - true: rozšírený režim - text je zalomený cez viac riadkov
   */
  enabled?: boolean;
  /**
   * Allow user to toggle - zobrazí toggle button v toolbar (default: true)
   */
  allowToggle?: boolean;
  /**
   * Persistence - ukladá multiline state do localStorage (default: true)
   */
  persistence?: boolean;
}

// ============================================
// FIELD MATRIX - SINGLE SOURCE OF TRUTH
// ============================================

/**
 * Centrálna konfigurácia pre jedno pole (field) v tabuľke
 * 
 * Single source of truth - všetky atribúty poľa na jednom mieste:
 * - Základné properties (type, header, size)
 * - Column panel & viditeľnosť
 * - Filter panel
 * - Editovateľnosť (modal, inline)
 * - Sortovanie, resizing, etc.
 */
export interface FieldMatrixItem {
  // ============================================
  // BASIC PROPERTIES
  // ============================================
  /** Field type (text, number, date, select, fk, tag, boolean, etc.) */
  type: 'text' | 'number' | 'temperature' | 'date' | 'time' | 'boolean' | 'select' | 'fk' | 'tag' | 'json';
  /** Column header label */
  header: string;
  /** Column width (default: 120) */
  size?: number;
  /** Minimum column width for resizing (default: 50) */
  minSize?: number;
  /** Maximum column width for resizing (default: 1000) */
  maxSize?: number;
  /** Poradie v tabuľke (zľava doprava, nižšie = ľavejšie) */
  order?: number;
  
  // ============================================
  // COLUMN PANEL & VISIBILITY
  // ============================================
  /** Je pole zobrazené v ColumnsPanel (pre toggle visibility)? (default: true) */
  isInColumnPanel?: boolean;
  /** Je pole defaultne viditeľné v tabuľke? (default: true) */
  defaultVisible?: boolean;
  
  // ============================================
  // FILTER PANEL
  // ============================================
  /** Je pole zobrazené v FilterPanel? (default: false) */
  isInFilterPanel?: boolean;
  /** Typ filtra (text, range, select, multiselect, daterange, etc.) */
  filterType?: 'text' | 'range' | 'select' | 'multiselect' | 'daterange' | 'timerange' | 'checkbox' | 'tag' | 'boolean';
  
  // ============================================
  // EDITING
  // ============================================
  /** Editovateľné v Edit modale? (default: true) */
  editableInEditModal?: boolean;
  /** Editovateľné v Add modale? (default: true pre non-system fields) */
  editableInAddModal?: boolean;
  /** Editovateľné inline double-click? (default: true) */
  editableInline?: boolean;
  /** Je pole povinné? (pre validáciu) */
  required?: boolean;
  /** Poradie v Edit modale (ak nie je zadané, použije sa `order`) */
  orderInEditModal?: number;
  /** Poradie v Add modale (ak nie je zadané, použije sa `order`) */
  orderInAddModal?: number;
  
  // ============================================
  // OTHER PROPERTIES
  // ============================================
  /** Sortovateľné? (default: true) */
  sortable?: boolean;
  /** Resizable column? (default: true) */
  resizable?: boolean;
  /** Format pre zobrazenie (napr. 'DD.MM.YYYY' pre date) */
  format?: string;
  /** Placeholder text pre input */
  placeholder?: string;
  /** Multiline text? (pre textarea) */
  multiline?: boolean;
  
  // ============================================
  // TYPE-SPECIFIC PROPERTIES
  // ============================================
  /** Options pre select/multiselect */
  options?: Array<{ value: string; label: string }>;
  /** Min hodnota pre number */
  min?: number;
  /** Max hodnota pre number */
  max?: number;
  /** Step pre number input */
  step?: number;
  /** Decimals pre number/temperature */
  decimals?: number;
  /** Align right (pre čísla)? */
  alignRight?: boolean;
  /** FK labelField (pre foreign key) */
  labelField?: string;
  /** FK API endpoint (pre foreign key, napr. '/api/factories') - ak nie je zadaný, použije sa pluralName alebo automatická pluralizácia */
  apiEndpoint?: string;
  /** FK plural name (pre automatickú konštrukciu endpoint-u, napr. 'factories' pre 'factory') - ak nie je zadaný, použije sa {fieldName}+'s' */
  pluralName?: string;
  /** FK scoped by factory? */
  scopedByFactory?: boolean;
  /** Use all_accessible=true parameter for this FK field (default: false) */
  useAllAccessible?: boolean;
  /** Tag suggestions */
  suggestions?: string[];
  /** Max tags */
  maxNumberOfTags?: number;
  
  // ============================================
  // BOOLEAN FIELD SPECIFIC
  // ============================================
  /** Label for true value (default: 'True') - for boolean fields */
  trueLabel?: string;
  /** Label for false value (default: 'False') - for boolean fields */
  falseLabel?: string;
  /** Display style: 'badge' (colored), 'icon' (checkmark/x), or 'text' - for boolean fields */
  style?: 'badge' | 'icon' | 'text';
  /** Quick toggle: single click toggles value (default: false = double-click opens dropdown) - for boolean fields */
  quickToggle?: boolean;
}

/**
 * Centrálny Field Matrix - mapa všetkých polí v tabuľke
 * 
 * Kľúč = field key (názov poľa v data objekte)
 * Hodnota = FieldMatrixItem (všetky atribúty poľa)
 * 
 * @example
 * ```typescript
 * fieldsMatrix: {
 *   id: {
 *     type: 'text',
 *     header: 'ID',
 *     size: 80,
 *     order: 1,
 *     isInColumnPanel: true,
 *     defaultVisible: true,
 *     isInFilterPanel: true,
 *     filterType: 'text',
 *     editableInEditModal: false,
 *     editableInline: false,
 *     sortable: true,
 *   },
 *   level: {
 *     type: 'select',
 *     header: 'Level',
 *     size: 100,
 *     order: 4,
 *     isInColumnPanel: true,
 *     defaultVisible: true,
 *     isInFilterPanel: true,
 *     filterType: 'multiselect',
 *     editableInEditModal: true,
 *     editableInline: true,
 *     sortable: true,
 *     options: [
 *       { value: 'info', label: 'Info' },
 *       { value: 'warning', label: 'Warning' },
 *     ],
 *   },
 * }
 * ```
 */
export type FieldMatrix<T = any> = Record<keyof T & string, FieldMatrixItem>;

/**
 * Konfigurácia pre Pagination
 * 
 * Nastavuje ako sa zobrazujú stránkované dáta.
 */
export interface PaginationConfig {
  /** Default page size - koľko riadkov zobrazit na stránku (default: 50) */
  defaultPageSize?: number;
  /** 
   * Available page sizes - možnosti v page size selecte (default: [10, 25, 50, 100, 250, 500])
   * Príklad: [5, 10, 25, 50, 100, 250]
   */
  pageSizeOptions?: number[];
  /**
   * Custom pagination mode:
   * - false: standard pagination (default)
   * - true: custom pagination with extended options
   */
  custom?: boolean;
  /** 
   * Custom max - maximálny počet záznamov pre custom pagination (default: 1000)
   * Používa sa len ak custom: true
   */
  customMax?: number;
  /** Enable persistence - ukladá page size do localStorage (default: true) */
  persistence?: boolean;
}

/**
 * Konfigurácia pre Empty State
 * 
 * Definuje ako sa zobrazí prázdna tabuľka (keď žiadne záznamy nevyhovujú filtrom).
 * 
 * @example
 * emptyState: {
 *   text: 'No log entries found.',
 *   icon: <InfoIcon />
 * }
 */
export interface EmptyStateConfig {
  /** 
   * Empty state text - správa zobrazená keď tabuľka nemá žiadne záznamy
   * (default: "No records match your criteria.")
   */
  text?: string;
  /** Empty state icon - voliteľná ikona zobrazená nad textom */
  icon?: ReactNode;
}

/**
 * Callback funkcie pre actions
 */
export interface MyTableCallbacks<T = any> {
  /** On add new record */
  onAdd?: () => void;
  /** On edit record */
  onEdit?: (record: T) => void;
  /** On delete record(s) */
  onDelete?: (records: T[]) => void;
  /** On save changes (bulk) */
  onSave?: (records: T[]) => void;
  /** On edit all */
  onEditAll?: () => void;
  /** On share records */
  onShare?: () => void;
  /** On export CSV */
  onExportCSV?: () => void;
  /** On export XLSX */
  onExportXLSX?: () => void;
  /** On export PDF */
  onExportPDF?: () => void;
  /** On data refresh */
  onRefresh?: () => void;
}

/**
 * Hlavná konfigurácia pre MyTable
 */
export interface MyTableConfig<T extends Record<string, any> = any> {
  // ============================================
  // IDENTIFIKÁCIA
  // ============================================
  /** Table name (zobrazí sa v header) */
  tableName: string;
  /** API endpoint pre data fetch (napr. '/api/logentries/') */
  apiEndpoint: string;
  /** Storage key pre persistence (filters, columns) */
  storageKey: string;

  // ============================================
  // COLUMNS - FieldFactory
  // ============================================
  /**
   * OPTION 1 (NEW): Field Matrix - Single source of truth
   * 
   * Centrálna konfigurácia všetkých polí na jednom mieste.
   * Definuje type, visibility, editability, filters, etc.
   * 
   * Ak je použitý fieldsMatrix, fields/columns/filters sa automaticky vygenerujú.
   */
  fieldsMatrix?: FieldMatrix<T>;
  
  /**
   * OPTION 2 (OLD): Manual field configurations
   * 
   * Manuálne field configs pre FieldFactory.
   * Použité len ak fieldsMatrix NIE je definovaný.
   */
  fields?: FieldConfig<T>[];

  // ============================================
  // VISIBILITY CONTROLS
  // ============================================
  /** Page header configuration */
  pageHeader?: PageHeaderConfig;
  /** Page footer configuration */
  pageFooter?: PageFooterConfig;
  /** TableHeader visibility flags */
  headerVisibility?: TableHeaderVisibility;
  /** TableToolbar visibility flags */
  toolbarVisibility?: TableToolbarVisibility;

  // ============================================
  // FEATURES
  // ============================================
  /** Filters configuration */
  filters?: FiltersConfig;
  /** Columns panel configuration */
  columns?: ColumnsConfig;
  /** Actions column configuration */
  actions?: ActionsConfig<T>;
  /** Quick create configuration */
  quickCreate?: QuickCreateConfig<T>;
  /** Inline edit configuration */
  inlineEdit?: InlineEditConfig;
  /** Export configuration */
  export?: ExportConfig;
  /** Global search configuration */
  globalSearch?: {
    /** Enable global search (default: true) */
    enabled?: boolean;
    /** Enable advanced search syntax with AND, OR, NOT, parentheses (default: false) */
    advancedSearch?: boolean;
    /** Použiť search microservice (ES) pre global search (default: true) */
    useSearchService?: boolean;
    /** Povoliť prepínanie simple/advanced v UI (default: true) */
    allowModeToggle?: boolean;
    /** Povoliť fuzzy/approximate toggle (default: true) */
    allowApprox?: boolean;
    /** Custom placeholder text (overrides default) */
    placeholder?: string;
    /** Debounce delay in ms (default: 300) */
    debounceMs?: number;
  };
  /** Row selection configuration */
  rowSelection?: RowSelectionConfig;
  /** Pagination configuration */
  pagination?: PaginationConfig;
  /** MultiLine configuration - prepína medzi kompaktným (1-riadkovým) a rozšíreným (viac-riadkovým) režimom */
  multiLine?: MultiLineConfig;
  /** Empty state configuration */
  emptyState?: EmptyStateConfig;

  // ============================================
  // CALLBACKS
  // ============================================
  /** Event callbacks */
  callbacks?: MyTableCallbacks<T>;

  // ============================================
  // ADVANCED
  // ============================================
  /** Disable automatic factory scope filter (for global tables like Users that don't belong to any factory) */
  disableFactoryScope?: boolean;
  /** Custom column definitions (if you need to override FieldFactory) */
  customColumns?: ColumnDef<T, any>[];
  /** Custom cell renderers for specific fields (e.g. graphs, custom components) */
  customCellRenderers?: Record<string, (row: T) => ReactNode>;
  /** Custom filter functions */
  customFilterFns?: Record<string, any>;
  /** Custom global filter function */
  customGlobalFilterFn?: (row: any, columnId: string, filterValue: any) => boolean;
  /** Custom toolbar buttons */
  customToolbarButtons?: ReactNode;
  /** Enable debug mode (logs state) */
  debug?: boolean;
  /** Disable backend snapshot/table-state persistence */
  disableSnapshot?: boolean;
  /** Disable backend filter preset persistence */
  disableFilterState?: boolean;
  /**
   * Use new MyState system for state persistence (mystate module)
   * 
   * When enabled:
   * - Current state (sorting, filters, pagination, columns) stored in LocalStorage
   * - Saved presets stored in STATE database (shareable)
   * 
   * When disabled (default):
   * - Uses legacy state module
   * 
   * @default false
   */
  useMyState?: boolean;
}

/**
 * Default config values (pre-filled defaults)
 */
export const DEFAULT_MY_TABLE_CONFIG: Partial<MyTableConfig> = {
  pageHeader: {
    visible: true,
    buildNumber: false,
  },
  pageFooter: {
    visible: true,
  },
  headerVisibility: {
    title: true,
    stats: true,
    pagination: true,
    pageSize: true,
    search: true,
    toolbar: true,
  },
  toolbarVisibility: {
    filters: true,
    columns: true,
    compact: false,
    add: true,
    share: true,
    csv: true,
    xlsx: true,
    pdf: false,
    reset: true,
    save: false,
    editAll: false,
    delete: false,
  },
  filters: {
    persistence: true,
  },
  columns: {
    enabled: true,
    persistence: true,
    fields: {}, // Empty by default - všetky columns sú v liste a zobrazené
  },
  actions: {
    edit: true,
    delete: true,
    expand: false,
    inlineShare: false,
  },
  inlineEdit: {
    enabled: true,
  },
  export: {
    share: true,
    csv: true,
    xlsx: true,
    pdf: false,
  },
  globalSearch: {
    enabled: true,
    advancedSearch: false, // Default: simple search
    useSearchService: true,
    allowModeToggle: true,
    allowApprox: true,
    debounceMs: 300,
  },
  rowSelection: {
    enabled: true,
    mode: 'multiple',
    persistence: false,
  },
  pagination: {
    defaultPageSize: 5,
    pageSizeOptions: [5, 10, 25, 50, 100, 250, 500],
    custom: false,
    customMax: 1000,
    persistence: true,
  },
  multiLine: {
    enabled: false, // Default: compact mode (single-line)
    allowToggle: true,
    persistence: true,
  },
  emptyState: {
    text: 'No records match your criteria.',
  },
  debug: false,
  useMyState: false, // Default: legacy state module
};

