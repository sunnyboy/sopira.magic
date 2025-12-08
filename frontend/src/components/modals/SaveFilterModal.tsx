//*........................................................
//*       www/thermal_eye_ui/src/components/ui_custom/table/SaveFilterModal.tsx
//*       Modal for saving filter state with custom name
//*........................................................

import React, { useState, useEffect } from 'react';
import { FormModal } from '@/components/modals/FormModal';
import { Input } from '@/components/ui_custom/input';

interface SaveFilterModalProps {
  open: boolean;
  onClose: () => void;
  onSave: (name: string) => Promise<void> | void;
  defaultName: string;
}

export function SaveFilterModal({
  open,
  onClose,
  onSave,
  defaultName,
}: SaveFilterModalProps) {
  const [filterName, setFilterName] = useState(defaultName);

  useEffect(() => {
    if (open) {
      setFilterName(defaultName);
    }
  }, [open, defaultName]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = filterName.trim();
    if (trimmed.length > 0 && trimmed.length <= 64) {
      await onSave(trimmed);
      onClose(); // Zavri modal po úspešnom uložení
    }
  };

  return (
    <FormModal
      open={open}
      title="Save Filter"
      onClose={onClose}
      onSubmit={handleSave}
      submitText="Save"
      size="sm"
    >
      <div className="flex flex-col gap-3">
        <label className="flex flex-col gap-1">
          <span className="text-sm font-medium">Filter Name</span>
          <Input
            value={filterName}
            onChange={(e) => setFilterName(e.target.value.slice(0, 64))}
            placeholder="Enter filter name (max 64 chars)"
            maxLength={64}
            autoFocus
          />
          <span className="text-xs text-muted-foreground">
            {filterName.length} / 64 characters
          </span>
        </label>
      </div>
    </FormModal>
  );
}
