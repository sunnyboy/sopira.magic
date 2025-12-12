/**
 * MyState Service - API and LocalStorage abstraction
 * 
 * Provides a unified interface for:
 * - Current state operations (LocalStorage - sync, fast)
 * - Saved state operations (API - async, persisted)
 * 
 * Architecture:
 * - Current state is stored in LocalStorage for instant access
 * - Saved presets are stored in backend database for persistence/sharing
 */

import { API_BASE } from '@/config/api';
import { getMutatingHeaders } from '@/security/csrf';
import type {
  ScopeType,
  GenericStateData,
  SavedState,
  SavedStateListItem,
  SharedState,
  MyStateConfig,
  CreateSavedStateRequest,
  UpdateSavedStateRequest,
  ShareStateRequest,
} from '@/types/myState';

// =============================================================================
// CONFIGURATION
// =============================================================================

/** LocalStorage key prefix */
const LOCALSTORAGE_PREFIX = 'mystate_';

/** LocalStorage version for migration support (reserved for future use) */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const _LOCALSTORAGE_VERSION = 1;

/** Default state values by scope type */
const DEFAULT_STATE: Record<ScopeType, GenericStateData> = {
  // Root level
  user: {
    preferences: {},
  },
  // Level 1
  application: {
    settings: {},
  },
  // Level 2
  page: {
    layout: {},
    widgets: [],
    collapsed: {},
    activeTab: null,
    scrollPosition: { x: 0, y: 0 },
    focusedField: null,
    panelSizes: {},
    expandedSections: [],
  },
  // Level 3 - page elements
  table: {
    pagination: { pageSize: 10, pageIndex: 0 },
    sorting: [],
    columnFilters: [],
    globalFilter: '',
    columnVisibility: {},
    columnOrder: [],
    columnSizing: {},
    rowSelection: {},
    scrollPosition: { x: 0, y: 0 },
    expandedRows: [],
    searchValue: '',
    focusedField: null,
    filterPanelState: { isOpen: false, activePresetId: null },
    columnPanelState: { isOpen: false, activePresetId: null },
    highlightedRowId: null,
  },
  pdfviewer: {
    zoom: 100,
    currentPage: 1,
    scrollPosition: { x: 0, y: 0 },
  },
  texteditor: {
    fontSize: 14,
    wordWrap: true,
    showLineNumbers: true,
  },
  formgenerator: {
    layout: 'vertical',
    expandedSections: [],
  },
  // Level 4 - table subelements
  table_columns: {
    columnVisibility: {},
    columnOrder: [],
    columnSizing: {},
  },
  table_filters: {
    columnFilters: [],
    globalFilter: '',
  },
  // Legacy compatibility
  global: {
    theme: 'dark',
    language: 'sk',
    sidebarCollapsed: false,
    selectedFactory: null,
    colorScheme: 'blue',
    notificationsEnabled: true,
    compactMode: false,
    lastVisitedPage: null,
  },
};

// =============================================================================
// HELPERS
// =============================================================================

/**
 * Generate LocalStorage key for a scope
 */
function getLocalStorageKey(scopeType: ScopeType, scopeKey: string): string {
  if (scopeType === 'global') {
    return `${LOCALSTORAGE_PREFIX}global`;
  }
  return `${LOCALSTORAGE_PREFIX}${scopeType}_${scopeKey}`;
}

/**
 * Get default state for a scope type
 */
function getDefaultState(scopeType: ScopeType): GenericStateData {
  return { ...DEFAULT_STATE[scopeType] };
}

/**
 * Shallow merge two objects (returns new object only if changed)
 */
function shallowMerge<T extends GenericStateData>(
  current: T,
  partial: Partial<T>
): T {
  const keys = Object.keys(partial) as Array<keyof T>;
  let hasChanges = false;

  for (const key of keys) {
    if (current[key] !== partial[key]) {
      hasChanges = true;
      break;
    }
  }

  if (!hasChanges) {
    return current;
  }

  return { ...current, ...partial };
}

// =============================================================================
// LOCALSTORAGE OPERATIONS (SYNC - FAST)
// =============================================================================

/**
 * Get current state from LocalStorage
 */
function getCurrentState(scopeType: ScopeType, scopeKey: string): GenericStateData {
  const key = getLocalStorageKey(scopeType, scopeKey);
  
  try {
    const stored = localStorage.getItem(key);
    if (stored) {
      const parsed = JSON.parse(stored);
      // Merge with defaults to handle new fields
      return { ...getDefaultState(scopeType), ...parsed };
    }
  } catch (error) {
    console.warn(`[MyState] Failed to read LocalStorage key "${key}":`, error);
  }
  
  return getDefaultState(scopeType);
}

