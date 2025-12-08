//*........................................................
//*       www/thermal_eye_ui/src/components/ui_custom/table/useEscapeKey.ts
//*       Hook for handling ESC key press events
//*........................................................

import { useEffect } from 'react';

/**
 * Hook to handle Escape key press for closing modals/panels
 * Pass callbacks in priority order - first callback that's defined will be called
 */
export function useEscapeKey(...callbacks: Array<(() => void) | undefined>) {
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        // Find first defined callback and execute it
        const callback = callbacks.find(cb => cb !== undefined);
        if (callback) callback();
      }
    };
    
    window.addEventListener('keydown', handleEscape);
    return () => window.removeEventListener('keydown', handleEscape);
  }, [callbacks]);
}
