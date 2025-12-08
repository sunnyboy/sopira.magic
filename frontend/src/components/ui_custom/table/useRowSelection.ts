//*........................................................
//*       www/thermal_eye_ui/src/components/ui_custom/table/useRowSelection.ts
//*       Hook for managing row selection state
//*........................................................

import { useState, useCallback } from 'react';

export function useRowSelection<TData extends { id: string | number }>() {
  const [selectedRows, setSelectedRows] = useState<Set<string>>(new Set());

  const toggleRow = useCallback((id: string | number) => {
    const idStr = String(id);
    setSelectedRows((prev) => {
      const next = new Set(prev);
      if (next.has(idStr)) {
        next.delete(idStr);
      } else {
        next.add(idStr);
      }
      return next;
    });
  }, []);

  const toggleAll = useCallback((data: TData[]) => {
    setSelectedRows((prev) => {
      const allIds = data.map((row) => String(row.id));
      const allSelected = allIds.every((id) => prev.has(id));

      if (allSelected) {
        // Deselect all
        const next = new Set(prev);
        allIds.forEach((id) => next.delete(id));
        return next;
      } else {
        // Select all
        const next = new Set(prev);
        allIds.forEach((id) => next.add(id));
        return next;
      }
    });
  }, []);

  const clearSelection = useCallback(() => {
    setSelectedRows(new Set());
  }, []);

  const isSelected = useCallback(
    (id: string | number) => {
      return selectedRows.has(String(id));
    },
    [selectedRows]
  );

  const isAllSelected = useCallback(
    (data: TData[]) => {
      if (data.length === 0) return false;
      return data.every((row) => selectedRows.has(String(row.id)));
    },
    [selectedRows]
  );

  const isIndeterminate = useCallback(
    (data: TData[]) => {
      if (data.length === 0) return false;
      const someSelected = data.some((row) => selectedRows.has(String(row.id)));
      const allSelected = data.every((row) => selectedRows.has(String(row.id)));
      return someSelected && !allSelected;
    },
    [selectedRows]
  );

  return {
    selectedRows,
    setSelectedRows,
    toggleRow,
    toggleAll,
    clearSelection,
    isSelected,
    isAllSelected,
    isIndeterminate,
    selectedCount: selectedRows.size,
  };
}
