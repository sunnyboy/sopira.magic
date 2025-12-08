//*........................................................
//*       www/thermal_eye_ui/src/components/ui_custom/table/ExpandedRowRenderer.tsx
//*       Renderer for expanded table rows with 4-column grid layout
//*       Uses same cell renderers as compact mode for consistency
//*........................................................

import React from 'react';
import { flexRender, type Row, type Column } from '@tanstack/react-table';

interface ExpandedRowRendererProps<TData> {
  row: Row<TData>;
  visibleColumns: Column<TData, any>[];
  totalColSpan: number;
  excludeColumns?: string[];
  customRenderers?: Record<string, (data: TData) => React.ReactNode>;
}

export function ExpandedRowRenderer<TData>({
  row,
  visibleColumns,
  totalColSpan,
  excludeColumns = ['select', 'actions'],
  customRenderers = {},
}: ExpandedRowRendererProps<TData>) {
  const columnsToShow = visibleColumns.filter(
    (col) => !excludeColumns.includes(col.id)
  );

  return (
    <tr className="block">
      <td colSpan={totalColSpan} className="p-0 block">
        {/* Match scroll container width using viewport-relative sizing */}
        <div className="bg-muted/20 w-screen max-w-full -ml-[var(--scroll-offset,0px)]">
          {/* 4-column grid layout matching FilterRow design */}
          <div className="p-6 grid grid-cols-4 gap-3 max-w-[1200px] mx-auto">
          {columnsToShow.map((column) => {
            const columnName =
              typeof column.columnDef.header === 'string'
                ? column.columnDef.header
                : column.id;

            // Use custom renderer if provided (for graphs)
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
              <div
                key={column.id}
                className="flex flex-col gap-1.5 p-3 bg-muted/50 border border-border rounded-md"
              >
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
      </td>
    </tr>
  );
}
