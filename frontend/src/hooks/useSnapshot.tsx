/**
 * useSnapshot - Global application state management hook
 * 
 * Manages the SNAPSHOT (__current__) - ONE record containing complete app state:
 * - All tables state (pagination, filters, columns, etc.)
 * - Global settings (theme, current page, etc.)
 * 
 * Real-time sync with backend via debounced updates.
 */

import { useState, useCallback, useRef, useEffect } from 'react';
import { useApi } from './useApi';

// ============================================================================
// TYPES
// ============================================================================

export interface TableState {
  pagination?: { pageSize: number; pageIndex: number };
  sorting?: Array<{ id: string; desc: boolean }>;
  globalFilter?: string;
  columnFilters?: Array<{ id: string; value: any }>;
  rowSelection?: Record<string, boolean>;
  visibility?: Record<string, boolean>;
  order?: string[];
  sizing?: Record<string, number>;
  filterPanelState?: { isOpen: boolean; activePresetId: number | null };
  columnPanelState?: { isOpen: boolean; activePresetId: number | null };
  highlightedRowId?: string | null;
  scrollPosition?: { x: number; y: number };
}

export interface GlobalState {
  factory?: string | null;
  currentPage?: string;
  currentTable?: string;
  currentComponent?: string;
  theme?: 'light' | 'dark';
  colorScheme?: string;
  sidebarCollapsed?: boolean;
  language?: string;
}

export interface SnapshotState {
  tables: Record<string, TableState>;
  global: GlobalState;
}

export interface Snapshot {
  id: number;
  user: number;
  username: string;
  factory: string | null;
  table_name: null;  // Always NULL for snapshot
  component: 'table';  // Always 'table' for snapshot
  preset_name: '__current__';
  description: string;
  state: SnapshotState;
  is_active: boolean;
  is_default: boolean;
  created: string;
  updated: string;
}

// TableStatePreset is the general preset type (includes saved presets AND snapshots)
export interface TableStatePreset {
  id: number;
  user: number;
  factory: string | null;
  factory_code: string | null;
  factory_name: string | null;
  username: string;
  table_name: string | null;  // NULL for __current__ snapshot
  component: 'columns' | 'filters' | 'sorting' | 'pagination' | 'table';
  preset_name: string;
  description: string;
  state: SnapshotState | TableState;  // Snapshot for __current__, TableState for saved presets
  is_active: boolean;
  is_default: boolean;
  created: string;
  updated: string;
}

export interface UseSnapshotReturn {
  snapshot: Snapshot | null;
  isLoading: boolean;
  error: string | null;
  
  // Update functions
  updateTable: (tableName: string, partialState: Partial<TableState>) => void;
  updateGlobal: (partialState: Partial<GlobalState>) => void;
  
  // Get table state
  getTableState: (tableName: string) => TableState;
  
  // Refresh from server
  refresh: () => Promise<void>;
}

// ============================================================================
// HOOK
// ============================================================================

