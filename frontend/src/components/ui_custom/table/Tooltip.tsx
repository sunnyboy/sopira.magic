//*........................................................
//*       www/thermal_eye_ui/src/components/ui_custom/table/Tooltip.tsx
//*       Tooltip component with portal rendering
//*........................................................

import React from 'react';
import { createPortal } from 'react-dom';
import { TooltipState } from './useTooltip';

interface TooltipProps {
  tooltip: TooltipState | null;
}

export function Tooltip({ tooltip }: TooltipProps) {
  if (!tooltip) return null;

  return createPortal(
    <div
      className="fixed z-50 px-3 py-1.5 text-sm text-popover-foreground bg-popover rounded-md shadow-lg border border-border pointer-events-none whitespace-nowrap"
      style={{
        left: `${tooltip.x}px`,
        top: `${tooltip.y}px`,
        transform: 'translate(-50%, -100%)',
      }}
    >
      {tooltip.text}
    </div>,
    document.body
  );
}
