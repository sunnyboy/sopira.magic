//*........................................................
//*       www/thermal_eye_ui/src/components/modals/AddRecordModal.tsx
//*       Generic modal add component for adding new records
//*
//*       Purpose: Add new records via modal form
//*       Uses: FormModal as base, dynamically generates fields from fieldsMatrix
//*       
//*       Features:
//*       - Dynamically generates form fields from fieldsMatrix (only addEditable: true)
//*       - Validates required fields before submit
//*       - Shows toast messages on success/error
//*       - Uses useErrorHandler for error handling
//*........................................................

import React, { useState, useEffect } from 'react';
import { FormModal } from './FormModal';
import { toastMessages } from '@/utils/toastMessages';
import { useErrorHandler } from '../ui_custom/table/useErrorHandler';
import { Input } from '@/components/ui_custom/input';
import { Textarea } from '@/components/ui_custom/textarea';
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from '@/components/ui/select';
import { Calendar } from '@/components/ui/calendar';
import { Popover, PopoverTrigger, PopoverContent } from '@/components/ui/popover';
import { Calendar as CalendarIcon } from 'lucide-react';
import { format } from 'date-fns';
import { TagEditor } from '@/components/TagEditor';
import { useScope } from '@/contexts/ScopeContext';
import { API_BASE } from '@/config/api';
import { getModelEndpoint } from '@/config/modelMetadata';
import type { FieldConfig, ForeignKeyFieldConfig, SelectFieldConfig, TagFieldConfig } from '../ui_custom/table/fieldFactory';
import { ConditionalFKSelect } from '../ui_custom/table/ConditionalFKSelect';

type Option = { id: string; label: string };

/**
 * Normalize order value to a valid number
 * Handles: undefined, null, NaN, Infinity, non-numbers
 * Returns: valid number or fallback (999)
 */
function normalizeOrder(value: number | undefined | null): number {
  if (typeof value !== 'number') return 999;
  if (!Number.isFinite(value)) return 999; // NaN, Infinity, -Infinity
  return value; // 0, negative, positive - all valid
}

/**
 * Sort fields by order (with secondary sort by field key for stability)
 */
function sortFieldsByAddOrder<T>(
  fields: [string, FieldConfig<T>][]
): [string, FieldConfig<T>][] {
  return [...fields].sort(([keyA, configA], [keyB, configB]) => {
    // Primary sort: order value (orderInAddModal ?? order)
    const orderA = normalizeOrder(
      (configA as any).orderInAddModal ?? (configA as any).order
    );
    const orderB = normalizeOrder(
      (configB as any).orderInAddModal ?? (configB as any).order
    );
    
    // If same order, use secondary sort by field key (alphabetical)
    if (orderA === orderB) {
      return keyA.localeCompare(keyB);
    }
    
    return orderA - orderB;
  });
}

/**
 * Helper: Fetch all options from API (pagination-aware)
 */
async function fetchAllOptions(endpoint: string, params: Record<string, string> = {}): Promise<Option[]> {
  const pageSize = 500;
  let page = 1;
  let out: Option[] = [];
  let total = Infinity;
  
  while (out.length < total) {
    const usp = new URLSearchParams({ ...params, page: String(page), page_size: String(pageSize) });
    const url = API_BASE 
      ? `${API_BASE}${endpoint}?${usp.toString()}`
      : `${endpoint}?${usp.toString()}`;
    
    try {
      const res = await fetch(url, { credentials: 'include' });
      
      if (!res.ok) {
        if (res.status === 400 || res.status === 404) {
          return [];
        }
        if (res.status === 500) {
          throw new Error(`HTTP ${res.status}`);
        }
        return [];
      }
      
      const data = await res.json();
      const results = (data.results || []) as any[];
      total = Number(data.count ?? results.length);
      
      out = out.concat(results.map((o: any) => ({
        id: String(o.id),
        label: o[`${endpoint.split('/').pop()?.slice(0, -1)}_display_label`] || 
               o.display_label || 
               `${o.name ?? o.title ?? o.code ?? o.id}${o.code ? ` (${o.code})` : ''}`,
      })));
      
      if (!results.length) break;
      page += 1;
    } catch (error) {
      console.warn(`Failed to load FK options from ${endpoint}:`, error);
      return [];
    }
  }
  
  return out.sort((a, b) => a.label.localeCompare(b.label));
}

