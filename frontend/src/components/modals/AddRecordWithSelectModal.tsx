//*........................................................
//*       frontend/src/components/modals/AddRecordWithSelectModal.tsx
//*       Generic modal for adding child records with hierarchical parent selection
//*
//*       Purpose: ConfigDriven modal for parent-child relationships with multi-level cascade
//*       Features:
//*       - Single level: company
//*       - Two level: company → factory
//*       - Three level: company → factory → location
//*       - 0 parents: disabled modal with message
//*       - 1 parent at each level: readonly field (automatically selected)
//*       - 2+ parents: dropdown selector with cascade filtering
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
import { API_BASE } from '@/config/api';
import { getMutatingHeaders } from '@/security/csrf';
import type { FieldConfig, ForeignKeyFieldConfig, SelectFieldConfig, TagFieldConfig } from '../ui_custom/table/fieldFactory';
import { ConditionalFKSelect } from '../ui_custom/table/ConditionalFKSelect';
import { EmptyState } from '../ui_custom/EmptyState';

type Option = { id: string; label: string };

interface HierarchyLevel {
  field: string;              // 'company', 'factory', 'location'
  endpoint: string;           // 'companies', 'factories', 'locations'
  label: string;              // 'Company', 'Factory', 'Location'
  parentField?: string;       // 'company' for factory, 'factory' for location
  requiredMessage?: string;   // 'Create company first'
}

interface HierarchyState {
  level: number;
  field: string;
  selectedValue: string | null;
  options: Option[];
  loading: boolean;
}

/**
 * Normalize order value to a valid number
 */
function normalizeOrder(value: number | undefined | null): number {
  if (typeof value !== 'number') return 999;
  if (!Number.isFinite(value)) return 999;
  return value;
}

/**
 * Sort fields by order
 */
function sortFieldsByAddOrder<T>(
  fields: [string, FieldConfig<T>][]
): [string, FieldConfig<T>][] {
  return [...fields].sort(([keyA, configA], [keyB, configB]) => {
    const orderA = normalizeOrder(
      (configA as any).orderInAddModal ?? (configA as any).order
    );
    const orderB = normalizeOrder(
      (configB as any).orderInAddModal ?? (configB as any).order
    );
    
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
      console.warn(`Failed to load options from ${endpoint}:`, error);
      return [];
    }
  }
  
  return out.sort((a, b) => a.label.localeCompare(b.label));
}

interface AddRecordWithSelectModalProps<T extends Record<string, any>> {
  open: boolean;
  fieldsMatrix: Record<string, FieldConfig<T>>;
  apiEndpoint: string;
  singularName?: string;
  
  // Hierarchical parent selection (NEW)
  parentHierarchy?: HierarchyLevel[];
  
  // Legacy single-parent support (backward compatible)
  parentField?: string;
  parentEndpoint?: string;
  parentOptions?: Option[];
  parentRequiredMessage?: string;
  parentLabel?: string;
  
  onClose: () => void;
  onSuccess?: (newRecord: T) => void;
  getCsrfToken?: () => string | null;
}

/**
 * AddRecordWithSelectModal component
 * 
 * ConfigDriven modal for adding child records with hierarchical parent selection:
 * - Single level (e.g., factory → company)
 * - Two levels (e.g., location → factory → company)
 * - Three levels (e.g., measurement → location → factory → company)
 * - Auto-detects readonly vs dropdown based on option count
 * - Cascade filtering: selecting parent filters child options
 */
