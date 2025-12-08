//*........................................................
//*       www/thermal_eye_ui/src/components/MyTable/useMyTableData.ts
//*       Data fetching and state management hook for MyTable
//*........................................................

import { useState, useEffect, useCallback } from 'react';
import { API_BASE } from '@/config/api';

/**
 * State returned by useMyTableData hook
 */
export interface MyTableDataState<T> {
  /** Table data */
  data: T[];
  /** Total count (for server-side pagination) */
  total: number;
  /** Loading state */
  isLoading: boolean;
  /** Error state */
  error: string | null;
  /** Refetch data */
  refetch: () => void;
  /** Add new record optimistically */
  addRecord: (record: T) => void;
  /** Update record optimistically */
  updateRecord: (id: string | number, updates: Partial<T>) => void;
  /** Update entire record from API response (for computed fields) */
  updateFullRecord: (id: string | number, fullRecord: any) => void;
  /** Delete records optimistically */
  deleteRecords: (ids: (string | number)[]) => void;
}

/**
 * Options for useMyTableData
 */
export interface UseMyTableDataOptions {
  /** API endpoint */
  endpoint: string;
  /** Enable auto-fetch on mount (default: true) */
  autoFetch?: boolean;
  /** Query parameters for server-side pagination/sorting/filtering */
  queryParams?: Record<string, string | number | boolean | undefined>;
  /** Transform response data */
  transformResponse?: (data: any) => any[];
  /** Error handler */
  onError?: (error: any) => void;
}

/**
 * Hook for fetching and managing table data
 * 
 * Features:
 * - Auto-fetch on mount
 * - Loading/error states
 * - Optimistic updates (add, update, delete)
 * - Refetch capability
 * 
 * @example
 * ```ts
 * const { data, isLoading, error, refetch } = useMyTableData({
 *   endpoint: '/api/logentries/',
 * });
 * ```
 */
export function useMyTableData<T extends Record<string, any>>(
  options: UseMyTableDataOptions
): MyTableDataState<T> {
  const {
    endpoint,
    autoFetch = true,
    queryParams,
    transformResponse,
    onError,
  } = options;

  const [data, setData] = useState<T[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Fetch data from API
   */
  const fetchData = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      // Build URL with query params
      const params = new URLSearchParams();
      if (queryParams) {
        Object.entries(queryParams).forEach(([key, value]) => {
          if (value !== undefined && value !== null && value !== '') {
            params.set(key, String(value));
          }
        });
      }
      
      const queryString = params.toString();
      const url = `${API_BASE}${endpoint}${queryString ? `?${queryString}` : ''}`;

      const response = await fetch(url, {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Accept': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch data: ${response.status} ${response.statusText}`);
      }

      const json = await response.json();
      
      // Handle Django REST Framework paginated response format
      let records = json;
      let count = 0;
      
      if (json && typeof json === 'object' && 'results' in json && Array.isArray(json.results)) {
        records = json.results;
        count = json.count || 0; // Extract total count for pagination
      } else if (Array.isArray(json)) {
        records = json;
        count = json.length;
      }
      
      // Apply custom transform if provided
      if (transformResponse) {
        records = transformResponse(records);
      }

      setData(Array.isArray(records) ? records : []);
      setTotal(count);
      setError(null);
    } catch (err: any) {
      const errorMsg = err.message || 'Failed to fetch data';
      setError(errorMsg);
      
      if (onError) {
        onError(err);
      }
      
      console.error('[useMyTableData] Fetch error:', err);
    } finally {
      setIsLoading(false);
    }
  }, [endpoint, queryParams, transformResponse, onError]);

  /**
   * Add record optimistically
   */
  const addRecord = useCallback((record: T) => {
    setData(prev => [record, ...prev]);
  }, []);

  /**
   * Update record optimistically
   */
  const updateRecord = useCallback((id: string | number, updates: Partial<T>) => {
    setData(prev => prev.map(item => 
      item.id === id ? { ...item, ...updates } : item
    ));
  }, []);

  /**
   * Update entire record from API response (for computed fields)
   */
  const updateFullRecord = useCallback((id: string | number, fullRecord: any) => {
    setData(prev => prev.map(item => 
      item.id === id ? { ...item, ...fullRecord } : item
    ));
  }, []);

  /**
   * Delete records optimistically
   */
  const deleteRecords = useCallback((ids: (string | number)[]) => {
    setData(prev => prev.filter(item => !ids.includes(item.id)));
  }, []);

  // Auto-fetch on mount and whenever fetchData changes (which includes queryParams changes)
  useEffect(() => {
    if (autoFetch) {
      fetchData();
    }
  }, [fetchData, autoFetch]);

  return {
    data,
    total,
    isLoading,
    error,
    refetch: fetchData,
    addRecord,
    updateRecord,
    updateFullRecord,
    deleteRecords,
  };
}