interface AddRecordModalProps<T extends Record<string, any>> {
  open: boolean;
  fieldsMatrix: Record<string, FieldConfig<T>>;
  apiEndpoint: string;
  singularName?: string;  // Singular model name (e.g., "Location", "Factory")
  onClose: () => void;
  onSuccess?: (newRecord: T) => void;
  getCsrfToken?: () => string | null;
}

/**
 * Generic AddRecordModal component
 * Dynamically generates form fields from fieldsMatrix (only addEditable: true)
 */
export function AddRecordModal<T extends Record<string, any>>({
  open,
  fieldsMatrix,
  apiEndpoint,
  singularName = 'Record',
  onClose,
  onSuccess,
  getCsrfToken,
}: AddRecordModalProps<T>) {
  const { handleSaveError } = useErrorHandler();
  const [formData, setFormData] = useState<Partial<T>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { selectedFactories } = useScope();
  const [fkOptions, setFkOptions] = useState<Record<string, Option[]>>({});
  const [loadingFkOptions, setLoadingFkOptions] = useState<Record<string, boolean>>({});

  // System fields that should be excluded from Add modal by default
  const SYSTEM_FIELDS = ['id', 'uuid', 'created', 'updated', 'created_by', 'created_by_username'];

  // Reset form when modal closes
  useEffect(() => {
    if (!open) {
      setFormData({});
      setIsSubmitting(false);
      setFkOptions({});
      setLoadingFkOptions({});
      return;
    }

    // Load FK options when modal opens
    const loadOptions = async () => {
      const fkFields = Object.entries(fieldsMatrix).filter(
        ([_, config]) => config.type === 'fk' && (config as any).editableInAddModal !== false
      ) as [string, ForeignKeyFieldConfig<T>][];

      for (const [key, config] of fkFields) {
        setLoadingFkOptions(prev => ({ ...prev, [key]: true }));
        try {
          let params: Record<string, string> = {};
          
          // Determine endpoint: use apiEndpoint if provided (non-empty), otherwise construct from pluralName or modelMetadata
          // Empty string ('') is treated as "not set" and triggers fallback logic
          let endpoint = (config.apiEndpoint && config.apiEndpoint.trim() !== '') ? config.apiEndpoint : '';
          if (!endpoint) {
            if (config.pluralName) {
              endpoint = `/api/${config.pluralName}`;
            } else {
              // Use modelMetadata for endpoint detection (SSOT)
              endpoint = getModelEndpoint(key);
              if (!endpoint || endpoint.trim() === '') {
                // Skip loading if modelMetadata returns empty (model has no API endpoint)
                console.warn(`[AddRecordModal] Skipping FK options for ${key}: no API endpoint in modelMetadata`);
                setFkOptions(prev => ({ ...prev, [key]: [] }));
                setLoadingFkOptions(prev => ({ ...prev, [key]: false }));
                continue;
              }
              // Fallback removed - if modelMetadata fails, skip loading
            }
          }
          
          // Skip loading options if endpoint is empty (model has no API endpoint)
          if (!endpoint || endpoint.trim() === '') {
            console.warn(`[AddRecordModal] Skipping FK options for ${key}: no API endpoint available`);
            setFkOptions(prev => ({ ...prev, [key]: [] }));
            setLoadingFkOptions(prev => ({ ...prev, [key]: false }));
            continue;
          }
          
          // For factory field in Add modal: use selectedFactories (scope) instead of all_accessible
          // This ensures users can only select from factories they've chosen in Dashboard
          if (config.useAllAccessible && key === 'factory' && selectedFactories.length > 0) {
            // Override: use selected factories instead of all accessible
            params.factory_ids = selectedFactories.join(',');
          } else if (config.useAllAccessible) {
            params.all_accessible = 'true';
          }
          // Backend automatically applies scope - no need to send factory_ids
          // scopedByFactory flag is deprecated - backend handles scoping automatically
          
          const options = await fetchAllOptions(endpoint, params);
          setFkOptions(prev => ({ ...prev, [key]: options }));
        } catch (error) {
          console.error(`Failed to load FK options for ${key}:`, error);
          setFkOptions(prev => ({ ...prev, [key]: [] }));
        } finally {
          setLoadingFkOptions(prev => ({ ...prev, [key]: false }));
        }
      }
    };

    loadOptions();
  }, [open, fieldsMatrix, selectedFactories]);

  // Dynamically reload scoped FK options when factory field changes
  useEffect(() => {
    if (!open) return;

    // Find factory field from config (field with useAllAccessible=true)
    const factoryFieldConfig = Object.entries(fieldsMatrix).find(
      ([_, cfg]) => cfg.type === 'fk' && (cfg as ForeignKeyFieldConfig<T>).useAllAccessible
    );
    if (!factoryFieldConfig) return;

    const factoryFieldKey = factoryFieldConfig[0];
    const factoryValue = formData[factoryFieldKey as keyof T];
    if (!factoryValue) return;

    const factoryId = typeof factoryValue === 'string' 
      ? factoryValue 
      : (factoryValue as any)?.id || String(factoryValue);

    // Backend automatically applies scope - all FK fields are automatically scoped
    // No need to filter by scopedByFactory - backend handles scoping based on ownership_hierarchy
    const scopedFields = Object.entries(fieldsMatrix).filter(
      ([key, config]) => 
        config.type === 'fk' && 
        key !== factoryFieldKey && // Don't reload the factory field itself
        (config as any).editableInAddModal !== false
    ) as [string, ForeignKeyFieldConfig<T>][];

    const loadScopedOptions = async () => {
      for (const [key, config] of scopedFields) {
        setLoadingFkOptions(prev => ({ ...prev, [key]: true }));
        try {
          // Determine endpoint: use apiEndpoint if provided (non-empty), otherwise construct from pluralName or modelMetadata
          // Empty string ('') is treated as "not set" and triggers fallback logic
          let endpoint = (config.apiEndpoint && config.apiEndpoint.trim() !== '') ? config.apiEndpoint : '';
          if (!endpoint && config.pluralName) {
            endpoint = `/api/${config.pluralName}`;
          } else if (!endpoint) {
            // Use modelMetadata for endpoint detection (SSOT)
            endpoint = getModelEndpoint(key);
            if (!endpoint || endpoint.trim() === '') {
              // Skip loading if modelMetadata returns empty (model has no API endpoint)
              console.warn(`[AddRecordModal] Skipping scoped FK options for ${key}: no API endpoint in modelMetadata`);
              setFkOptions(prev => ({ ...prev, [key]: [] }));
              setLoadingFkOptions(prev => ({ ...prev, [key]: false }));
              continue;
            }
            // Fallback removed - if modelMetadata fails, skip loading
          }
          
          // Skip loading options if endpoint is empty (model has no API endpoint)
          if (!endpoint || endpoint.trim() === '') {
            console.warn(`[AddRecordModal] Skipping scoped FK options for ${key}: no API endpoint available`);
            setFkOptions(prev => ({ ...prev, [key]: [] }));
            setLoadingFkOptions(prev => ({ ...prev, [key]: false }));
            continue;
          }
          
          const options = await fetchAllOptions(endpoint, {
            factory_ids: factoryId,
          });
          setFkOptions(prev => ({ ...prev, [key]: options }));
        } catch (error) {
          console.error(`Failed to load scoped FK options for ${key}:`, error);
          setFkOptions(prev => ({ ...prev, [key]: [] }));
        } finally {
          setLoadingFkOptions(prev => ({ ...prev, [key]: false }));
        }
      }
    };

    loadScopedOptions();
  }, [formData, open, fieldsMatrix]);

  // Get addable fields (editableInAddModal: true, or default true for non-system fields)
  const addableFields = sortFieldsByAddOrder(
    Object.entries(fieldsMatrix).filter(([key, config]) => {
      // System fields are excluded by default
      if (SYSTEM_FIELDS.includes(key)) {
        return (config as any).editableInAddModal === true; // Only include if explicitly set to true
      }
      // For non-system fields: include if editableInAddModal is true or undefined (default true)
      return (config as any).editableInAddModal !== false;
    })
  );

  const handleChange = (key: string, value: any) => {
    setFormData((prev) => ({ ...prev, [key]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validate required fields
    const missingFields: string[] = [];
    addableFields.forEach(([key, config]) => {
      const required = (config as any).required;
      if (required && (formData[key as keyof T] === undefined || formData[key as keyof T] === null || formData[key as keyof T] === '')) {
        missingFields.push(config.header || key);
      }
    });

    if (missingFields.length > 0) {
      toastMessages.validationFailed('Required fields', `Please fill in: ${missingFields.join(', ')}`);
      return;
    }

    setIsSubmitting(true);

    try {
      // Build create payload
      const payload: Record<string, any> = {};
      
      addableFields.forEach(([key, config]) => {
        const value = formData[key as keyof T];
        
        if (config.type === 'fk') {
          // FK fields: extract ID from object or use value directly
          // Ensure it's a string UUID, not an object
          if (value === null || value === undefined || value === '') {
            payload[key] = null;
          } else if (typeof value === 'object' && (value as any)?.id) {
            payload[key] = String((value as any).id);
          } else {
            payload[key] = String(value);
          }
        } else if (config.type === 'date') {
          // Date fields: format as YYYY-MM-DD
          payload[key] = value ? format(value as Date, 'yyyy-MM-dd') : null;
        } else if (config.type === 'time') {
          // Time fields: ensure format HH:MM:SS
          payload[key] = value ? `${value}:00` : null;
        } else if (config.type === 'tag') {
          // Tag fields: send as _names array
          payload[`${key}_names`] = value || [];
        } else {
          payload[key] = value;
        }
      });

      // Debug logging

      // Make API call
      const response = await fetch(apiEndpoint, {
        method: 'POST',
        credentials: 'include',
        headers: getCsrfToken ? getMutatingHeaders() : { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error('[AddRecordModal] API Error:', {
          status: response.status,
          statusText: response.statusText,
          errorData,
          payload,
        });
        
        // Extract validation errors from DRF response
        let errorMessage = 'Failed to create record';
        if (errorData && typeof errorData === 'object') {
          if (errorData.detail) {
            errorMessage = errorData.detail;
          } else if (Array.isArray(errorData.non_field_errors)) {
            errorMessage = errorData.non_field_errors.join(', ');
          } else {
            // Format field-specific errors
            const fieldErrors: string[] = [];
            Object.keys(errorData).forEach(field => {
              const errors = errorData[field];
              if (Array.isArray(errors)) {
                fieldErrors.push(`${field}: ${errors.join(', ')}`);
              } else if (typeof errors === 'string') {
                fieldErrors.push(`${field}: ${errors}`);
              }
            });
            if (fieldErrors.length > 0) {
              errorMessage = fieldErrors.join('; ');
            }
          }
        }
        
        toastMessages.saveFailed(errorMessage);
        handleSaveError('new', errorData);
        setIsSubmitting(false);
        return;
      }

      const newRecord = await response.json();
      toastMessages.recordCreated();
      
      if (onSuccess) {
        onSuccess(newRecord);
      }
      
      setIsSubmitting(false);
      onClose();
    } catch (error: any) {
      handleSaveError('new', error);
      setIsSubmitting(false);
    }
  };

  const renderFormField = (key: string, config: FieldConfig<T>, value: any) => {
    const commonProps = {
      id: key,
      name: key,
      value: value,
      onChange: (e: any) => handleChange(key, e.target.value),
      placeholder: (config as any).placeholder || config.header,
      disabled: isSubmitting,
    };

    switch (config.type) {
      case 'text':
        return (config as any).multiline ? (
          <Textarea
            {...commonProps}
            value={String(value ?? '')}
            onChange={(e) => handleChange(key, e.target.value)}
          />
        ) : (
          <Input {...commonProps} value={String(value ?? '')} />
        );

      case 'number':
      case 'temperature':
        return (
          <Input
            {...commonProps}
            type="number"
            step={(config as any).step || 'any'}
            min={(config as any).min}
            max={(config as any).max}
          />
        );

      case 'date':
        const displayDate = value ? format(new Date(value), 'PPP') : null;
        return (
          <Popover>
            <PopoverTrigger asChild>
              <button
                type="button"
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
              >
                <CalendarIcon className="mr-2 h-4 w-4" />
                {displayDate || 'Select date'}
              </button>
            </PopoverTrigger>
            <PopoverContent className="w-auto p-0">
              <Calendar
                mode="single"
                selected={value ? new Date(value) : undefined}
                onSelect={(date) => {
                  if (date) {
                    handleChange(key, date);
                  }
                }}
              />
            </PopoverContent>
          </Popover>
        );

      case 'time':
        return (
          <Input
            type="time"
            value={String(value ?? '').slice(0, 5)}
            onChange={(e) => handleChange(key, e.target.value)}
            disabled={isSubmitting}
          />
        );

      case 'boolean':
        return (
          <Select
            value={value ? 'true' : 'false'}
            onValueChange={(val) => handleChange(key, val === 'true')}
            disabled={isSubmitting}
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="true">{(config as any).trueLabel || 'Yes'}</SelectItem>
              <SelectItem value="false">{(config as any).falseLabel || 'No'}</SelectItem>
            </SelectContent>
          </Select>
        );

      case 'select':
        const selectConfig = config as SelectFieldConfig<T>;
        const selectOptions = typeof selectConfig.options === 'function' 
          ? selectConfig.options({} as T) 
          : selectConfig.options || [];
        // Radix UI Select neumožňuje prázdny string ako hodnotu
        // Ak value nie je v options, použijeme undefined (zobrazí placeholder)
        const selectValue = value != null && selectOptions.some(opt => String(opt.value) === String(value))
          ? String(value)
          : undefined;
        return (
          <Select
            value={selectValue}
            onValueChange={(val) => handleChange(key, val)}
            disabled={isSubmitting}
          >
            <SelectTrigger>
              <SelectValue placeholder={selectConfig.placeholder || 'Select...'} />
            </SelectTrigger>
            <SelectContent>
              {selectOptions.map((opt) => (
                <SelectItem key={opt.value} value={String(opt.value)}>
                  {opt.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        );

      case 'tag':
        const tagConfig = config as TagFieldConfig<T>;
        return (
          <TagEditor
            value={Array.isArray(value) ? value : []}
            onChange={(newTags) => handleChange(key, newTags)}
            suggestions={tagConfig.suggestions || []}
          />
        );

      case 'fk':
        const fkConfig = config as ForeignKeyFieldConfig<T>;
        const options = fkOptions[key] || [];
        const isLoading = loadingFkOptions[key];
        const currentValue = value ? String(value) : '';
        const required = (config as any).required || false;
        const isFactoryField = fkConfig.useAllAccessible === true;
        
        // Pre factory field: ak je len 1 factory vybratá, automaticky nastaviť hodnotu
        const autoSetValue = isFactoryField && selectedFactories.length === 1 
          ? selectedFactories[0] 
          : null;
        
        return (
          <ConditionalFKSelect
            options={options}
            value={currentValue}
            onChange={(val) => handleChange(key, val === null ? null : val)}
            isLoading={isLoading}
            disabled={isSubmitting}
            placeholder={(config as any).placeholder || `Select ${config.header}`}
            required={required}
            autoSetValue={autoSetValue}
          />
        );

      default:
        return (
          <Input {...commonProps} value={String(value ?? '')} />
        );
    }
  };

  return (
    <FormModal
      open={open}
      title={
        <>
          Add New
          <span style={{ marginLeft: '100px' }} className="text-3xl font-extrabold tracking-wide opacity-90">{singularName}</span>
        </>
      }
      onClose={onClose}
      onSubmit={handleSubmit}
      submitText={isSubmitting ? 'Creating...' : 'Create'}
      size="lg"
    >
      <div className="space-y-4">
        {addableFields.map(([key, config]) => {
          const fieldValue = formData[key as keyof T];
          
          return (
            <div key={key} className="space-y-2">
              <label className="text-sm font-medium">
                {config.header || key}
                {(config as any).required && <span className="text-destructive ml-1">*</span>}
              </label>
              {renderFormField(key, config, fieldValue)}
            </div>
          );
        })}
      </div>
    </FormModal>
  );
}

