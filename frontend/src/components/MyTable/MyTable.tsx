//*.............................................................................
//*       www/thermal_eye_ui/src/components/MyTable/MyTable.tsx
//*       Unified table component - orchestrates all table features
//*       
//*       Purpose: Single component pre všetky tabuľky
//*       Architecture: Composer pattern - skladá existujúce shadcn komponenty
//*.............................................................................

import React from 'react';
import * as TI from '@/components/ui_custom/table/tableImports';
import { PageHeader } from '@/components/PageHeader';
import { PageFooter } from '@/components/PageFooter';
import { getCsrfToken } from '@/utils/csrf';
import type { MyTableConfig } from './MyTableTypes';
import { DEFAULT_MY_TABLE_CONFIG } from './MyTableTypes';
import { useMyTableData } from './useMyTableData';
import { TagEditor } from '@/components/TagEditor';
import {
  matrixToFieldConfigs,
  matrixToColumnsFields,
  matrixToColumnOrder,
  matrixToFiltersFields,
} from './MyTableHelpers';
import { useSnapshot } from '@/hooks/useSnapshot';
import { useTableState, useTableColumnsState, useTableFiltersState } from '@/hooks/useMyState';
import { getModelEndpoint, loadModelMetadata, getDefaultOrdering, getModelSingular, getOwnershipField } from '@/config/modelMetadata';
import { SaveStateModal } from '@/components/modals/SaveStateModal';
import { LoadStateModal } from '@/components/modals/LoadStateModal';
import { ShareFactoryModal } from '@/components/modals/ShareFactoryModal';
import { EditRecordModal } from '@/components/modals/EditRecordModal';
import { AddRecordModal } from '@/components/modals/AddRecordModal';
import { AddRecordWithSelectModal } from '@/components/modals/AddRecordWithSelectModal';
import { useScope } from '@/contexts/ScopeContext';
import { useAuth } from '@/contexts/AuthContext';
import { useAccessRights } from '@/hooks/useAccessRights';
import { useApi } from '@/hooks/useApi';
import { API_BASE } from '@/config/api';

/** Option type for FK dropdowns
 */
type Option = { id: string; label: string };

/** Helper: Get singular model name from tableName or API endpoint
 * 
 * Example: 'Locations' -> 'Location', '/api/locations/' -> 'Location'
 * Uses tableName first (most reliable), then falls back to endpoint conversion.
 * #TODO_SOPIRA.MAGIC: toto si myslim ze je zbytocne, lebo singular/plural uz generujem priamo z modelov
 */
function getSingularNameFromEndpoint(apiEndpoint: string, tableName?: string): string {
  // First, try to use tableName if provided (e.g., 'Locations' -> 'Location')
  if (tableName) {
    // Convert plural tableName to singular using metadata
    const tableNameLower = tableName.toLowerCase();
    let singular = getModelSingular(tableNameLower);
    
    // If not found in metadata, try simple plural->singular conversion
    if (!singular) {
      let singularFieldName = tableNameLower;
      if (tableNameLower.endsWith('ies')) {
        singularFieldName = tableNameLower.slice(0, -3) + 'y'; // Factories -> Factory
      } else if (tableNameLower.endsWith('es') && tableNameLower.length > 3) {
        singularFieldName = tableNameLower.slice(0, -2); // Locations -> Location
      } else if (tableNameLower.endsWith('s') && tableNameLower.length > 1) {
        singularFieldName = tableNameLower.slice(0, -1); // Users -> User
      }
      
      // Try metadata again with converted name
      singular = getModelSingular(singularFieldName);
      
      // If still not found, capitalize the converted name
      if (!singular) {
        singular = singularFieldName.charAt(0).toUpperCase() + singularFieldName.slice(1);
      } else {
        // Capitalize first letter of metadata result
        singular = singular.charAt(0).toUpperCase() + singular.slice(1);
      }
    } else {
      // Capitalize first letter of metadata result
      singular = singular.charAt(0).toUpperCase() + singular.slice(1);
    }
    
    return singular;
  }
  
  // Fallback: extract from endpoint
  const match = apiEndpoint.match(/\/api\/([^\/]+)\/?$/);
  if (!match) return 'Record';
  const pluralEndpointName = match[1]; // e.g., 'locations'
  
  // Convert plural endpoint to singular field name
  let singularFieldName = pluralEndpointName;
  if (pluralEndpointName.endsWith('ies')) {
    singularFieldName = pluralEndpointName.slice(0, -3) + 'y'; // factories -> factory
  } else if (pluralEndpointName.endsWith('es') && pluralEndpointName.length > 3) {
    singularFieldName = pluralEndpointName.slice(0, -2); // locations -> location
  } else if (pluralEndpointName.endsWith('s') && pluralEndpointName.length > 1) {
    singularFieldName = pluralEndpointName.slice(0, -1); // users -> user
  }
  
  // Get singular from metadata
  let singular = getModelSingular(singularFieldName);
  if (singular) {
    // Capitalize first letter
    singular = singular.charAt(0).toUpperCase() + singular.slice(1);
  } else {
    // Fallback: capitalize converted name
    singular = singularFieldName.charAt(0).toUpperCase() + singularFieldName.slice(1);
  }
  
  return singular;
}

/**
 * MyTable - Unified table component
 * 
 * @example
 * ```tsx
 * <MyTable config={{
 *   tableName: 'Log Entries',
 *   apiEndpoint: '/api/logentries/',
 *   storageKey: 'logentry',
 *   fields: [
 *     { key: 'id', header: 'ID', type: 'number', size: 80 },
 *     { key: 'timestamp', header: 'Timestamp', type: 'date', size: 180 },
 *   ],
 * }} />
 * ```
 */
