//*........................................................
//*       www/thermal_eye_ui/src/components/ui_custom/table/ToggleButton.tsx
//*       Toggle button with pressed/unpressed visual states
//*........................................................

import React from 'react';
import { Button } from '@/components/ui_custom/button';

interface ToggleButtonProps {
  pressed: boolean;
  onClick: () => void;
  icon?: React.ReactNode;
  children?: React.ReactNode;
  className?: string;
}

export function ToggleButton({
  pressed,
  onClick,
  icon,
  children,
  className = '',
}: ToggleButtonProps) {
  return (
    <Button
      onClick={onClick}
      className={`
        flex items-center gap-2 px-3 py-1.5 rounded transition-all
        ${pressed 
          ? 'bg-card text-primary border-2 border-primary shadow-md' 
          : 'bg-primary text-primary-foreground border-2 border-transparent hover:opacity-90'
        }
        ${className}
      `.trim()}
    >
      {icon}
      {children}
    </Button>
  );
}