/**
 * Set current state in LocalStorage
 */
function setCurrentState(
  scopeType: ScopeType,
  scopeKey: string,
  state: GenericStateData
): void {
  const key = getLocalStorageKey(scopeType, scopeKey);
  
  try {
    localStorage.setItem(key, JSON.stringify(state));
  } catch (error) {
    console.warn(`[MyState] Failed to write LocalStorage key "${key}":`, error);
  }
}

/**
 * Update current state with partial merge
 */
function updateCurrentState(
  scopeType: ScopeType,
  scopeKey: string,
  partial: Partial<GenericStateData>
): GenericStateData {
  const current = getCurrentState(scopeType, scopeKey);
  const updated = shallowMerge(current, partial);
  
  if (updated !== current) {
    setCurrentState(scopeType, scopeKey, updated);
  }
  
  return updated;
}

/**
 * Clear current state from LocalStorage
 */
function clearCurrentState(scopeType: ScopeType, scopeKey: string): void {
  const key = getLocalStorageKey(scopeType, scopeKey);
  
  try {
    localStorage.removeItem(key);
  } catch (error) {
    console.warn(`[MyState] Failed to clear LocalStorage key "${key}":`, error);
  }
}

/**
 * Reset current state to defaults
 */
function resetCurrentState(scopeType: ScopeType, scopeKey: string): GenericStateData {
  const defaultState = getDefaultState(scopeType);
  setCurrentState(scopeType, scopeKey, defaultState);
  return defaultState;
}

// =============================================================================
// API OPERATIONS (ASYNC - PERSISTED)
// =============================================================================

/**
 * List saved states for a scope
 */
async function listSavedStates(
  scopeType: ScopeType,
  scopeKey: string
): Promise<SavedStateListItem[]> {
  const params = new URLSearchParams({
    scope_type: scopeType,
    scope_key: scopeKey,
  });
  
  console.log('[myStateService] listSavedStates for scope:', scopeType, scopeKey);
  
  const response = await fetch(`${API_BASE}/api/mystate/saved/?${params}`, {
    credentials: 'include',
  });
  
  if (!response.ok) {
    throw new Error(`Failed to list saved states: ${response.status}`);
  }
  
  const data = await response.json();
  // Handle paginated response from DRF
  const results = data.results || data;
  console.log('[myStateService] listSavedStates results:', results.map((r: any) => ({ id: r.id, name: r.preset_name })));
  return results;
}

/**
 * Get a specific saved state by ID
 */
async function getSavedState(presetId: string): Promise<SavedState> {
  console.log('[myStateService] getSavedState called with ID:', presetId);
  const url = `${API_BASE}/api/mystate/saved/${presetId}/`;
  console.log('[myStateService] Fetching URL:', url);
  
  const response = await fetch(url, {
    credentials: 'include',
  });
  
  if (!response.ok) {
    throw new Error(`Failed to get saved state: ${response.status}`);
  }
  
  const data = await response.json();
  console.log('[myStateService] getSavedState response:', {
    id: data.id,
    preset_name: data.preset_name,
    state_data: data.state_data,
  });
  return data;
}

/** Response from load endpoint with hierarchy metadata */
interface LoadPresetResponse extends SavedState {
  _hierarchy: {
    valid_children: ScopeType[];
    has_children: boolean;
  };
}

/**
 * Load a preset with full hierarchical data
 * Use this when loading a parent preset that may have children
 */
async function loadSavedState(presetId: string): Promise<LoadPresetResponse> {
  const response = await fetch(`${API_BASE}/api/mystate/saved/${presetId}/load/`, {
    credentials: 'include',
  });
  
  if (!response.ok) {
    throw new Error(`Failed to load saved state: ${response.status}`);
  }
  
  return response.json();
}

/**
 * Create a new saved state
 */
async function createSavedState(data: CreateSavedStateRequest): Promise<SavedState> {
  const response = await fetch(`${API_BASE}/api/mystate/saved/`, {
    method: 'POST',
    credentials: 'include',
    headers: getMutatingHeaders(),
    body: JSON.stringify(data),
  });
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || error.preset_name?.[0] || `Failed to create: ${response.status}`);
  }
  
  return response.json();
}

/**
 * Update an existing saved state
 */
