/**
 * useMyState - Main hook for state management
 * 
 * Combines:
 * - LocalStorage-backed current state (via MyStateContext)
 * - API-backed saved presets
 * 
 * Plus shortcut hooks for common use cases:
 * - useTableState(tableKey) - for tables
 * - usePageState(pageKey) - for pages
 * - useGlobalState() - for global state
 */

import { useState, useEffect, useCallback, useSyncExternalStore } from 'react';
import { useMyStateContext } from '@/contexts/MyStateContext';
import { myStateService } from '@/services/myStateService';
import { toast } from 'sonner';
import type {
  ScopeType,
  GenericStateData,
  TableStateData,
  PageStateData,
  GlobalStateData,
  SavedState,
  SavedStateListItem,
  UseMyStateReturn,
  ChildrenState,
} from '@/types/myState';

// Column-specific state fields
export interface TableColumnsStateData {
  columnVisibility?: Record<string, boolean>;
  columnOrder?: string[];
  columnSizing?: Record<string, number>;
}

// Filter-specific state fields
export interface TableFiltersStateData {
  columnFilters?: Array<{ id: string; value: any }>;
  globalFilter?: string;
}

// =============================================================================
// MAIN HOOK
// =============================================================================

/**
 * Main hook for state management
 * 
 * @param scopeType - Type of scope ('table', 'page', 'global')
 * @param scopeKey - Specific scope key (e.g., 'companies', 'dashboard')
 * @returns State and methods for managing state
 * 
 * @example
 * ```tsx
 * const { state, updateState, savedStates, savePreset } = useMyState('table', 'companies');
 * 
 * // Update current state
 * updateState({ pagination: { pageSize: 25, pageIndex: 0 } });
 * 
 * // Save as preset
 * await savePreset('My View', 'Custom sorting and filters');
 * ```
 */
