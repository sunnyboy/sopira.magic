/**
 * MyStateContext - Shared context for state management
 * 
 * Provides a centralized state store with:
 * - LocalStorage-backed state persistence
 * - Debounced updates for performance
 * - Subscriber pattern for reactive updates
 * 
 * One instance per app - all tables/pages share this context.
 */

import React, {
  createContext,
  useContext,
  useRef,
  useCallback,
  useEffect,
  useMemo,
  type FC,
  type PropsWithChildren,
} from 'react';
import { myStateService } from '@/services/myStateService';
import type {
  ScopeType,
  GenericStateData,
  MyStateContextValue,
} from '@/types/myState';

// =============================================================================
// CONTEXT
// =============================================================================

const MyStateContext = createContext<MyStateContextValue | null>(null);

// =============================================================================
// DEBOUNCE UTILITY
// =============================================================================

function createDebouncedPersist(delayMs: number = 100) {
  const timers = new Map<string, ReturnType<typeof setTimeout>>();
  
  return (fullKey: string, data: GenericStateData) => {
    // Clear existing timer for this key
    const existingTimer = timers.get(fullKey);
    if (existingTimer) {
      clearTimeout(existingTimer);
    }
    
    // Set new timer
    const timer = setTimeout(() => {
      try {
        localStorage.setItem(`mystate_${fullKey}`, JSON.stringify(data));
      } catch (error) {
        console.warn(`[MyState] Failed to persist ${fullKey}:`, error);
      }
      timers.delete(fullKey);
    }, delayMs);
    
    timers.set(fullKey, timer);
  };
}

// =============================================================================
// PROVIDER
// =============================================================================

export const MyStateProvider: FC<PropsWithChildren> = ({ children }) => {
  // Central state store (Map<fullKey, StateData>)
  const statesRef = useRef<Map<string, GenericStateData>>(new Map());
  
  // Subscribers for reactive updates (Map<fullKey, Set<callback>>)
  const subscribersRef = useRef<Map<string, Set<() => void>>>(new Map());
  
  // Version counter to force re-renders
  const versionRef = useRef<Map<string, number>>(new Map());
  
  // Debounced persist function
  const persistDebounced = useMemo(() => createDebouncedPersist(100), []);
  
  /**
   * Generate full key from scope type and key
   */
  const getFullKey = useCallback((scopeType: ScopeType, scopeKey: string): string => {
    if (scopeType === 'global') return 'global';
    return `${scopeType}_${scopeKey}`;
  }, []);
  
  /**
   * Notify all subscribers for a scope
   */
  const notifySubscribers = useCallback((fullKey: string) => {
    const callbacks = subscribersRef.current.get(fullKey);
    if (callbacks) {
      callbacks.forEach(cb => {
        try {
          cb();
        } catch (error) {
          console.error(`[MyState] Subscriber error for ${fullKey}:`, error);
        }
      });
    }
  }, []);
  
  /**
   * Get current state for a scope
   */
  const getState = useCallback(<T extends GenericStateData = GenericStateData>(
    scopeType: ScopeType,
    scopeKey: string
  ): T => {
    const fullKey = getFullKey(scopeType, scopeKey);
    
    // Check if already loaded in memory
    let state = statesRef.current.get(fullKey);
    
    if (!state) {
      // Load from LocalStorage
      state = myStateService.getCurrentState(scopeType, scopeKey);
      statesRef.current.set(fullKey, state);
    }
    
    return state as T;
  }, [getFullKey]);
  
  /**
   * Update state for a scope (partial merge)
   */
  const updateState = useCallback(<T extends GenericStateData = GenericStateData>(
    scopeType: ScopeType,
    scopeKey: string,
    partial: Partial<T>
  ) => {
    const fullKey = getFullKey(scopeType, scopeKey);
    const current = getState(scopeType, scopeKey);
    
    // Shallow merge (O(1) per key check)
    const updated = myStateService.shallowMerge(current, partial);
    
    // Only update if actually changed
    if (updated !== current) {
      statesRef.current.set(fullKey, updated);
      
      // Increment version
      const currentVersion = versionRef.current.get(fullKey) || 0;
      versionRef.current.set(fullKey, currentVersion + 1);
      
      // Debounced persist to LocalStorage
      persistDebounced(fullKey, updated);
      
      // Notify subscribers
      notifySubscribers(fullKey);
    }
  }, [getFullKey, getState, persistDebounced, notifySubscribers]);
  
  /**
   * Reset state for a scope to defaults
   */
  const resetState = useCallback((scopeType: ScopeType, scopeKey: string) => {
    const fullKey = getFullKey(scopeType, scopeKey);
    const defaultState = myStateService.getDefaultState(scopeType);
    
    statesRef.current.set(fullKey, defaultState);
    myStateService.setCurrentState(scopeType, scopeKey, defaultState);
    
    // Increment version
    const currentVersion = versionRef.current.get(fullKey) || 0;
    versionRef.current.set(fullKey, currentVersion + 1);
    
    notifySubscribers(fullKey);
  }, [getFullKey, notifySubscribers]);
  
  /**
   * Load a preset into current state
   */
  const loadPreset = useCallback((
    scopeType: ScopeType,
    scopeKey: string,
    stateData: GenericStateData
  ) => {
    const fullKey = getFullKey(scopeType, scopeKey);
    const defaultState = myStateService.getDefaultState(scopeType);
    
    // Merge preset with defaults (in case preset is missing some fields)
    const mergedState = { ...defaultState, ...stateData };
    
    statesRef.current.set(fullKey, mergedState);
    myStateService.setCurrentState(scopeType, scopeKey, mergedState);
    
    // Increment version
    const currentVersion = versionRef.current.get(fullKey) || 0;
    versionRef.current.set(fullKey, currentVersion + 1);
    
    notifySubscribers(fullKey);
  }, [getFullKey, notifySubscribers]);
  
  /**
   * Subscribe to state changes for a scope
   */
  const subscribe = useCallback((
    scopeType: ScopeType,
    scopeKey: string,
    callback: () => void
  ): (() => void) => {
    const fullKey = getFullKey(scopeType, scopeKey);
    
    // Get or create subscriber set
    let callbacks = subscribersRef.current.get(fullKey);
    if (!callbacks) {
      callbacks = new Set();
      subscribersRef.current.set(fullKey, callbacks);
    }
    
    // Add callback
    callbacks.add(callback);
    
    // Return unsubscribe function
    return () => {
      callbacks?.delete(callback);
      if (callbacks?.size === 0) {
        subscribersRef.current.delete(fullKey);
      }
    };
  }, [getFullKey]);
  
  // Context value (memoized to prevent unnecessary re-renders)
  const contextValue = useMemo<MyStateContextValue>(() => ({
    getState,
    updateState,
    resetState,
    loadPreset,
    subscribe,
  }), [getState, updateState, resetState, loadPreset, subscribe]);
  
  return (
    <MyStateContext.Provider value={contextValue}>
      {children}
    </MyStateContext.Provider>
  );
};

// =============================================================================
// HOOK
// =============================================================================

/**
 * Hook to access MyStateContext
 * 
 * @throws Error if used outside MyStateProvider
 */
export function useMyStateContext(): MyStateContextValue {
  const context = useContext(MyStateContext);
  
  if (!context) {
    throw new Error(
      'useMyStateContext must be used within MyStateProvider. ' +
      'Make sure to wrap your app with <MyStateProvider>.'
    );
  }
  
  return context;
}

export default MyStateContext;
