//*........................................................
//*       www/thermal_eye_ui/src/components/MyTable/MyTableHelpers.ts
//*       Helper functions for MyTable
//*       
//*       Purpose: Convert FieldMatrix to existing structures
//*........................................................

import type { FieldMatrix, FieldMatrixItem } from './MyTableTypes';
import type { FieldConfig } from '@/components/ui_custom/table/fieldFactory';

/**
 * Convert FieldMatrix to FieldConfig array
 * 
 * Konvertuje Field Matrix na pole FieldConfig objektov
 * (kompatibilné s existujúcim FieldFactory).
 * 
 * @param matrix - Field Matrix
 * @returns Array of FieldConfig objects sorted by order
 */
export function matrixToFieldConfigs<T extends Record<string, any>>(
  matrix: FieldMatrix<T>
): FieldConfig<T>[] {
  const entries = Object.entries(matrix) as Array<[keyof T & string, FieldMatrixItem]>;
  
  // Sort by order (lower = more left)
  const sorted = entries.sort((a, b) => {
    const orderA = a[1].order ?? 999;
    const orderB = b[1].order ?? 999;
    return orderA - orderB;
  });
  
  // Convert to FieldConfig
  return sorted.map(([key, item]) => ({
    key,
    type: item.type,
    header: item.header,
    size: item.size,
    minSize: item.minSize,
    maxSize: item.maxSize,
    order: item.order,
    editable: item.editableInline ?? true,
    editableInline: item.editableInline ?? true,
    sortable: item.sortable ?? true,  // Use from matrix, don't force
    filterable: item.isInFilterPanel ?? false,
    placeholder: item.placeholder,
    multiline: item.multiline,
    // Edit modal properties
    editableInEditModal: item.editableInEditModal,
    editableInAddModal: item.editableInAddModal,
    required: item.required,
    // Type-specific properties
    options: item.options,
    min: item.min,
    max: item.max,
    step: item.step,
    decimals: item.decimals,
    alignRight: item.alignRight,
    labelField: item.labelField,
    apiEndpoint: item.apiEndpoint,
    scopedByFactory: item.scopedByFactory,
    suggestions: item.suggestions,
    maxNumberOfTags: item.maxNumberOfTags,
    format: item.format,
    // Boolean field properties
    trueLabel: item.trueLabel,
    falseLabel: item.falseLabel,
    style: item.style,
    quickToggle: item.quickToggle,
  })) as FieldConfig<T>[];
}

/**
 * Convert FieldMatrix to ColumnsConfig.fields
 * 
 * Konvertuje Field Matrix na columns.fields štruktúru
 * (KEY:[isInList, defaultVisibility]).
 * 
 * @param matrix - Field Matrix
 * @returns Columns fields configuration
 */
export function matrixToColumnsFields<T extends Record<string, any>>(
  matrix: FieldMatrix<T>
): Record<string, [boolean, boolean]> {
  const result: Record<string, [boolean, boolean]> = {};
  
  for (const [key, item] of Object.entries(matrix)) {
    const isInList = item.isInColumnPanel ?? true;
    const defaultVisible = item.defaultVisible ?? true;
    result[key] = [isInList, defaultVisible];
  }
  
  return result;
}

/**
 * Convert FieldMatrix to column order array
 * 
 * Konvertuje Field Matrix na pole kľúčov zoradených podľa order property.
 * 
 * @param matrix - Field Matrix
 * @returns Array of field keys sorted by order
 */
export function matrixToColumnOrder<T extends Record<string, any>>(
  matrix: FieldMatrix<T>
): string[] {
  const entries = Object.entries(matrix) as Array<[keyof T & string, FieldMatrixItem]>;
  
  // Sort by order
  const sorted = entries.sort((a, b) => {
    const orderA = a[1].order ?? 999;
    const orderB = b[1].order ?? 999;
    return orderA - orderB;
  });
  
  return sorted.map(([key]) => key as string);
}

/**
 * Convert FieldMatrix to FiltersConfig.fields
 * 
 * Konvertuje Field Matrix na filters.fields štruktúru
 * (KEY:true pre polia ktoré majú byť vo FilterPanel).
 * 
 * @param matrix - Field Matrix
 * @returns Filters fields configuration
 */
export function matrixToFiltersFields<T extends Record<string, any>>(
  matrix: FieldMatrix<T>
): Record<string, boolean> {
  const result: Record<string, boolean> = {};
  
  for (const [key, item] of Object.entries(matrix)) {
    if (item.isInFilterPanel) {
      result[key] = true;
    }
  }
  
  return result;
}

/**
 * Get inline editable fields from matrix
 * 
 * Vráti zoznam polí ktoré sú inline editable.
 * 
 * @param matrix - Field Matrix
 * @returns Array of field keys that are inline editable
 */
export function matrixToInlineEditableFields<T extends Record<string, any>>(
  matrix: FieldMatrix<T>
): string[] {
  const result: string[] = [];
  
  for (const [key, item] of Object.entries(matrix)) {
    if (item.editableInline ?? true) {
      result.push(key);
    }
  }
  
  return result;
}

/**
 * Get modal editable fields from matrix
 * 
 * Vráti zoznam polí ktoré sú editable v modal.
 * 
 * @param matrix - Field Matrix
 * @returns Array of field keys that are modal editable
 */
export function matrixToModalEditableFields<T extends Record<string, any>>(
  matrix: FieldMatrix<T>
): string[] {
  const result: string[] = [];
  
  for (const [key, item] of Object.entries(matrix)) {
    if (item.editableInEditModal ?? true) {
      result.push(key);
    }
  }
  
  return result;
}


