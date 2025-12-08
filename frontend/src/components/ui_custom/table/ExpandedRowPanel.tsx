//*........................................................
//*       www/thermal_eye_ui/src/components/ui_custom/table/ExpandedRowPanel.tsx
//*       Panel for displaying expanded row content (similar to FilterPanel)
//*       DRY shared component for all tables
//*........................................................

import React from 'react';
import { flexRender, type Row, type Column } from '@tanstack/react-table';

interface ExpandedRowPanelProps<TData> {
  row: Row<TData>;
  visibleColumns: Column<TData, any>[];
  excludeColumns?: string[];
  customRenderers?: Record<string, (data: TData) => React.ReactNode>;
  onClose: () => void;
}

export function ExpandedRowPanel<TData>({
  row,
  visibleColumns,
  excludeColumns = ['select', 'actions'],
  customRenderers = {},
  onClose,
}: ExpandedRowPanelProps<TData>) {
  const columnsToShow = visibleColumns.filter(
    (col) => !excludeColumns.includes(col.id)
  );

  return (
    <div className="bg-muted/10 border-t border-b border-border animate-in slide-in-from-top-2">
      {/* Header with close button */}
      <div className="flex items-center justify-between p-3 border-b border-border bg-background/50">
        <div className="text-sm font-medium">
          Record Details: {String((row.original as any).id || '').slice(0, 16)}...
        </div>
        <button
          onClick={onClose}
          className="text-muted-foreground hover:text-foreground transition-colors"
          title="Close expanded view"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>

      {/* 4-column grid content */}
      <div className="p-6 grid grid-cols-4 gap-3">
        {columnsToShow.map((column) => {
          const columnName =
            typeof column.columnDef.header === 'string'
              ? column.columnDef.header
              : column.id;

          // Use custom renderer if provided (for graphs, etc.)
          const customRenderer = customRenderers[column.id];
          let content: React.ReactNode;

          if (customRenderer) {
            content = customRenderer(row.original);
          } else {
            // Reuse exact same cell renderer from compact mode
            const cell = row
              .getVisibleCells()
              .find((c) => c.column.id === column.id);
            content = cell
              ? flexRender(column.columnDef.cell, cell.getContext())
              : '—';
          }

          return (
            <div key={column.id} className="flex flex-col gap-1.5 p-3 bg-muted/50 border border-border rounded-md">
              {/* Label matching filter input style */}
              <label className="text-xs font-medium text-muted-foreground">
                {columnName}
              </label>
              {/* Content uses same cell renderer as compact mode */}
              <div className="w-full text-xs">{content}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
