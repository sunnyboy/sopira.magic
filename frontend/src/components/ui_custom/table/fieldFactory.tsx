/* eslint-disable @typescript-eslint/no-unused-vars */
//*........................................................
//*       www/thermal_eye_ui/src/components/ui_custom/table/fieldFactory.tsx
//*       Declarative field factory for table columns
//*       [CACHE BUST v2]
//*........................................................

import React from 'react';
import * as TI from './tableImports';
import type { OptimisticFieldConfig } from './useOptimisticField';
import type { ColumnDef, Row } from '@tanstack/react-table';
import { ScopedFKCell } from './ScopedFKCell';
import { getOwnershipField } from '@/config/modelMetadata';

/**
 * Base field configuration
 */
export interface BaseFieldConfig<TData = any> {
  /** Field name/key in data object */
  key: string;
  /** Column header label */
  header: string;
  /** Phantom field to keep TData used in generics */
  __dataType?: TData;
  /** Column width (default: 120) */
  size?: number;
  /** Minimum column width for resizing (default: 50) */
  minSize?: number;
  /** Maximum column width for resizing (default: 1000) */
  maxSize?: number;
  /** Column order (for sorting in table, lower = more left) */
  order?: number;
  /** Is field editable */
  editable?: boolean;
  /** Is column sortable */
  sortable?: boolean;
  /** Is column filterable */
  filterable?: boolean;
  /** Is field required (for validation) */
  required?: boolean;
}

/**
 * Text field configuration
 */
export interface TextFieldConfig<TData = any> extends BaseFieldConfig<TData> {
  type: 'text';
  /** Maximum length */
  maxLength?: number;
  /** Multiline (textarea) */
  multiline?: boolean;
  /** Placeholder text */
  placeholder?: string;
}

/**
 * Number field configuration
 */
export interface NumberFieldConfig<TData = any> extends BaseFieldConfig<TData> {
  type: 'number';
  /** Minimum value */
  min?: number;
  /** Maximum value */
  max?: number;
  /** Step increment */
  step?: number;
  /** Number of decimal places */
  decimals?: number;
  /** Unit suffix (e.g., "kg", "°C") */
  unit?: string;
  /** Align right */
  alignRight?: boolean;
}

/**
 * Temperature field (specialized number field)
 */
export interface TemperatureFieldConfig<TData = any> extends BaseFieldConfig<TData> {
  type: 'temperature';
  /** Temperature range */
  range?: { min: number; max: number };
  /** Decimal places (default: 1) */
  decimals?: number;
  /** Unit (default: °C) */
  unit?: string;
}

/**
 * Date field configuration
 */
export interface DateFieldConfig<TData = any> extends BaseFieldConfig<TData> {
  type: 'date';
  /** Date format for display */
  format?: 'DD.MM.YYYY' | 'YYYY-MM-DD';
}

/**
 * Time field configuration
 */
export interface TimeFieldConfig<TData = any> extends BaseFieldConfig<TData> {
  type: 'time';
  /** Time format */
  format?: 'HH:MM' | 'HH:MM:SS';
}

/**
 * Boolean field configuration
 */
export interface BooleanFieldConfig<TData = any> extends BaseFieldConfig<TData> {
  type: 'boolean';
  /** Label for true value (default: 'True') */
  trueLabel?: string;
  /** Label for false value (default: 'False') */
  falseLabel?: string;
  /** Display style: 'badge' (colored), 'icon' (checkmark/x), or 'text' */
  style?: 'badge' | 'icon' | 'text';
  /** Quick toggle: single click toggles value (true/false), default: false = double-click opens dropdown */
  quickToggle?: boolean;
}

/**
 * Select/dropdown field configuration
 */
export interface SelectFieldConfig<TData = any> extends BaseFieldConfig<TData> {
  type: 'select';
  /** Options for select */
  options: { value: string; label: string }[] | ((row: TData) => { value: string; label: string }[]);
  /** Placeholder when empty */
  placeholder?: string;
}

/**
 * Foreign key field configuration
 */
