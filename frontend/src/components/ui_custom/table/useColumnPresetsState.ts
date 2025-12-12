//*........................................................
//*       www/thermal_eye_ui/src/components/ui_custom/table/useColumnPresetsState.ts
//*       Hook for managing saved column presets (named) via backend API
//*........................................................

import { useState, useEffect, useCallback } from 'react';
import type { SavedFilter } from './RecallFilterModal';
import { API_BASE } from '@/config/api';
import { useAuth } from '@/contexts/AuthContext';
import { toast } from 'sonner';
import { getMutatingHeaders } from '@/security/csrf';

export function useColumnPresetsState(storageKey: string) {
  const { csrfToken } = useAuth();
  const [savedColumns, setSavedColumns] = useState<SavedFilter[]>([]);
  const [loading, setLoading] = useState(true);

  // Load saved column presets from backend API on mount
  const loadColumns = useCallback(async () => {
    setLoading(true);
    try {
      const base = API_BASE || '';
      const endpoint = `${base}/api/user/columns/?storageKey=${encodeURIComponent(storageKey)}`;
      const res = await fetch(endpoint, {
        credentials: 'include',
      });
      if (res.ok) {
        const data = await res.json();
        const normalizedKey = storageKey.replace(/[^a-z0-9]/gi, "").toLowerCase();
        const scoped = (data.columns || [])
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
        setSavedColumns(scoped);
      } else {
        const errorText = await res.text();
        console.error(`Failed to load saved column presets: ${res.status} ${res.statusText}`, errorText);
      }
    } catch (err) {
      console.error('Failed to load saved column presets:', err);
    } finally {
      setLoading(false);
    }
  }, [storageKey]);

  useEffect(() => {
    loadColumns();
  }, [loadColumns]);

  // Save a new column preset
  const saveColumn = async (name: string, state: any) => {
    console.log('🔵 [saveColumn] START', { name, stateKeys: Object.keys(state), API_BASE });
    
    try {
      console.log('🔵 [saveColumn] CSRF:', csrfToken ? 'present' : 'missing');
      
      const url = `${API_BASE}/api/user/columns/`;
      console.log('🔵 [saveColumn] URL:', url);
      
      const payload = { name, state, storageKey };
      const payloadStr = JSON.stringify(payload);
      console.log('🔵 [saveColumn] Payload size:', payloadStr.length, 'bytes');
      console.log('🔵 [saveColumn] Payload preview:', payloadStr.substring(0, 100));
      
      console.log('🔵 [saveColumn] Calling fetch...');
      const res = await fetch(url, {
        method: 'POST',
        credentials: 'include',
        headers: getMutatingHeaders(),
        body: JSON.stringify(payload),
      });
      console.log('🔵 [saveColumn] Response status:', res.status);

      if (res.ok) {
        const data = await res.json();
        // Reload all columns to get updated list from backend
        await loadColumns();
        toast.success('Column preset saved successfully!');
      } else if (res.status === 401 || res.status === 403) {
        toast.error('Please log in to save column presets.');
      } else {
        const error = await res.json().catch(() => ({ error: 'Unknown error' }));
        console.error('Failed to save column preset:', error);
        toast.error(`Failed to save column preset: ${error.error || error.detail || 'Unknown error'}`);
      }
    } catch (err) {
      console.error('🔴 [saveColumn] CATCH ERROR:', err);
      console.error('🔴 [saveColumn] Error type:', err instanceof TypeError ? 'TypeError' : typeof err);
      console.error('🔴 [saveColumn] Error message:', (err as Error).message);
      console.error('🔴 [saveColumn] Error stack:', (err as Error).stack);
      toast.error('Failed to save column preset. Backend may be unavailable.');
    }
  };

  // Delete a column preset
  const deleteColumn = async (name: string) => {
    try {
      const base = API_BASE || '';
      const res = await fetch(`${base}/api/user/columns/`, {
        method: 'DELETE',
        credentials: 'include',
        headers: getMutatingHeaders(),
        body: JSON.stringify({ name, storageKey }),
      });

      if (res.ok) {
        // Reload column presets from server
        await loadColumns();
      } else {
        const error = await res.json();
        console.error('Failed to delete column preset:', error);
      }
    } catch (err) {
      console.error('Failed to delete column preset:', err);
    }
  };

  // Get default column preset name
  const getDefaultColumnName = (tableName: string) => {
    const timestamp = new Date().toISOString().slice(0, 19).replace(/[T:-]/g, '');
    return `${tableName}Columns${timestamp}`;
  };

  return {
    savedColumns,
    saveColumn,
    deleteColumn,
    getDefaultColumnName,
    loading,
  };
}

