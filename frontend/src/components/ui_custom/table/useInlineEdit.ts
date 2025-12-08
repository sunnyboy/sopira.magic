//*........................................................
//*       www/thermal_eye_ui/src/components/ui_custom/table/useInlineEdit.ts
//*       Hook for inline table cell editing
//*........................................................

import { useState, useCallback } from 'react';

export interface EditingCell {
  id: string | number;
  field: string;
}

export function useInlineEdit() {
  const [editingCell, setEditingCell] = useState<EditingCell | null>(null);

  const startEdit = useCallback((id: string | number, field: string) => {
    setEditingCell({ id, field });
  }, []);

  const stopEdit = useCallback(() => {
    setEditingCell(null);
  }, []);

  const isEditing = useCallback((id: string | number, field: string) => {
    return editingCell?.id === id && editingCell?.field === field;
  }, [editingCell]);

  return {
    editingCell,
    startEdit,
    stopEdit,
    isEditing,
  };
}