export interface ForeignKeyFieldConfig<TData = any> extends BaseFieldConfig<TData> {
  type: 'fk';
  /** Options for FK select (global list, will be scoped if scopedByFactory=true) */
  options: { id: string; label: string }[];
  /** Label field name (e.g., 'location_label') */
  labelField?: string;
  /** Enable professional UUID-based factory scoping (fetches from API on focus) */
  scopedByFactory?: boolean;
  /** Factory UUID field name (default: 'factory') */
  factoryField?: string;
  /** Use all_accessible=true parameter for this FK field (default: false) */
  useAllAccessible?: boolean;
  /** API endpoint for fetching options (if not provided, will be constructed from pluralName) */
  apiEndpoint?: string;
  /** Plural name for auto-constructing endpoint (e.g., 'factories', 'locations') */
  pluralName?: string;
}

/**
 * Tag field configuration
 */
export interface TagFieldConfig<TData = any> extends BaseFieldConfig<TData> {
  type: 'tag';
  /** Tag suggestions */
  suggestions?: string[];
  /** Allow adding new tags */
  addingAllowed?: boolean;
  /** Maximum number of tags */
  maxNumberOfTags?: number;
  /** Maximum tag length */
  maxTagLength?: number;
  /** Callback when new tag created */
  onNewTag?: (tagName: string) => void;
}

/**
 * Selection checkbox column (for row selection)
 */
export interface SelectionFieldConfig<TData = any> {
  type: 'selection';
  /** Column key (always 'select') */
  key: 'select';
  /** No header needed (will be auto-generated) */
  header?: never;
  /** Fixed width */
  size?: 40;
  /** Column order (default: 0 - first) */
  order?: number;
  editable?: false;
  sortable?: false;
  filterable?: false;
  /** Phantom field to keep TData used in generics */
  __dataType?: TData;
}

/**
 * Actions column (Edit, Delete, custom buttons)
 */
export interface ActionsFieldConfig<TData = any> {
  type: 'actions';
  /** Column key (always 'actions') */
  key: 'actions';
  /** Column header */
  header?: string;
  /** Fixed width */
  size?: number;
  /** Column order (default: 5 - second) */
  order?: number;
  /** Show edit button */
  showEdit?: boolean;
  /** Show delete button */
  showDelete?: boolean;
  /** Show expand button */
  showExpand?: boolean;
  /** Show share button (Admin/SA only) */
  showShare?: boolean;
  /** Custom action buttons */
  customButtons?: React.ReactNode;
  editable?: false;
  sortable?: false;
  filterable?: false;
  /** Phantom field to keep TData used in generics */
  __dataType?: TData;
}

/**
 * JSON field configuration (for viewing/editing JSON data)
 */
export interface JsonFieldConfig<TData = any> extends BaseFieldConfig<TData> {
  type: 'json';
  /** Pretty print JSON */
  pretty?: boolean;
  /** Max height for JSON viewer */
  maxHeight?: number;
  /** Show copy button */
  showCopy?: boolean;
}

/**
 * Union type of all field configs
 */
export type FieldConfig<TData = any> = 
  | TextFieldConfig<TData>
  | NumberFieldConfig<TData>
  | TemperatureFieldConfig<TData>
  | DateFieldConfig<TData>
  | TimeFieldConfig<TData>
  | BooleanFieldConfig<TData>
  | SelectFieldConfig<TData>
  | ForeignKeyFieldConfig<TData>
  | TagFieldConfig<TData>
  | SelectionFieldConfig<TData>
  | ActionsFieldConfig<TData>
  | JsonFieldConfig<TData>;

/**
 * Context for field factory (table-specific data)
 */
export interface FieldFactoryContext<TData = any> {
  /** API endpoint base (e.g., '/api/measurements') */
  apiEndpoint: string;
  /** Current editing cell state */
  editingCell: { id: string; field: string } | null;
  /** Set editing cell */
  setEditingCell: (cell: { id: string; field: string } | null) => void;
  /** Update field callback (optimistic update) */
  updateField: (recordId: string | number, fieldName: string, newValue: any) => void;
  /** Update entire record from API response (for computed fields like *_display_label) */
  updateFullRecord?: (recordId: string | number, fullRecord: any) => void;
  /** Error handler */
  handleError: (recordId: string | number, errorData: any) => void;
  /** CSRF token getter */
  getCsrfToken: () => string | null;
  /** Global filter/search term (for highlighting) */
  searchTerm?: string;
  /** Highlight text function */
  highlightText?: (text: string, searchTerm: string) => React.ReactNode;
  /** Tags cell component (optional) */
  TagsCell?: React.ComponentType<{ row: TData; value: string[]; onSave: (tags: string[]) => void }>;
  