async function updateSavedState(
  presetId: string,
  data: UpdateSavedStateRequest
): Promise<SavedState> {
  const response = await fetch(`${API_BASE}/api/mystate/saved/${presetId}/`, {
    method: 'PATCH',
    credentials: 'include',
    headers: getMutatingHeaders(),
    body: JSON.stringify(data),
  });
  
  if (!response.ok) {
    throw new Error(`Failed to update saved state: ${response.status}`);
  }
  
  return response.json();
}

/**
 * Delete a saved state
 */
async function deleteSavedState(presetId: string): Promise<void> {
  const response = await fetch(`${API_BASE}/api/mystate/saved/${presetId}/`, {
    method: 'DELETE',
    credentials: 'include',
    headers: getMutatingHeaders(),
  });
  
  if (!response.ok) {
    throw new Error(`Failed to delete saved state: ${response.status}`);
  }
}

/**
 * Set a saved state as default
 */
async function setDefaultSavedState(presetId: string): Promise<SavedState> {
  const response = await fetch(`${API_BASE}/api/mystate/saved/${presetId}/set-default/`, {
    method: 'POST',
    credentials: 'include',
    headers: getMutatingHeaders(),
  });
  
  if (!response.ok) {
    throw new Error(`Failed to set default: ${response.status}`);
  }
  
  return response.json();
}

/**
 * Share a saved state with another user
 */
async function shareSavedState(
  presetId: string,
  data: ShareStateRequest
): Promise<SharedState> {
  const response = await fetch(`${API_BASE}/api/mystate/saved/${presetId}/share/`, {
    method: 'POST',
    credentials: 'include',
    headers: getMutatingHeaders(),
    body: JSON.stringify(data),
  });
  
  if (!response.ok) {
    throw new Error(`Failed to share saved state: ${response.status}`);
  }
  
  return response.json();
}

/**
 * List shared states (presets shared with current user)
 */
async function listSharedStates(
  scopeType?: ScopeType,
  scopeKey?: string
): Promise<SharedState[]> {
  const params = new URLSearchParams();
  if (scopeType) params.append('scope_type', scopeType);
  if (scopeKey) params.append('scope_key', scopeKey);
  
  const url = params.toString()
    ? `${API_BASE}/api/mystate/shared/?${params}`
    : `${API_BASE}/api/mystate/shared/`;
  
  const response = await fetch(url, {
    credentials: 'include',
  });
  
  if (!response.ok) {
    throw new Error(`Failed to list shared states: ${response.status}`);
  }
  
  const data = await response.json();
  // Handle paginated response from DRF
  return data.results || data;
}

/**
 * Remove a share (unsubscribe from shared preset)
 */
async function removeShare(shareId: string): Promise<void> {
  const response = await fetch(`${API_BASE}/api/mystate/shared/${shareId}/`, {
    method: 'DELETE',
    credentials: 'include',
    headers: getMutatingHeaders(),
  });
  
  if (!response.ok) {
    throw new Error(`Failed to remove share: ${response.status}`);
  }
}

/**
 * Get MYSTATE_CONFIG from backend
 */
async function getConfig(): Promise<MyStateConfig> {
  const response = await fetch(`${API_BASE}/api/mystate/config/`, {
    credentials: 'include',
  });
  
  if (!response.ok) {
    throw new Error(`Failed to get config: ${response.status}`);
  }
  
  return response.json();
}

/**
 * Get default preset for a scope (if exists)
 */
async function getDefaultPreset(
  scopeType: ScopeType,
  scopeKey: string
): Promise<SavedState | null> {
  const params = new URLSearchParams({
    scope_type: scopeType,
    scope_key: scopeKey,
  });
  
  const response = await fetch(`${API_BASE}/api/mystate/default/?${params}`, {
    credentials: 'include',
  });
  
  if (response.status === 404) {
    return null;
  }
  
  if (!response.ok) {
    throw new Error(`Failed to get default preset: ${response.status}`);
  }
  
  return response.json();
}

// =============================================================================
// EXPORT SERVICE
// =============================================================================

export const myStateService = {
  // LocalStorage operations (sync)
  getCurrentState,
  setCurrentState,
  updateCurrentState,
  clearCurrentState,
  resetCurrentState,
  getLocalStorageKey,
  getDefaultState,
  shallowMerge,
  
  // API operations (async)
  listSavedStates,
  getSavedState,
  loadSavedState,
  createSavedState,
  updateSavedState,
  deleteSavedState,
  setDefaultSavedState,
  shareSavedState,
  listSharedStates,
  removeShare,
  getConfig,
  getDefaultPreset,
};

export default myStateService;
