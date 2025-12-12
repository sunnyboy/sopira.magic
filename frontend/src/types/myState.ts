/**
 * MyState Types - TypeScript definitions for state management
 * 
 * Types for the new mystate module including:
 * - Scope types and state data structures
 * - API response types
 * - Hook return types
 * 
 * These types mirror the backend MYSTATE_CONFIG structure.
 */

// =============================================================================
// SCOPE TYPES
// =============================================================================

/** 
 * Available scope types - hierarchical structure
 * user → application → page → page_element → subelement
 */
export type ScopeType = 
  // Root level
  | 'user'
  // Level 1
  | 'application'
  // Level 2  
  | 'page'
  // Level 3 - page elements
  | 'table'
  | 'pdfviewer'
  | 'texteditor'
  | 'formgenerator'
  // Level 4 - subelements (table-specific)
  | 'table_columns'
  | 'table_filters'
  // Legacy compatibility
  | 'global';

/** Scope configuration from backend */
export interface ScopeConfig {
  key_pattern: string;
  description: string;
  tracked_states: string[];
}

/** Scope hierarchy definition */
export interface ScopeHierarchyConfig {
  parent: ScopeType | null;
  children: ScopeType[];
  state_fields: string[];
  description: string;
  depth: number;
}

/** Child state snapshot - stored in parent's children_state */
export interface ChildStateSnapshot {
  preset_name: string | null;
  preset_id: string | null;
  state_data: GenericStateData;
}

/** Children state map - scope_type -> snapshot */
export type ChildrenState = Record<ScopeType, ChildStateSnapshot>;

// =============================================================================
// STATE DATA TYPES
// =============================================================================

/** Pagination state */
export interface PaginationState {
  pageSize: number;
  pageIndex: number;
}

/** Sorting state item */
export interface SortingItem {
  id: string;
  desc: boolean;
}

/** Column filter state item */
export interface ColumnFilterItem {
  id: string;
  value: any;
}

/** Scroll position state */
export interface ScrollPosition {
  x: number;
  y: number;
}

/** Panel state (filter/column panels) */
export interface PanelState {
  isOpen: boolean;
  activePresetId: string | null;
}

/** Table-specific state fields */
export interface TableStateData {
  pagination?: PaginationState;
  sorting?: SortingItem[];
  columnFilters?: ColumnFilterItem[];
  globalFilter?: string;
  columnVisibility?: Record<string, boolean>;
  columnOrder?: string[];
  columnSizing?: Record<string, number>;
  rowSelection?: Record<string, boolean>;
  scrollPosition?: ScrollPosition;
  expandedRows?: string[];
  searchValue?: string;
  focusedField?: string | null;
  filterPanelState?: PanelState;
  columnPanelState?: PanelState;
  highlightedRowId?: string | null;
}

/** Page-specific state fields */
export interface PageStateData {
  layout?: Record<string, any>;
  widgets?: any[];
  collapsed?: Record<string, boolean>;
  activeTab?: string | null;
  scrollPosition?: ScrollPosition;
  focusedField?: string | null;
  panelSizes?: Record<string, number>;
  expandedSections?: string[];
}

/** Global state fields */
export interface GlobalStateData {
  theme?: 'light' | 'dark';
  language?: string;
  sidebarCollapsed?: boolean;
  selectedFactory?: string | null;
  colorScheme?: string;
  notificationsEnabled?: boolean;
  compactMode?: boolean;
  lastVisitedPage?: string | null;
}

/** Union type for all state data */
export type StateData = TableStateData | PageStateData | GlobalStateData;

/** Generic state data (for type flexibility) */
export type GenericStateData = Record<string, any>;

// =============================================================================
// API TYPES
// =============================================================================

/** Saved state from API */
export interface SavedState {
  id: string;
  uuid: string;
  user_id: string;
  scope_type: ScopeType;
  scope_key: string;
  preset_name: string;
  description: string;
  state_data: GenericStateData;
  /** Hierarchical children state snapshots */
  children_state: ChildrenState | null;
  is_default: boolean;
  created: string;
  updated: string;
  scope_display: string;
  /** Whether this preset has any children state */
  has_children: boolean;
  /** Names of child presets (for display) */
  child_preset_names: Record<ScopeType, string | null>;
}

/** Saved state list item (without full state_data) */
export interface SavedStateListItem {
  id: string;
  uuid: string;
  scope_type: ScopeType;
  scope_key: string;
  preset_name: string;
  description: string;
  is_default: boolean;
  created: string;
  updated: string;
  scope_display: string;
  state_summary: {
    keys: string[];
    size: number;
  };
  /** Whether this preset has any children state */
  has_children: boolean;
  /** Names of child presets (for display) */
  child_preset_names: Record<ScopeType, string | null>;
}

/** Shared state from API */
export interface SharedState {
  id: string;
  uuid: string;
  source_preset: string;
  source_preset_detail: SavedStateListItem;
  shared_by_id: string;
  shared_with_id: string;
  can_edit: boolean;
  created: string;
  updated: string;
}

