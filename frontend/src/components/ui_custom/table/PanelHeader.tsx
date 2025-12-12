//*........................................................
//*       www/thermal_eye_ui/src/components/ui_custom/table/PanelHeader.tsx
//*       Reusable panel header with title and action buttons
//*........................................................

import React from 'react';
import { Button } from '@/components/ui_custom/button';
import { Save, RotateCcw, Clock, X, Bug, CheckSquare, Square } from 'lucide-react';
import { StateStatusLine } from '@/components/ui_custom/StateStatusLine';

interface PanelHeaderProps {
  title: string;
  icon?: React.ReactNode;
  activePresetName?: string | null;
  /** Whether the current state has been modified from loaded preset */
  isModified?: boolean;
  /** Callback to revert to loaded preset state */
  onRevertToPreset?: () => void;
  /** Callback to save modifications to existing preset */
  onSaveModification?: () => void;
  /** Whether save operation is in progress */
  isSaving?: boolean;
  onSet?: () => void;
  onReset?: () => void;
  onRecall?: () => void;
  onClose?: () => void;
  onToggleDebug?: () => void;
  showDebug?: boolean;
  onSelectAll?: () => void;
  onDeselectAll?: () => void;
}

export function PanelHeader({
  title,
  icon,
  activePresetName,
  isModified = false,
  onRevertToPreset,
  onSaveModification,
  isSaving = false,
  onSet,
  onReset,
  onRecall,
  onClose,
  onToggleDebug,
  showDebug = false,
  onSelectAll,
  onDeselectAll,
}: PanelHeaderProps) {
  return (
    <div className="mb-4 pb-3 border-b border-border">
      {/* First row: Title + Icon (left) and Action Buttons (right) */}
      <div className="flex items-center justify-between">
        {/* Left: Title + Icon */}
        <div className="flex items-center gap-2 text-sm font-semibold">
          {icon}
          <span>{title}</span>
        </div>

        {/* Right: Action Buttons */}
        <div className="flex items-center gap-2">
          {onToggleDebug && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onToggleDebug}
              className={`h-8 px-2 text-xs ${showDebug ? 'bg-muted' : ''}`}
              title="Toggle debug info (column widths)"
            >
              <Bug size={14} className="mr-1" />
              Debug
            </Button>
          )}
          {onSelectAll && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onSelectAll}
              className="h-8 px-2 text-xs"
              title="Select all columns"
            >
              <CheckSquare size={14} className="mr-1" />
              Select All
            </Button>
          )}
          {onDeselectAll && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onDeselectAll}
              className="h-8 px-2 text-xs"
              title="Deselect all columns"
            >
              <Square size={14} className="mr-1" />
              Deselect All
            </Button>
          )}
          {onSet && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onSet}
              className="h-8 px-2 text-xs"
              title="Save current state"
            >
              <Save size={14} className="mr-1" />
              Set
            </Button>
          )}
          {onReset && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onReset}
              className="h-8 px-2 text-xs"
              title="Reset to defaults"
            >
              <RotateCcw size={14} className="mr-1" />
              Reset
            </Button>
          )}
          {onRecall && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onRecall}
              className="h-8 px-2 text-xs"
              title="Recall saved state"
            >
              <Clock size={14} className="mr-1" />
              Recall
            </Button>
          )}
          {onClose && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onClose}
              className="h-8 px-2 text-xs"
              title="Close panel"
            >
              <X size={14} className="mr-1" />
              Close
            </Button>
          )}
        </div>
      </div>
      
      {/* Second row: Currently loaded setting with modification actions */}
      {activePresetName && (
        <div className="flex justify-end mt-2">
          <span className="text-xs text-muted-foreground">
            Currently loaded setting:{' '}
          </span>
          <StateStatusLine
            activePresetName={activePresetName}
            isModified={isModified}
            onRevert={onRevertToPreset}
            onSaveModification={onSaveModification}
            isSaving={isSaving}
            compact
            showIcon={false}
            className="ml-1"
          />
        </div>
      )}
    </div>
  );
}
