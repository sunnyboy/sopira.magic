//*........................................................
//*       www/thermal_eye_ui/src/components/MyTable/index.ts
//*       MyTable module exports
//*........................................................

export { MyTable } from './MyTable';
export { useMyTableData } from './useMyTableData';
export type {
  MyTableConfig,
  TableHeaderVisibility,
  TableToolbarVisibility,
  PageHeaderConfig,
  PageFooterConfig,
  ActionsConfig,
  QuickCreateConfig,
  InlineEditConfig,
  FiltersConfig,
  ColumnsConfig,
  ExportConfig,
  RowSelectionConfig,
  PaginationConfig,
  MultiLineConfig,
  EmptyStateConfig,
  MyTableCallbacks,
  // NEW: Field Matrix types
  FieldMatrix,
  FieldMatrixItem,
} from './MyTableTypes';
export { DEFAULT_MY_TABLE_CONFIG } from './MyTableTypes';
export type { MyTableDataState, UseMyTableDataOptions } from './useMyTableData';

// NEW: Field Matrix helper functions
export {
  matrixToFieldConfigs,
  matrixToColumnsFields,
  matrixToColumnOrder,
  matrixToFiltersFields,
  matrixToInlineEditableFields,
  matrixToModalEditableFields,
} from './MyTableHelpers';

