//*........................................................
//*       www/thermal_eye_ui/src/components/ui_custom/table/useOptimisticField.ts
//*       Custom hook for optimistic field updates with API integration
//*........................................................

import { useState, useCallback } from 'react';

/**
 * Configuration for optimistic field updates
 */
export interface OptimisticFieldConfig<T = any> {
  /** Unique identifier of the record */
  recordId: string | number;
  
  /** Name of the field being edited */
  fieldName: string;
  
  /** Initial value of the field */
  initialValue: T;
  
  /** Base API endpoint (e.g., '/api/measurements') */
  apiEndpoint: string;
  
  /** Callback to update parent's data state optimistically */
  onDataUpdate: (recordId: string | number, fieldName: string, newValue: T) => void;
  
  /** Callback to update entire record from API response (for computed fields like *_display_label) */
  onFullRecordUpdate?: (recordId: string | number, fullRecord: any) => void;
  
  /** Callback when save error occurs (for error modal) */
  onError: (recordId: string | number, errorData: any) => void;
  
  /** Optional: callback when save succeeds */
  onSuccess?: () => void;
  
  /** Optional: transform value before sending to API */
  transformForApi?: (value: T) => any;
  
  /** Optional: CSRF token getter */
  getCsrfToken?: () => string | null;
}

/**
 * Return type of useOptimisticField hook
 */
export interface OptimisticFieldResult<T = any> {
  /** Current value (includes optimistic updates) */
  value: T;
  
  /** Function to save new value with optimistic update */
  save: (newValue: T) => Promise<void>;
  
  /** Whether save is in progress */
  isSaving: boolean;
  
  /** Manually revert to original value (in case of error) */
  revert: () => void;
}

/**
 * Custom hook for managing optimistic field updates with API integration.
 * 
 * This hook encapsulates the entire optimistic update pattern:
 * 1. Immediate UI update (optimistic)
 * 2. Background API call (PATCH)
 * 3. On error: revert + show error modal
 * 4. On success: keep the change
 * 
 * @example
 * ```tsx
 * const potWeight = useOptimisticField({
 *   recordId: row.id,
 *   fieldName: 'pot_weight_kg',
 *   initialValue: row.pot_weight_kg,
 *   apiEndpoint: '/api/measurements',
 *   onDataUpdate: (id, field, value) => setData(prev => 
 *     prev.map(r => r.id === id ? { ...r, [field]: value } : r)
 *   ),
 *   onError: handleSaveError,
 * });
 * 
 * // In render:
 * <EditableCell
 *   value={potWeight.value}
 *   onSave={potWeight.save}
 *   isSaving={potWeight.isSaving}
 * />
 * ```
 */
export function useOptimisticField<T = any>(
  config: OptimisticFieldConfig<T>
): OptimisticFieldResult<T> {
  const {
    recordId,
    fieldName,
    initialValue,
    apiEndpoint,
    onDataUpdate,
    onError,
    onSuccess,
    transformForApi,
    getCsrfToken,
  } = config;

  const [currentValue, setCurrentValue] = useState<T>(initialValue);
  const [originalValue, setOriginalValue] = useState<T>(initialValue);
  const [isSaving, setIsSaving] = useState(false);

  /**
   * Save new value with optimistic update
   */
  const save = useCallback(async (newValue: T) => {
    // Guard: prevent multiple simultaneous saves
    if (isSaving) {
      console.warn('Save already in progress, ignoring duplicate request');
      return;
    }
    
    // Store original for potential revert
    setOriginalValue(currentValue);
    
    // 1. Optimistic update - immediate UI change
    setCurrentValue(newValue);
    onDataUpdate(recordId, fieldName, newValue);
    
    setIsSaving(true);
    
    // 2. Background API call
    // Normalize URL: remove trailing slash from apiEndpoint to avoid double slashes
    const normalizedEndpoint = apiEndpoint.endsWith('/') 
      ? apiEndpoint.slice(0, -1) 
      : apiEndpoint;
    const url = `${normalizedEndpoint}/${recordId}/`;
    const valueForApi = transformForApi ? transformForApi(newValue) : newValue;
    
    // If transformForApi returns an object, merge it into body (for tags -> tags_names mapping)
    // Otherwise, use fieldName as key
    const body: Record<string, any> = typeof valueForApi === 'object' && valueForApi !== null && !Array.isArray(valueForApi)
      ? { ...valueForApi }  // Merge object directly (e.g., { tags_names: [...] })
      : { [fieldName]: valueForApi };  // Use fieldName as key (normal case)
    
    // Special normalization for date/time fields
    if (fieldName === 'dump_time' && typeof valueForApi === 'string') {
      body.dump_time = valueForApi.slice(0, 8);
    }
    if (fieldName === 'dump_date' && typeof valueForApi === 'string') {
      body.dump_date = valueForApi.slice(0, 10);
    }
    
    try {
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      };
      
      // Add CSRF token if available
      const csrfToken = getCsrfToken ? getCsrfToken() : null;
      if (csrfToken) {
        headers['X-CSRFToken'] = csrfToken;
      }
      
      const res = await fetch(url, {
        method: 'PATCH',
        credentials: 'include',
        headers,
        body: JSON.stringify(body),
      });
      
      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        
        // 3a. Revert optimistic update on error
        setCurrentValue(originalValue);
        onDataUpdate(recordId, fieldName, originalValue);
        
        // Show error modal
        onError(recordId, errorData);
        
        setIsSaving(false);
        throw new Error('Save failed'); // Don't propagate to parent
      }
      
      // 3b. Success - use response data to update entire record
      // Backend returns full updated record (including computed fields like *_display_label)
      const responseData = await res.json();
      
      // Update entire record in parent state (not just single field)
      // This ensures computed fields (e.g., factory_display_label) are updated
      if (config.onFullRecordUpdate) {
        config.onFullRecordUpdate(recordId, responseData);
      } else {
        // Fallback: update only single field (backward compatibility)
        onDataUpdate(recordId, fieldName, newValue);
      }
      
      setIsSaving(false);
      
      // Call success callback (e.g., show toast)
      if (onSuccess) {
        onSuccess();
      }
      
    } catch (err) {
      console.error('Save error:', err);
      setIsSaving(false);
      // Error already handled (revert + modal shown)
    }
  }, [
    recordId,
    fieldName,
    currentValue,
    originalValue,
    apiEndpoint,
    onDataUpdate,
    onError,
    onSuccess,
    transformForApi,
    getCsrfToken,
  ]);

  /**
   * Manually revert to original value
   */
  const revert = useCallback(() => {
    setCurrentValue(originalValue);
    onDataUpdate(recordId, fieldName, originalValue);
  }, [recordId, fieldName, originalValue, onDataUpdate]);

  return {
    value: currentValue,
    save,
    isSaving,
    revert,
  };
}
