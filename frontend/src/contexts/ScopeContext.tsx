//*........................................................
//*       www/thermal_eye_ui/src/contexts/ScopeContext.tsx
//*       Globálny scope (výber fabrík) pre aplikáciu
//*........................................................

import React, { createContext, useContext, useEffect, useMemo, useRef, useState } from 'react';
import { useAuth } from './AuthContext';
import { API_BASE } from '@/config/api';
import { getMutatingHeaders } from '@/security/csrf';

export type ScopeContextType = {
  selectedFactories: string[];
  setSelectedFactories: (ids: string[]) => void;
  clearScope: () => void;
  toggleFactory: (id: string) => void;
  rebuildFKCache: () => Promise<void>;
  updateTableState: (removedFactoryIds?: string[]) => Promise<void>;
};

const ScopeContext = createContext<ScopeContextType | undefined>(undefined);

export function useScope(): ScopeContextType {
  const ctx = useContext(ScopeContext);
  if (!ctx) throw new Error('useScope must be used within ScopeProvider');
  return ctx;
}

const STORAGE_KEY = 'te-scope-factories';

export const ScopeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  // Get auth context - must call hook unconditionally (React rules)
  // If context is not available during HMR, useAuth will throw, but that's handled by error boundary
  const auth = useAuth();
  const { csrfToken, isAuthenticated } = auth;
  
  // Initialize selectedFactories state
  // Start with empty array - will be loaded from DATABASE (primary source)
  // localStorage is only used as fallback if server fails
  const [selectedFactories, setSelectedFactoriesState] = useState<string[]>([]);
  
  // Track if we've loaded from server (to prevent overwriting with localStorage)
  const loadedFromServer = useRef(false);
  const loadingFromServerRef = useRef(false);

  const setSelectedFactories = (ids: string[]) => {
    const uniq = Array.from(new Set(ids.map(String)));
    setSelectedFactoriesState(uniq);
  };

  const clearScope = () => setSelectedFactoriesState([]);

  const toggleFactory = (id: string) => {
    setSelectedFactoriesState((prev) => {
      const s = new Set(prev);
      const key = String(id);
      if (s.has(key)) s.delete(key); else s.add(key);
      return Array.from(s);
    });
  };

  // Load from DATABASE FIRST (primary source) - this is the source of truth
  useEffect(() => {
    (async () => {
      if (!isAuthenticated || loadingFromServerRef.current) return;
      
      loadingFromServerRef.current = true;
      try {
        const prefsUrl = API_BASE 
          ? `${API_BASE}/api/user/preferences/`
          : '/api/user/preferences/';
        const res = await fetch(prefsUrl, { credentials: 'include' });
        
        if (res.ok) {
          const json = await res.json();
          
          // Priority: 1) selected_factories (from database), 2) default_factories (from general_settings)
          let factoriesToLoad: string[] = [];
          
          if (json && Array.isArray(json.selected_factories) && json.selected_factories.length > 0) {
            // Use selected_factories from database (primary source)
            factoriesToLoad = json.selected_factories;
          } else if (json?.general_settings?.default_factories && Array.isArray(json.general_settings.default_factories)) {
            // Fallback to default factories from general_settings
            factoriesToLoad = json.general_settings.default_factories;
          }
          
          // Validate UUIDs before using (filter out invalid UUIDs)
          const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
          const validFactories = factoriesToLoad
            .map(String)
            .filter(id => uuidRegex.test(id));
          
          // If we found invalid UUIDs, clean them up in database
          if (validFactories.length !== factoriesToLoad.length) {
            const invalidUUIDs = factoriesToLoad.filter(id => !validFactories.includes(String(id)));
            console.warn('[ScopeContext] Found invalid UUIDs, cleaning up:', {
              original: factoriesToLoad,
              valid: validFactories,
              invalid: invalidUUIDs
            });
            
            // Save cleaned UUIDs back to database immediately
            try {
              const prefsUrl = API_BASE 
                ? `${API_BASE}/api/user/preferences/`
                : '/api/user/preferences/';
              await fetch(prefsUrl, {
                method: 'PUT',
                credentials: 'include',
                headers: getMutatingHeaders(),
                body: JSON.stringify({ selected_factories: validFactories }),
              });
              console.log('[ScopeContext] Cleaned invalid UUIDs from database');
            } catch (error) {
              console.error('[ScopeContext] Failed to clean invalid UUIDs from database', error);
            }
          }
          
          if (validFactories.length > 0) {
            setSelectedFactoriesState(validFactories);
            // Update localStorage to match database (sync localStorage with DB)
            try {
              localStorage.setItem(STORAGE_KEY, JSON.stringify(validFactories));
            } catch {}
          } else {
            // No valid factories selected - try to auto-select all accessible factories
            console.log('[ScopeContext] No factories selected, fetching accessible factories to auto-select');
            try {
              const factoriesUrl = API_BASE 
                ? `${API_BASE}/api/factories/?page=1&page_size=500&all_accessible=true`
                : '/api/factories/?page=1&page_size=500&all_accessible=true';
              const factoriesRes = await fetch(factoriesUrl, { credentials: 'include' });
              
              if (factoriesRes.ok) {
                const factoriesData = await factoriesRes.json();
                const accessibleFactoryIds = (factoriesData.results || [])
                  .map((f: any) => f.id)
                  .filter((id: string) => {
                    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
                    return uuidRegex.test(String(id));
                  });
                
                if (accessibleFactoryIds.length > 0) {
                  console.log(`[ScopeContext] Auto-selecting ${accessibleFactoryIds.length} accessible factories`);
                  // Save to database
                  const prefsUrl = API_BASE 
                    ? `${API_BASE}/api/user/preferences/`
                    : '/api/user/preferences/';
                  await fetch(prefsUrl, {
                    method: 'PUT',
                    credentials: 'include',
                    headers: getMutatingHeaders(),
                    body: JSON.stringify({ selected_factories: accessibleFactoryIds }),
                  });
                  
                  setSelectedFactoriesState(accessibleFactoryIds);
                  // Update localStorage
                  try {
                    localStorage.setItem(STORAGE_KEY, JSON.stringify(accessibleFactoryIds));
                  } catch {}
                } else {
                  // No accessible factories - clear localStorage
                  try {
                    localStorage.removeItem(STORAGE_KEY);
                  } catch {}
                }
              } else {
                // Failed to fetch accessible factories - clear localStorage
                console.warn('[ScopeContext] Failed to fetch accessible factories for auto-selection');
                try {
                  localStorage.removeItem(STORAGE_KEY);
                } catch {}
              }
            } catch (error) {
              console.error('[ScopeContext] Error fetching accessible factories for auto-selection', error);
              // Clear localStorage on error
              try {
                localStorage.removeItem(STORAGE_KEY);
              } catch {}
            }
          }
          
          loadedFromServer.current = true;
        } else {
          // Server error - try localStorage as fallback ONLY if server fails
          console.warn('[ScopeContext] Server error, trying localStorage fallback');
          try {
            const raw = localStorage.getItem(STORAGE_KEY);
            const arr = raw ? JSON.parse(raw) : [];
            if (Array.isArray(arr) && arr.length > 0) {
              // Validate UUIDs from localStorage too
              const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
              const validFactories = arr.map(String).filter(id => uuidRegex.test(id));
              
              // Clean localStorage if it contains invalid UUIDs
              if (validFactories.length !== arr.length) {
                console.warn('[ScopeContext] Cleaning invalid UUIDs from localStorage');
                if (validFactories.length > 0) {
                  localStorage.setItem(STORAGE_KEY, JSON.stringify(validFactories));
                } else {
                  localStorage.removeItem(STORAGE_KEY);
                }
              }
              
              if (validFactories.length > 0) {
                setSelectedFactoriesState(validFactories);
              }
            }
          } catch {
            // localStorage also failed - keep empty array
          }
        }
      } catch (error) {
        // Network error - try localStorage as fallback ONLY if server fails
        console.warn('[ScopeContext] Network error, trying localStorage fallback', error);
        try {
          const raw = localStorage.getItem(STORAGE_KEY);
          const arr = raw ? JSON.parse(raw) : [];
          if (Array.isArray(arr) && arr.length > 0) {
            // Validate UUIDs from localStorage too
            const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
            const validFactories = arr.map(String).filter(id => uuidRegex.test(id));
            if (validFactories.length > 0) {
              setSelectedFactoriesState(validFactories);
            }
          }
        } catch {
          // localStorage also failed - keep empty array
        }
      } finally {
        loadingFromServerRef.current = false;
      }
    })();
  }, [isAuthenticated, auth?.user?.is_superuser_role]);

  // Sync localStorage with database (localStorage is backup, DB is source of truth)
  useEffect(() => {
    // Only update localStorage if we've loaded from server (to avoid overwriting with stale data)
    if (loadedFromServer.current) {
      try {
        if (selectedFactories.length > 0) {
          localStorage.setItem(STORAGE_KEY, JSON.stringify(selectedFactories));
        } else {
          // Clear localStorage if no factories selected
          localStorage.removeItem(STORAGE_KEY);
        }
      } catch {}
    }
  }, [selectedFactories, auth?.user?.is_superuser]);

  // Persist to DATABASE (primary storage) - immediate save on change
  const lastSavedRef = useRef<string>('');
  const savingRef = useRef(false);
  useEffect(() => {
    console.log('[ScopeContext] Save effect triggered', {
      isAuthenticated,
      savingRef: savingRef.current,
      loadingFromServer: loadingFromServerRef.current,
      loadedFromServer: loadedFromServer.current,
      lastSavedRef: lastSavedRef.current,
      selectedFactories,
      selectedFactoriesLength: selectedFactories.length,
    });
    
    if (!isAuthenticated || savingRef.current) {
      console.log('[ScopeContext] Skipping save: not authenticated or already saving');
      return;
    }
    
    // CRITICAL: Don't save if we're still loading from server (prevents saving empty array on hard refresh)
    if (loadingFromServerRef.current) {
      console.log('[ScopeContext] Skipping save: still loading from server');
      return;
    }
    
    // CRITICAL: Don't save empty array if we haven't loaded from server yet (prevents saving empty array on hard refresh)
    if (!loadedFromServer.current) {
      console.log('[ScopeContext] Skipping save: not loaded from server yet');
      return;
    }
    
    // Don't save if we just loaded from server (avoid immediate save after load)
    if (loadedFromServer.current && lastSavedRef.current === '') {
      // Mark as saved to prevent immediate save after load
      const currentKey = JSON.stringify([...selectedFactories].sort());
      lastSavedRef.current = currentKey;
      console.log('[ScopeContext] Marked as saved after load:', currentKey);
      return;
    }
    
    // Create a stable key for comparison
    const currentKey = JSON.stringify([...selectedFactories].sort());
    
    // Skip if nothing changed
    if (lastSavedRef.current === currentKey) {
      console.log('[ScopeContext] Skipping save: nothing changed');
      return;
    }
    
    console.log('[ScopeContext] Saving to database:', {
      lastSaved: lastSavedRef.current,
      current: currentKey,
      selectedFactories,
    });
    
    // Save immediately to database (no debounce - user wants persistence)
    savingRef.current = true;
    (async () => {
      try {
        // Validate UUIDs before sending (filter out invalid UUIDs)
        const validUUIDs = selectedFactories.filter(id => {
          // Basic UUID format validation (8-4-4-4-12 hex characters)
          const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
          return uuidRegex.test(String(id));
        });
        
        if (validUUIDs.length !== selectedFactories.length) {
          console.warn('[ScopeContext] Filtered out invalid UUIDs:', {
            original: selectedFactories,
            valid: validUUIDs,
            filtered: selectedFactories.filter(id => !validUUIDs.includes(id))
          });
        }
        
        const prefsUrl = API_BASE 
          ? `${API_BASE}/api/user/preferences/`
          : '/api/user/preferences/';
        const res = await fetch(prefsUrl, {
          method: 'PUT',
          credentials: 'include',
          headers: getMutatingHeaders(),
          body: JSON.stringify({ selected_factories: validUUIDs }),
        });
        
        if (res.ok) {
          lastSavedRef.current = currentKey;
          console.log('[ScopeContext] ✓ Saved selected_factories to database', { 
            count: validUUIDs.length,
            factories: validUUIDs 
          });
        } else {
          // Get error details from response
          let errorDetails = '';
          try {
            const errorJson = await res.json();
            errorDetails = JSON.stringify(errorJson, null, 2);
          } catch {
            errorDetails = await res.text();
          }
          console.error('[ScopeContext] Failed to save selected_factories to database', {
            status: res.status,
            statusText: res.statusText,
            error: errorDetails,
            payload: { selected_factories: validUUIDs }
          });
        }
      } catch (error) {
        console.error('[ScopeContext] Error saving selected_factories to database', error);
      } finally {
        savingRef.current = false;
      }
    })();
  }, [selectedFactories, isAuthenticated, csrfToken, auth?.user?.is_superuser]);

  // Rebuild FK cache for active scope
  const rebuildFKCache = async (): Promise<void> => {
    try {
      const url = API_BASE 
        ? `${API_BASE}/api/fk-options-cache/rebuild-scope/`
        : '/api/fk-options-cache/rebuild-scope/';
      
      const res = await fetch(url, {
        method: 'POST',
        credentials: 'include',
        headers: getMutatingHeaders(),
        body: JSON.stringify({}), // Empty body - uses all FK fields by default
      });
      
      if (res.ok) {
        const data = await res.json();
        console.log('[ScopeContext] FK cache rebuilt for active scope', data);
      } else {
        console.error('[ScopeContext] Failed to rebuild FK cache', res.status, res.statusText);
      }
    } catch (error) {
      console.error('[ScopeContext] Error rebuilding FK cache', error);
    }
  };
  
  // Update TableState to sync with current selection
  const updateTableState = async (removedFactoryIds: string[] = []): Promise<void> => {
    try {
      const url = API_BASE 
        ? `${API_BASE}/api/table-state/sync-scope/`
        : '/api/table-state/sync-scope/';
      
      const res = await fetch(url, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          ...(csrfToken ? { 'X-CSRFToken': csrfToken } : {}),
        },
        body: JSON.stringify({ removed_factory_ids: removedFactoryIds }),
      });
      
      if (res.ok) {
        const data = await res.json();
        console.log('[ScopeContext] TableState synced with scope', data);
      } else {
        console.error('[ScopeContext] Failed to sync TableState', res.status, res.statusText);
      }
    } catch (error) {
      console.error('[ScopeContext] Error updating TableState', error);
    }
  };

  const value = useMemo<ScopeContextType>(
    () => ({ 
      selectedFactories, 
      setSelectedFactories, 
      clearScope, 
      toggleFactory,
      rebuildFKCache,
      updateTableState,
    }),
    [selectedFactories, csrfToken]
  );

  return <ScopeContext.Provider value={value}>{children}</ScopeContext.Provider>;
};