  // ============================================
  // FK OPTIONS
  // ============================================
  /** FK options loaded from API (keyed by field name, e.g. 'factory', 'location') */
  fkOptions?: Record<string, Array<{ id: string; label: string }>>;
  /** Get scoped FK options - backend automatically applies scope */
  getScopedOptions?: (key: string, factoryId?: string) => Promise<Array<{ id: string; label: string }>>;
  /** Scoped options cache */
  scopedCache?: Map<string, Array<{ id: string; label: string }>>;
  /** Trigger re-render when scoped cache updates */
  onScopeCacheUpdate?: () => void;
  
  // ============================================
  // SELECTION COLUMN (type: 'selection')
  // ============================================
  /** Table data (needed for selection header) */
  data?: TData[];
  /** Check if row is selected */
  isSelected?: (id: string | number) => boolean;
  /** Toggle row selection */
  toggleRow?: (id: string | number) => void;
  /** Check if all rows are selected */
  isAllSelected?: (data: TData[]) => boolean;
  /** Toggle all rows selection */
  toggleAll?: (data: TData[]) => void;
  /** Check if selection is indeterminate */
  isIndeterminate?: (data: TData[]) => boolean;
  
  // ============================================
  // ACTIONS COLUMN (type: 'actions')
  // ============================================
  /** Check if cell is being edited */
  checkIsEditing?: (id: string, field: string) => boolean;
  /** Handle edit action */
  onEdit?: (row: TData) => void;
  /** Handle delete action */
  onDelete?: (row: TData) => void;
  /** Handle share action */
  onShare?: (row: TData) => void;
  /** Handle save action */
  onSave?: (row: TData) => void;
  /** Handle expand action */
  onExpand?: (id: string) => void;
  /** Check if row is expanded */
  isExpanded?: (id: string) => boolean;
  /** Expanded rows set */
  expandedRows?: Set<string>;
}

/**
 * Get column sizing from config with fallback defaults (DRY helper)
 */
function getColumnSizing(
  config: { size?: number; minSize?: number; maxSize?: number },
  defaults?: { size?: number; minSize?: number; maxSize?: number }
) {
  return {
    size: config.size ?? defaults?.size ?? 120,
    minSize: config.minSize ?? defaults?.minSize ?? 50,
    maxSize: config.maxSize ?? defaults?.maxSize ?? 1000,
  };
}

/**
 * Creates a TanStack Table column definition from field config
 */
