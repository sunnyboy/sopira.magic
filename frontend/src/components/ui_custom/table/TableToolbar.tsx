//*........................................................
//*       www/thermal_eye_ui/src/components/ui_custom/table/TableToolbar.tsx
//*       Unified toolbar with action buttons for all tables
//*
//*       Inheritance: Uses shadcn Button + cn utility for styling
//*       Deployed in: MeasurementsTable, FactoriesTable
//*       
//*       Features:
//*       - Toggle buttons: Filters, Columns, Compact mode
//*       - Action buttons: Add, Export (CSV/XLSX), Reset
//*       - Conditional buttons: Save (with count), Delete (with count)
//*       - Visual separator between main and action buttons
//*       - Fully customizable via className prop
//*       - Consistent spacing and styling across all tables
//*       - DRY principle: Single component for all table toolbars
//*........................................................

import React from 'react';
import { Button } from '@/components/ui_custom/button';
import { ToggleButton } from './ToggleButton';
import {
  SlidersHorizontal,
  Columns as ColumnsIcon,
  LayoutList,
  LayoutGrid,
  Plus,
  FileUp,
  Download,
  RotateCcw,
  Save,
  Trash2,
  Share2,
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface TableToolbarProps {
  // Toggle states
  showFilters?: boolean;
  showColumns?: boolean;
  compactMode?: boolean;
  
  // Callbacks
  onToggleFilters?: () => void;
  onToggleColumns?: () => void;
  onToggleCompact?: () => void;
  onAdd?: () => void;
  onExportCSV?: () => void;
  onExportXLSX?: () => void;
  onReset?: () => void;
  onSave?: () => void;
  onDelete?: () => void;
  onShare?: () => void;
  
  // Conditional display
  showAdd?: boolean;
  showExportCSV?: boolean;
  showExportXLSX?: boolean;
  showSave?: boolean;
  showDelete?: boolean;
  showShare?: boolean;
  
  // Counts/labels
  saveCount?: number;
  deleteCount?: number;
  shareCount?: number;
  
  // Custom buttons slot
  customButtons?: React.ReactNode;
  
  // Styling
  className?: string;
}

export function TableToolbar({
  showFilters = false,
  showColumns = false,
  compactMode = false,
  onToggleFilters,
  onToggleColumns,
  onToggleCompact,
  onAdd,
  onExportCSV,
  onExportXLSX,
  onReset,
  onSave,
  onDelete,
  onShare,
  showAdd = true,
  showExportCSV = true,
  showExportXLSX = true,
  showSave = false,
  showDelete = false,
  showShare = false,
  saveCount = 0,
  deleteCount = 0,
  shareCount = 0,
  customButtons,
  className,
}: TableToolbarProps) {
  // Check if we have any action buttons to show
  const hasActionButtons = (showSave && onSave && saveCount > 0) || (showDelete && onDelete && deleteCount > 0) || (showShare && onShare && shareCount > 0);
  
  return (
    <div className={cn("flex items-center gap-3 flex-wrap", className)}>
      {/* Main toolbar buttons */}
      {onToggleFilters && (
        <ToggleButton
          pressed={showFilters}
          onClick={onToggleFilters}
          icon={<SlidersHorizontal size={16} />}
        >
          Filters
        </ToggleButton>
      )}
      
      {onToggleColumns && (
        <ToggleButton
          pressed={showColumns}
          onClick={onToggleColumns}
          icon={<ColumnsIcon size={16} />}
        >
          Columns
        </ToggleButton>
      )}
      
      {onToggleCompact && (
        <ToggleButton
          pressed={compactMode}
          onClick={onToggleCompact}
          icon={compactMode ? <LayoutGrid size={16} /> : <LayoutList size={16} />}
        >
          {compactMode ? 'Expand' : 'Compact'}
        </ToggleButton>
      )}
      
      {showAdd && onAdd && (
        <Button onClick={onAdd} variant="solid">
          <Plus size={16} />
          Add
        </Button>
      )}
      
      {showExportCSV && onExportCSV && (
        <Button onClick={onExportCSV} variant="solid">
          <FileUp size={16} />
          CSV
        </Button>
      )}
      
      {showExportXLSX && onExportXLSX && (
        <Button onClick={onExportXLSX} variant="solid">
          <Download size={16} />
          XLSX
        </Button>
      )}
      
      {onReset && (
        <Button onClick={onReset} variant="solid">
          <RotateCcw size={16} />
          Reset
        </Button>
      )}
      
      {customButtons}
      
      {/* Action buttons (Save/Delete) - inline with other buttons */}
      {hasActionButtons && <div className="w-px h-6 bg-border" />}
      
      {showSave && onSave && saveCount > 0 && (
        <Button onClick={onSave} variant="solid">
          <Save size={16} />
          Save ({saveCount})
        </Button>
      )}
      
      {showShare && onShare && shareCount > 0 && (
        <Button onClick={onShare} variant="default">
          <Share2 size={16} />
          Share ({shareCount})
        </Button>
      )}
      
      {showDelete && onDelete && deleteCount > 0 && (
        <Button onClick={onDelete} variant="danger">
          <Trash2 size={16} />
          Delete ({deleteCount})
        </Button>
      )}
    </div>
  );
}
