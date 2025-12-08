//*........................................................
//*       www/thermal_eye_ui/src/components/ui_custom/table/ExportModal.tsx
//*       Export modal with CSV/XLSX options
//*       
//*       Extends: BaseModal
//*       Features: Export scope selection, progress tracking, cancellation
//*........................................................

import React, { useState } from 'react';
import { BaseModal } from '@/components/modals/BaseModal';
import { Button } from '@/components/ui_custom/button';
import { RadioGroup, RadioGroupItem } from '@/components/ui_custom/radio-group';
import { Label } from '@/components/ui_custom/label';

export type ExportFormat = 'csv' | 'xlsx';
export type ExportScope = 'selected' | 'visible' | 'all';

export interface ExportProgress {
  isExporting: boolean;
  current: number;
  total: number;
  cancelled: boolean;
  completed: boolean;
  exportedCount: number;
}

interface ExportModalProps {
  open: boolean;
  format: ExportFormat;
  selectedCount: number;
  visibleCount: number;
  totalCount: number;
  onExport: (scope: ExportScope) => Promise<void>;
  onClose: () => void;
  progress?: ExportProgress;
  onCancel?: () => void;
}

export function ExportModal({
  open,
  format,
  selectedCount,
  visibleCount,
  totalCount,
  onExport,
  onClose,
  progress,
  onCancel,
}: ExportModalProps) {
  const [selectedScope, setSelectedScope] = useState<ExportScope>(
    selectedCount > 0 ? 'selected' : 'visible'
  );

  const formatUpper = format.toUpperCase();
  const isExporting = progress?.isExporting || false;
  const isCompleted = progress?.completed || false;

  const handleExport = async () => {
    if (isExporting) return;
    await onExport(selectedScope);
  };

  const handleClose = () => {
    // Prevent closing during export unless cancelling
    if (isExporting && onCancel) {
      onCancel();
    } else if (!isExporting) {
      onClose();
    }
  };

  const progressPercent = progress?.total 
    ? Math.round((progress.current / progress.total) * 100) 
    : 0;

  return (
    <BaseModal 
      open={open} 
      onClose={handleClose}
      size="md"
      borderColor=""
    >
      <div className="flex items-center justify-between p-6 border-b">
        <h2 className="text-lg font-semibold">Export to {formatUpper}</h2>
        <Button
          type="button"
          variant="ghost"
          size="icon"
          onClick={handleClose}
          disabled={isExporting}
          className="h-8 w-8 p-0 text-2xl"
        >
          ×
        </Button>
      </div>

      <div className="p-6">
        <p className="text-sm text-muted-foreground mb-4">
          Choose which records to export:
        </p>

        <RadioGroup
          value={selectedScope}
          onValueChange={(value) => setSelectedScope(value as ExportScope)}
          disabled={isExporting}
          className="space-y-3 mb-6"
        >
          <Label
            htmlFor="scope-selected"
            className="flex items-center gap-3 p-3 border rounded-lg cursor-pointer hover:bg-muted/50"
          >
            <RadioGroupItem
              id="scope-selected"
              value="selected"
              disabled={selectedCount === 0 || isExporting}
            />
            <div className="flex-1">
              <span className="font-medium">Selected records ({selectedCount})</span>
              {selectedCount === 0 && (
                <span className="text-xs text-muted-foreground ml-2">(no records selected)</span>
              )}
            </div>
          </Label>

          <Label
            htmlFor="scope-visible"
            className="flex items-center gap-3 p-3 border rounded-lg cursor-pointer hover:bg-muted/50"
          >
            <RadioGroupItem
              id="scope-visible"
              value="visible"
              disabled={isExporting}
            />
            <div className="flex-1">
              <span className="font-medium">Visible records ({visibleCount})</span>
              <span className="text-xs text-muted-foreground ml-2">(current page)</span>
            </div>
          </Label>

          <Label
            htmlFor="scope-all"
            className="flex items-center gap-3 p-3 border rounded-lg cursor-pointer hover:bg-muted/50"
          >
            <RadioGroupItem
              id="scope-all"
              value="all"
              disabled={isExporting}
            />
            <div className="flex-1">
              <span className="font-medium">All records ({totalCount})</span>
              <span className="text-xs text-muted-foreground ml-2">(entire dataset)</span>
            </div>
          </Label>
        </RadioGroup>

        <p className="text-xs text-muted-foreground mb-4">
          Export will include only visible columns in their current order.
        </p>

        {/* Progress Bar */}
        {(isExporting || isCompleted) && progress && (
          <div className="p-4 border rounded-lg bg-muted/20 space-y-3">
            <div className="flex items-center gap-3">
              {isCompleted ? (
                <div className="flex items-center justify-center w-6 h-6 rounded-full bg-primary text-primary-foreground text-xs">
                  ✓
                </div>
              ) : (
                <div className="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin" />
              )}
              <span className="text-sm font-medium">
                {isCompleted
                  ? `Successfully exported ${progress.exportedCount} records to ${formatUpper}`
                  : progress.cancelled
                  ? 'Cancelling export...'
                  : 'Exporting records...'}
              </span>
            </div>

            <div>
              <div className="text-xs text-muted-foreground mb-2">
                {isCompleted
                  ? `${progress.exportedCount} of ${progress.exportedCount} records (100%)`
                  : `${progress.current} of ${progress.total} records (${progressPercent}%)`}
              </div>
              <div className="h-2 bg-muted rounded-full overflow-hidden">
                <div
                  className={`h-full transition-all duration-300 ${
                    isCompleted ? 'bg-primary' : 'bg-primary'
                  }`}
                  style={{ width: `${isCompleted ? 100 : progressPercent}%` }}
                />
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="flex justify-end gap-3 p-6 pt-0 border-t">
        <Button
          variant="ghost"
          onClick={handleClose}
        >
          {isExporting ? 'Cancel' : 'Close'}
        </Button>
        <Button onClick={handleExport} disabled={isExporting}>
          {isExporting ? 'Exporting...' : isCompleted ? 'Export Again' : 'Export'}
        </Button>
      </div>
    </BaseModal>
  );
}
