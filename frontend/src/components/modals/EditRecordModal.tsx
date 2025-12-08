//*........................................................
//*       www/thermal_eye_ui/src/components/modals/EditRecordModal.tsx
//*       Generic modal edit component for editing records
//*
//*       Purpose: Edit existing records via modal form
//*       Uses: FormModal as base, dynamically generates fields from fieldsMatrix
//*       
//*       Features:
//*       - Dynamically generates form fields from fieldsMatrix (only modalEditable: true)
//*       - Uses useOptimisticField or similar hook for API calls
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
import { toDisplayDate } from '@/utils/date';
import { TagEditor } from '@/components/TagEditor';
import { useScope } from '@/contexts/ScopeContext';
import { API_BASE } from '@/config/api';
import type { FieldConfig, ForeignKeyFieldConfig, NumberFieldConfig, TemperatureFieldConfig, SelectFieldConfig, TagFieldConfig } from '../ui_custom/table/fieldFactory';
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
function sortFieldsByEditOrder<T>(
  fields: [string, FieldConfig<T>][]
): [string, FieldConfig<T>][] {
  return [...fields].sort(([keyA, configA], [keyB, configB]) => {
    // Primary sort: order value (orderInEditModal ?? order)
    const orderA = normalizeOrder(
      (configA as any).orderInEditModal ?? (configA as any).order
    );
    const orderB = normalizeOrder(
      (configB as any).orderInEditModal ?? (configB as any).order
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

interface EditRecordModalProps<T extends Record<string, any>> {
  open: boolean;
  record: T | null;
  fieldsMatrix: Record<string, FieldConfig<T>>;
  apiEndpoint: string;
  singularName?: string;  // Singular model name (e.g., "Location", "Factory")
  onClose: () => void;
  onSuccess?: (updatedRecord: T) => void;
  getCsrfToken?: () => string | null;
}

/**
 * Generic EditRecordModal component
 * Dynamically generates form fields from fieldsMatrix (only modalEditable: true)
 */
export function EditRecordModal<T extends Record<string, any>>({
  open,
  record,
  fieldsMatrix,
  apiEndpoint,
  singularName = 'Record',
  onClose,
  onSuccess,
  getCsrfToken,
}: EditRecordModalProps<T>) {
  const { handleSaveError } = useErrorHandler();
  const [formData, setFormData] = useState<Partial<T>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { selectedFactories } = useScope();
  const [fkOptions, setFkOptions] = useState<Record<string, Option[]>>({});
  const [loadingFkOptions, setLoadingFkOptions] = useState<Record<string, boolean>>({});

  // Initialize form data when record changes
  useEffect(() => {
    if (record) {
      const initialData: Partial<T> = {};
      Object.keys(fieldsMatrix).forEach((key) => {
        const fieldConfig = fieldsMatrix[key];
        if ((fieldConfig as any).editableInEditModal !== false) {
          initialData[key as keyof T] = record[key];
        }
      });
      setFormData(initialData);
    }
  }, [record, fieldsMatrix]);

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
      if (!record) return;
      
      const fkFields = Object.entries(fieldsMatrix).filter(
        ([_, config]) => config.type === 'fk' && (config as any).editableInEditModal !== false
      ) as [string, ForeignKeyFieldConfig<T>][];

      for (const [key, config] of fkFields) {
        setLoadingFkOptions(prev => ({ ...prev, [key]: true }));
        try {
          let params: Record<string, string> = {};
          
          // Determine endpoint: use apiEndpoint if provided, otherwise construct from pluralName or key
          let endpoint = config.apiEndpoint || '';
          if (!endpoint) {
            if (config.pluralName) {
              endpoint = `/api/${config.pluralName}`;
            } else {
              // Fallback: try to pluralize key
              endpoint = `/api/${key}${key.endsWith('y') ? 'ies' : key.endsWith('s') ? '' : 's'}`;
            }
          }
          
          // Use all_accessible parameter if configured
          if (config.useAllAccessible) {
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
  }, [open, record, fieldsMatrix, selectedFactories]);

  // Dynamically reload scoped FK options when factory field changes in formData
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
        (config as any).editableInEditModal !== false
    ) as [string, ForeignKeyFieldConfig<T>][];

    const loadScopedOptions = async () => {
      for (const [key, config] of scopedFields) {
        setLoadingFkOptions(prev => ({ ...prev, [key]: true }));
        try {
          // Determine endpoint: use apiEndpoint if provided, otherwise construct from pluralName
          let endpoint = config.apiEndpoint || '';
          if (!endpoint && config.pluralName) {
            endpoint = `/api/${config.pluralName}`;
          } else if (!endpoint) {
            endpoint = `/api/${key}${key.endsWith('y') ? 'ies' : key.endsWith('s') ? '' : 's'}`;
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

  // Get editable fields (only editableInEditModal: true), sorted by orderInEditModal
  const editableFields = sortFieldsByEditOrder(
    Object.entries(fieldsMatrix).filter(
      ([_, config]) => (config as any).editableInEditModal !== false
    )
  );

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!record) return;

    setIsSubmitting(true);

    try {
      // Build update payload (only changed fields)
      const payload: Partial<T> = {};
      let hasChanges = false;

      editableFields.forEach(([key]) => {
        const currentValue = formData[key as keyof T];
        const originalValue = record[key];

        // Check if value changed
        if (currentValue !== originalValue) {
          hasChanges = true;
          payload[key as keyof T] = currentValue;
        }
      });

      if (!hasChanges) {
        toastMessages.processing('No changes to save');
        setIsSubmitting(false);
        return;
      }

      // Make API call
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      };

      const csrfToken = getCsrfToken ? getCsrfToken() : null;
      if (csrfToken) {
        headers['X-CSRFToken'] = csrfToken;
      }

      const response = await fetch(`${apiEndpoint}${record.id}/`, {
        method: 'PATCH',
        credentials: 'include',
        headers,
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        
        // Add status code to error data for better error handling
        const errorWithStatus = {
          ...errorData,
          status: response.status,
          statusText: response.statusText,
        };
        
        // Show specific message for 405 Method Not Allowed
        if (response.status === 405) {
          toastMessages.saveFailed('Operácia nie je podporovaná. Server nepodporuje úpravu tohto záznamu.');
        }
        
        handleSaveError(record.id, errorWithStatus);
        setIsSubmitting(false);
        return;
      }

      const updatedRecord = await response.json();

      // Call success callback (toast is handled by parent component via onSuccess)
      if (onSuccess) {
        onSuccess(updatedRecord);
      }

      // Close modal
      onClose();
    } catch (err: any) {
      handleSaveError(record.id, err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleFieldChange = (fieldName: string, value: any) => {
    setFormData((prev) => ({
      ...prev,
      [fieldName]: value,
    }));
  };

  const renderFormField = (key: string, config: FieldConfig<T>, value: any) => {
    const handleChange = (newValue: any) => handleFieldChange(key, newValue);

    switch (config.type) {
      case 'text':
        if (config.multiline) {
          return (
            <Textarea
              value={String(value ?? '')}
              onChange={(e) => handleChange(e.target.value)}
              placeholder={config.placeholder}
            />
          );
        }
        return (
          <Input
            type="text"
            value={String(value ?? '')}
            onChange={(e) => handleChange(e.target.value)}
            placeholder={config.placeholder}
          />
        );

      case 'number':
        const numberConfig = config as NumberFieldConfig<T>;
        return (
          <Input
            type="number"
            value={value ?? ''}
            onChange={(e) => handleChange(e.target.value)}
            min={numberConfig.min}
            max={numberConfig.max}
            step={numberConfig.step}
          />
        );
      case 'temperature':
        const tempConfig = config as TemperatureFieldConfig<T>;
        return (
          <Input
            type="number"
            value={value ?? ''}
            onChange={(e) => handleChange(e.target.value)}
            min={tempConfig.range?.min}
            max={tempConfig.range?.max}
            step={tempConfig.decimals ? Math.pow(10, -tempConfig.decimals) : undefined}
          />
        );

      case 'date':
        const displayDate = value ? toDisplayDate(value) : '';
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
                    handleChange(date.toISOString().split('T')[0]);
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
            onChange={(e) => handleChange(e.target.value)}
          />
        );

      case 'boolean':
        return (
          <Select
            value={value ? 'true' : 'false'}
            onValueChange={(val) => handleChange(val === 'true')}
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="true">{config.trueLabel || 'Yes'}</SelectItem>
              <SelectItem value="false">{config.falseLabel || 'No'}</SelectItem>
            </SelectContent>
          </Select>
        );

      case 'select':
        const selectConfig = config as SelectFieldConfig<T>;
        const selectOptions = typeof selectConfig.options === 'function' 
          ? selectConfig.options(record || ({} as T)) 
          : selectConfig.options || [];
        // Radix UI Select neumožňuje prázdny string ako hodnotu
        // Ak value nie je v options, použijeme undefined (zobrazí placeholder)
        const selectValue = value != null && selectOptions.some(opt => String(opt.value) === String(value))
          ? String(value)
          : undefined;
        return (
          <Select
            value={selectValue}
            onValueChange={handleChange}
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
            suggestions={tagConfig.suggestions || []}
            onChange={handleChange}
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
            onChange={(val) => handleChange(val === null ? null : val)}
            isLoading={isLoading}
            disabled={isSubmitting}
            placeholder={(config as any).placeholder || `Select ${config.header}`}
            required={required}
            autoSetValue={autoSetValue}
          />
        );

      default:
        return (
          <Input
            type="text"
            value={String(value ?? '')}
            onChange={(e) => handleChange(e.target.value)}
          />
        );
    }
  };

  if (!record) return null;

  return (
    <FormModal
      open={open}
      title={
        <>
          Edit
          <span style={{ marginLeft: '100px' }} className="text-3xl font-extrabold tracking-wide opacity-90">{singularName}</span>
        </>
      }
      onClose={onClose}
      onSubmit={handleSubmit}
      submitText={isSubmitting ? 'Saving...' : 'Save'}
      size="lg"
    >
      <div className="space-y-4">
        {editableFields.map(([key, config]) => {
          const fieldValue = formData[key as keyof T] ?? record[key];
          
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

