/**
 * StateStatusLine - Displays active preset status for state-managed components
 * 
 * Features:
 * - Shows active preset name (or "Custom" if no preset)
 * - Modified indicator when state differs from loaded preset
 * - Revert link to restore original preset state
 * - Save modification link to persist changes
 * - Compact inline display for panels
 */

import React from 'react';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import { Bookmark, BookmarkCheck, Edit3 } from 'lucide-react';

export interface StateStatusLineProps {
  /** Name of the active preset (null if no preset loaded) */
  activePresetName: string | null;
  /** Whether the current state has been modified from the loaded preset */
  isModified?: boolean;
  /** Label prefix (e.g., "Columns", "Filters") */
  label?: string;
  /** Compact mode for inline display in panels */
  compact?: boolean;
  /** Additional CSS classes */
  className?: string;
  /** Show icon */
  showIcon?: boolean;
  /** Callback to revert to original preset state */
  onRevert?: () => void;
  /** Callback to save modifications to existing preset */
  onSaveModification?: () => void;
  /** Whether save operation is in progress */
  isSaving?: boolean;
}

/**
 * StateStatusLine - Shows active preset status
 * 
 * @example
 * ```tsx
 * // In a panel header
 * <StateStatusLine 
 *   activePresetName={columnsState.activePresetName}
 *   isModified={false}
 *   label="Columns"
 *   compact
 * />
 * 
 * // With modification actions
 * <StateStatusLine 
 *   activePresetName="My Preset"
 *   isModified={true}
 *   onRevert={handleRevert}
 *   onSaveModification={handleSave}
 * />
 * ```
 */
export function StateStatusLine({
  activePresetName,
  isModified = false,
  label,
  compact = false,
  className,
  showIcon = true,
  onRevert,
  onSaveModification,
  isSaving = false,
}: StateStatusLineProps) {
  // Determine display text
  const displayName = activePresetName || 'Custom';
  const hasPreset = activePresetName !== null;
  const showModificationActions = isModified && hasPreset && (onRevert || onSaveModification);

  if (compact) {
    // Compact inline display for panel headers
    return (
      <div className={cn('flex items-center gap-1.5 text-xs flex-wrap', className)}>
        {showIcon && (
          hasPreset ? (
            <BookmarkCheck className="h-3 w-3 text-primary" />
          ) : (
            <Bookmark className="h-3 w-3 text-muted-foreground" />
          )
        )}
        {label && (
          <span className="text-muted-foreground">{label}:</span>
        )}
        {/* Preset name - clickable when modified to revert */}
        {showModificationActions && onRevert ? (
          <button
            onClick={onRevert}
            className="state-status-preset-link font-medium truncate max-w-[120px]"
            title="Click to revert to saved state"
          >
            "{displayName}"
          </button>
        ) : (
          <span className={cn(
            'font-medium truncate max-w-[120px]',
            hasPreset ? 'text-primary' : 'text-muted-foreground'
          )}>
            "{displayName}"
          </span>
        )}
        {/* Save modification link */}
        {showModificationActions && onSaveModification && (
          <button
            onClick={onSaveModification}
            disabled={isSaving}
            className="state-status-save-link"
          >
            ({isSaving ? 'saving...' : 'save modification'})
          </button>
        )}
        {/* Modified indicator when no actions available */}
        {isModified && !showModificationActions && (
          <Edit3 className="h-3 w-3 text-warning" title="Modified" />
        )}
      </div>
    );
  }

  // Full display with badge
  return (
    <div className={cn('flex items-center gap-2 flex-wrap', className)}>
      {showIcon && (
        hasPreset ? (
          <BookmarkCheck className="h-4 w-4 text-primary" />
        ) : (
          <Bookmark className="h-4 w-4 text-muted-foreground" />
        )
      )}
      {label && (
        <span className="text-sm text-muted-foreground">{label}:</span>
      )}
      {/* Preset name - clickable when modified to revert */}
      {showModificationActions && onRevert ? (
        <button
          onClick={onRevert}
          className="state-status-preset-link-badge"
          title="Click to revert to saved state"
        >
          "{displayName}"
        </button>
      ) : (
        <Badge 
          variant={hasPreset ? 'default' : 'secondary'}
          className={cn(
            'font-medium',
            isModified && !showModificationActions && 'border-warning'
          )}
        >
          "{displayName}"
        </Badge>
      )}
      {/* Save modification link */}
      {showModificationActions && onSaveModification && (
        <button
          onClick={onSaveModification}
          disabled={isSaving}
          className="state-status-save-link"
        >
          ({isSaving ? 'saving...' : 'save modification'})
        </button>
      )}
      {/* Modified indicator when no actions available */}
      {isModified && !showModificationActions && (
        <Edit3 className="h-4 w-4 text-warning ml-1" title="Modified" />
      )}
    </div>
  );
}

export default StateStatusLine;