export function useMyState<T extends GenericStateData = GenericStateData>(
  scopeType: ScopeType,
  scopeKey: string
): UseMyStateReturn<T> {
  const ctx = useMyStateContext();
  
  // ==========================================================================
  // CURRENT STATE (from Context/LocalStorage)
  // ==========================================================================
  
  // Use useSyncExternalStore for reactive updates
  const subscribe = useCallback(
    (callback: () => void) => ctx.subscribe(scopeType, scopeKey, callback),
    [ctx, scopeType, scopeKey]
  );
  
  const getSnapshot = useCallback(
    () => ctx.getState<T>(scopeType, scopeKey),
    [ctx, scopeType, scopeKey]
  );
  
  const state = useSyncExternalStore(subscribe, getSnapshot, getSnapshot);
  
  // Update state (partial merge)
  const updateState = useCallback(
    (partial: Partial<T>) => {
      ctx.updateState(scopeType, scopeKey, partial);
    },
    [ctx, scopeType, scopeKey]
  );
  
  // Reset state to defaults
  const resetState = useCallback(() => {
    ctx.resetState(scopeType, scopeKey);
  }, [ctx, scopeType, scopeKey]);
  
  // ==========================================================================
  // SAVED STATES (from API)
  // ==========================================================================
  
  const [savedStates, setSavedStates] = useState<SavedStateListItem[]>([]);
  const [isLoadingSaved, setIsLoadingSaved] = useState(false);
  const [activePresetName, setActivePresetName] = useState<string | null>(null);
  const [activePresetId, setActivePresetId] = useState<string | null>(null);
  const [loadedPresetData, setLoadedPresetData] = useState<GenericStateData | null>(null);
  const [isSavingPreset, setIsSavingPreset] = useState(false);
  
  // Load saved states
  const refreshSavedStates = useCallback(async () => {
    setIsLoadingSaved(true);
    try {
      const states = await myStateService.listSavedStates(scopeType, scopeKey);
      setSavedStates(states);
    } catch (error) {
      console.error('[useMyState] Failed to load saved states:', error);
      // Don't show error toast - silent failure
    } finally {
      setIsLoadingSaved(false);
    }
  }, [scopeType, scopeKey]);
  
  // Load saved states on mount
  useEffect(() => {
    refreshSavedStates();
  }, [refreshSavedStates]);
  
  // Check if preset name exists
  const presetNameExists = useCallback(
    (name: string): boolean => {
      return savedStates.some(
        (preset) => preset.preset_name.toLowerCase() === name.toLowerCase()
      );
    },
    [savedStates]
  );
  
  // Save current state as new preset
  // NOTE: stateData parameter allows passing current state directly to avoid closure issues
  const savePreset = useCallback(
    async (
      name: string,
      description?: string,
      childrenState?: ChildrenState,
      stateData?: GenericStateData
    ): Promise<SavedState> => {
      try {
        // Use provided stateData or fall back to context state
        const dataToSave = stateData ?? state;
        console.log('[useMyState] savePreset - saving state_data:', dataToSave);
        
        const saved = await myStateService.createSavedState({
          scope_type: scopeType,
          scope_key: scopeKey,
          preset_name: name,
          description: description || '',
          state_data: dataToSave,
          children_state: childrenState,
        });
        
        toast.success(`Preset "${name}" saved`);
        
        // Set this saved preset as the active/loaded preset
        setActivePresetName(name);
        setActivePresetId(saved.id);
        setLoadedPresetData(structuredClone(dataToSave)); // Deep copy for comparison
        
        await refreshSavedStates();
        return saved;
      } catch (error: any) {
        // Re-throw with structured error for modal handling
        throw error;
      }
    },
    [scopeType, scopeKey, state, refreshSavedStates]
  );
  
  // Load a saved preset into current state
  // Returns the loaded state data so caller can apply it
  const loadPreset = useCallback(
    async (preset: SavedState | SavedStateListItem | { id: string; preset_name: string }): Promise<GenericStateData> => {
      try {
        let stateData: GenericStateData;
        
        // Check if we already have state_data (full SavedState)
        // Otherwise fetch from API (list item or transformed object)
        if ('state_data' in preset && preset.state_data) {
          // Already have full state_data
          stateData = preset.state_data;
        } else {
          // Fetch full preset from API
          console.log('[useMyState] Fetching preset from API:', preset.id);
          const fullPreset = await myStateService.getSavedState(preset.id);
          console.log('[useMyState] Fetched preset state_data:', fullPreset.state_data);
          stateData = fullPreset.state_data;
        }
        
        // Apply to context (LocalStorage)
        ctx.loadPreset(scopeType, scopeKey, stateData);
        
        // Store active preset info for revert/update functionality
        setActivePresetName(preset.preset_name);
        setActivePresetId(preset.id);
        setLoadedPresetData(structuredClone(stateData)); // Deep copy for comparison
        
        toast.success(`Preset "${preset.preset_name}" loaded`);
        
        // Return the loaded data so caller can use it
        return stateData;
      } catch (error) {
        console.error('[useMyState] Failed to load preset:', error);
        toast.error('Failed to load preset');
        throw error;
      }
    },
    [ctx, scopeType, scopeKey]
  );
  
  // Delete a saved preset
  const deletePreset = useCallback(
    async (presetId: string): Promise<void> => {
      try {
        await myStateService.deleteSavedState(presetId);
        toast.success('Preset deleted');
        await refreshSavedStates();
      } catch (error: any) {
        toast.error(error.message || 'Failed to delete preset');
        throw error;
      }
    },
    [refreshSavedStates]
  );
  
  // Set a preset as default
  const setDefaultPreset = useCallback(
    async (presetId: string): Promise<void> => {
      try {
        await myStateService.setDefaultSavedState(presetId);
        toast.success('Default preset updated');
        await refreshSavedStates();
      } catch (error: any) {
        toast.error(error.message || 'Failed to set default');
        throw error;
      }
    },
    [refreshSavedStates]
  );
  
  // Update existing preset with new state data
  const updatePreset = useCallback(
    async (stateData?: GenericStateData): Promise<SavedState> => {
      if (!activePresetId) {
        throw new Error('No active preset to update');
      }
      
      setIsSavingPreset(true);
      try {
        const dataToSave = stateData ?? state;
        console.log('[useMyState] updatePreset - updating preset:', activePresetId, 'with data:', dataToSave);
        
        const updated = await myStateService.updateSavedState(activePresetId, {
          state_data: dataToSave,
        });
        
        // Update loadedPresetData to reflect the new saved state
        setLoadedPresetData(structuredClone(dataToSave));
        
        toast.success(`Preset "${activePresetName}" updated`);
        await refreshSavedStates();
        return updated;
      } catch (error: any) {
        toast.error(error.message || 'Failed to update preset');
        throw error;
      } finally {
        setIsSavingPreset(false);
      }
    },
    [activePresetId, activePresetName, state, refreshSavedStates]
  );
  
  // Revert to loaded preset data (restore original state)
  const revertToLoadedPreset = useCallback(() => {
    if (!loadedPresetData) {
      console.warn('[useMyState] No loaded preset data to revert to');
      return null;
    }
    
    // Apply original data to context
    ctx.loadPreset(scopeType, scopeKey, loadedPresetData);
    toast.success(`Reverted to "${activePresetName}"`);
    
    return loadedPresetData;
  }, [ctx, scopeType, scopeKey, loadedPresetData, activePresetName]);
  
  // Clear active preset (when user makes custom changes without preset)
  const clearActivePreset = useCallback(() => {
    setActivePresetName(null);
    setActivePresetId(null);
    setLoadedPresetData(null);
  }, []);
  
  return {
    state,
    updateState,
    resetState,
    savedStates,
    isLoadingSaved,
    activePresetName,
    setActivePresetName,
    activePresetId,
    loadedPresetData,
    isSavingPreset,
    savePreset,
    loadPreset,
    updatePreset,
    revertToLoadedPreset,
    clearActivePreset,
    deletePreset,
    setDefaultPreset,
    refreshSavedStates,
    presetNameExists,
  };
}

