/**
 * SaveStateModal - Universal modal for saving table state presets
 * Works with any component (filters, columns, sorting, table, etc.)
 */

import React, { useState, useEffect } from 'react';
import { FormModal } from '@/components/modals/FormModal';
import { Input } from '@/components/ui_custom/input';
import { Textarea } from '@/components/ui_custom/textarea';

export interface SaveStateModalProps {
  open: boolean;
  onClose: () => void;
  onSave: (name: string, description?: string) => Promise<void> | void;
  defaultName: string;
  title?: string;
  nameLabel?: string;
  descriptionLabel?: string;
  showDescription?: boolean;
}

export function SaveStateModal({
  open,
  onClose,
  onSave,
  defaultName,
  title = 'Save State',
  nameLabel = 'Preset Name',
  descriptionLabel = 'Description (optional)',
  showDescription = true,
}: SaveStateModalProps) {
  const [presetName, setPresetName] = useState(defaultName);
  const [description, setDescription] = useState('');

  useEffect(() => {
    if (open) {
      setPresetName(defaultName);
      setDescription('');
    }
  }, [open, defaultName]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    const trimmedName = presetName.trim();
    const trimmedDescription = description.trim();
    
    if (trimmedName.length > 0 && trimmedName.length <= 255) {
      await onSave(trimmedName, showDescription ? trimmedDescription : undefined);
      onClose();
    }
  };

  return (
    <FormModal
      open={open}
      title={title}
      onClose={onClose}
      onSubmit={handleSave}
      submitText="Save"
      size="sm"
    >
      <div className="flex flex-col gap-4">
        {/* Preset Name */}
        <label className="flex flex-col gap-1.5">
          <span className="text-sm font-medium">{nameLabel}</span>
          <Input
            value={presetName}
            onChange={(e) => setPresetName(e.target.value.slice(0, 255))}
            placeholder="Enter preset name (max 255 chars)"
            maxLength={255}
            autoFocus
            required
          />
          <span className="text-xs text-muted-foreground">
            {presetName.length} / 255 characters
          </span>
        </label>

        {/* Description (optional) */}
        {showDescription && (
          <label className="flex flex-col gap-1.5">
            <span className="text-sm font-medium">{descriptionLabel}</span>
            <Textarea
              value={description}
              onChange={(e) => setDescription(e.target.value.slice(0, 500))}
              placeholder="Enter description (max 500 chars)"
              maxLength={500}
              rows={3}
              className="resize-none"
            />
            <span className="text-xs text-muted-foreground">
              {description.length} / 500 characters
            </span>
          </label>
        )}
      </div>
    </FormModal>
  );
}