export function MyTable<T extends { id: string | number } & Record<string, any>>({
  config,
}: {
  config: MyTableConfig<T>;
}) {
  // ============================================
  // FIELD MATRIX CONVERSION (if provided)
  // ============================================
  // Convert fieldsMatrix to existing structures for backward compatibility
  const processedConfig = TI.useMemo(() => {
    if (!config.fieldsMatrix) {
      // No matrix - use config as-is
      return config;
    }
    
    // Convert matrix to fields, columns, filters
    const generatedFields = matrixToFieldConfigs(config.fieldsMatrix);
    const generatedColumnsFields = matrixToColumnsFields(config.fieldsMatrix);
    const generatedColumnOrder = matrixToColumnOrder(config.fieldsMatrix);
    const generatedFiltersFields = matrixToFiltersFields(config.fieldsMatrix);
    
    // Build complete column order: selection + actions + data fields
    const completeColumnOrder: string[] = [];
    
    // Add selection column first (if enabled)
    const rowSelectionEnabled = config.rowSelection?.enabled ?? true; // default true
    if (rowSelectionEnabled) {
      completeColumnOrder.push('select');
    }
    
    // Add actions column second (if enabled)
    const actionsEnabled = config.actions?.edit || config.actions?.delete || (config.actions?.customActions?.length ?? 0) > 0;
    if (actionsEnabled) {
      completeColumnOrder.push('actions');
    }
    
    // Add data fields from matrix
    completeColumnOrder.push(...generatedColumnOrder);
    
    
    return {
      ...config,
      fields: generatedFields,
      columns: {
        ...config.columns,
        fields: generatedColumnsFields,
        defaultOrder: completeColumnOrder,
      },
      filters: {
        ...config.filters,
        fields: generatedFiltersFields,
      },
    };
  }, [config]);
  
  // ============================================
  // MERGE CONFIG WITH DEFAULTS
  // ============================================
  const cfg = {
    ...DEFAULT_MY_TABLE_CONFIG,
    ...processedConfig,
    pageHeader: { ...DEFAULT_MY_TABLE_CONFIG.pageHeader, ...processedConfig.pageHeader },
    pageFooter: { ...DEFAULT_MY_TABLE_CONFIG.pageFooter, ...processedConfig.pageFooter },
    headerVisibility: { ...DEFAULT_MY_TABLE_CONFIG.headerVisibility, ...processedConfig.headerVisibility },
    toolbarVisibility: { ...DEFAULT_MY_TABLE_CONFIG.toolbarVisibility, ...processedConfig.toolbarVisibility },
    filters: { ...DEFAULT_MY_TABLE_CONFIG.filters, ...processedConfig.filters },
    columns: { ...DEFAULT_MY_TABLE_CONFIG.columns, ...processedConfig.columns },
    actions: { ...DEFAULT_MY_TABLE_CONFIG.actions, ...processedConfig.actions },
    inlineEdit: { ...DEFAULT_MY_TABLE_CONFIG.inlineEdit, ...processedConfig.inlineEdit },
    export: { ...DEFAULT_MY_TABLE_CONFIG.export, ...processedConfig.export },
    rowSelection: { ...DEFAULT_MY_TABLE_CONFIG.rowSelection, ...processedConfig.rowSelection },
    pagination: { ...DEFAULT_MY_TABLE_CONFIG.pagination, ...processedConfig.pagination },
    multiLine: { ...DEFAULT_MY_TABLE_CONFIG.multiLine, ...processedConfig.multiLine },
    emptyState: { ...DEFAULT_MY_TABLE_CONFIG.emptyState, ...processedConfig.emptyState },
    useMyState: processedConfig.useMyState ?? false,
  } as Required<MyTableConfig<T>>;

  // ============================================
  // SCOPE MANAGEMENT
  // ============================================
  const { selectedFactories } = useScope();
  const { user } = useAuth();
  const { getActions } = useAccessRights();

  // Derive view name from apiEndpoint (e.g., /api/companies/ -> companies)
  const viewName = TI.useMemo(() => {
    const api = config.apiEndpoint ?? '';
    const match = api.match(/\/api\/([^/]+)\/?$/);
    if (match) return match[1];
    // Fallback: storageKey or lowercased tableName without spaces
    if ((config as any).storageKey) return (config as any).storageKey.replace(/Table$/i, '').toLowerCase();
    if (config.tableName) return config.tableName.toLowerCase().replace(/\\s+/g, '');
    return '';
  }, [config.apiEndpoint, config.tableName, (config as any).storageKey]);

  const accessActions = getActions(viewName || '');
  const allowAdd = accessActions?.add ?? true;
  const allowEdit = accessActions?.edit ?? true;
  const allowDelete = accessActions?.delete ?? true;
  const allowExport = accessActions?.export ?? true;
  // Get ownership_field from modelMetadata (SSOT) - backend automatically applies scope
  // Note: scopeFactory is deprecated - backend handles scoping automatically
  const ownershipFieldFromMetadata = getOwnershipField(cfg.storageKey);
  // Map ownership_field (e.g., "factory_id") to filter field name (e.g., "factory")
  const ownershipFilterField = ownershipFieldFromMetadata 
    ? ownershipFieldFromMetadata.replace('_id', '').replace('_', '') 
    : 'factory'; // Fallback for backward compatibility
  
  // ============================================
  // API HOOK (for authenticated requests)
  // ============================================
  const api = useApi();
  
  // ============================================
  // STATE
  // ============================================
  const [globalFilter, setGlobalFilter] = TI.useState<string>('');
  const [globalFilterInput, setGlobalFilterInput] = TI.useState('');
  const debouncedGlobalFilter = TI.useDebounced(globalFilterInput, cfg.globalSearch.debounceMs);
  const [searchMode, setSearchMode] = TI.useState<'simple' | 'advanced'>(cfg.globalSearch.advancedSearch ? 'advanced' : 'simple');
  const [approximateSearch, setApproximateSearch] = TI.useState(false);
  const isAdvancedSearch = searchMode === 'advanced';
  const searchPlaceholder = TI.useMemo(() => {
    if (cfg.globalSearch.placeholder) return cfg.globalSearch.placeholder;
    return isAdvancedSearch
      ? 'Pokročilé vyhľadávanie (AND/OR/NOT, +/-, "fráza")'
      : 'Hľadaj...';
  }, [cfg.globalSearch.placeholder, isAdvancedSearch]);

  
  // Table state (sorting, filtering, pagination)
  const [sorting, setSorting] = TI.useState<TI.SortingState>([]);
  const [columnFilters, setColumnFilters] = TI.useState<TI.ColumnFiltersState>([]);
  const [pageIndex, setPageIndex] = TI.useState<number>(0);
  const [pageSize, setPageSize] = TI.useState<number>(cfg.pagination.defaultPageSize || 10);
  
  // Show only selected mode
  const [showOnlySelected, setShowOnlySelected] = TI.useState(false);
  
  // Update columnFilters when scope changes (apply factory filter from scope)
  // NOTE: Only apply factory filter if there are selected factories
  // If no factories are selected, don't add factory filter (show all user's factories)
  // Use ref to prevent unnecessary updates during initial load
  const prevSelectedFactoriesRef = TI.useRef<string[]>([]);
  TI.useEffect(() => {
    // Skip factory scope logic if disabled (for global tables like Users)
    if (cfg.disableFactoryScope) {
      return;
    }
    
    // Only update if selectedFactories actually changed (deep comparison)
    const currentKey = JSON.stringify([...selectedFactories].sort());
    const prevKey = JSON.stringify([...prevSelectedFactoriesRef.current].sort());
    if (currentKey === prevKey) return;
    
    console.log('[MyTable] Factory scope effect triggered, selectedFactories:', selectedFactories);
    prevSelectedFactoriesRef.current = [...selectedFactories];
    
    setColumnFilters((prev) => {
      console.log('[MyTable] Factory scope effect - prev filters:', prev);
      // Use ownership_field from metadata (SSOT) instead of hardcode 'factory'
      const others = prev.filter((f) => f.id !== ownershipFilterField);
      // Backend automatically applies scope - frontend doesn't need to filter
      // This code is kept for backward compatibility but backend handles scoping
      if (selectedFactories.length > 0) {
        const newFilters = [{ id: ownershipFilterField, value: selectedFactories }, ...others];
        console.log('[MyTable] Factory scope effect - new filters:', newFilters);
        return newFilters;
      }
      // No factories selected - remove filter (backend handles scoping automatically)
      console.log('[MyTable] Factory scope effect - returning others only:', others);
      return others;
    });
    setPageIndex(0);
  }, [selectedFactories, cfg.disableFactoryScope]);
  
  // Update globalFilter when debounced value changes
  TI.useEffect(() => {
    setGlobalFilter(debouncedGlobalFilter);
  }, [debouncedGlobalFilter]);
  
  // Clear "show only selected" mode when filters change
  TI.useEffect(() => {
    if (showOnlySelected && (columnFilters.length > 0 || globalFilterInput.length > 0)) {
      setShowOnlySelected(false);
    }
  }, [columnFilters, globalFilterInput, showOnlySelected]);

  // Panel states
  const [showFilters, setShowFilters] = TI.useState(false);
  const [showColumns, setShowColumns] = TI.useState(false);
  
  // Debug state (len pre superuserov)
  const [showDebugInfo, setShowDebugInfo] = TI.useState(false);
  
  // State preset modals (legacy - for non-myState mode)
  const [showSaveStateModal, setShowSaveStateModal] = TI.useState(false);
  const [showLoadStateModal, setShowLoadStateModal] = TI.useState(false);
  const [statePresetComponent, setStatePresetComponent] = TI.useState<'columns' | 'filters'>('columns');
  
  // Separate modal states for myState mode (independent panel presets)
  const [showColumnsSaveModal, setShowColumnsSaveModal] = TI.useState(false);
  const [showColumnsLoadModal, setShowColumnsLoadModal] = TI.useState(false);
  const [showFiltersSaveModal, setShowFiltersSaveModal] = TI.useState(false);
  const [showFiltersLoadModal, setShowFiltersLoadModal] = TI.useState(false);
  
  // Active preset names (for display in panels) - local state for legacy mode
  const [activeColumnsPresetNameLocal, setActiveColumnsPresetNameLocal] = TI.useState<string | null>(null);
  const [activeFiltersPresetNameLocal, setActiveFiltersPresetNameLocal] = TI.useState<string | null>(null);
  
  // ============================================
  // BUILD QUERY PARAMS (for server-side fetching)
  // ============================================
  const useSearchService = (cfg.globalSearch.useSearchService ?? false) && Boolean(globalFilterInput.trim());

  const queryParams = TI.useMemo(() => {
    // Fix: use fallback/defaults for pageIndex and pageSize in case they are undefined/null
    const params: Record<string, string | number> = {
      page: typeof pageIndex === 'number' && pageIndex >= 0 ? pageIndex + 1 : 1,
      page_size: typeof pageSize === 'number' && pageSize > 0 ? pageSize : 10,
    };
    
    // Sorting
    if (sorting.length > 0) {
      const sort = sorting[0];
      params.ordering = `${sort.desc ? '-' : ''}${sort.id}`;
    }
    
    // Global search
    if (!useSearchService && globalFilter) {
      params.search = globalFilter;
    }
    
    // Column filters - convert to API query params based on filterType
    columnFilters.forEach((filter) => {
      const fieldKey = filter.id;
      const fieldConfig = cfg.fieldsMatrix?.[fieldKey];
      const filterType = fieldConfig?.filterType;
      const fieldType = fieldConfig?.type;
      const value = filter.value;
      
      if (!value) return; // Skip empty filters
      
      // FK multiselect filters -> {field}_in (except ownership_field which uses {field})
      if (filterType === 'multiselect' && fieldType === 'fk') {
        if (Array.isArray(value) && value.length > 0) {
          // Ownership field filter uses '{field}' parameter (supports comma-separated list)
          // Other FK filters use '{field}_in' parameter
          // Use ownership_field from metadata (SSOT) instead of hardcode 'factory'
          if (fieldKey === ownershipFilterField) {
            params[fieldKey] = value.join(',');
          } else {
          params[`${fieldKey}_in`] = value.join(',');
          }
        }
      }
      // Select multiselect filters -> {field}_in
      else if (filterType === 'multiselect' && fieldType === 'select') {
        if (Array.isArray(value) && value.length > 0) {
          params[`${fieldKey}_in`] = value.join(',');
        }
      }
      // Boolean filters -> {field}_in (converts 'true'/'false' strings to boolean)
      else if (filterType === 'boolean') {
        if (Array.isArray(value) && value.length > 0) {
          // Convert string values ('true', 'false') to boolean values
          const booleanValues = value.map(v => v === 'true' ? 'true' : 'false');
          params[`${fieldKey}_in`] = booleanValues.join(',');
        }
      }
      // Text filters -> {field}_icontains
      else if (filterType === 'text') {
        if (typeof value === 'string' && value.trim()) {
          params[`${fieldKey}_icontains`] = value.trim();
        }
      }
      // Date range filters -> {field}_after and {field}_before
      else if (filterType === 'daterange') {
        if (value && typeof value === 'object') {
          const range = value as { from?: string; to?: string };
          if (range.from) {
            params[`${fieldKey}_after`] = range.from;
          }
          if (range.to) {
            params[`${fieldKey}_before`] = range.to;
          }
        }
      }
      // Numeric range filters -> {field}_min and {field}_max
      else if (filterType === 'range') {
        if (value && typeof value === 'object') {
          const range = value as { min?: number; max?: number };
          if (range.min !== undefined && !Number.isNaN(range.min)) {
            params[`${fieldKey}_min`] = range.min;
          }
          if (range.max !== undefined && !Number.isNaN(range.max)) {
            params[`${fieldKey}_max`] = range.max;
          }
        }
      }
    });
    
    return params;
  }, [pageIndex, pageSize, sorting, globalFilter, columnFilters, cfg.fieldsMatrix, useSearchService]);

  const searchQueryParams = TI.useMemo(() => {
    const params: Record<string, string | number> = {
      ...queryParams,
      view: viewName,
      q: globalFilter,
      mode: isAdvancedSearch ? 'advanced' : 'simple',
      approximate: approximateSearch ? '1' : '0',
    };
    delete params.search; // search sa pri ES posiela ako 'q'
    return params;
  }, [queryParams, viewName, globalFilter, isAdvancedSearch, approximateSearch]);

  const transformSearchResults = TI.useCallback((records: any[]) => {
    return records.map((hit: any) => {
      const row = hit?.data ?? hit;
      if (hit?.highlight) {
        (row as any).__highlight = hit.highlight;
      }
      return row;
    });
  }, []);

  // ============================================
  // DATA FETCHING (server-side)
  // ============================================
  const {
    data,
    total,
    isLoading,
    error: fetchError,
    refetch,
    updateRecord,
    updateFullRecord,
  } = useMyTableData<T>({
    endpoint: useSearchService ? '/api/search/' : cfg.apiEndpoint,
    queryParams: useSearchService ? searchQueryParams : queryParams,
    transformResponse: useSearchService ? transformSearchResults : undefined,
  });

  const fieldConfigMap = TI.useMemo<Record<string, TI.FieldConfig<T>>>(() => {
    const map: Record<string, TI.FieldConfig<T>> = {};
    cfg.fields.forEach((f) => {
      map[String(f.key)] = f;
    });
    return map;
  }, [cfg.fields]);

  // MultiLine mode state (false = compact/single-line, true = expanded/multi-line)
  const [isMultiLine, setIsMultiLine] = TI.useState(cfg.multiLine.enabled || false);
  
  // Row expansion state
  const [expandedRows, setExpandedRows] = TI.useState<Set<string>>(new Set());

  // Inline edit state
  const [editingCell, setEditingCell] = TI.useState<{ id: string; field: string } | null>(null);

  // Modals
  const [showAddModal, setShowAddModal] = TI.useState(false);
  const [editingRecord, setEditingRecord] = TI.useState<T | null>(null);
  const [deletingRecords, setDeletingRecords] = TI.useState<T[]>([]);
  const [sharingRecords, setSharingRecords] = TI.useState<T[]>([]);

  // ============================================
  // HOOKS
  // ============================================
  const tableRef = TI.useRef<any>(null);

  // Error handling
  const { error, isErrorModalOpen, showError, closeErrorModal } = TI.useErrorHandler();

  // Tooltip
  const { tooltip } = TI.useTooltip();

  // Debounced search
  const debouncedFilter = TI.useDebounced(globalFilterInput, 300);

  // Column state (visibility, order, sizing)
  const columnHelper = TI.useMemo(() => TI.createColumnHelper<T>(), []);

  // ============================================
  // FK OPTIONS STATE
  // ============================================
  // FK options state (keyed by field name) - declared early for use in fieldFactoryContext
  const [fkOptions, setFkOptions] = TI.useState<Record<string, Option[]>>({});
  
  // Trigger for re-rendering when scoped cache updates
  const [renderTrigger, setRenderTrigger] = TI.useState(0);

  // ============================================
  // SCOPED FK OPTIONS (must be before fieldFactoryContext)
  // ============================================
  // Scoped cache by factory (UUID-based filtering for performance)
  const scopedCache = TI.useRef(new Map<string, Option[]>()).current;
  
  /**
   * Get scoped options for a FK field
   * Backend automatically applies scope - frontend does NOT send factoryId
   * Uses backend FK cache API for fast loading
   */
  const getScopedOptions = TI.useCallback(async (
    fieldKey: string,
    _factoryId?: string // DEPRECATED: Backend automatically applies scope, this parameter is ignored
  ): Promise<Option[]> => {
    const cacheKey = `${fieldKey}`;
    if (scopedCache.has(cacheKey)) {
      return scopedCache.get(cacheKey)!;
    }
    try {
      const { loadFKOptionsFromCache } = await import('../../services/fkCacheService');
      const options = await loadFKOptionsFromCache(fieldKey, []);
      const formattedOptions: Option[] = options.map(opt => ({
        id: opt.id,
        label: opt.label,
        ...(opt.code !== undefined && { code: opt.code }),
        ...(opt.name !== undefined && { name: opt.name }),
        ...(opt.human_id !== undefined && { human_id: opt.human_id }),
        ...Object.keys(opt).reduce((acc, key) => {
          if (key !== 'id' && key !== 'label' && opt[key] !== undefined) {
            acc[key] = opt[key];
          }
          return acc;
        }, {} as Record<string, any>)
      }));
      scopedCache.set(cacheKey, formattedOptions);
      return formattedOptions;
    } catch (_error) {
      return [];
    }
  }, []);

  // ============================================
  // TAG SUGGESTIONS CACHE
  // ============================================
  const tagSuggestionsCache = TI.useRef(new Map<string, string[]>()).current;
  
  /**
   * Get tag suggestions for a factory and model
   */
  const getTagSuggestions = TI.useCallback(async (
    factoryId: string,
    model: string = 'measurement'
  ): Promise<string[]> => {
    const cacheKey = `${factoryId}:${model}`;
    
    // Return cached result if available
    if (tagSuggestionsCache.has(cacheKey)) {
      return tagSuggestionsCache.get(cacheKey)!;
    }
    
    // Fetch tag suggestions from API
    try {
      const url = `${API_BASE}/api/tags/suggest/?factory=${factoryId}&model=${encodeURIComponent(model)}`;
      const response = await fetch(url, { credentials: 'include' });
      if (!response.ok) return [];
      
      const data = await response.json();
      const suggestions = data.tags || [];
      
      // Cache result
      tagSuggestionsCache.set(cacheKey, suggestions);
      return suggestions;
    } catch (error) {
      console.error(`[MyTable.getTagSuggestions] ERROR for ${cacheKey}:`, error);
      return [];
    }
  }, []);

  // ============================================
  // FIELD FACTORY CONTEXT
  // ============================================
  const fieldFactoryContext: TI.FieldFactoryContext<T> = TI.useMemo(
    () => {
      // TagsCell wrapper component
      const TagsCell: React.ComponentType<{ row: T; value: string[]; onSave: (tags: string[]) => void }> = ({ row, value, onSave }) => {
        const [suggestions, setSuggestions] = React.useState<string[]>([]);
        
        // Get ownership field value from row using ownership_field from metadata (SSOT)
        // Map ownership_field (e.g., "factory_id") to row property (e.g., "factory")
        const ownershipFieldValue = ownershipFieldFromMetadata 
          ? (row as any)[ownershipFilterField] || (row as any)[ownershipFieldFromMetadata]
          : (row as any).factory; // Fallback for backward compatibility
        const model = cfg.tableName?.toLowerCase().replace(/s$/, '') || 'measurement';
        
        // Load tag suggestions - use first selected factory from active scope if available
        // Backend automatically applies scope, but tag suggestions still need factory ID
        React.useEffect(() => {
          const factoryId = ownershipFieldValue || (selectedFactories.length > 0 ? selectedFactories[0] : null);
          if (factoryId) {
            getTagSuggestions(factoryId, model).then(sugg => {
              setSuggestions(sugg);
            }).catch(() => {});
          }
        }, [ownershipFieldValue, selectedFactories, model, getTagSuggestions]);
        
        // Get suggestions from field config if available
        const tagFieldConfig = cfg.fieldsMatrix?.['tags'] as any;
        const configSuggestions = tagFieldConfig?.suggestions || [];
        const allSuggestions = [...new Set([...suggestions, ...configSuggestions])];
        
        return (
          <div className="min-w-[200px] p-2">
            <TagEditor
              value={value}
              onChange={onSave}
              suggestions={allSuggestions}
              onNewTag={(tagName) => {
                // Add new tag to cache for this factory
                // Use ownershipFieldValue or first selected factory from active scope
                const tagFactoryId = ownershipFieldValue || (selectedFactories.length > 0 ? selectedFactories[0] : null);
                if (tagFactoryId) {
                  const cacheKey = `${tagFactoryId}:${model}`;
                  const current = tagSuggestionsCache.get(cacheKey) || [];
                  if (!current.includes(tagName)) {
                    tagSuggestionsCache.set(cacheKey, [...current, tagName]);
                    setSuggestions(prev => [...prev, tagName]);
                  }
                }
              }}
            />
          </div>
        );
      };
      
      const ctx = {
        apiEndpoint: cfg.apiEndpoint,
        editingCell,
        setEditingCell,
        updateField: (recordId: string | number, fieldName: keyof T, newValue: T[keyof T]) => {
          updateRecord(recordId, { [fieldName]: newValue } as Partial<T>);
        },
        updateFullRecord,
        handleError: (recordId: string | number, errorData: unknown) => {
          showError({
            operation: 'save',
            message: `Failed to update record ${recordId}`,
            details: errorData,
          });
        },
        getCsrfToken,
        searchTerm: globalFilter,
        highlightText: (text: string, searchTerm: string) => {
          const terms = TI.extractSearchTerms(searchTerm);
          return TI.highlightText(text, terms);
        },
        fkOptions, // FK options loaded from API for dropdown editing
        getScopedOptions, // Set directly in useMemo
        scopedCache, // Set directly in useMemo
        onScopeCacheUpdate: () => setRenderTrigger(prev => prev + 1),
        TagsCell, // Tag editor component for inline editing
      };
      // debug disabled
      return ctx;
    },
    [cfg.apiEndpoint, cfg.tableName, cfg.fieldsMatrix, editingCell, setEditingCell, updateRecord, updateFullRecord, globalFilter, showError, getCsrfToken, fkOptions, renderTrigger, getScopedOptions, getTagSuggestions]
  );

  // ============================================
  // ROW SELECTION
  // ============================================
  const {
    selectedRows,
    setSelectedRows,
    toggleRow,
    toggleAll,
    clearSelection,
    isSelected,
    isAllSelected,
    isIndeterminate,
    selectedCount,
  } = TI.useRowSelection<T>();

// ============================================
// VISIBLE SELECTED (VisibleSelected concept)
// ============================================
// Only rows that are BOTH selected AND in visible scope
const visibleSelectedRows = TI.useMemo(() => {
  return data.filter((row) => selectedRows.has(String(row.id)));
}, [data, selectedRows]);

const visibleSelectedCount = visibleSelectedRows.length;

const rowSelectionState = TI.useMemo<Record<string, boolean>>(() => {
  const obj: Record<string, boolean> = {};
  selectedRows.forEach((id) => {
    obj[String(id)] = true;
  });
  return obj;
}, [selectedRows]);

  // ============================================
  // COLUMNS - ALL via FieldFactory (DRY!)
  // ============================================
  
  // Build complete field list: selection + data fields + actions
  const allFieldConfigs: TI.FieldConfig<T>[] = TI.useMemo(() => {
    const configs: TI.FieldConfig<T>[] = [];
    
    // Selection column (if enabled) - FIRST column (order: 0)
    if (cfg.rowSelection.enabled) {
      configs.push({ type: 'selection', key: 'select', order: 0 } as TI.FieldConfig<T>);
    }
    
    // Actions column (if any actions are enabled) - SECOND column (order: 5)
    if ((cfg.actions.edit && allowEdit) || (cfg.actions.delete && allowDelete) || cfg.actions.expand || cfg.actions.inlineShare || cfg.actions.customActions?.length) {
      const showShare = !!(cfg.actions.inlineShare && (user?.role?.toLowerCase() === 'admin' || user?.role?.toLowerCase() === 'superadmin' || user?.is_superuser_role));
      
      const actionsConfig = {
        type: 'actions' as const,
        key: 'actions' as const,
        header: 'Actions',
        showEdit: cfg.actions.edit && allowEdit,
        showDelete: cfg.actions.delete && allowDelete,
        showExpand: cfg.actions.expand,
        showShare,
        order: 5,
      };
      
      configs.push(actionsConfig);
    }
    
    // Data fields (start from order: 10)
    configs.push(...cfg.fields);
    
    // Sort by order property (ascending)
    configs.sort((a, b) => {
      const orderA = (a as any).order ?? 999;
      const orderB = (b as any).order ?? 999;
      return orderA - orderB;
    });
    
    return configs;
  }, [cfg.rowSelection.enabled, cfg.fields, cfg.actions.edit, cfg.actions.delete, cfg.actions.expand, cfg.actions.inlineShare, user]);

  // Update fieldFactoryContext with selection & actions handlers
  const extendedFieldContext: TI.FieldFactoryContext<T> = TI.useMemo(() => ({
    ...fieldFactoryContext,
    // Selection handlers
    data,
    isSelected,
    toggleRow,
    isAllSelected,
    toggleAll,
    isIndeterminate,
    // Actions handlers
    checkIsEditing: (id: string, field: string) => {
      return editingCell?.id === id && editingCell?.field === field;
    },
    onEdit: (row: T) => {
      setEditingRecord(row);
      cfg.callbacks?.onEdit?.(row);
    },
    onDelete: (row: T) => {
      setDeletingRecords([row]);
    },
    onShare: (row: T) => {
      setSharingRecords([row]);
    },
    onSave: (row: T) => {
      cfg.callbacks?.onSave?.([row]);
    },
    // Row expansion handlers
    expandedRows,
    isExpanded: (id: string) => expandedRows.has(id),
    onExpand: (id: string) => {
      setExpandedRows((prev) => {
        const next = new Set(prev);
        if (next.has(id)) {
          next.delete(id);
        } else {
          next.add(id);
        }
        return next;
      });
    },
  }), [fieldFactoryContext, data, isSelected, toggleRow, isAllSelected, toggleAll, isIndeterminate, editingCell, expandedRows, cfg.callbacks, setSharingRecords, user]);

  // All columns generated via FieldFactory (DRY - single source of truth!)
  const allColumns = TI.useMemo(
    () => {
      const columns = TI.createTableColumns(allFieldConfigs, extendedFieldContext, columnHelper);
      // Apply custom cell renderers if provided
      if (cfg.customCellRenderers) {
        return columns.map((col) => {
          const columnId = col.id as string;
          const customRenderer = cfg.customCellRenderers?.[columnId];
          
          if (customRenderer) {
            // Override cell renderer with custom one
            return {
              ...col,
              cell: (cellContext: any) => customRenderer(cellContext.row.original),
            };
          }
          
          return col;
        });
      }
      
        return columns;
    },
    [allFieldConfigs, extendedFieldContext, columnHelper, cfg.customCellRenderers]
  );

  // ============================================
  // COLUMN STATE (visibility, order, sizing) - LOCAL ONLY
  // Backend persistence is handled by TableStatePreset system below
  // ============================================
  // Extract defaultVisibility from fields config [isInList, defaultVisibility]
  const defaultVisibility = TI.useMemo(() => {
    if (!cfg.columns.fields) return {};
    const visibility: Record<string, boolean> = {};
    Object.entries(cfg.columns.fields).forEach(([key, [_, defaultVisible]]) => {
      visibility[key] = defaultVisible;
    });
    return visibility;
  }, [cfg.columns.fields]);

  // ============================================
  // SNAPSHOT - Global state management (MUST BE BEFORE useState)
  // ============================================
  // Use first selected factory for snapshot (backward compatibility)
  // Backend automatically applies scope, but snapshot still needs factory for state storage
  const snapshotFactory = selectedFactories.length > 0 ? selectedFactories[0] : null;
  
  // If useMyState is enabled, disable snapshot (mystate handles persistence)
  const shouldDisableSnapshot = processedConfig.disableSnapshot || cfg.useMyState;
  const snapshot: any = shouldDisableSnapshot
    ? {
        snapshot: null,
        getTableState: (_: string) => ({} as any),
        updateTable: (_: string, __: any) => {},
        refresh: async () => {},
      }
    : useSnapshot(snapshotFactory);
  
  // ============================================
  // MYSTATE - New state management (LocalStorage + API presets)
  // ============================================
  // Always call hooks (Rules of Hooks), but only use result if useMyState is enabled
  // Using a stable key to avoid re-creating state on each render
  const myStateHook = useTableState(cfg.storageKey);
  const columnsMyStateHook = useTableColumnsState(cfg.storageKey);
  const filtersMyStateHook = useTableFiltersState(cfg.storageKey);
  
  // Only expose hooks if useMyState is enabled
  const myState = cfg.useMyState ? myStateHook : null;
  const columnsMyState = cfg.useMyState ? columnsMyStateHook : null;
  const filtersMyState = cfg.useMyState ? filtersMyStateHook : null;
  
  // Computed active preset names - prefer myState if available
  const activeColumnsPresetName = columnsMyState?.activePresetName ?? activeColumnsPresetNameLocal;
  const activeFiltersPresetName = filtersMyState?.activePresetName ?? activeFiltersPresetNameLocal;
  
  // ============================================
  // MODIFICATION TRACKING FOR PRESET PANELS
  // ============================================
  // Helper to deep compare filter arrays
  const areFiltersEqual = TI.useCallback((a: any[], b: any[]): boolean => {
    if (!a && !b) return true;
    if (!a || !b) return false;
    if (a.length !== b.length) return false;
    return JSON.stringify(a) === JSON.stringify(b);
  }, []);
  
  // Helper to deep compare column state objects
  const areColumnsEqual = TI.useCallback((current: any, loaded: any): boolean => {
    if (!loaded) return true; // No loaded preset = not modified
    return JSON.stringify({
      columnVisibility: current.columnVisibility,
      columnOrder: current.columnOrder,
      columnSizing: current.columnSizing,
    }) === JSON.stringify({
      columnVisibility: loaded.columnVisibility,
      columnOrder: loaded.columnOrder,
      columnSizing: loaded.columnSizing,
    });
  }, []);
  
  // Local column state
  const [columnVisibility, setColumnVisibility] = TI.useState<Record<string, boolean>>(defaultVisibility);
  const [columnOrder, setColumnOrder] = TI.useState<string[]>(cfg.columns.defaultOrder || []);
  // Start with empty sizing - will be loaded from snapshot in useEffect
  const [columnSizing, setColumnSizing] = TI.useState<Record<string, number>>({});

  // Reset functions
  const resetColumnVisibility = TI.useCallback(() => {
    setColumnVisibility(defaultVisibility);
  }, [defaultVisibility]);

  const resetColumnOrder = TI.useCallback(() => {
    setColumnOrder(cfg.columns.defaultOrder || []);
  }, [cfg.columns.defaultOrder]);

  const resetColumnSizing = TI.useCallback(() => {
    setColumnSizing({});
  }, []);

  // Combine into columnState object for compatibility
  const columnState = TI.useMemo(() => ({
    columnVisibility,
    setColumnVisibility,
    resetColumnVisibility,
    columnOrder,
    setColumnOrder,
    resetColumnOrder,
    columnSizing,
    setColumnSizing,
    resetColumnSizing,
  }), [
    columnVisibility,
    setColumnVisibility,
    resetColumnVisibility,
    columnOrder,
    setColumnOrder,
    resetColumnOrder,
    columnSizing,
    setColumnSizing,
    resetColumnSizing,
  ]);
  
  // ============================================
  // PRESET MODIFICATION DETECTION & HANDLERS
  // ============================================
  
  // Check if filters have been modified from loaded preset
  const isFiltersModified = TI.useMemo(() => {
    if (!filtersMyState?.loadedPresetData || !filtersMyState?.activePresetId) {
      console.log('[MyTable] isFiltersModified: no loadedPresetData or activePresetId', {
        loadedPresetData: filtersMyState?.loadedPresetData,
        activePresetId: filtersMyState?.activePresetId,
      });
      return false;
    }
    const loaded = filtersMyState.loadedPresetData;
    const currentFilters = columnFilters || [];
    const loadedFilters = loaded.columnFilters || [];
    const currentGlobal = globalFilterInput || '';
    const loadedGlobal = loaded.globalFilter || '';
    const filtersEqual = areFiltersEqual(currentFilters, loadedFilters);
    const globalEqual = currentGlobal === loadedGlobal;
    const isModified = !filtersEqual || !globalEqual;
    console.log('[MyTable] isFiltersModified:', isModified, {
      currentFilters,
      loadedFilters,
      filtersEqual,
      currentGlobal,
      loadedGlobal,
      globalEqual,
    });
    return isModified;
  }, [filtersMyState?.loadedPresetData, filtersMyState?.activePresetId, columnFilters, globalFilterInput, areFiltersEqual]);
  
  // Check if columns have been modified from loaded preset
  const isColumnsModified = TI.useMemo(() => {
    if (!columnsMyState?.loadedPresetData || !columnsMyState?.activePresetId) return false;
    const loaded = columnsMyState.loadedPresetData;
    return !areColumnsEqual({
      columnVisibility,
      columnOrder,
      columnSizing,
    }, loaded);
  }, [columnsMyState?.loadedPresetData, columnsMyState?.activePresetId, columnVisibility, columnOrder, columnSizing, areColumnsEqual]);
  
  // Handler to revert filters to loaded preset
  const handleRevertFilters = TI.useCallback(() => {
    if (!filtersMyState) return;
    const revertedData = filtersMyState.revertToLoadedPreset();
    if (revertedData) {
      // Apply reverted data to local state
      setColumnFilters(revertedData.columnFilters || []);
      setGlobalFilterInput(revertedData.globalFilter || '');
    }
  }, [filtersMyState]);
  
  // Handler to save filter modifications to existing preset
  const handleSaveFilterModification = TI.useCallback(async () => {
    if (!filtersMyState) return;
    const filtersState = {
      columnFilters,
      globalFilter: globalFilterInput,
    };
    await filtersMyState.updatePreset(filtersState);
  }, [filtersMyState, columnFilters, globalFilterInput]);
  
  // Handler to revert columns to loaded preset
  const handleRevertColumns = TI.useCallback(() => {
    if (!columnsMyState) return;
    const revertedData = columnsMyState.revertToLoadedPreset();
    if (revertedData) {
      // Apply reverted data to local state
      if (revertedData.columnVisibility) setColumnVisibility(revertedData.columnVisibility);
      if (revertedData.columnOrder) setColumnOrder(revertedData.columnOrder);
      if (revertedData.columnSizing) setColumnSizing(revertedData.columnSizing);
    }
  }, [columnsMyState]);
  
  // Handler to save column modifications to existing preset
  const handleSaveColumnModification = TI.useCallback(async () => {
    if (!columnsMyState) return;
    const columnsState = {
      columnVisibility,
      columnOrder,
      columnSizing,
    };
    await columnsMyState.updatePreset(columnsState);
  }, [columnsMyState, columnVisibility, columnOrder, columnSizing]);

  // ============================================
  // FILTER STATE (for save/load presets)
  // ============================================
  const filterState = processedConfig.disableFilterState
    ? {
        savedFilters: [],
        saveFilter: async () => {},
        deleteFilter: async () => {},
        getDefaultFilterName: (_tableName: string) => "",
        loading: false,
      }
    : TI.useFilterState(`${cfg.storageKey}-filters`);

  // Get table-specific state from snapshot
  
  // Track if initial state has been loaded from snapshot
  const hasLoadedStateRef = TI.useRef(false);
  
  // Track if we're currently loading a preset (to avoid clearing preset names during load)
  const isLoadingPresetRef = TI.useRef(false);
  
  // Load state from snapshot on mount (ONCE - only when snapshot first becomes available)
  // Also reloads when hasLoadedStateRef is reset to false (e.g., after loading a preset)
  TI.useEffect(() => {
    if (!snapshot.snapshot) return;
    if (hasLoadedStateRef.current) return;
    
    const state = snapshot.getTableState(cfg.storageKey);
    
    // Only load if there is actually state to load
    const hasState = state && Object.keys(state).length > 0;
    if (!hasState) {
      hasLoadedStateRef.current = true;
      return;
    }
    
    // Apply column state
    if (state.visibility) {
      columnState.setColumnVisibility(state.visibility);
    }
    if (state.order) {
      columnState.setColumnOrder(state.order);
    }
    // Load sizing from snapshot
    if (state.sizing) {
      const filteredSizing: Record<string, number> = {};
      Object.entries(state.sizing).forEach(([key, value]) => {
        if (typeof value === 'number') {
          filteredSizing[key] = value;
        } else if (typeof value === 'object' && value && 'size' in value) {
          filteredSizing[key] = (value as any).size;
        }
      });
      columnState.setColumnSizing(filteredSizing);
    }
    
    // Apply filter state
    if (state.columnFilters) {
      setColumnFilters(state.columnFilters);
    }
    if (state.globalFilter) {
      setGlobalFilterInput(state.globalFilter);
    }
    
    // Apply sorting - validate and use default if null/invalid
    if (state.sorting && state.sorting.length > 0 && state.sorting[0]?.id) {
      // Valid sorting exists - use it
      setSorting(state.sorting);
    } else {
      // Invalid/null sorting - load default from metadata (VIEWS_MATRIX SSOT)
      const defaultOrdering = getDefaultOrdering(cfg.storageKey);
      if (defaultOrdering && defaultOrdering.length > 0) {
        // Convert backend default_ordering format ["-created"] to frontend sorting format [{id: 'created', desc: true}]
        const defaultSort = defaultOrdering[0];
        const fieldName = defaultSort.replace(/^-/, ''); // Remove leading minus
        const desc = defaultSort.startsWith('-');
        const defaultSorting = [{ id: fieldName, desc }];
        
        // Set local state
        setSorting(defaultSorting);
        
        // Selektívne aktualizovať len sorting v tejto tabuľke (puzzle approach)
        snapshot.updateTable(cfg.storageKey, { sorting: defaultSorting });
      }
    }
    
    // Apply pagination - use local setters (table not initialized yet)
    if (state.pagination) {
      const nextPageSize = typeof state.pagination.pageSize === 'number' ? state.pagination.pageSize : (cfg.pagination.defaultPageSize || 10);
      const nextPageIndex = typeof state.pagination.pageIndex === 'number' ? state.pagination.pageIndex : 0;
      setPageSize(nextPageSize);
      setPageIndex(nextPageIndex);
    }
    
    // Apply row selection
    if (state.rowSelection) {
      setSelectedRows(new Set(Object.keys(state.rowSelection).filter(key => state.rowSelection![key])));
    }
    
    // Mark as loaded
    hasLoadedStateRef.current = true;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [snapshot.snapshot, hasLoadedStateRef.current]); // Re-run when snapshot changes OR hasLoadedStateRef is reset
  
  // Track previous state values to detect actual user changes (not just useEffect re-runs)
  const prevStateRef = TI.useRef<{
    visibility?: Record<string, boolean>;
    order?: string[];
    sizing?: Record<string, number>;
    columnFilters?: TI.ColumnFiltersState;
    globalFilter?: string;
    sorting?: TI.SortingState;
    pageSize?: number;
    pageIndex?: number;
  }>({});
  
  // Sync table changes to snapshot (real-time with debouncing)
  // Only sync AFTER initial state has been loaded to avoid overwriting
  TI.useEffect(() => {
    if (!hasLoadedStateRef.current) return; // Don't sync until after initial load
    
    // Check if state actually changed (not just useEffect re-run)
    const prevState = prevStateRef.current;
    const visibilityChanged = JSON.stringify(columnState.columnVisibility) !== JSON.stringify(prevState.visibility);
    const orderChanged = JSON.stringify(columnState.columnOrder) !== JSON.stringify(prevState.order);
    const sizingChanged = JSON.stringify(columnState.columnSizing) !== JSON.stringify(prevState.sizing);
    const filtersChanged = JSON.stringify(columnFilters) !== JSON.stringify(prevState.columnFilters);
    const globalFilterChanged = globalFilterInput !== prevState.globalFilter;
    const sortingChanged = JSON.stringify(sorting) !== JSON.stringify(prevState.sorting);
    const pageSizeChanged = pageSize !== prevState.pageSize;
    const pageIndexChanged = pageIndex !== prevState.pageIndex;
    
    const stateChanged = visibilityChanged || orderChanged || sizingChanged || filtersChanged || 
                         globalFilterChanged || sortingChanged || pageSizeChanged || pageIndexChanged;
    
    // Clear active preset names ONLY when state actually changes AND we're not loading a preset
    if (stateChanged && Object.keys(prevState).length > 0 && !isLoadingPresetRef.current) {
      // Clear columns preset if columns-related state changed
      if (visibilityChanged || orderChanged || sizingChanged) {
        if (columnsMyState) {
          columnsMyState.setActivePresetName(null);
        } else {
          setActiveColumnsPresetNameLocal(null);
        }
      }
      // Clear filters preset if filters-related state changed
      if (filtersChanged || globalFilterChanged) {
        if (filtersMyState) {
          filtersMyState.setActivePresetName(null);
        } else {
          setActiveFiltersPresetNameLocal(null);
        }
      }
    }
    
    if (!stateChanged) {
      return;
    }

    // Update previous state ref
    prevStateRef.current = {
      visibility: columnState.columnVisibility,
      order: columnState.columnOrder,
      sizing: columnState.columnSizing,
      columnFilters,
      globalFilter: globalFilterInput,
      sorting,
      pageSize,
      pageIndex,
    };
    
    // Convert Set<string> to Record<string, boolean> for snapshot
    const rowSelectionRecord: Record<string, boolean> = {};
    selectedRows.forEach(id => {
      rowSelectionRecord[id] = true;
    });
    
    // Filter sizing to only include size values, not minSize/maxSize
    // (minSize/maxSize are config constants, not user state)
    const filteredSizing: Record<string, number> = {};
    Object.entries(columnState.columnSizing).forEach(([key, value]) => {
      if (typeof value === 'number') {
        filteredSizing[key] = value;
      } else if (typeof value === 'object' && value && 'size' in value) {
        filteredSizing[key] = (value as any).size;
      }
    });
    
    snapshot.updateTable(cfg.storageKey, {
      visibility: columnState.columnVisibility,
      order: columnState.columnOrder,
      sizing: filteredSizing,
      columnFilters,
      globalFilter: globalFilterInput,
      sorting,
      pagination: {
        pageSize,
        pageIndex
      },
      rowSelection: rowSelectionRecord
    });
  }, [
    columnState.columnVisibility,
    columnState.columnOrder,
    columnState.columnSizing,
    columnFilters,
    globalFilterInput,
    sorting,
    pageSize,
    pageIndex,
    selectedRows,
    snapshot.updateTable,  // Stable function reference
    cfg.storageKey
  ]);
  
  // ============================================
  // MYSTATE - Load initial state from LocalStorage (if useMyState enabled)
  // ============================================
  const hasLoadedMyStateRef = TI.useRef(false);
  
  TI.useEffect(() => {
    if (!cfg.useMyState || !myState) return;
    if (hasLoadedMyStateRef.current) return;
    
    const state = myState.state;
    if (!state || Object.keys(state).length === 0) {
      hasLoadedMyStateRef.current = true;
      return;
    }
    
    // Apply state from myState
    if (state.sorting && state.sorting.length > 0) {
      setSorting(state.sorting);
    }
    if (state.columnFilters) {
      setColumnFilters(state.columnFilters);
    }
    if (state.pagination) {
      if (typeof state.pagination.pageSize === 'number') {
        setPageSize(state.pagination.pageSize);
      }
      if (typeof state.pagination.pageIndex === 'number') {
        setPageIndex(state.pagination.pageIndex);
      }
    }
    if (state.columnVisibility) {
      columnState.setColumnVisibility(state.columnVisibility);
    }
    if (state.columnOrder) {
      columnState.setColumnOrder(state.columnOrder);
    }
    if (state.columnSizing) {
      columnState.setColumnSizing(state.columnSizing);
    }
    if (state.globalFilter) {
      setGlobalFilterInput(state.globalFilter);
    }
    
    hasLoadedMyStateRef.current = true;
  }, [cfg.useMyState, myState?.state]);
  
  // ============================================
  // MYSTATE - Sync state changes to LocalStorage (if useMyState enabled)
  // ============================================
  const prevMyStateRef = TI.useRef<any>({});
  
  TI.useEffect(() => {
    if (!cfg.useMyState || !myState) return;
    if (!hasLoadedMyStateRef.current) return;
    
    // Build current state
    const currentState = {
      sorting,
      columnFilters,
      pagination: { pageSize, pageIndex },
      columnVisibility: columnState.columnVisibility,
      columnOrder: columnState.columnOrder,
      columnSizing: columnState.columnSizing,
      globalFilter: globalFilterInput,
    };
    
    // Check if state changed
    const prevState = prevMyStateRef.current;
    const stateChanged = JSON.stringify(currentState) !== JSON.stringify(prevState);
    
    if (!stateChanged) return;
    
    // Update ref
    prevMyStateRef.current = currentState;
    
    // Sync to myState (debounced via context)
    myState.updateState(currentState);
  }, [
    cfg.useMyState,
    myState,
    sorting,
    columnFilters,
    pageSize,
    pageIndex,
    columnState.columnVisibility,
    columnState.columnOrder,
    columnState.columnSizing,
    globalFilterInput,
  ]);
  
  // ============================================
  // INITIALIZATION & MODEL METADATA
  // ============================================
  // Load model metadata on component mount (needed for FK endpoint resolution)
  const [metadataLoaded, setMetadataLoaded] = TI.useState(false);
  
  TI.useEffect(() => {
    loadModelMetadata()
      .then(() => setMetadataLoaded(true))
      .catch(err => {
        console.error('Failed to load model metadata in MyTable:', err);
        setMetadataLoaded(true); // Continue even if metadata fails
      });
  }, []);
  
  // ============================================
  // FK OPTIONS MANAGEMENT (scope-aware)
  // ============================================
  // Map field key -> endpoint name (e.g., 'factory' -> 'factories', 'location' -> 'locations')
  const fkEndpointMap = TI.useMemo(() => {
    // Wait for metadata to load before creating endpoint map
    if (!metadataLoaded) return {};
    
    if (!cfg.fieldsMatrix) return {};
    const map: Record<string, string> = {};
    
    Object.entries(cfg.fieldsMatrix).forEach(([key, item]) => {
      if (item.type === 'fk') {
        // Priority:
        // 1. Explicit apiEndpoint (full path like '/api/factories')
        //    - If empty string (''), skip this FK field (no endpoint available)
        // 2. Explicit pluralName (construct as '/api/{pluralName}')
        // 3. Auto-detect from model metadata (loaded from /api/models/metadata/)
        // 4. Fallback: Standard pluralization (construct as '/api/{key}s')
        if (item.apiEndpoint !== undefined) {
          // Explicit endpoint specified (could be empty string to disable)
          if (item.apiEndpoint !== '') {
            map[key] = item.apiEndpoint;
          }
          // else: empty string = skip this FK field
        } else if (item.pluralName) {
          map[key] = `/api/${item.pluralName}`;
        } else {
          // Try to get from model metadata (loaded from backend)
          const metadataEndpoint = getModelEndpoint(key);
          if (metadataEndpoint) {
            map[key] = metadataEndpoint;
          } else {
            // Fallback: standard pluralization
          map[key] = `/api/${key}s`;
          }
        }
      }
    });
    return map;
  }, [cfg.fieldsMatrix, metadataLoaded]);

  /**
   * Load FK options from backend cache (FAST!)
   * Uses /api/fk-options-cache/ endpoint for pre-computed options
   */
  const loadFkOptions = TI.useCallback(async () => {
    if (!cfg.fieldsMatrix) return;

    // Get all FK fields that need options
    const fkFields = Object.entries(cfg.fieldsMatrix)
      .filter(([_, item]) => item.type === 'fk' && item.isInFilterPanel);

    if (fkFields.length === 0) return;

    // Backend automatically applies scope - no need to separate scoped/global fields
    // All FK fields are automatically scoped by backend based on ownership_hierarchy from VIEWS_MATRIX
    const newOptions: Record<string, Option[]> = {};

    // Load all FK options - backend automatically applies scope
    // Backend determines which fields are scoped based on ownership_hierarchy
    // Frontend just loads options - backend handles all scoping logic
    for (const [fieldKey] of fkFields) {
      try {
        const { loadFKOptionsFromCache } = await import('../../services/fkCacheService');
        // Backend automatically applies scope - no need to pass factoryIds
        const options = await loadFKOptionsFromCache(fieldKey, []);
        
        // Convert to Option format - preserve all fields (code, name, human_id, etc.) for template support
        const formattedOptions: Option[] = options.map(opt => ({
          id: opt.id,
          label: opt.label,
          // Preserve individual fields for template string support (SSOT from Camera.tsx)
          ...(opt.code !== undefined && { code: opt.code }),
          ...(opt.name !== undefined && { name: opt.name }),
          ...(opt.human_id !== undefined && { human_id: opt.human_id }),
          // Preserve any other fields that might be in the option
          ...Object.keys(opt).reduce((acc, key) => {
            if (key !== 'id' && key !== 'label' && opt[key] !== undefined) {
              acc[key] = opt[key];
            }
            return acc;
          }, {} as Record<string, any>)
        }));
        
        newOptions[fieldKey] = formattedOptions.sort((a, b) => a.label.localeCompare(b.label));
      } catch (error: any) {
        console.warn(`Failed to load global ${fieldKey} from cache:`, error);
        newOptions[fieldKey] = [];
      }
    }

    setFkOptions(newOptions);
  }, [cfg.fieldsMatrix, selectedFactories, fkEndpointMap]);

  // Load FK options when selectedFactories or fieldsMatrix changes
  TI.useEffect(() => {
    loadFkOptions();
  }, [loadFkOptions]);

  // ============================================
  // CLIENT-SIDE FILTERING FOR "SHOW ONLY SELECTED"
  // ============================================
  const displayData = TI.useMemo(() => {
    if (!showOnlySelected) return data;
    if (selectedRows.size === 0) return data;
    
    const selectedIds = Array.from(selectedRows);
    return data.filter(row => selectedIds.includes(String(row.id)));
  }, [data, showOnlySelected, selectedRows]);

  const safePageSize = pageSize || cfg.pagination.defaultPageSize || 10;
  const safePageIndex = typeof pageIndex === 'number' ? pageIndex : 0;

  // ============================================
  // TANSTACK TABLE
  // ============================================
  const manualPagination = !(cfg.pagination?.custom === true);

  const table = TI.useReactTable({
    data: displayData,
    columns: allColumns,
    state: {
      globalFilter,
      columnVisibility: columnState.columnVisibility,
      columnOrder: columnState.columnOrder,
      columnSizing: columnState.columnSizing,
      columnFilters,
      sorting,
      pagination: { pageIndex: safePageIndex, pageSize: safePageSize },
      rowSelection: rowSelectionState,
    },
    onGlobalFilterChange: setGlobalFilter,
    onColumnVisibilityChange: columnState.setColumnVisibility,
    onColumnOrderChange: columnState.setColumnOrder,
    onColumnSizingChange: (updater) => {
      // Validate minSize/maxSize constraints
      const newSizing = typeof updater === 'function' 
        ? updater(columnState.columnSizing) 
        : updater;
      
      // Apply constraints from fieldsMatrix
      const validatedSizing: Record<string, number> = {};
      Object.entries(newSizing).forEach(([key, value]) => {
        const fieldConfig = cfg.fieldsMatrix[key];
        if (fieldConfig) {
          const minSize = fieldConfig.minSize ?? 50;
          const maxSize = fieldConfig.maxSize ?? 1000;
          const constrainedValue = Math.max(minSize, Math.min(maxSize, value));
          
          validatedSizing[key] = constrainedValue;
        } else {
          validatedSizing[key] = value;
        }
      });
      
      columnState.setColumnSizing(validatedSizing);
    },
    onColumnFiltersChange: setColumnFilters,
    onSortingChange: setSorting,
    onPaginationChange: (updater) => {
      if (typeof updater === 'function') {
        const next = updater({ pageIndex, pageSize });
        setPageIndex(next.pageIndex);
        setPageSize(next.pageSize);
      }
    },
    getCoreRowModel: TI.getCoreRowModel(),
    // CRITICAL: When advancedSearch is enabled, use getCoreRowModel() instead of getFilteredRowModel()
    // to prevent client-side filtering that would break advanced search logic
    // When manualFiltering: true, TanStack Table should NOT filter locally, but getFilteredRowModel()
    // with globalFilterFn can still apply client-side filtering
    getFilteredRowModel: isAdvancedSearch
      ? TI.getCoreRowModel()  // Use core model (no filtering) for advanced search
      : TI.getFilteredRowModel(),  // Use filtered model for simple search
    getSortedRowModel: TI.getSortedRowModel(),
    getPaginationRowModel: TI.getPaginationRowModel(),
    // SERVER-SIDE MODE
    manualPagination,
    manualSorting: true,
    manualFiltering: true,
    pageCount: manualPagination ? Math.max(1, Math.ceil(total / safePageSize) || 1) : undefined,
    columnResizeMode: 'onChange',
    enableColumnResizing: true,
    defaultColumn: {
      size: 120,
      minSize: 50,
      maxSize: 1000,
    },
    getRowId: (row) => String(row.id),
    enableRowSelection: cfg.rowSelection.enabled,
    enableMultiRowSelection: cfg.rowSelection.mode === 'multiple',
    // CRITICAL: When advancedSearch is enabled, disable client-side filtering
    // Advanced search (AND/OR/NOT/parentheses) must be handled server-side only
    // Client-side 'includesString' filter would break advanced search logic
    globalFilterFn: isAdvancedSearch 
      ? undefined  // Disable client-side filtering for advanced search
      : (cfg.customGlobalFilterFn || 'includesString'),  // Use custom or default for simple search
    filterFns: cfg.customFilterFns,
  });

  TI.useEffect(() => {
    tableRef.current = table;
  }, [table]);

  // ============================================
  // ============================================
  // DEBOUNCED SEARCH
  // ============================================
  TI.useEffect(() => {
    setGlobalFilter(debouncedFilter);
  }, [debouncedFilter]);

  // ============================================
  // ESCAPE KEY
  // ============================================
  TI.useEscapeKey(() => {
    if (editingCell) {
      setEditingCell(null);
    } else if (showFilters) {
      setShowFilters(false);
    } else if (showColumns) {
      setShowColumns(false);
    }
  });

  // ============================================
  // HANDLERS
  // ============================================
  const handleReset = TI.useCallback(() => {
    setGlobalFilter('');
    setGlobalFilterInput('');
    setColumnFilters([]);
    setSorting([]);
    columnState.resetColumnVisibility();
    columnState.resetColumnOrder();
    columnState.resetColumnSizing();
    clearSelection();
    setShowOnlySelected(false);
  }, [filterState, columnState, clearSelection]);

  const handleDelete = TI.useCallback(async () => {
    if (deletingRecords.length === 0) return;

    try {
      const ids = deletingRecords.map((r) => r.id);
      
      // Generic DELETE implementation: call API for each record
      // Uses authenticated api.delete() to include CSRF token
      await Promise.all(
        deletingRecords.map((record) => 
          api.delete(`${cfg.apiEndpoint}${record.id}/`)
        )
      );
      
      // Call optional callback (for custom logic)
      cfg.callbacks?.onDelete?.(deletingRecords);

      // Refetch data to get updated list and total count
      await refetch();

      // Close modal & clear selection
      setDeletingRecords([]);
      clearSelection();

      TI.toastMessages.recordDeleted(ids.length);
    } catch (err: any) {
      showError({
        operation: 'delete',
        title: 'Delete Failed',
        message: err.message || 'Failed to delete records',
      });
    }
  }, [deletingRecords, clearSelection, cfg.callbacks, cfg.apiEndpoint, api, showError, refetch]);

  const handleExportCSV = TI.useCallback(() => {
    cfg.callbacks?.onExportCSV?.();
  }, [cfg.callbacks]);

  const handleExportXLSX = TI.useCallback(() => {
    cfg.callbacks?.onExportXLSX?.();
  }, [cfg.callbacks]);

  const handleSelectedCountClick = TI.useCallback(() => {
    // Show only selected records:
    // 1. Get selected row IDs (selectedRows is a Set!)
    const selectedIds = Array.from(selectedRows);
    
    // 2. If no rows selected, do nothing
    if (selectedIds.length === 0) {
      return;
    }
    
    // 3. Enable "show only selected" mode
    setShowOnlySelected(true);
    
    // 4. Clear all server-side filters
    setColumnFilters([]);
    setGlobalFilterInput('');
    
    // 5. Reset pagination to first page
    setPageIndex(0);
    
    // 6. Close filter panel if open
    setShowFilters(false);
    
    // 7. Show toast notification
    TI.toastMessages.showingSelectedRecords(selectedIds.length);
  }, [selectedRows, setColumnFilters, setGlobalFilterInput, setPageIndex, setShowFilters]);

  // ============================================
  // STATE PRESET HANDLERS
  // ============================================
  
  // Load saved presets list (legacy API - used when useMyState is false)
  const [savedPresets, setSavedPresets] = TI.useState<any[]>([]);
  const loadSavedPresets = TI.useCallback(async () => {
    // If useMyState is enabled, use myState.savedStates instead
    if (cfg.useMyState && myState) {
      return; // myState handles its own state loading
    }
    
    try {
      const params = new URLSearchParams({
        table_name: cfg.storageKey,
        component: statePresetComponent,
      });
      const response = await api.get(`/api/table-state-presets/?${params.toString()}`);
      const results = response.results || response || [];
      setSavedPresets(Array.isArray(results) ? results : []);
    } catch (err) {
      console.error('Failed to load presets:', err);
    } finally {
    }
  }, [cfg.storageKey, statePresetComponent, api, cfg.useMyState, myState]);
  
  // Load presets when modal opens OR when component type changes
  // This ensures correct component filtering (columns vs filters)
  TI.useEffect(() => {
    if (showLoadStateModal && !cfg.useMyState) {
      loadSavedPresets();
    }
  }, [showLoadStateModal, statePresetComponent, loadSavedPresets, cfg.useMyState]);
  
  // Get presets list - either from myState or legacy API
  const presetsForModal = TI.useMemo(() => {
    if (cfg.useMyState && myState) {
      // Convert myState savedStates to format expected by LoadStateModal
      const states = Array.isArray(myState.savedStates) ? myState.savedStates : [];
      return states.map(preset => ({
        id: preset.id,
        preset_name: preset.preset_name,
        description: preset.description,
        component: statePresetComponent, // myState stores full state, not component-specific
        created: preset.created,
        is_default: preset.is_default,
        // Mark as mystate preset for handler
        _isMyState: true,
      }));
    }
    return savedPresets;
  }, [cfg.useMyState, myState?.savedStates, savedPresets, statePresetComponent]);
  
  const handleSaveState = TI.useCallback(async (name: string, description?: string) => {
    // If useMyState is enabled, use myState.savePreset
    if (cfg.useMyState && myState) {
      // Let the error bubble up to SaveStateModal for display
      // Modal closes itself on success, shows error on failure
      await myState.savePreset(name, description);
      // Update active preset name based on component
      if (statePresetComponent === 'columns') {
        if (columnsMyState) {
          columnsMyState.setActivePresetName(name);
        } else {
          setActiveColumnsPresetNameLocal(name);
        }
      } else if (statePresetComponent === 'filters') {
        if (filtersMyState) {
          filtersMyState.setActivePresetName(name);
        } else {
          setActiveFiltersPresetNameLocal(name);
        }
      }
      return;
    }
    
    // Legacy: use old table-state-presets API
    try {
      // Extract current table state from snapshot
      const currentTableState = snapshot.getTableState(cfg.storageKey);
      
      // Extract only the relevant part based on component
      let stateToSave: any = {};
      if (statePresetComponent === 'columns') {
        stateToSave = {
          visibility: currentTableState.visibility,
          order: currentTableState.order,
          sizing: currentTableState.sizing
        };
      } else if (statePresetComponent === 'filters') {
        stateToSave = {
          columnFilters: currentTableState.columnFilters,
          globalFilter: currentTableState.globalFilter
        };
      }
      
      // Save preset to backend (with factory from active scope)
      // Backend automatically applies scope, but preset storage still needs factory ID
      await api.post('/api/table-state-presets/', {
        table_name: cfg.storageKey,
        component: statePresetComponent,
        preset_name: name,
        description: description || '',
        state: stateToSave,
        factory: snapshotFactory  // Use snapshot factory (first selected factory)
      });
      
      TI.toastMessages.presetSaved(name);
      setShowSaveStateModal(false);
      loadSavedPresets(); // Refresh list
    } catch (err: any) {
      TI.toastMessages.presetSaveFailed(err.response?.data?.error);
    }
  }, [cfg.useMyState, myState, snapshot, cfg.storageKey, statePresetComponent, api, snapshotFactory, loadSavedPresets]);
  
  const handleLoadState = TI.useCallback(async (preset: any) => {
    // If useMyState is enabled, use myState.loadPreset
    if (cfg.useMyState && myState && preset._isMyState) {
      myState.loadPreset(preset);
      setShowLoadStateModal(false);
      // Set active preset name (legacy mode sets both, new mode should use component-specific)
      if (columnsMyState) {
        columnsMyState.setActivePresetName(preset.preset_name);
      } else {
        setActiveColumnsPresetNameLocal(preset.preset_name);
      }
      if (filtersMyState) {
        filtersMyState.setActivePresetName(preset.preset_name);
      } else {
        setActiveFiltersPresetNameLocal(preset.preset_name);
      }
      return;
    }
    
    // Legacy: use old table-state-presets API
    try {
      // Set flag to prevent clearing preset names during load
      isLoadingPresetRef.current = true;
      
      // Call recall endpoint - backend will merge into snapshot
      await api.post(`/api/table-state-presets/${preset.id}/recall/`);
      
      // Refresh snapshot from server to get updated state
      await snapshot.refresh();
      
      // Reset the hasLoadedStateRef flag so the useEffect can reload state from snapshot
      // This is necessary because the useEffect only runs once on mount by design
      hasLoadedStateRef.current = false;
      
      // Set active preset name AFTER state is applied (defer to avoid being cleared by sync useEffect)
      // Wait for React to process state updates and useEffect to run
      setTimeout(() => {
        if (preset.component === 'columns') {
          setActiveColumnsPresetNameLocal(preset.preset_name);
        } else if (preset.component === 'filters') {
          setActiveFiltersPresetNameLocal(preset.preset_name);
        }
        // Clear flag after preset name is set
        isLoadingPresetRef.current = false;
      }, 100); // Small delay to ensure state is applied first
      
      setShowLoadStateModal(false);
      TI.toastMessages.presetLoaded(preset.preset_name);
    } catch (err: any) {
      // Clear flag on error
      isLoadingPresetRef.current = false;
      TI.toastMessages.presetLoadFailed(err.response?.data?.error);
    }
  }, [cfg.useMyState, myState, api, snapshot]);
  
  const handleDeletePreset = TI.useCallback(async (presetId: string | number) => {
    // If useMyState is enabled, use myState.deletePreset
    if (cfg.useMyState && myState) {
      try {
        await myState.deletePreset(String(presetId));
        // Refresh is handled by deletePreset
      } catch (err: any) {
        // Error toast is handled by deletePreset
      }
      return;
    }
    
    // Legacy: use old table-state-presets API
    try {
      await api.delete(`/api/table-state-presets/${presetId}/`);
      TI.toastMessages.presetDeleted();
      loadSavedPresets(); // Refresh list
    } catch (err: any) {
      TI.toastMessages.presetDeleteFailed();
    }
  }, [cfg.useMyState, myState, api, loadSavedPresets]);

  // ============================================
  // PAGINATION
  // ============================================
  const visibleCount = data.length; // Current page visible rows
  const totalCount = total; // Total count from server

  // ============================================
  // FILTER RENDERING (from fieldsMatrix)
  // ============================================
  /**
   * Render filter components from fieldsMatrix
   * 
   * Logika: FilterPanel zobrazuje len filtre pre polia, ktoré sú VIDITEĽNÉ v stĺpcoch.
   * ColumnsPanel má master pozíciu - ak je pole viditeľné v stĺpcoch, malo by byť dostupné aj na filtrovanie.
   */
  const renderFiltersFromMatrix = TI.useCallback(() => {
    // Ak nie je fieldsMatrix, vráť prázdny fragment
    if (!cfg.fieldsMatrix) {
      return null;
    }

    // Získaj viditeľné stĺpce (len tie, ktoré sú aktuálne zobrazené v tabuľke)
    const visibleColumns = table.getVisibleLeafColumns();
    const visibleColumnIds = new Set(visibleColumns.map(col => col.id));

    // Filtruj polia z fieldsMatrix:
    // 1. Musia byť viditeľné v stĺpcoch (v visibleColumnIds)
    // 2. Musia mať isInFilterPanel: true
    const filterableFields = Object.entries(cfg.fieldsMatrix)
      .filter(([key, item]) => {
        // Skip actions column (nie je data field)
        if (key === 'actions') return false;
        // Musí byť viditeľný v stĺpcoch
        if (!visibleColumnIds.has(key)) return false;
        // Musí mať isInFilterPanel: true
        return item.isInFilterPanel === true;
      })
      .sort((a, b) => {
        // Zoraď podľa order (rovnaké poradie ako v stĺpcoch)
        const orderA = a[1].order ?? 999;
        const orderB = b[1].order ?? 999;
        return orderA - orderB;
      });

    // Check if select column is visible and should be in filter panel
    const hasSelectColumn = visibleColumnIds.has('select') && cfg.rowSelection?.enabled;
    
    // If no filterable fields and no select column, return null
    if (filterableFields.length === 0 && !hasSelectColumn) {
      return null;
    }

    // Build all filters including select if present
    const allFilters: JSX.Element[] = [];
    
    // Add select filter first if present
    if (hasSelectColumn) {
      const selectedIds = Array.from(selectedRows);
      const hasSelection = selectedIds.length > 0;
      
      allFilters.push(
        <div key="select-filter" className="flex flex-col gap-2 border rounded-md p-3 bg-card">
          <div className="flex items-center justify-between gap-2">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={showOnlySelected && hasSelection}
                disabled={!hasSelection}
                onChange={() => {
                  if (hasSelection) {
                    if (showOnlySelected) {
                      // Turn off: clear the filter
                      setShowOnlySelected(false);
                      TI.toastMessages.showingAllRecords();
                    } else {
                      // Turn on: show only selected
                      handleSelectedCountClick();
                    }
                  }
                }}
                className="h-4 w-4 cursor-pointer disabled:cursor-not-allowed"
              />
              <span className="text-sm font-medium">Show only selected</span>
            </label>
            <span className="text-xs text-muted-foreground">
              {selectedIds.length} selected
            </span>
          </div>
        </div>
      );
    }
    
    // Add regular field filters
    filterableFields.forEach(([key, item]) => {
      const column = table.getColumn(key);
      if (!column) return;

      // Podľa filterType vyber správny komponent
      switch (item.filterType) {
        case 'text':
          allFilters.push(
            <TI.FilterInput
              key={key}
              label={item.header}
              type="text"
              table={table}
              columnId={key}
              placeholder={item.placeholder || `Search ${item.header.toLowerCase()}...`}
            />
          );
          break;

        case 'range':
          allFilters.push(
            <TI.FilterInput
              key={key}
              label={item.header}
              type="range"
              table={table}
              columnId={key}
              min={item.min}
              max={item.max}
            />
          );
          break;

        case 'daterange':
          allFilters.push(
            <TI.FilterDateRange
              key={key}
              label={item.header}
              table={table}
              columnId={key}
            />
          );
          break;

        case 'multiselect':
          // Pre FK fields (type: 'fk') - použij FilterCheckboxGroup
          // Pre select fields (type: 'select') - použij FilterButtonGroup
          if (item.type === 'fk') {
            // Get options from loaded FK options (scoped by selectedFactories)
            const fkFieldOptions = fkOptions[key] || [];
            
            // If no options loaded yet, show loading state
            if (fkFieldOptions.length === 0 && selectedFactories.length > 0) {
              allFilters.push(
                <div key={key} className="flex flex-col gap-2 border rounded-md p-3 bg-card">
                  <div className="text-sm font-medium">{item.header}</div>
                  <div className="text-sm text-muted-foreground">Loading...</div>
                </div>
              );
              break;
            }
            
            // Convert to FilterCheckboxGroup format
            const checkboxOptions = fkFieldOptions.map(opt => ({
              id: opt.id,
              label: opt.label,
            }));
            
            allFilters.push(
              <TI.FilterCheckboxGroup
                key={key}
                label={item.header}
                options={checkboxOptions}
                selectedIds={(column.getFilterValue() as string[]) || []}
                onChange={(selectedIds) => column.setFilterValue(selectedIds.length ? selectedIds : undefined)}
              />
            );
          } else if (item.type === 'select' && item.options) {
            // Pre select fields s options
            allFilters.push(
              <TI.FilterButtonGroup
                key={key}
                label={item.header}
                options={item.options}
                selectedValues={(column.getFilterValue() as string[]) || []}
                onChange={(selectedValues) => column.setFilterValue(selectedValues.length ? selectedValues : undefined)}
              />
            );
          }
          break;

        case 'select':
          // Single select - použij FilterButtonGroup
          if (item.options) {
            allFilters.push(
              <TI.FilterButtonGroup
                key={key}
                label={item.header}
                options={item.options}
                selectedValues={(column.getFilterValue() as string[]) || []}
                onChange={(selectedValues) => column.setFilterValue(selectedValues.length ? selectedValues : undefined)}
              />
            );
          }
          break;

        case 'boolean':
          // Boolean filter - použij FilterButtonGroup s true/false možnosťami
          const trueLabel = (item as any).trueLabel || 'True';
          const falseLabel = (item as any).falseLabel || 'False';
          const booleanOptions = [
            { value: 'true', label: trueLabel },
            { value: 'false', label: falseLabel },
          ];
          allFilters.push(
            <TI.FilterButtonGroup
              key={key}
              label={item.header}
              options={booleanOptions}
              selectedValues={(column.getFilterValue() as string[]) || []}
              onChange={(selectedValues) => column.setFilterValue(selectedValues.length ? selectedValues : undefined)}
            />
          );
          break;

        default:
          // Default: text filter
          allFilters.push(
            <TI.FilterInput
              key={key}
              label={item.header}
              type="text"
              table={table}
              columnId={key}
              placeholder={item.placeholder || `Search ${item.header.toLowerCase()}...`}
            />
          );
      }
    });

    // Group filters into rows (4 filters per row)
    const rows: JSX.Element[][] = [];
    for (let i = 0; i < allFilters.length; i += 4) {
      rows.push(allFilters.slice(i, i + 4));
    }

    return (
      <>
        {rows.map((row, rowIndex) => (
          <TI.FilterRow key={rowIndex} cols={row.length as 2 | 3 | 4}>
            {row}
          </TI.FilterRow>
        ))}
      </>
    );
  }, [cfg.fieldsMatrix, cfg.rowSelection, table, selectedRows, handleSelectedCountClick, fkOptions, selectedFactories, showOnlySelected]);

  // ============================================
  // RENDER
  // ============================================
  if (fetchError) {
    return (
      <div className="bg-background flex items-center justify-center py-10 px-4">
        <div className="text-center space-y-4">
          <h2 className="text-xl font-semibold text-destructive">Error Loading Data</h2>
          <p className="text-muted-foreground">{fetchError}</p>
          <TI.Button onClick={refetch}>Retry</TI.Button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-[1400px] mx-auto px-4 py-6 space-y-4">
      {/* PAGE HEADER */}
      {cfg.pageHeader.visible && <PageHeader />}

      {/* MAIN CONTAINER */}
      <div className="max-w-full">
      <TI.TableCard className="w-full">
          {/* TABLE HEADER */}
          <TI.TableHeader
            title={cfg.tableName}
            selectedCount={visibleSelectedCount}
            visibleCount={visibleCount}
            totalCount={totalCount}
            pageIndex={table.getState().pagination.pageIndex}
            pageSize={table.getState().pagination.pageSize}
            pageSizeOptions={cfg.pagination.pageSizeOptions}
            onPageChange={(page) => table.setPageIndex(page)}
            onPageSizeChange={(size) => table.setPageSize(size)}
            canPreviousPage={table.getCanPreviousPage()}
            canNextPage={table.getCanNextPage()}
            onSelectedCountClick={handleSelectedCountClick}
          >
            {/* Search on left, Toolbar on right */}
            <div className="flex items-center justify-between gap-3 flex-wrap w-full">
              {/* Search field - left side */}
              {cfg.headerVisibility.search && cfg.globalSearch.enabled && (
                <div className="flex items-center gap-2 flex-shrink-0">
                  <TI.TableSearch
                    value={globalFilterInput}
                    onChange={setGlobalFilterInput}
                    placeholder={searchPlaceholder}
                  />
                  {cfg.globalSearch.allowModeToggle !== false && (
                    <TI.Button
                      size="sm"
                      variant={isAdvancedSearch ? 'default' : 'ghost'}
                      onClick={() => setSearchMode(isAdvancedSearch ? 'simple' : 'advanced')}
                    >
                      {isAdvancedSearch ? 'Pokročilé' : 'Jednoduché'}
                    </TI.Button>
                  )}
                  {cfg.globalSearch.allowApprox !== false && (
                    <TI.Button
                      size="sm"
                      variant={approximateSearch ? 'default' : 'ghost'}
                      onClick={() => setApproximateSearch(!approximateSearch)}
                    >
                      {approximateSearch ? 'Fuzzy ON' : 'Fuzzy OFF'}
                    </TI.Button>
                  )}
                </div>
              )}

              {/* Toolbar buttons - right side */}
              {cfg.headerVisibility.toolbar && (
                <div className="flex items-center gap-3 flex-wrap ml-auto">
                  <TI.TableToolbar
                  showFilters={showFilters}
                  showColumns={showColumns}
                  compactMode={!isMultiLine} // Inverted: compactMode = !multiLine
                  onToggleFilters={cfg.toolbarVisibility.filters ? () => setShowFilters(!showFilters) : undefined}
                  onToggleColumns={cfg.toolbarVisibility.columns ? () => setShowColumns(!showColumns) : undefined}
                  onToggleCompact={cfg.multiLine.allowToggle ? () => setIsMultiLine(!isMultiLine) : undefined}
                  onAdd={cfg.toolbarVisibility.add && allowAdd ? (cfg.callbacks?.onAdd || (() => setShowAddModal(true))) : undefined}
                  onExportCSV={cfg.toolbarVisibility.csv && cfg.export.csv && allowExport && user?.can_export ? handleExportCSV : undefined}
                  onExportXLSX={cfg.toolbarVisibility.xlsx && cfg.export.xlsx && allowExport && user?.can_export ? handleExportXLSX : undefined}
                  onReset={cfg.toolbarVisibility.reset ? handleReset : undefined}
                  onSave={cfg.toolbarVisibility.save && cfg.callbacks?.onSave ? () => cfg.callbacks?.onSave?.(data) : undefined}
                  onShare={
                    cfg.toolbarVisibility.share && visibleSelectedCount > 0 && (user?.role?.toLowerCase() === 'admin' || user?.role?.toLowerCase() === 'superadmin' || user?.is_superuser_role)
                      ? () => {
                          setSharingRecords(visibleSelectedRows);
                        }
                      : undefined
                  }
                  onDelete={
                    cfg.toolbarVisibility.delete && allowDelete && visibleSelectedCount > 0
                      ? () => {
                          setDeletingRecords(visibleSelectedRows);
                        }
                      : undefined
                  }
                  showAdd={cfg.toolbarVisibility.add && allowAdd}
                  showExportCSV={cfg.toolbarVisibility.csv && cfg.export.csv && allowExport && (user?.can_export ?? false)}
                  showExportXLSX={cfg.toolbarVisibility.xlsx && cfg.export.xlsx && allowExport && (user?.can_export ?? false)}
                  showSave={cfg.toolbarVisibility.save}
                  showShare={cfg.toolbarVisibility.share}
                  showDelete={cfg.toolbarVisibility.delete && allowDelete}
                  shareCount={visibleSelectedCount}
                  deleteCount={visibleSelectedCount}
                  customButtons={cfg.customToolbarButtons}
                />
                </div>
              )}
            </div>
          </TI.TableHeader>

          {/* FILTER PANEL */}
          {showFilters && cfg.filters.fields && (
            <TI.FilterPanel
              title="Filters"
              activePresetName={activeFiltersPresetName}
              isModified={cfg.useMyState ? isFiltersModified : false}
              onRevertToPreset={cfg.useMyState ? handleRevertFilters : undefined}
              onSaveModification={cfg.useMyState ? handleSaveFilterModification : undefined}
              isSaving={filtersMyState?.isSavingPreset}
              onClose={() => setShowFilters(false)}
              onSet={() => {
                if (cfg.useMyState && filtersMyState) {
                  // Use independent filters scope modal
                  setShowFiltersSaveModal(true);
                } else {
                  // Legacy mode
                  setStatePresetComponent('filters');
                  setShowSaveStateModal(true);
                }
              }}
              onReset={() => {
                setColumnFilters([]);
                setGlobalFilterInput('');
                if (cfg.useMyState && filtersMyState) {
                  filtersMyState.setActivePresetName(null);
                } else {
                  setActiveFiltersPresetNameLocal(null);
                }
              }}
              onRecall={() => {
                if (cfg.useMyState && filtersMyState) {
                  // Use independent filters scope modal
                  setShowFiltersLoadModal(true);
                } else {
                  // Legacy mode
                  setStatePresetComponent('filters');
                  setShowLoadStateModal(true);
                }
              }}
            >
              {renderFiltersFromMatrix()}
              {cfg.filters.customFilters}
            </TI.FilterPanel>
          )}

          {/* COLUMNS PANEL */}
          {showColumns && cfg.columns.enabled && (
            <TI.ColumnsPanel
              columns={table.getAllLeafColumns().filter(col => {
                const fieldConfig = cfg.columns.fields?.[col.id];
                if (!fieldConfig) return true; // Not configured = show by default
                const [isInList] = fieldConfig;
                return isInList; // Only show if isInList === true
              })}
              activePresetName={activeColumnsPresetName}
              isModified={cfg.useMyState ? isColumnsModified : false}
              onRevertToPreset={cfg.useMyState ? handleRevertColumns : undefined}
              onSaveModification={cfg.useMyState ? handleSaveColumnModification : undefined}
              isSaving={columnsMyState?.isSavingPreset}
              onReorder={(columnIds) => columnState.setColumnOrder(columnIds)}
              onClose={() => setShowColumns(false)}
              onSet={() => {
                if (cfg.useMyState && columnsMyState) {
                  // Use independent columns scope modal
                  setShowColumnsSaveModal(true);
                } else {
                  // Legacy mode
                  setStatePresetComponent('columns');
                  setShowSaveStateModal(true);
                }
              }}
              onReset={() => {
                columnState.resetColumnVisibility();
                columnState.resetColumnOrder();
                columnState.resetColumnSizing();
                if (cfg.useMyState && columnsMyState) {
                  columnsMyState.setActivePresetName(null);
                } else {
                  setActiveColumnsPresetNameLocal(null);
                }
              }}
              onRecall={() => {
                if (cfg.useMyState && columnsMyState) {
                  // Use independent columns scope modal
                  setShowColumnsLoadModal(true);
                } else {
                  // Legacy mode
                  setStatePresetComponent('columns');
                  setShowLoadStateModal(true);
                }
              }}
              onToggleDebug={user?.is_superuser_role ? () => setShowDebugInfo(prev => !prev) : undefined}
              showDebug={showDebugInfo}
            />
          )}

          {/* TABLE WRAPPER */}
          <TI.TableWrapper>
            {isLoading ? (
              <div className="flex items-center justify-center py-10">
                <TI.Spinner />
                <span className="ml-2 text-sm text-muted-foreground">Loading...</span>
              </div>
            ) : (
              <table className="w-full border-collapse">
                {/* THEAD */}
                <thead className="bg-muted/30 sticky top-0 z-10 border-b border-border">
                  {table.getHeaderGroups().map((headerGroup) => (
                    <tr key={headerGroup.id}>
                      {headerGroup.headers.map((header) => (
                        <th
                          key={header.id}
                          className="px-3 py-2 text-left text-xs font-semibold uppercase tracking-wide border-r border-border relative"
                          style={{ 
                            width: header.getSize(),
                            minWidth: header.column.columnDef.minSize ?? 50,
                            maxWidth: header.column.columnDef.maxSize ?? 1000,
                          }}
                        >
                          {header.isPlaceholder ? null : (
                            <>
                              <div
                                className={
                                  header.column.getCanSort()
                                    ? 'cursor-pointer select-none flex items-center gap-1'
                                    : 'flex items-center gap-1'
                                }
                                onClick={header.column.getToggleSortingHandler()}
                              >
                                {TI.flexRender(header.column.columnDef.header, header.getContext())}
                                {header.column.getIsSorted() && (
                                  <span className="ml-1">
                                    {header.column.getIsSorted() === 'asc' ? '▲' : '▼'}
                                  </span>
                                )}
                              </div>
                              {/* Debug: Show column width info (len pre superuserov) */}
                              {showDebugInfo && user?.is_superuser_role && (
                                <div className="text-[9px] text-muted-foreground/60 font-mono mt-1">
                                  {Math.round(header.getSize())}px
                                  <br />
                                  min:{Math.round(header.column.columnDef.minSize || 0)} 
                                  max:{Math.round(header.column.columnDef.maxSize || 0)}
                                  <br />
                                  def:{Math.round(header.column.columnDef.size || 0)}
                                  <br />
                                  state:{JSON.stringify(table.getState().columnSizing[header.column.id] || 'none')}
                                </div>
                              )}
                            </>
                          )}
                          {/* Resize handle */}
                          {header.column.getCanResize() && (
                            <TI.ColumnResizeHandle 
                              onMouseDown={header.getResizeHandler()}
                              onTouchStart={header.getResizeHandler()}
                              isResizing={header.column.getIsResizing()}
                            />
                          )}
                        </th>
                      ))}
                    </tr>
                  ))}
                </thead>

                {/* TBODY */}
                <tbody>
                  {table.getRowModel().rows.length === 0 ? (
                    <tr>
                      <td
                        colSpan={allColumns.length}
                        className="text-center text-sm text-muted-foreground py-10"
                      >
                        {cfg.emptyState.text}
                      </td>
                    </tr>
                  ) : (
                    table.getRowModel().rows.map((row) => (
                      <tr
                        key={row.id}
                        className="border-b border-border hover:bg-muted/20 transition-colors"
                      >
                        {row.getVisibleCells().map((cell) => (
                          <td
                            key={cell.id}
                            className={`px-3 py-2 text-sm border-r border-border ${
                              !isMultiLine ? 'truncate overflow-hidden whitespace-nowrap max-w-[300px]' : 'whitespace-normal break-words'
                            }`}
                            style={{ 
                              width: cell.column.getSize(),
                              minWidth: cell.column.columnDef.minSize ?? 50,
                              maxWidth: cell.column.columnDef.maxSize ?? 1000,
                            }}
                          >
                            {TI.flexRender(cell.column.columnDef.cell, cell.getContext())}
                          </td>
                        ))}
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            )}
          </TI.TableWrapper>
        </TI.TableCard>
      </div>

      {/* PAGE FOOTER */}
      {cfg.pageFooter.visible && <PageFooter />}

      {/* MODALS */}
      <TI.ErrorModal open={isErrorModalOpen} onClose={closeErrorModal} error={error} />
      {tooltip && <TI.Tooltip tooltip={tooltip} />}

      {/* DELETE CONFIRM MODAL */}
      {deletingRecords.length > 0 && (
        <TI.ConfirmModal
          open={deletingRecords.length > 0}
          onCancel={() => setDeletingRecords([])}
          onConfirm={handleDelete}
          title="Confirm Delete"
          message={`Are you sure you want to delete ${deletingRecords.length} record(s)?`}
          confirmText="Delete"
          variant="danger"
        />
      )}

      {/* SHARE FACTORY MODAL */}
      {sharingRecords.length > 0 && (
        <ShareFactoryModal
          open={sharingRecords.length > 0}
          onClose={() => setSharingRecords([])}
          factoryIds={sharingRecords.map((r) => String(r.id))}
          factoryNames={sharingRecords.map((r) => (r as any).factory_display_label || (r as any).name || (r as any).code || String(r.id))}
          onSuccess={() => {
            setSharingRecords([]);
            clearSelection();
          }}
        />
      )}

      {/* ADD RECORD MODAL - Auto-detect which modal to use */}
      {showAddModal && cfg.toolbarVisibility.add && allowAdd && (() => {
        // Auto-detection: use AddRecordWithSelectModal if parentHierarchy OR legacy parentField exists
        const hasParentHierarchy = cfg.parentHierarchy && cfg.parentHierarchy.length > 0;
        const hasLegacyParent = cfg.parentField && cfg.parentEndpoint;
        const useSelectModal = hasParentHierarchy || hasLegacyParent || cfg.customAddModal === 'AddRecordWithSelectModal';
        
        if (useSelectModal && (hasParentHierarchy || hasLegacyParent)) {
          return (
            <AddRecordWithSelectModal
              open={showAddModal}
              fieldsMatrix={fieldConfigMap}
              apiEndpoint={cfg.apiEndpoint}
              singularName={getSingularNameFromEndpoint(cfg.apiEndpoint, cfg.tableName)}
              // New hierarchical config (preferred)
              parentHierarchy={cfg.parentHierarchy}
              // Legacy single-parent config (backward compatible)
              parentField={cfg.parentField}
              parentEndpoint={cfg.parentEndpoint}
              parentOptions={cfg.parentOptions}
              parentRequiredMessage={cfg.parentRequiredMessage}
              parentLabel={cfg.parentLabel}
              onClose={() => setShowAddModal(false)}
              onSuccess={async (_newRecord) => {
                setShowAddModal(false);
                await refetch();
                TI.toastMessages.recordCreated();
              }}
              getCsrfToken={getCsrfToken}
            />
          );
        }
        
        // Standard modal
        return (
          <AddRecordModal
            open={showAddModal}
            fieldsMatrix={fieldConfigMap}
            apiEndpoint={cfg.apiEndpoint}
            singularName={getSingularNameFromEndpoint(cfg.apiEndpoint, cfg.tableName)}
            onClose={() => setShowAddModal(false)}
            onSuccess={async (_newRecord) => {
              setShowAddModal(false);
              await refetch();
              TI.toastMessages.recordCreated();
            }}
            getCsrfToken={getCsrfToken}
          />
        );
      })()}

      {/* EDIT RECORD MODAL */}
      {editingRecord && cfg.actions.edit && allowEdit && (
        <EditRecordModal
          open={!!editingRecord}
          record={editingRecord}
          fieldsMatrix={fieldConfigMap}
          apiEndpoint={cfg.apiEndpoint}
          singularName={getSingularNameFromEndpoint(cfg.apiEndpoint, cfg.tableName)}
          onClose={() => setEditingRecord(null)}
          onSuccess={async (_updatedRecord) => {
            setEditingRecord(null);
            await refetch();
            TI.toastMessages.changesSaved();
          }}
          getCsrfToken={getCsrfToken}
        />
      )}

      {/* SAVE STATE PRESET MODAL */}
      <SaveStateModal
        open={showSaveStateModal}
        onClose={() => setShowSaveStateModal(false)}
        onSave={handleSaveState}
        defaultName={cfg.useMyState ? `${cfg.storageKey}-${new Date().toISOString().slice(0, 10)}` : `${statePresetComponent}-${new Date().toISOString().slice(0, 10)}`}
        title={cfg.useMyState ? 'Save Table State' : `Save ${statePresetComponent.charAt(0).toUpperCase() + statePresetComponent.slice(1)} Preset`}
        nameLabel="Preset Name"
        showDescription={true}
        presetNameExists={cfg.useMyState && myState ? myState.presetNameExists : undefined}
      />

      {/* LOAD STATE PRESET MODAL */}
      <LoadStateModal
        open={showLoadStateModal}
        onClose={() => setShowLoadStateModal(false)}
        presets={presetsForModal}
        onLoad={handleLoadState}
        onDelete={handleDeletePreset}
        title={cfg.useMyState ? 'Load Saved Preset' : `Load ${statePresetComponent.charAt(0).toUpperCase() + statePresetComponent.slice(1)} Preset`}
      />

      {/* COLUMNS SAVE MODAL (myState mode - independent scope) */}
      {cfg.useMyState && columnsMyState && (
        <SaveStateModal
          open={showColumnsSaveModal}
          onClose={() => setShowColumnsSaveModal(false)}
          onSave={async (name, description) => {
            // Get current columns state
            const columnsState = {
              columnVisibility: columnState.columnVisibility,
              columnOrder: columnState.columnOrder,
              columnSizing: columnState.columnSizing,
            };
            console.log('[MyTable] Saving columns preset with state:', columnsState);
            // Update columnsMyState with current state before saving
            columnsMyState.updateState(columnsState);
            // Save preset - pass state directly to avoid closure issues
            await columnsMyState.savePreset(name, description, undefined, columnsState);
          }}
          defaultName={`columns-${new Date().toISOString().slice(0, 10)}`}
          title="Save Columns Preset"
          nameLabel="Preset Name"
          showDescription={true}
          presetNameExists={columnsMyState.presetNameExists}
        />
      )}

      {/* COLUMNS LOAD MODAL (myState mode - independent scope) */}
      {cfg.useMyState && columnsMyState && (
        <LoadStateModal
          open={showColumnsLoadModal}
          onClose={() => setShowColumnsLoadModal(false)}
          presets={(
            Array.isArray(columnsMyState.savedStates) ? columnsMyState.savedStates : []
          ).map(preset => ({
            id: preset.id,
            preset_name: preset.preset_name,
            description: preset.description || '',
            component: 'columns',
            created: preset.created,
            updated: preset.updated,
            is_default: preset.is_default,
            _isMyState: true,
          })) as any
          }
          onLoad={async (preset: any) => {
            try {
              console.log('[MyTable] Loading columns preset:', preset.preset_name);
              const loadedState = await columnsMyState.loadPreset(preset);
              console.log('[MyTable] Loaded columns state:', loadedState);
              setShowColumnsLoadModal(false);
              // Apply loaded state to local column state
              if (loadedState.columnVisibility) {
                console.log('[MyTable] Applying columnVisibility:', loadedState.columnVisibility);
                columnState.setColumnVisibility(loadedState.columnVisibility);
              }
              if (loadedState.columnOrder) {
                console.log('[MyTable] Applying columnOrder:', loadedState.columnOrder);
                columnState.setColumnOrder(loadedState.columnOrder);
              }
              if (loadedState.columnSizing) {
                console.log('[MyTable] Applying columnSizing:', loadedState.columnSizing);
                columnState.setColumnSizing(loadedState.columnSizing);
              }
            } catch (error) {
              console.error('[MyTable] Error loading columns preset:', error);
            }
          }}
          onDelete={async (presetId) => {
            await columnsMyState.deletePreset(String(presetId));
          }}
          title="Load Columns Preset"
        />
      )}
      {/* FILTERS SAVE MODAL (myState mode - independent scope) */}
      {cfg.useMyState && filtersMyState && (
        <SaveStateModal
          open={showFiltersSaveModal}
          onClose={() => setShowFiltersSaveModal(false)}
          onSave={async (name, description) => {
            // Get current filters state
            const filtersState = {
              columnFilters,
              globalFilter: globalFilterInput,
            };
            console.log('[MyTable] Saving filters preset with state:', filtersState);
            // Update filtersMyState with current state before saving
            filtersMyState.updateState(filtersState);
            // Save preset - pass state directly to avoid closure issues
            await filtersMyState.savePreset(name, description, undefined, filtersState);
          }}
          defaultName={`filters-${new Date().toISOString().slice(0, 10)}`}
          title="Save Filters Preset"
          nameLabel="Preset Name"
          showDescription={true}
          presetNameExists={filtersMyState.presetNameExists}
        />
      )}

      {/* FILTERS LOAD MODAL (myState mode - independent scope) */}
      {cfg.useMyState && filtersMyState && (
        <LoadStateModal
          open={showFiltersLoadModal}
          onClose={() => setShowFiltersLoadModal(false)}
          presets={(() => {
            const states = Array.isArray(filtersMyState.savedStates) ? filtersMyState.savedStates : [];
            console.log('[MyTable] Raw savedStates for filters:', states.map(s => ({ id: s.id, name: s.preset_name })));
            return states.map(preset => {
              const transformed = {
                id: preset.id,
                preset_name: preset.preset_name,
                description: preset.description || '',
                component: 'filters',
                created: preset.created,
                updated: preset.updated,
                is_default: preset.is_default,
                _isMyState: true,
              };
              return transformed;
            });
          })() as any
          }
          onLoad={async (preset: any) => {
            try {
              console.log('[MyTable] Loading filters preset - ID:', preset.id, 'Name:', preset.preset_name);
              const loadedState = await filtersMyState.loadPreset(preset);
              console.log('[MyTable] Loaded filters state for', preset.preset_name, ':', loadedState);
              setShowFiltersLoadModal(false);
              // Apply loaded state to local filter state
              if (loadedState.columnFilters) {
                console.log('[MyTable] Applying columnFilters:', JSON.stringify(loadedState.columnFilters, null, 2));
                setColumnFilters(loadedState.columnFilters);
              }
              if (loadedState.globalFilter !== undefined) {
                console.log('[MyTable] Applying globalFilter:', loadedState.globalFilter);
                setGlobalFilterInput(loadedState.globalFilter);
              }
            } catch (error) {
              console.error('[MyTable] Error loading filters preset:', error);
            }
          }}
          onDelete={async (presetId) => {
            await filtersMyState.deletePreset(String(presetId));
          }}
          title="Load Filters Preset"
        />
      )}
      {/* DEBUG */}
      {cfg.debug && (
        <div className="fixed bottom-4 right-4 bg-background border border-border rounded p-4 shadow-lg max-w-md text-xs">
          <h4 className="font-semibold mb-2">Debug Info</h4>
          <pre>{JSON.stringify({ 
            data: data.length, 
            visibleCount, 
            selectedCount,           // Total selected (all, persist across filters)
            visibleSelectedCount     // Effective action count (selected AND visible)
          }, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
