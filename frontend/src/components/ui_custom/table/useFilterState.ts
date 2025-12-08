//*........................................................
//*       www/thermal_eye_ui/src/components/ui_custom/table/useFilterState.ts
//*       Hook for managing saved filter states via backend API
//*........................................................

import { useState, useEffect, useCallback } from 'react';
import type { SavedFilter } from './RecallFilterModal';
import { API_BASE } from '@/config/api';
import { useAuth } from '@/contexts/AuthContext';
import { toast } from 'sonner';

export function useFilterState(storageKey: string) {
  const { csrfToken } = useAuth();
  const [savedFilters, setSavedFilters] = useState<SavedFilter[]>([]);
  const [loading, setLoading] = useState(true);

  // Load saved filters from backend API on mount
  const loadFilters = useCallback(async () => {
    setLoading(true);
    try {
      const base = API_BASE || '';
      const endpoint = `${base}/api/user/filters/?storageKey=${encodeURIComponent(storageKey)}`;
      const res = await fetch(endpoint, {
        credentials: 'include',
      });
      if (res.ok) {
        const data = await res.json();
        const normalizedKey = storageKey.replace(/[^a-z0-9]/gi, "").toLowerCase();
        const scoped = (data.filters || [])
          .filter((item: any) => {
            const entryKey = item.storageKey ?? item.storage_key;
            if (entryKey) {
              return entryKey === storageKey;
            }
            if (typeof item.name === "string") {
              const normalizedName = item.name.replace(/[^a-z0-9]/gi, "").toLowerCase();
              return normalizedName.includes(normalizedKey);
            }
            return false;
          })
          .map((item: any) => ({
            name: item.name,
            timestamp: item.timestamp ?? 0,
            state: item.state ?? {},
          })) as SavedFilter[];
        setSavedFilters(scoped);
      } else {
        const errorText = await res.text();
        console.error(`Failed to load saved filters: ${res.status} ${res.statusText}`, errorText);
      }
    } catch (err) {
      console.error('Failed to load saved filters:', err);
    } finally {
      setLoading(false);
    }
  }, [storageKey]);

  useEffect(() => {
    loadFilters();
  }, [loadFilters]);


  // Save a new filter
  const saveFilter = async (name: string, state: any) => {
    console.log('🔵 [saveFilter] START', { name, stateKeys: Object.keys(state), API_BASE });
    
    try {
      console.log('🔵 [saveFilter] CSRF:', csrfToken ? 'present' : 'missing');
      
      const url = `${API_BASE}/api/user/filters/`;
      console.log('🔵 [saveFilter] URL:', url);
      
      const payload = { name, state, storageKey };
      const payloadStr = JSON.stringify(payload);
      console.log('🔵 [saveFilter] Payload size:', payloadStr.length, 'bytes');
      console.log('🔵 [saveFilter] Payload preview:', payloadStr.substring(0, 100));
      
      console.log('🔵 [saveFilter] Calling fetch...');
      const res = await fetch(url, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          ...(csrfToken ? { 'X-CSRFToken': csrfToken } : {}),
        },
        body: JSON.stringify(payload),
      });
      console.log('🔵 [saveFilter] Response status:', res.status);

      if (res.ok) {
        const data = await res.json();
        await loadFilters();
        toast.success('Filter saved successfully!');
      } else if (res.status === 401 || res.status === 403) {
        toast.error('Please log in to save filters.');
      } else {
        const error = await res.json().catch(() => ({ error: 'Unknown error' }));
        console.error('Failed to save filter:', error);
        toast.error(`Failed to save filter: ${error.error || error.detail || 'Unknown error'}`);
      }
    } catch (err) {
      console.error('🔴 [saveFilter] CATCH ERROR:', err);
      console.error('🔴 [saveFilter] Error type:', err instanceof TypeError ? 'TypeError' : typeof err);
      console.error('🔴 [saveFilter] Error message:', (err as Error).message);
      console.error('🔴 [saveFilter] Error stack:', (err as Error).stack);
      toast.error('Failed to save filter. Backend may be unavailable.');
    }
  };

  // Delete a filter
  const deleteFilter = async (name: string) => {
    try {
      const base = API_BASE || '';
      const res = await fetch(`${base}/api/user/filters/`, {
        method: 'DELETE',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          ...(csrfToken ? { 'X-CSRFToken': csrfToken } : {}),
        },
        body: JSON.stringify({ name, storageKey }),
      });

      if (res.ok) {
        // Reload filters from server
        await loadFilters();
      } else {
        const error = await res.json();
        console.error('Failed to delete filter:', error);
      }
    } catch (err) {
      console.error('Failed to delete filter:', err);
    }
  };

  // Get default filter name
  const getDefaultFilterName = (tableName: string) => {
    const timestamp = new Date().toISOString().slice(0, 19).replace(/[T:-]/g, '');
    return `${tableName}Filter${timestamp}`;
  };

  return {
    savedFilters,
    saveFilter,
    deleteFilter,
    getDefaultFilterName,
    loading,
  };
}
