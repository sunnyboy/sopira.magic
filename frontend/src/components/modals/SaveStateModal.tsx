/**
 * SaveStateModal - Universal modal for saving table state presets
 * Works with any component (filters, columns, sorting, table, etc.)
 * 
 * Features:
 * - Real-time duplicate name validation
 * - Error display in modal (doesn't close on error)
 * - Support for hierarchical presets
 */

import React, { useState, useEffect } from 'react';
import { FormModal } from '@/components/modals/FormModal';
import { Input } from '@/components/ui_custom/input';
import { Textarea } from '@/components/ui_custom/textarea';
import { AlertCircle } from 'lucide-react';

export interface SaveStateModalProps {
  open: boolean;
  onClose: () => void;
  onSave: (name: string, description?: string) => Promise<void> | void;
  defaultName: string;
  title?: string;
  nameLabel?: string;
  descriptionLabel?: string;
  showDescription?: boolean;
  /** Check if preset name already exists (for real-time validation) */
  presetNameExists?: (name: string) => boolean;
  /** Initial error message (e.g., when opening modal due to duplicate) */
  initialError?: string;
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
  presetNameExists,
  initialError,
}: SaveStateModalProps) {
  const [presetName, setPresetName] = useState(defaultName);
  const [description, setDescription] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Reset state when modal opens
  useEffect(() => {
    if (open) {
      setPresetName(defaultName);
      setDescription('');
      setError(initialError || null);
      setIsSubmitting(false);
    }
  }, [open, defaultName, initialError]);

  // Real-time duplicate check
  const isDuplicate = presetNameExists ? presetNameExists(presetName.trim()) : false;

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    const trimmedName = presetName.trim();
    const trimmedDescription = description.trim();
    
    // Validate name length
    if (trimmedName.length === 0 || trimmedName.length > 255) {
      setError('Preset name is required (max 255 characters)');
      return;
    }
    
    // Check for duplicate
    if (isDuplicate) {
      setError('A preset with this name already exists. Please choose a different name.');
      return;
    }
    
    setIsSubmitting(true);
    setError(null);
    
    try {
      await onSave(trimmedName, showDescription ? trimmedDescription : undefined);
      onClose();
    } catch (err: any) {
      // Handle error from API (e.g., duplicate on backend)
      const errorMessage = err?.message || 'Failed to save preset';
      setError(errorMessage);
      setIsSubmitting(false);
    }
  };

  // Determine if save button should be disabled
  const isSaveDisabled = isSubmitting || isDuplicate || presetName.trim().length === 0;

  return (
    <FormModal
      open={open}
      title={title}
      onClose={onClose}
      onSubmit={handleSave}
      submitText={isSubmitting ? 'Saving...' : 'Save'}
      size="sm"
      submitDisabled={isSaveDisabled}
    >
      <div className="flex flex-col gap-4">
        {/* Error Message */}
        {error && (
          <div className="flex items-center gap-2 p-3 text-sm text-destructive bg-destructive/10 border border-destructive/20 rounded-md">
            <AlertCircle className="h-4 w-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}
        
        {/* Preset Name */}
        <label className="flex flex-col gap-1.5">
          <span className="text-sm font-medium">{nameLabel}</span>
          <Input
            value={presetName}
            onChange={(e) => {
              setPresetName(e.target.value.slice(0, 255));
              setError(null); // Clear error when user types
            }}
            placeholder="Enter preset name (max 255 chars)"
            maxLength={255}
            autoFocus
            required
            className={isDuplicate ? 'border-destructive' : ''}
          />
          <div className="flex justify-between items-center">
            <span className="text-xs text-muted-foreground">
              {presetName.length} / 255 characters
            </span>
            {isDuplicate && (
              <span className="text-xs text-destructive">
                Name already exists
              </span>
            )}
          </div>
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