export function AddRecordWithSelectModal<T extends Record<string, any>>({
  open,
  fieldsMatrix,
  apiEndpoint,
  singularName = 'Record',
  parentHierarchy: providedHierarchy,
  // Legacy props
  parentField: legacyParentField,
  parentEndpoint: legacyParentEndpoint,
  parentOptions: legacyParentOptions,
  parentRequiredMessage: legacyRequiredMessage,
  parentLabel: legacyParentLabel,
  onClose,
  onSuccess,
  getCsrfToken,
}: AddRecordWithSelectModalProps<T>) {
  const { handleSaveError } = useErrorHandler();
  const [formData, setFormData] = useState<Partial<T>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [hierarchyState, setHierarchyState] = useState<HierarchyState[]>([]);
  const [fkOptions, setFkOptions] = useState<Record<string, Option[]>>({});
  const [loadingFkOptions, setLoadingFkOptions] = useState<Record<string, boolean>>({});

  // System fields that should be excluded from Add modal by default
  const SYSTEM_FIELDS = ['id', 'uuid', 'created', 'updated', 'created_by', 'created_by_username'];

  // Auto-migrate legacy config to parentHierarchy
  const parentHierarchy: HierarchyLevel[] = React.useMemo(() => {
    if (providedHierarchy && providedHierarchy.length > 0) {
      return providedHierarchy;
    }
    
    // Legacy fallback
    if (legacyParentField && legacyParentEndpoint) {
      return [{
        field: legacyParentField,
        endpoint: legacyParentEndpoint,
        label: legacyParentLabel || 'Parent',
        requiredMessage: legacyRequiredMessage
      }];
    }
    
    return [];
  }, [providedHierarchy, legacyParentField, legacyParentEndpoint, legacyParentLabel, legacyRequiredMessage]);

  // Load hierarchy options when modal opens
  useEffect(() => {
    if (!open || parentHierarchy.length === 0) {
      setFormData({});
      setIsSubmitting(false);
      setHierarchyState([]);
      setFkOptions({});
      setLoadingFkOptions({});
      return;
    }

    const loadHierarchy = async () => {
      const states: HierarchyState[] = [];

      // Load root level (level 0)
      const rootLevel = parentHierarchy[0];
      const endpoint = rootLevel.endpoint.startsWith('/api/') 
        ? rootLevel.endpoint 
        : `/api/${rootLevel.endpoint}`;
      
      const rootOptions = await fetchAllOptions(endpoint);
      
      states.push({
        level: 0,
        field: rootLevel.field,
        selectedValue: rootOptions.length === 1 ? rootOptions[0].id : null,
        options: rootOptions,
        loading: false
      });

      // Initialize child levels (empty, disabled)
      for (let i = 1; i < parentHierarchy.length; i++) {
        states.push({
          level: i,
          field: parentHierarchy[i].field,
          selectedValue: null,
          options: [],
          loading: false
        });
      }

      setHierarchyState(states);

      // If root has 1 option, auto-select and load next level
      if (rootOptions.length === 1) {
        setFormData(prev => ({ ...prev, [rootLevel.field]: rootOptions[0].id } as Partial<T>));
        
        // Load next level if exists
        if (parentHierarchy.length > 1) {
          await loadChildLevel(states, 0, rootOptions[0].id);
        }
      }
    };

    loadHierarchy();
  }, [open, parentHierarchy]);

  // Load child level options based on parent selection
  const loadChildLevel = async (currentStates: HierarchyState[], parentLevelIndex: number, parentValue: string) => {
    if (parentLevelIndex + 1 >= parentHierarchy.length) return;

    const childLevel = parentHierarchy[parentLevelIndex + 1];
    const parentFieldName = childLevel.parentField;

    // Set loading
    setHierarchyState(prev => {
      const next = [...prev];
      next[parentLevelIndex + 1].loading = true;
      return next;
    });

    // Fetch filtered options
    const endpoint = childLevel.endpoint.startsWith('/api/') 
      ? childLevel.endpoint 
      : `/api/${childLevel.endpoint}`;
    
    const params = parentFieldName ? { [parentFieldName]: parentValue } : {};
    const options = await fetchAllOptions(endpoint, params);

    setHierarchyState(prev => {
      const next = [...prev];
      next[parentLevelIndex + 1].options = options;
      next[parentLevelIndex + 1].loading = false;
      
      // Auto-select if only 1 option
      if (options.length === 1) {
        next[parentLevelIndex + 1].selectedValue = options[0].id;
        setFormData(prev => ({ ...prev, [childLevel.field]: options[0].id } as Partial<T>));
        
        // Recursively load next level if exists
        if (parentLevelIndex + 2 < parentHierarchy.length) {
          loadChildLevel(next, parentLevelIndex + 1, options[0].id);
        }
      }
      
      return next;
    });
  };

  // Handle hierarchy selection change
  const handleHierarchyChange = async (levelIndex: number, value: string) => {
    const level = parentHierarchy[levelIndex];
    
    // Update current level
    setHierarchyState(prev => {
      const next = [...prev];
      next[levelIndex].selectedValue = value;
      return next;
    });
    
    setFormData(prev => ({ ...prev, [level.field]: value } as Partial<T>));

    // Clear all child levels
    setHierarchyState(prev => {
      const next = [...prev];
      for (let i = levelIndex + 1; i < next.length; i++) {
        next[i].selectedValue = null;
        next[i].options = [];
        const childField = parentHierarchy[i].field;
        setFormData(prev => {
          const updated = { ...prev };
          delete updated[childField as keyof T];
          return updated;
        });
      }
      return next;
    });

    // Load next level options
    await loadChildLevel(hierarchyState, levelIndex, value);
  };

  // Load FK options for other fields (excluding hierarchy fields)
  useEffect(() => {
    if (!open || hierarchyState.length === 0) return;

    // Check if all hierarchy levels are selected
    const allHierarchySelected = hierarchyState.every(state => state.selectedValue !== null);
    if (!allHierarchySelected) return;

    const loadOptions = async () => {
      const hierarchyFields = parentHierarchy.map(level => level.field);
      
      const fkFields = Object.entries(fieldsMatrix).filter(
        ([key, config]) => 
          !hierarchyFields.includes(key) && // Exclude hierarchy fields
          config.type === 'fk' && 
          (config as any).editableInAddModal !== false
      ) as [string, ForeignKeyFieldConfig<T>][];

      for (const [key, config] of fkFields) {
        setLoadingFkOptions(prev => ({ ...prev, [key]: true }));
        try {
          let endpoint = (config.apiEndpoint && config.apiEndpoint.trim() !== '') 
            ? config.apiEndpoint 
            : '';
          
          if (!endpoint && config.pluralName) {
            endpoint = `/api/${config.pluralName}`;
          }
          
          if (!endpoint || endpoint.trim() === '') {
            console.warn(`[AddRecordWithSelectModal] Skipping FK options for ${key}: no API endpoint`);
            setFkOptions(prev => ({ ...prev, [key]: [] }));
            setLoadingFkOptions(prev => ({ ...prev, [key]: false }));
            continue;
          }
          
          const params: Record<string, string> = {};
          if (config.useAllAccessible) {
            params.all_accessible = 'true';
          }
          
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
  }, [open, fieldsMatrix, hierarchyState, parentHierarchy]);

  // Get editable fields (excluding hierarchy fields and system fields)
  const editableFields = sortFieldsByAddOrder(
    Object.entries(fieldsMatrix).filter(([key, config]) => {
      // Exclude hierarchy fields (handled separately)
      const hierarchyFields = parentHierarchy.map(level => level.field);
      if (hierarchyFields.includes(key)) return false;
      
      // System fields are excluded by default
      if (SYSTEM_FIELDS.includes(key)) {
        return (config as any).editableInAddModal === true;
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

    // Validate all hierarchy levels selected
    const missingLevels: string[] = [];
    hierarchyState.forEach((state, index) => {
      if (!state.selectedValue) {
        missingLevels.push(parentHierarchy[index].label);
      }
    });

    if (missingLevels.length > 0) {
      toastMessages.validationFailed('Missing fields', `Please select: ${missingLevels.join(', ')}`);
      return;
    }

    // Validate required fields
    const missingFields: string[] = [];
    editableFields.forEach(([key, config]) => {
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
      // Build create payload with hierarchy fields
      const payload: Record<string, any> = {};
      
      hierarchyState.forEach(state => {
        payload[state.field] = state.selectedValue;
      });
      
      editableFields.forEach(([key, config]) => {
        const value = formData[key as keyof T];
        
        if (config.type === 'fk') {
          if (value === null || value === undefined || value === '') {
            payload[key] = null;
          } else if (typeof value === 'object' && (value as any)?.id) {
            payload[key] = String((value as any).id);
          } else {
            payload[key] = String(value);
          }
        } else if (config.type === 'date') {
          payload[key] = value ? format(value as Date, 'yyyy-MM-dd') : null;
        } else if (config.type === 'time') {
          payload[key] = value ? `${value}:00` : null;
        } else if (config.type === 'tag') {
          payload[`${key}_names`] = value || [];
        } else {
          payload[key] = value;
        }
      });

      // Make API call
      const response = await fetch(apiEndpoint, {
        method: 'POST',
        credentials: 'include',
        headers: getCsrfToken ? getMutatingHeaders() : { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error('[AddRecordWithSelectModal] API Error:', {
          status: response.status,
          statusText: response.statusText,
          errorData,
          payload,
        });
        
        let errorMessage = 'Failed to create record';
        if (errorData && typeof errorData === 'object') {
          if (errorData.detail) {
            errorMessage = errorData.detail;
          } else if (Array.isArray(errorData.non_field_errors)) {
            errorMessage = errorData.non_field_errors.join(', ');
          } else {
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
        
        return (
          <ConditionalFKSelect
            options={options}
            value={currentValue}
            onChange={(val) => handleChange(key, val === null ? null : val)}
            isLoading={isLoading}
            disabled={isSubmitting}
            placeholder={(config as any).placeholder || `Select ${config.header}`}
            required={required}
          />
        );

      default:
        return (
          <Input {...commonProps} value={String(value ?? '')} />
        );
    }
  };

  // Render hierarchical selects
  const renderHierarchySelects = () => {
    if (hierarchyState.length === 0) return null;

    // Check if ALL levels have exactly 1 option (all readonly)
    const allReadonly = hierarchyState.every(s => s.options.length === 1);

    return hierarchyState.map((state, index) => {
      const level = parentHierarchy[index];
      const isDisabled = index > 0 && !hierarchyState[index - 1].selectedValue;

      // If all levels have 1 option, show readonly
      if (allReadonly && state.options.length === 1) {
        return (
          <div key={state.field} className="space-y-2">
            <label className="text-sm font-medium">
              {level.label}
              <span className="text-destructive ml-1">*</span>
            </label>
            <Input
              value={state.options[0].label}
              disabled
              className="bg-muted"
            />
          </div>
        );
      }

      // Level 0 empty state
      if (index === 0 && state.options.length === 0) {
        return (
          <EmptyState
            key={state.field}
            message={level.requiredMessage || `Create ${level.label.toLowerCase()} first`}
            icon="AlertCircle"
          />
        );
      }

      // Single option at this level (readonly)
      if (state.options.length === 1) {
        return (
          <div key={state.field} className="space-y-2">
            <label className="text-sm font-medium">
              {level.label}
              <span className="text-destructive ml-1">*</span>
            </label>
            <Input
              value={state.options[0].label}
              disabled
              className="bg-muted"
            />
          </div>
        );
      }

      // Dropdown selector (2+ options or waiting for parent)
      return (
        <div key={state.field} className="space-y-2">
          <label className="text-sm font-medium">
            {level.label}
            <span className="text-destructive ml-1">*</span>
          </label>
          <Select
            value={state.selectedValue || undefined}
            onValueChange={(val) => handleHierarchyChange(index, val)}
            disabled={isDisabled || isSubmitting || state.loading}
          >
            <SelectTrigger>
              <SelectValue placeholder={state.loading ? 'Loading...' : `Select ${level.label}`} />
            </SelectTrigger>
            <SelectContent>
              {state.options.map((opt) => (
                <SelectItem key={opt.id} value={opt.id}>
                  {opt.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      );
    });
  };

  // If 0 parents at root level, show empty state modal
  if (open && hierarchyState.length > 0 && hierarchyState[0].options.length === 0 && !hierarchyState[0].loading) {
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
        onSubmit={(e) => e.preventDefault()}
        submitText="Create"
        hideSubmit
        size="lg"
      >
        <EmptyState
          message={parentHierarchy[0]?.requiredMessage || `Create ${parentHierarchy[0]?.label.toLowerCase()} first`}
          icon="AlertCircle"
        />
      </FormModal>
    );
  }

  // Check if all hierarchy levels are selected (needed to show other fields)
  const allHierarchySelected = hierarchyState.length > 0 && hierarchyState.every(state => state.selectedValue !== null);

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
        {/* Hierarchical parent selection */}
        {renderHierarchySelects()}
        
        {/* Editable fields (only if all hierarchy levels selected) */}
        {allHierarchySelected && editableFields.map(([key, config]) => {
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