export function createTableColumn<TData extends Record<string, any>>(
  config: FieldConfig<TData>,
  context: FieldFactoryContext<TData>,
  columnHelper: any
): ColumnDef<TData, any> {
  
  // ============================================
  // SPECIAL COLUMNS (display type, not accessor)
  // ============================================
  
  // Selection column
  if (config.type === 'selection') {
    return columnHelper.display({
      id: 'select',
      header: () => {
        const data = context.data || [];
        const allSelected = data.length > 0 && context.isAllSelected?.(data);
        const indeterminate = data.length > 0 && context.isIndeterminate?.(data);
        
        return (
          <input
            type="checkbox"
            checked={allSelected}
            ref={(input) => {
              if (input) input.indeterminate = indeterminate || false;
            }}
            onChange={() => context.toggleAll?.(data)}
          />
        );
      },
      cell: ({ row }: { row: Row<TData> }) => (
        <input
          type="checkbox"
          checked={context.isSelected?.(row.original.id) || false}
          onChange={() => context.toggleRow?.(row.original.id)}
        />
      ),
      ...getColumnSizing(config, { size: 40, minSize: 40, maxSize: 40 }),
      enableSorting: false,
      enableColumnFilter: false,
      enableResizing: false,
    });
  }
  
  // Actions column
  if (config.type === 'actions') {
    return columnHelper.display({
      id: 'actions',
      header: config.header || 'Actions',
      cell: ({ row }: { row: Row<TData> }) => {
        const r = row.original;
        const editing = context.checkIsEditing?.(String(r.id), 'actions') || false;
        const rowId = String(r.id);
        
        return (
          <TI.TableActionButtons
            showExpand={config.showExpand}
            showExpandButton={config.showExpand}
            isExpanded={context.isExpanded?.(rowId) || false}
            onExpand={config.showExpand ? () => context.onExpand?.(rowId) : undefined}
            onEdit={config.showEdit && !editing ? () => context.onEdit?.(r) : undefined}
            onDelete={config.showDelete ? () => context.onDelete?.(r) : undefined}
            onShare={config.showShare ? () => context.onShare?.(r) : undefined}
            showShare={config.showShare}
            customButtons={editing && context.onSave ? (
              <TI.Button variant="solid" size="sm" onClick={() => context.onSave?.(r)} title="Save">
                <TI.Save size={12} />
              </TI.Button>
            ) : config.customButtons}
          />
        );
      },
      ...getColumnSizing(config, { size: 120, minSize: 80, maxSize: 200 }),
      enableSorting: false,
      enableColumnFilter: false,
    });
  }
  
  // JSON column
  if (config.type === 'json') {
    return columnHelper.accessor(config.key, {
      id: config.key,
      header: config.header,
      ...getColumnSizing(config, { size: 200, minSize: 100, maxSize: 500 }),
      enableSorting: false,
      enableColumnFilter: false,
      cell: (info: any) => {
        const value = info.getValue();
        if (!value) return <span className="text-muted-foreground">—</span>;
        
        const jsonString = typeof value === 'string' 
          ? value 
          : JSON.stringify(value, null, config.pretty ? 2 : 0);
        
        return (
          <div 
            className="font-mono text-xs overflow-auto"
            style={{ maxHeight: config.maxHeight || 100 }}
          >
            <pre className="m-0">{jsonString}</pre>
            {config.showCopy && (
              <TI.Button
                size="sm"
                variant="ghost"
                onClick={() => {
                  navigator.clipboard.writeText(jsonString);
                  TI.toastMessages.copiedToClipboard();
                }}
                title="Copy JSON"
              >
                <TI.Copy size={12} />
              </TI.Button>
            )}
          </div>
        );
      },
    });
  }
  
  // ============================================
  // STANDARD COLUMNS (accessor type)
  // ============================================
  
  const {
    key,
    header,
    editable = true,
    sortable = true,
    filterable = true,
  } = config;

  const baseColumn = {
    header,
    ...getColumnSizing(config),
    enableSorting: sortable,
    enableColumnFilter: filterable,
  };

  // Build cell renderer based on field type
  const cell = (info: any) => {
    const r = info.row.original as TData;
    const isEditing = context.editingCell?.id === String(r.id) && context.editingCell?.field === key;

    if (!editable) {
      // Read-only field
      let displayValue: string;
      const rawValue = (r as any)[key];
      
      // Format numbers: temperature and weight to 1 decimal place
      if (config.type === 'temperature' || config.type === 'number') {
        if (rawValue != null && rawValue !== '') {
          const numValue = Number(rawValue);
          if (!isNaN(numValue)) {
            const decimals = config.type === 'temperature' 
              ? (config.decimals ?? 1)
              : (config.decimals ?? 1);
            displayValue = numValue.toFixed(decimals);
          } else {
            displayValue = String(rawValue ?? '');
          }
        } else {
          displayValue = '';
        }
      } else if (config.type === 'fk') {
        /**
         * Foreign Key field label rendering logic:
         * 
         * SSOT (Single Source of Truth): Backend VIEWS_MATRIX in view_configs.py
         * - Backend generates *_display_label fields using fk_display_template from VIEWS_MATRIX
         * - Example: factory_display_label is generated using VIEWS_MATRIX['factories']['fk_display_template']
         * 
         * Optional override: Frontend labelField in table config (e.g., Camera.tsx)
         * - If labelField is defined: Uses frontend template (table-specific override)
         * - If labelField is NOT defined: Falls back to backend *_display_label (uses SSOT)
         * 
         * Template format: "{code}-{human_id}-{name}" where placeholders are replaced with FK object fields
         * 
         * Priority order:
         * 1. Frontend labelField template (if defined) → applied to FK object from cache
         * 2. Backend *_display_label (from API response, generated using view_configs.py template)
         * 3. Fallback to raw FK value (UUID)
         */
        const val = String(rawValue ?? '');
        const labelField = config.labelField;
        
        // Check if labelField is a template string (contains {})
        const isTemplate = labelField && typeof labelField === 'string' && labelField.includes('{');
        
        if (isTemplate && rawValue) {
          // Frontend template override: Apply template from table config (e.g., Camera.tsx)
          // First, try to get FK object from fkOptions cache
          const fkOptions = context.fkOptions?.[key] || [];
          const fkId = String(rawValue);
          const fkObj = fkOptions.find((opt: any) => 
            String(opt.id) === fkId || String(opt.id) === String(rawValue)
          );
          
          if (fkObj) {
            // Apply template: replace {code}, {name}, {human_id}, etc. with actual values
            // fkObj contains individual fields (code, name, human_id) from backend FK cache
            let templateResult = labelField.replace(/\{(\w+)\}/g, (_match, fieldName) => {
              // Try to get field from fkObj (code, name, human_id, etc.)
              const fieldValue = (fkObj as any)[fieldName];
              if (fieldValue !== undefined && fieldValue !== null && fieldValue !== '') {
                return String(fieldValue);
              }
              // Field not found - return empty string (will be cleaned up)
              return '';
            });
            
            // Clean up empty placeholders and separators
            // Remove patterns like "--" or "-" at start/end, and multiple consecutive separators
            templateResult = templateResult.replace(/^[- ]+/, '').replace(/[- ]+$/, '').replace(/[- ]{2,}/g, '-');
            
            // If template result is empty or only separators, fallback to backend label
            if (!templateResult || templateResult.trim() === '' || templateResult === '-') {
              displayValue = (r as any)[`${key}_display_label`] || val;
            } else {
              displayValue = templateResult;
            }
          } else {
            // FK object not found in options cache - use backend-generated label (SSOT from view_configs.py)
            displayValue = (r as any)[`${key}_display_label`] || val;
          }
        } else {
          // No frontend template override - use backend-generated label (SSOT from view_configs.py)
          // This is the default behavior when labelField is not defined in table config
          displayValue = (r as any)[`${key}_display_label`] 
            || (labelField && !isTemplate ? (r as any)[labelField] : null)
            || (r as any)[`${key}_label`] 
            || val;
        }
      } else {
        displayValue = String(rawValue ?? '');
      }
      
      const highlighted = context.highlightText && context.searchTerm 
        ? context.highlightText(displayValue, context.searchTerm)
        : displayValue;
      
      return (
        <div 
          className="px-2 py-1 text-xs overflow-hidden whitespace-nowrap text-ellipsis"
          style={{ maxHeight: '1.5rem', lineHeight: '1.5rem' }}
          title={displayValue}
        >
          {highlighted}
        </div>
      );
    }

    // Create optimistic field
    const fieldConfig: OptimisticFieldConfig = {
      recordId: r.id,
      fieldName: key,
      initialValue: (r as any)[key],
      apiEndpoint: context.apiEndpoint,
      onDataUpdate: context.updateField,
      onFullRecordUpdate: context.updateFullRecord,
      onError: context.handleError,
      onSuccess: () => TI.toastMessages.changesSaved(),
      getCsrfToken: context.getCsrfToken,
    };

    // Add type-specific transforms
    if (config.type === 'time') {
      fieldConfig.transformForApi = (v: string) => v ? v + ':00' : '';
      fieldConfig.initialValue = String((r as any)[key] || '').slice(0, 5);
    }

    if (config.type === 'tag') {
      fieldConfig.transformForApi = (tags: string[]) => ({ tags_names: tags });
    }

    const field = TI.useOptimisticField(fieldConfig);

    // Render EditableCell based on type
    return renderEditableField(config, field, r, isEditing, context);
  };

  return columnHelper.accessor(key, {
    id: key, // Explicitly set id to match field key for sorting
    ...baseColumn,
    cell,
  });
}