/** MyState config from API */
export interface MyStateConfig {
  scopes: Record<ScopeType, ScopeConfig>;
  state_fields: Record<string, {
    type: string;
    default: any;
    description: string;
  }>;
  debounce: {
    default: number;
    scroll: number;
    resize: number;
    search: number;
  };
  localStorage_prefix: string;
  localStorage_version: number;
}

// =============================================================================
// REQUEST/RESPONSE TYPES
// =============================================================================

/** Create saved state request */
export interface CreateSavedStateRequest {
  scope_type: ScopeType;
  scope_key: string;
  preset_name: string;
  description?: string;
  state_data: GenericStateData;
  /** Include children state for hierarchical presets */
  children_state?: ChildrenState;
  is_default?: boolean;
}

/** Update saved state request */
export interface UpdateSavedStateRequest {
  preset_name?: string;
  description?: string;
  state_data?: GenericStateData;
  children_state?: ChildrenState;
  is_default?: boolean;
}

/** Share state request */
export interface ShareStateRequest {
  shared_with_id: string;
  can_edit?: boolean;
}

// =============================================================================
// HOOK TYPES
// =============================================================================

/** Return type for useMyState hook */
export interface UseMyStateReturn<T extends GenericStateData = GenericStateData> {
  /** Current state (from LocalStorage) */
  state: T;
  
  /** Update state (partial merge) */
  updateState: (partial: Partial<T>) => void;
  
  /** Reset state to defaults */
  resetState: () => void;
  
  /** List of saved presets for this scope */
  savedStates: SavedStateListItem[];
  
  /** Loading state for saved states */
  isLoadingSaved: boolean;
  
  /** Currently active preset name (null if no preset active) */
  activePresetName: string | null;
  
  /** Set the active preset name */
  setActivePresetName: (name: string | null) => void;
  
  /** Currently active preset ID (null if no preset active) */
  activePresetId: string | null;
  
  /** Original state data from loaded preset (for comparison/revert) */
  loadedPresetData: GenericStateData | null;
  
  /** Whether a save/update operation is in progress */
  isSavingPreset: boolean;
  
  /** Save current state as a new preset.
   * @param stateData - Optional state data to save (bypasses context state for immediate save) */
  savePreset: (name: string, description?: string, childrenState?: ChildrenState, stateData?: GenericStateData) => Promise<SavedState>;
  
  /** Load a saved preset into current state, returns loaded state data */
  loadPreset: (preset: SavedState | SavedStateListItem) => Promise<GenericStateData>;
  
  /** Update existing active preset with new state data.
   * @param stateData - Optional state data to save (bypasses context state for immediate save) */
  updatePreset: (stateData?: GenericStateData) => Promise<SavedState>;
  
  /** Revert current state to originally loaded preset data */
  revertToLoadedPreset: () => GenericStateData | null;
  
  /** Clear active preset (no preset active) */
  clearActivePreset: () => void;
  
  /** Delete a saved preset */
  deletePreset: (presetId: string) => Promise<void>;
  
  /** Set a preset as default */
  setDefaultPreset: (presetId: string) => Promise<void>;
  
  /** Refresh saved states list */
  refreshSavedStates: () => Promise<void>;
  
  /** Check if a preset name already exists */
  presetNameExists: (name: string) => boolean;
}

/** Return type for useTableState hook */
export type UseTableStateReturn = UseMyStateReturn<TableStateData>;

/** Return type for usePageState hook */
export type UsePageStateReturn = UseMyStateReturn<PageStateData>;

/** Return type for useGlobalState hook */
export type UseGlobalStateReturn = UseMyStateReturn<GlobalStateData>;

// =============================================================================
// CONTEXT TYPES
// =============================================================================

/** Context value type */
export interface MyStateContextValue {
  /** Get current state for a scope */
  getState: <T extends GenericStateData = GenericStateData>(
    scopeType: ScopeType,
    scopeKey: string
  ) => T;
  
  /** Update state for a scope (partial merge) */
  updateState: <T extends GenericStateData = GenericStateData>(
    scopeType: ScopeType,
    scopeKey: string,
    partial: Partial<T>
  ) => void;
  
  /** Reset state for a scope to defaults */
  resetState: (scopeType: ScopeType, scopeKey: string) => void;
  
  /** Load a preset into current state */
  loadPreset: (
    scopeType: ScopeType,
    scopeKey: string,
    stateData: GenericStateData
  ) => void;
  
  /** Subscribe to state changes for a scope */
  subscribe: (
    scopeType: ScopeType,
    scopeKey: string,
    callback: () => void
  ) => () => void;
}

// =============================================================================
// UTILITY TYPES
// =============================================================================

/** LocalStorage key generator */
export type LocalStorageKeyGenerator = (
  scopeType: ScopeType,
  scopeKey: string
) => string;

/** Debounce config by state field */
export type DebounceConfig = Record<string, number>;
