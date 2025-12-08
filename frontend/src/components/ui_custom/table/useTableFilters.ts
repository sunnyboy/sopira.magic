//*........................................................
//*       www/thermal_eye_ui/src/components/ui_custom/table/useTableFilters.ts
//*       Centralized hook for table filter management
//*       
//*       DRY: Single source of truth for all table filter logic
//*       Used by: MeasurementsTable, FactoriesTable, and all future tables
//*........................................................

import { useState, useCallback } from 'react';
import type { ColumnFiltersState } from '@tanstack/react-table';
import { useFilterState } from './useFilterState';
import type { SavedFilter } from './RecallFilterModal';

interface UseTableFiltersOptions {
  /** Storage key for saved filters (e.g. 'measurements-filters') */
  storageKey: string;
  /** Table name for default filter naming (e.g. 'Measurements') */
  tableName: string;
  /** Initial column filters state */
  initialColumnFilters?: ColumnFiltersState;
  /** Initial global filter */
  initialGlobalFilter?: string;
}

interface FilterState {
  columnFilters: ColumnFiltersState;
  globalFilter: string;
}

/**
 * Centralized hook for managing table filters with save/load/reset functionality
 * 
 * @example
 * ```tsx
 * const filters = useTableFilters({
 *   storageKey: 'measurements-filters',
 *   tableName: 'Measurements',
 * });
 * 
 * // In FilterPanel
 * <FilterPanel
 *   onSet={filters.handleSetFilter}
 *   onReset={filters.handleResetFilters}
 *   onRecall={filters.handleRecallFilter}
 * />
 * 
 * // Modals
 * <SaveFilterModal {...filters.saveModalProps} />
 * <RecallFilterModal {...filters.recallModalProps} />
 * ```
 */
export function useTableFilters({
  storageKey,
  tableName,
  initialColumnFilters = [],
  initialGlobalFilter = '',
}: UseTableFiltersOptions) {
  // Filter state
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>(initialColumnFilters);
  const [globalFilter, setGlobalFilter] = useState(initialGlobalFilter);
  const [resetKey, setResetKey] = useState(0);

  // Modal state
  const [showSaveFilterModal, setShowSaveFilterModal] = useState(false);
  const [showRecallFilterModal, setShowRecallFilterModal] = useState(false);

  // Saved filters management
  const {
    savedFilters,
    saveFilter,
    deleteFilter,
    getDefaultFilterName,
  } = useFilterState(storageKey);

  // Get current filter state
  const getCurrentFilterState = useCallback((): FilterState => ({
    columnFilters,
    globalFilter,
  }), [columnFilters, globalFilter]);

  // Open Save modal
  const handleSetFilter = useCallback(() => {
    setShowSaveFilterModal(true);
  }, []);

  // Reset all filters
  const handleResetFilters = useCallback(() => {
    setColumnFilters([]);
    setGlobalFilter('');
    setResetKey(k => k + 1);
  }, []);

  // Open Recall modal
  const handleRecallFilter = useCallback(() => {
    setShowRecallFilterModal(true);
  }, []);

  // Save filter with name
  const handleSaveFilter = useCallback(async (name: string) => {
    await saveFilter(name, getCurrentFilterState());
  }, [saveFilter, getCurrentFilterState]);

  // Load saved filter
  const handleLoadFilter = useCallback((filter: SavedFilter) => {
    setColumnFilters(filter.state.columnFilters || []);
    setGlobalFilter(filter.state.globalFilter || '');
    setResetKey(k => k + 1);
  }, []);

  // Return everything needed for filter management
  return {
    // State
    columnFilters,
    setColumnFilters,
    globalFilter,
    setGlobalFilter,
    resetKey,
    setResetKey,

    // Saved filters
    savedFilters,

    // Callbacks for FilterPanel
    handleSetFilter,
    handleResetFilters,
    handleRecallFilter,

    // Props for SaveFilterModal
    saveModalProps: {
      open: showSaveFilterModal,
      onClose: () => setShowSaveFilterModal(false),
      onSave: handleSaveFilter,
      defaultName: getDefaultFilterName(tableName),
    },

    // Props for RecallFilterModal
    recallModalProps: {
      open: showRecallFilterModal,
      onClose: () => setShowRecallFilterModal(false),
      savedFilters,
      onRecall: handleLoadFilter,
      onDelete: deleteFilter,
    },
  };
}