/**
 * Renders editable field based on config type
 */
function renderEditableField<TData>(
  config: FieldConfig<TData>,
  field: any,
  row: TData,
  isEditing: boolean,
  context: FieldFactoryContext<TData>
): React.ReactNode {
  const commonProps = {
    isEditing,
    onStartEdit: () => context.setEditingCell({ id: String((row as any).id), field: config.key }),
    onCancel: () => context.setEditingCell(null),
    isSaving: field.isSaving,
  };

  const onSave = (v: any) => {
    field.save(v);
    context.setEditingCell(null);
  };

  // Text field
  if (config.type === 'text') {
    const displayValue = context.highlightText && context.searchTerm
      ? context.highlightText(String(field.value ?? ''), context.searchTerm)
      : undefined;

    return (
      <TI.EditableCell
        {...commonProps}
        value={String(field.value ?? '')}
        onSave={onSave}
        multiline={config.multiline}
        placeholder={config.placeholder}
        highlightedContent={displayValue}
      />
    );
  }

  // Number field
  if (config.type === 'number') {
    return (
      <TI.EditableCell
        {...commonProps}
        value={String(field.value ?? '')}
        type="number"
        min={config.min}
        max={config.max}
        step={config.step}
        decimals={config.decimals}
        onSave={(v) => onSave(Number(v))}
        className={config.alignRight ? 'text-right' : ''}
      />
    );
  }

  // Temperature field (specialized number)
  if (config.type === 'temperature') {
    return (
      <TI.EditableCell
        {...commonProps}
        value={String(field.value ?? '')}
        type="number"
        min={config.range?.min}
        max={config.range?.max}
        step={Math.pow(10, -(config.decimals ?? 1))}
        decimals={config.decimals ?? 1}
        onSave={(v) => onSave(Number(v))}
        className="text-right"
      />
    );
  }

  // Date field
  if (config.type === 'date') {
    const toDDMMYYYY = (s: string) => {
      const m = (s || '').match(/^(\d{4})-(\d{2})-(\d{2})$/);
      return m ? `${m[3]}.${m[2]}.${m[1]}` : s || '';
    };
    const formatted = toDDMMYYYY(field.value || '');

    return (
      <TI.EditableCell
        {...commonProps}
        value={field.value || ''}
        type="date"
        rowId={(row as any).id}
        onSave={onSave}
        highlightedContent={formatted}
        className="text-center text-xs whitespace-nowrap"
      />
    );
  }

  // Time field
  if (config.type === 'time') {
    return (
      <TI.EditableCell
        {...commonProps}
        value={String(field.value).slice(0, 5)}
        type="time"
        rowId={(row as any).id}
        onSave={onSave}
        highlightedContent={String(field.value).slice(0, 5)}
      />
    );
  }

  // Boolean field
  if (config.type === 'boolean') {
    const boolValue = field.value === true || field.value === 'true';
    const trueLabel = config.trueLabel || 'True';
    const falseLabel = config.falseLabel || 'False';
    const style = config.style || 'badge';
    const quickToggle = config.quickToggle ?? false;

    // Quick toggle handler: single click to toggle value
    const handleQuickToggle = (e: React.MouseEvent) => {
      if (quickToggle) {
        e.stopPropagation();
        e.preventDefault();  // Prevent any default behavior
        onSave(!boolValue); // Toggle value immediately
      }
    };

    // Edit mode: select dropdown (only if NOT quickToggle)
    if (isEditing && !quickToggle) {
      return (
        <TI.EditableCell
          {...commonProps}
          value={String(boolValue)}
          type="select"
          options={[
            { value: 'true', label: trueLabel },
            { value: 'false', label: falseLabel }
          ]}
          onSave={(v) => onSave(v === 'true')}
        />
      );
    }

    // Display mode: badge, icon, or text
    const displayProps = {
      className: `flex items-center justify-center rounded px-2 py-1 ${
        quickToggle 
          ? 'cursor-pointer hover:bg-accent/70 active:scale-95 transition-all' 
          : 'cursor-pointer hover:bg-accent/50'
      }`,
      onClick: quickToggle ? handleQuickToggle : undefined,
      onDoubleClick: quickToggle ? undefined : () => context.setEditingCell({ id: String((row as any).id), field: config.key }),
      title: quickToggle ? 'Click to toggle' : 'Double-click to edit',
    };

    if (style === 'icon') {
      return (
        <div {...displayProps}>
          {boolValue ? (
            <TI.CheckCircle className="text-green-600" size={20} />
          ) : (
            <TI.XCircle className="text-red-600" size={20} />
          )}
        </div>
      );
    }

    if (style === 'text') {
      return (
        <div {...displayProps} className={`${displayProps.className.replace('flex items-center justify-center', '')} text-center`}>
          <span className={boolValue ? 'text-green-600' : 'text-red-600'}>
            {boolValue ? trueLabel : falseLabel}
          </span>
        </div>
      );
    }

    // Default: badge style
    return (
      <div {...displayProps}>
        {boolValue ? (
          <TI.Badge className="bg-green-600 hover:bg-green-700 text-white border-0">
            ✓ {trueLabel}
          </TI.Badge>
        ) : (
          <TI.Badge variant="destructive">
            ✗ {falseLabel}
          </TI.Badge>
        )}
      </div>
    );
  }

  // Select field
  if (config.type === 'select') {
    const opts = typeof config.options === 'function' 
      ? config.options(row) 
      : config.options;

    return (
      <TI.EditableCell
        {...commonProps}
        value={String(field.value)}
        type="select"
        options={opts}
        selectPlaceholder={config.placeholder}
        onSave={onSave}
      />
    );
  }

  // Foreign key field (professional UUID-based scoping)
  if (config.type === 'fk') {
    // Get ownership_field from modelMetadata (SSOT)
    // Extract model name from apiEndpoint (e.g., '/api/measurements/' -> 'measurement')
    const modelNameFromEndpoint = context.apiEndpoint?.match(/\/api\/([^\/]+)\/?$/)?.[1] || '';
    const ownershipFieldFromMetadata = getOwnershipField(modelNameFromEndpoint);
    // Map ownership_field (e.g., "factory_id") to filter field name (e.g., "factory")
    const ownershipFilterField = ownershipFieldFromMetadata 
      ? ownershipFieldFromMetadata.replace('_id', '').replace('_', '') 
      : 'factory'; // Fallback for backward compatibility
    const isOwnershipField = config.key === ownershipFilterField;
    
    const val = String((row as any)[config.key] ?? '');
    
    // Use backend-generated compound display label or apply template
    const labelField = config.labelField;
    const isTemplate = labelField && typeof labelField === 'string' && labelField.includes('{');
    
    let displayLabel: string;
    
    if (isTemplate && val) {
      // SSOT: Apply template from Camera.tsx (or other table config)
      const fkOptions = context.fkOptions?.[config.key] || [];
      const fkObj = fkOptions.find((opt: any) => 
        String(opt.id) === val || String(opt.id) === String((row as any)[config.key])
      );
      
      if (fkObj) {
        // Apply template: replace {code}, {name}, {human_id}, etc.
        // fkObj should have individual fields (code, name, human_id) from backend cache
        let templateResult = labelField.replace(/\{(\w+)\}/g, (_match, fieldName) => {
          const fieldValue = (fkObj as any)[fieldName];
          if (fieldValue !== undefined && fieldValue !== null && fieldValue !== '') {
            return String(fieldValue);
          }
          // Field not found - return empty string (will be cleaned up)
          return '';
        });
        
        // Clean up empty placeholders and separators
        templateResult = templateResult.replace(/^[- ]+/, '').replace(/[- ]+$/, '').replace(/[- ]{2,}/g, '-');
        
        // If template result is empty or only separators, fallback to backend label
        if (!templateResult || templateResult.trim() === '' || templateResult === '-') {
          displayLabel = (row as any)[`${config.key}_display_label`] || val;
        } else {
          displayLabel = templateResult;
        }
      } else {
        // FK object not found in options - use backend-generated label (fallback from view_configs.py)
        displayLabel = (row as any)[`${config.key}_display_label`] || val;
      }
    } else {
      // No template in labelField - use backend-generated label or field name
      displayLabel = (row as any)[`${config.key}_display_label`] 
        || (labelField && !isTemplate ? (row as any)[labelField] : null)
        || (row as any)[`${config.key}_label`] 
        || val;
    }

    const highlighted = context.highlightText && context.searchTerm
      ? context.highlightText(displayLabel, context.searchTerm)
      : displayLabel;

    // Use ScopedFKCell for scoped fields, regular EditableCell for global fields
    // Backend automatically applies scope - scopedByFactory flag is deprecated but kept for backward compatibility
    if (config.scopedByFactory && !isOwnershipField) {
      return (
        <ScopedFKCell
          config={config}
          field={field}
          row={row}
          isEditing={isEditing}
          context={context}
          commonProps={commonProps}
          val={val}
          displayLabel={displayLabel}
          highlighted={highlighted}
          onSave={(v) => field.save(v)}
        />
      );
    }

    // Global FK field (factory) - use regular logic
    let options = context.fkOptions?.[config.key] || config.options || [];

    if (isEditing) {
      return (
        <TI.EditableCell
          {...commonProps}
          value={val}
          isEditing={true}
          type="select"
          options={options.map(o => ({ value: o.id, label: o.label }))}
          onSave={(v) => field.save(v || null)}
        />
      );
    }

    return (
      <TI.EditableCell
        {...commonProps}
        value={displayLabel}
        isEditing={false}
        editingAllowed={true}
        onSave={() => {}}
        highlightedContent={highlighted}
      />
    );
  }

  // Tag field
  if (config.type === 'tag') {
    const tags = (field.value || []) as string[];
    
    if (isEditing) {
      const TagsComponent = context.TagsCell;
      if (TagsComponent) {
        return <TagsComponent row={row} value={tags} onSave={(t: string[]) => {
          field.save(t);
          context.setEditingCell(null);
        }} />;
      }
      // Fallback if TagsCell not provided
      return <div className="px-2 py-1 text-muted-foreground">Tags editor not available</div>;
    }
    
    // Display mode
    if (!tags.length) return (
      <div 
        className="cursor-pointer hover:bg-accent/50 rounded px-2 py-1"
        onDoubleClick={() => context.setEditingCell({ id: String((row as any).id), field: config.key })}
        title="Double-click to edit"
      />
    );
    
    return (
      <div 
        className="flex flex-nowrap gap-1 cursor-pointer hover:bg-accent/50 rounded pl-2 pr-3 py-1 overflow-hidden items-center"
        style={{ maxHeight: '1.5rem', height: '1.5rem' }}
        onDoubleClick={() => context.setEditingCell({ id: String((row as any).id), field: config.key })}
        title="Double-click to edit"
      >
        {tags.map((t, i) => (
          <span 
            key={i} 
            className="inline-flex items-center rounded-full bg-primary/10 px-1 py-0 text-[10px] leading-tight font-medium text-primary border border-primary/20 whitespace-nowrap shrink-0"
            style={{ 
              maxWidth: '150px',
              overflow: 'hidden',
              textOverflow: 'ellipsis'
            }}
            title={t}
          >
            {t}
          </span>
        ))}
      </div>
    );
  }

  console.error(`[renderEditableField] FALLBACK: Unhandled type=${config.type}, key=${config.key}`);
  return <div className="px-2 py-1 text-red-600">Unsupported: {config.type}</div>;
}

/**
 * Batch create multiple columns from configs
 */
export function createTableColumns<TData extends Record<string, any>>(
  configs: FieldConfig<TData>[],
  context: FieldFactoryContext<TData>,
  columnHelper: any
): ColumnDef<TData, any>[] {
  return configs.map(config => createTableColumn(config, context, columnHelper));
}
