//*........................................................
//*       frontend/src/components/ui_custom/EmptyState.tsx
//*       Empty state component with icon, message, and optional action
//*
//*       Purpose: Display empty state with customizable content
//*       Features: Icon, message, optional action button
//*........................................................

import React from 'react';
import { AlertCircle, Info, XCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';

export interface EmptyStateProps {
  /** Message to display */
  message: string;
  /** Icon to display (default: 'AlertCircle') */
  icon?: 'AlertCircle' | 'Info' | 'XCircle' | React.ReactNode;
  /** Optional action button label */
  actionLabel?: string;
  /** Optional action button onClick handler */
  onAction?: () => void;
  /** Optional action button variant */
  actionVariant?: 'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link';
}

/**
 * EmptyState component
 * 
 * Displays an icon, message, and optional action button
 * Used for empty tables, missing dependencies, etc.
 */
export function EmptyState({
  message,
  icon = 'AlertCircle',
  actionLabel,
  onAction,
  actionVariant = 'default',
}: EmptyStateProps) {
  // Render icon based on type
  const renderIcon = () => {
    if (React.isValidElement(icon)) {
      return icon;
    }

    const IconComponent = 
      icon === 'Info' ? Info :
      icon === 'XCircle' ? XCircle :
      AlertCircle;

    return <IconComponent className="w-12 h-12 mb-4 text-muted-foreground" />;
  };

  return (
    <div className="flex flex-col items-center justify-center p-8 text-center">
      {renderIcon()}
      <p className="text-muted-foreground mb-4">{message}</p>
      {actionLabel && onAction && (
        <Button onClick={onAction} variant={actionVariant}>
          {actionLabel}
        </Button>
      )}
    </div>
  );
}