export function useSnapshot(factory: string | null = null): UseSnapshotReturn {
  const api = useApi();
  
  const [snapshot, setSnapshot] = useState<Snapshot | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Ref to track current snapshot (for stable function identities)
  const snapshotRef = useRef<Snapshot | null>(null);
  
  // Update ref whenever snapshot changes
  useEffect(() => {
    snapshotRef.current = snapshot;
  }, [snapshot]);
  
  // Debounce timer for updates
  const updateTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const pendingUpdateRef = useRef<Partial<SnapshotState> | null>(null);
  
  // ============================================================================
  // LOAD SNAPSHOT (on mount)
  // ============================================================================
  
  const loadSnapshot = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Get snapshot - backend will create if missing
      const params = new URLSearchParams({
        preset_name: '__current__',
        show_current: 'true',  // Show __current__ records
      });
      if (factory) params.append('factory', factory);
      
      const response = await api.get(`/api/table-state-presets/?${params.toString()}`);
      const results = response.results || response || [];
      
      if (Array.isArray(results) && results.length > 0) {
        // Always use the newest snapshot (sorted by updated desc, then id desc)
        // Backend should return only one active, but we ensure we get the newest if multiple exist
        const sortedResults = [...results].sort((a: Snapshot, b: Snapshot) => {
          const dateA = new Date(a.updated).getTime();
          const dateB = new Date(b.updated).getTime();
          if (dateB !== dateA) return dateB - dateA; // Newer first
          return b.id - a.id; // Higher ID first as tiebreaker
        });
        const snap = sortedResults[0] as Snapshot;
        
        // Log warning if multiple snapshots found (shouldn't happen with new logic)
        if (results.length > 1) {
          console.warn(`⚠️ Multiple __current__ snapshots found (${results.length}), using newest (ID=${snap.id})`);
        }
        
        // Ensure snapshot has correct structure
        if (!snap.state) {
          snap.state = { tables: {}, global: {} };
        }
        if (!snap.state.tables) {
          snap.state.tables = {};
        }
        if (!snap.state.global) {
          snap.state.global = {};
        }
        
        setSnapshot(snap);
        console.log('✓ Loaded SNAPSHOT', snap);
        console.log('📊 INITIAL __current__ STATE:', {
          id: snap.id,
          preset_name: snap.preset_name,
          factory: snap.factory,
          state: JSON.parse(JSON.stringify(snap.state))
        });
      } else {
        // Create new snapshot via backend
        console.log('📝 Creating new snapshot for factory:', factory);
        const payload = {
          table_name: null,
          component: 'table',
          preset_name: '__current__',
          description: 'Live application snapshot',
          factory: factory || null,  // Add factory field
          state: {
            tables: {},
            global: {
              factory: null,
              currentPage: '/',
              currentTable: null,
              currentComponent: 'table',
              theme: 'dark',
              colorScheme: 'blue',
              sidebarCollapsed: false,
              language: 'sk'
            }
          }
        };
        console.log('📤 POST payload:', payload);
        const newSnap = await api.post('/api/table-state-presets/', payload);
        
        setSnapshot(newSnap as Snapshot);
        console.log('✓ Created SNAPSHOT', newSnap);
        console.log('📊 NEW __current__ STATE:', {
          id: (newSnap as Snapshot).id,
          preset_name: (newSnap as Snapshot).preset_name,
          factory: (newSnap as Snapshot).factory,
          state: JSON.parse(JSON.stringify((newSnap as Snapshot).state))
        });
      }
    } catch (err: any) {
      const errorMsg = err.response?.data?.error || err.message || 'Failed to load snapshot';
      setError(errorMsg);
      console.error('❌ Failed to load snapshot:', errorMsg);
    } finally {
      setIsLoading(false);
    }
  }, [factory, api]);
  
  // Load on mount ONLY (empty deps to prevent re-loading)
  useEffect(() => {
    loadSnapshot();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  
  // ============================================================================
  // UPDATE FUNCTIONS (with debouncing)
  // ============================================================================
  
  const flushUpdate = useCallback(async () => {
    const currentSnapshot = snapshotRef.current;
    if (!currentSnapshot || !pendingUpdateRef.current) return;
    
    try {
      // Deep merge pending updates into snapshot state
      const updatedState = {
        ...currentSnapshot.state,
        tables: {
          ...currentSnapshot.state.tables,
          // Deep merge each table's state
          ...Object.keys(pendingUpdateRef.current.tables || {}).reduce((acc, tableName) => {
            acc[tableName] = {
              ...(currentSnapshot.state.tables[tableName] || {}),
              ...(pendingUpdateRef.current!.tables![tableName] || {})
            };
            return acc;
          }, {} as Record<string, TableState>)
        },
        global: {
          ...currentSnapshot.state.global,
          ...(pendingUpdateRef.current.global || {})
        }
      };
      
      // PATCH to backend (no setSnapshot here to avoid infinite loop)
      await api.patch(`/api/table-state-presets/${currentSnapshot.id}/`, {
        state: updatedState
      });
      
      // Clear pending (important: do this AFTER successful PATCH)
      pendingUpdateRef.current = null;
      
      console.log('✓ Synced SNAPSHOT to backend');
      console.log('📊 SYNCED __current__ STATE TO BACKEND:', {
        id: currentSnapshot.id,
        preset_name: currentSnapshot.preset_name,
        state: JSON.parse(JSON.stringify(updatedState))
      });
    } catch (err: any) {
      console.error('❌ Failed to sync snapshot:', err);
      // Keep pending updates in case of error (will retry on next change)
    }
  }, [api]);
  
  const scheduleUpdate = useCallback(() => {
    // Clear existing timer
    if (updateTimerRef.current) {
      clearTimeout(updateTimerRef.current);
    }
    
    // Schedule new update
    updateTimerRef.current = setTimeout(() => {
      flushUpdate();
    }, 500);  // 500ms debounce
  }, [flushUpdate]);
  
  const updateTable = useCallback((tableName: string, partialState: Partial<TableState>) => {
    // Update local state immediately (optimistic update)
    setSnapshot(prev => {
      if (!prev) return null;
      
      // Merge into pending updates
      if (!pendingUpdateRef.current) {
        pendingUpdateRef.current = { tables: {}, global: {} };
      }
      if (!pendingUpdateRef.current.tables) {
        pendingUpdateRef.current.tables = {};
      }
      
      // Deep merge table state
      const currentTableState = prev.state.tables[tableName] || {};
      pendingUpdateRef.current.tables[tableName] = {
        ...currentTableState,
        ...partialState
      };
      
      const newSnapshot = {
        ...prev,
        state: {
          ...prev.state,
          tables: {
            ...prev.state.tables,
            [tableName]: {
              ...(prev.state.tables[tableName] || {}),
              ...partialState
            }
          }
        }
      };
      
      // 📊 Console log kompletného stavu po zmene
      console.log('🔄 SNAPSHOT UPDATED [table: ' + tableName + ']:', {
        id: newSnapshot.id,
        preset_name: newSnapshot.preset_name,
        state: JSON.parse(JSON.stringify(newSnapshot.state)), // Deep clone pre lepší display
        updated_table: tableName,
        updated_fields: Object.keys(partialState)
      });
      
      return newSnapshot;
    });
    
    // Schedule backend sync
    scheduleUpdate();
  }, [scheduleUpdate]);
  
  const updateGlobal = useCallback((partialState: Partial<GlobalState>) => {
    // Update local state immediately (optimistic update)
    setSnapshot(prev => {
      if (!prev) return null;
      
      // Merge into pending updates
      if (!pendingUpdateRef.current) {
        pendingUpdateRef.current = { tables: {}, global: {} };
      }
      
      pendingUpdateRef.current.global = {
        ...pendingUpdateRef.current.global,
        ...partialState
      };
      
      const newSnapshot = {
        ...prev,
        state: {
          ...prev.state,
          global: {
            ...prev.state.global,
            ...partialState
          }
        }
      };
      
      // 📊 Console log kompletného stavu po zmene
      console.log('🔄 SNAPSHOT UPDATED [global]:', {
        id: newSnapshot.id,
        preset_name: newSnapshot.preset_name,
        state: JSON.parse(JSON.stringify(newSnapshot.state)), // Deep clone pre lepší display
        updated_global_fields: Object.keys(partialState)
      });
      
      return newSnapshot;
    });
    
    // Schedule backend sync
    scheduleUpdate();
  }, [scheduleUpdate]);
  
  // ============================================================================
  // UTILITY FUNCTIONS
  // ============================================================================
  
  const getTableState = useCallback((tableName: string): TableState => {
    const currentSnapshot = snapshotRef.current;
    if (!currentSnapshot) return {};
    return currentSnapshot.state.tables[tableName] || {};
  }, []);
  
  const refresh = useCallback(async () => {
    await loadSnapshot();
  }, [loadSnapshot]);
  
  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (updateTimerRef.current) {
        clearTimeout(updateTimerRef.current);
      }
      // Flush any pending updates
      if (pendingUpdateRef.current) {
        flushUpdate();
      }
    };
  }, [flushUpdate]);
  
  return {
    snapshot,
    isLoading,
    error,
    updateTable,
    updateGlobal,
    getTableState,
    refresh,
  };
}