// =============================================================================
// SHORTCUT HOOKS
// =============================================================================

/**
 * Hook for table state management
 * 
 * @param tableKey - Table identifier (e.g., 'companies', 'factories')
 * @returns Table state and methods
 * 
 * @example
 * ```tsx
 * const { state, updateState } = useTableState('companies');
 * updateState({ sorting: [{ id: 'name', desc: false }] });
 * ```
 */
export function useTableState(tableKey: string): UseMyStateReturn<TableStateData> {
  return useMyState<TableStateData>('table', tableKey);
}

/**
 * Hook for page state management
 * 
 * @param pageKey - Page identifier (e.g., 'dashboard', 'settings')
 * @returns Page state and methods
 * 
 * @example
 * ```tsx
 * const { state, updateState } = usePageState('dashboard');
 * updateState({ activeTab: 'overview' });
 * ```
 */
export function usePageState(pageKey: string): UseMyStateReturn<PageStateData> {
  return useMyState<PageStateData>('page', pageKey);
}

/**
 * Hook for global state management
 * 
 * @returns Global state and methods
 * 
 * @example
 * ```tsx
 * const { state, updateState } = useGlobalState();
 * updateState({ theme: 'dark', sidebarCollapsed: true });
 * ```
 */
export function useGlobalState(): UseMyStateReturn<GlobalStateData> {
  return useMyState<GlobalStateData>('global', 'global');
}

// =============================================================================
// TABLE SUBELEMENT HOOKS
// =============================================================================

/**
 * Hook for table columns state management
 * 
 * @param tableKey - Table identifier (e.g., 'companies', 'factories')
 * @returns Column-specific state and methods
 * 
 * @example
 * ```tsx
 * const { state, updateState, savedStates, savePreset } = useTableColumnsState('companies');
 * updateState({ columnVisibility: { id: false } });
 * await savePreset('Compact View');
 * ```
 */
export function useTableColumnsState(tableKey: string): UseMyStateReturn<TableColumnsStateData> {
  return useMyState<TableColumnsStateData>('table_columns', tableKey);
}

/**
 * Hook for table filters state management
 * 
 * @param tableKey - Table identifier (e.g., 'companies', 'factories')
 * @returns Filter-specific state and methods
 * 
 * @example
 * ```tsx
 * const { state, updateState, savedStates, savePreset } = useTableFiltersState('companies');
 * updateState({ columnFilters: [{ id: 'status', value: 'active' }] });
 * await savePreset('Active Only');
 * ```
 */
export function useTableFiltersState(tableKey: string): UseMyStateReturn<TableFiltersStateData> {
  return useMyState<TableFiltersStateData>('table_filters', tableKey);
}

export default useMyState;
