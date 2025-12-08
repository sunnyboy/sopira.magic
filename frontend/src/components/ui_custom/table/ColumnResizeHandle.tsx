//*........................................................
//*       www/thermal_eye_ui/src/components/ui_custom/table/ColumnResizeHandle.tsx
//*       Resize handle for table columns (Drag and Drop)
//*........................................................

import React from 'react';
import { cn } from '@/lib/utils';

interface ColumnResizeHandleProps {
  onMouseDown: (e: React.MouseEvent<HTMLDivElement>) => void;
  onTouchStart?: (e: React.TouchEvent<HTMLDivElement>) => void;
  isResizing?: boolean;
  className?: string;
}

export function ColumnResizeHandle({
  onMouseDown,
  onTouchStart,
  isResizing = false,
  className,
}: ColumnResizeHandleProps) {
  return (
    <div
      onMouseDown={onMouseDown}
      onTouchStart={onTouchStart}
      className={cn(
        "absolute right-0 top-0 h-full w-3 -translate-x-1/2 cursor-col-resize select-none touch-none",
        "flex items-center justify-center",
        "transition-colors",
        isResizing && "bg-primary/10",
        className,
        "group",
      )}
      style={{
        userSelect: "none",
        touchAction: "none",
      }}
    >
      <div
        className={cn(
          "h-[70%] w-px rounded-full",
          "bg-border/70 transition-colors",
          "group-hover:bg-primary/60",
          isResizing && "bg-primary",
        )}
      />
    </div>
  );
}


