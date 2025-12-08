//*........................................................
//*       www/thermal_eye_ui/src/components/ui_custom/table/ColumnsPanel.tsx
//*       Panel for managing column visibility and order with drag & drop
//*........................................................

import React from 'react';
import { GripVertical } from 'lucide-react';
import { type Column } from '@tanstack/react-table';
import { Checkbox } from '@/components/ui_custom/checkbox';
import { TablePanel } from './TablePanel';
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  type DragEndEvent,
} from '@dnd-kit/core';
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  useSortable,
  rectSortingStrategy,
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';

interface ColumnsPanelProps<TData> {
  columns: Column<TData, any>[];
  onReorder: (columnIds: string[]) => void;
  title?: string;
  icon?: React.ReactNode;
  activePresetName?: string | null;
  onSet?: () => void;
  onReset?: () => void;
  onRecall?: () => void;
  onClose?: () => void;
  onToggleDebug?: () => void;
  showDebug?: boolean;
  onSelectAll?: () => void;
  onDeselectAll?: () => void;
}

interface SortableColumnItemProps {
  column: any;
  isSelect: boolean;
}

function SortableColumnItem({ column, isSelect }: SortableColumnItemProps) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ 
    id: column.id,
    disabled: isSelect, // 'select' column cannot be reordered
  });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  const columnName =
    typeof column.columnDef.header === 'string'
      ? column.columnDef.header
      : column.id;

  return (
    <div
      ref={setNodeRef}
      style={style}
      className="flex items-center gap-2 p-2 border rounded-lg hover:bg-muted/50 bg-background"
    >
      {/* Drag handle */}
      <div
        {...attributes}
        {...listeners}
        className={`cursor-grab active:cursor-grabbing p-1 ${isSelect ? 'opacity-30 cursor-not-allowed' : ''}`}
        title={isSelect ? 'Selection column is fixed' : 'Drag to reorder'}
      >
        <GripVertical size={16} className="text-muted-foreground" />
      </div>

      {/* Visibility checkbox */}
      <Checkbox
        checked={column.getIsVisible()}
        onCheckedChange={(checked) => column.toggleVisibility(!!checked)}
      />

      {/* Column name */}
      <span className="flex-1 text-sm">{columnName}</span>
    </div>
  );
}

export function ColumnsPanel<TData>({
  columns,
  onReorder,
  title = 'Columns',
  icon,
  activePresetName,
  onSet,
  onReset,
  onRecall,
  onClose,
  onToggleDebug,
  showDebug,
  onSelectAll,
  onDeselectAll,
}: ColumnsPanelProps<TData>) {
  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  const columnIds = columns.map((col) => col.id);

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;

    if (!over || active.id === over.id) return;

    // Don't allow moving 'select' column
    if (active.id === 'select') return;

    const oldIndex = columnIds.indexOf(active.id as string);
    const newIndex = columnIds.indexOf(over.id as string);

    // Don't allow moving any column before 'select'
    if (columnIds[newIndex] === 'select' || newIndex === 0) return;

    const newOrder = arrayMove(columnIds, oldIndex, newIndex);
    onReorder(newOrder);
  };

  const handleSelectAll = () => {
    columns.forEach((column) => {
      if (!column.getIsVisible()) {
        column.toggleVisibility(true);
      }
    });
    if (onSelectAll) onSelectAll();
  };

  const handleDeselectAll = () => {
    columns.forEach((column) => {
      // Don't hide 'select' and 'actions' columns
      if (column.id !== 'select' && column.id !== 'actions' && column.getIsVisible()) {
        column.toggleVisibility(false);
      }
    });
    if (onDeselectAll) onDeselectAll();
  };

  return (
    <TablePanel
      open={true}
      title={title}
      icon={icon}
      activePresetName={activePresetName}
      onSet={onSet}
      onReset={onReset}
      onRecall={onRecall}
      onClose={onClose}
      onToggleDebug={onToggleDebug}
      showDebug={showDebug}
      onSelectAll={handleSelectAll}
      onDeselectAll={handleDeselectAll}
    >
      <DndContext
        sensors={sensors}
        collisionDetection={closestCenter}
        onDragEnd={handleDragEnd}
      >
        <SortableContext items={columnIds} strategy={rectSortingStrategy}>
          <div 
            className="grid gap-3"
            style={{
              gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))'
            }}
          >
            {columns.map((column) => (
              <SortableColumnItem
                key={column.id}
                column={column}
                isSelect={column.id === 'select'}
              />
            ))}
          </div>
        </SortableContext>
      </DndContext>
    </TablePanel>
  );
}