//*........................................................
//*       www/thermal_eye_ui/src/components/ui_custom/table/useTooltip.ts
//*       Hook for tooltip positioning and state
//*........................................................

import { useState, useCallback } from 'react';

export interface TooltipState {
  text: string;
  x: number;
  y: number;
}

export function useTooltip() {
  const [tooltip, setTooltip] = useState<TooltipState | null>(null);

  const showTooltip = useCallback((text: string, event: React.MouseEvent) => {
    if (!text) return; // Don't show empty tooltips
    const rect = event.currentTarget.getBoundingClientRect();
    setTooltip({
      text,
      x: rect.left + rect.width / 2,
      y: rect.top - 10
    });
  }, []);

  const hideTooltip = useCallback(() => {
    setTooltip(null);
  }, []);

  return { tooltip, showTooltip, hideTooltip };
}
