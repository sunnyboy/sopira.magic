//*........................................................
//*       www/thermal_eye_ui/src/components/ui_custom/table/ConfirmModal.tsx
//*       Confirmation dialog modal for dangerous operations
//*
//*       Primary use: Confirming delete operations (single/bulk)
//*       Secondary use: Any "Are you sure?" confirmation needed
//*       
//*       Inheritance: Extends BaseModal (parent component)
//*       Uses: shadcn Button + cn utility
//*       
//*       Features:
//*       - Two variants: 'danger' (red) and 'default' (blue)
//*       - Auto-close after confirm (configurable)
//*       - Pale green border (inherited from BaseModal)
//*........................................................

import React from 'react';
import { Button } from '@/components/ui_custom/button';
import { cn } from '@/lib/utils';
import { BaseModal } from '@/components/modals/BaseModal';

interface ConfirmModalProps {
  open: boolean;
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  variant?: 'danger' | 'default';
  onConfirm: () => void;
  onCancel: () => void;
  autoClose?: boolean; // Auto-close after confirm (default: true)
  className?: string; // Custom styling for modal content
}

export function ConfirmModal({
  open,
  title,
  message,
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  variant = 'default',
  onConfirm,
  onCancel,
  autoClose = true,
  className,
}: ConfirmModalProps) {
  const handleConfirm = () => {
    onConfirm();
    if (autoClose) {
      onCancel();
    }
  };

  return (
    <BaseModal
      open={open}
      onClose={onCancel}
      size="sm"
      borderColor=""
      className={className}
    >
      <div className="p-6 border-b border-border">
        <h2 className={cn(
          "text-lg font-semibold",
          variant === 'danger' && 'text-destructive'
        )}>
          {title}
        </h2>
      </div>
      
      <div className="p-6">
        <p className="text-sm text-muted-foreground whitespace-pre-line">
          {message}
        </p>
      </div>
      
      <div className="flex justify-end gap-3 p-6 pt-0">
        <Button variant="ghost" onClick={onCancel}>
          {cancelText}
        </Button>
        <Button
          variant={variant === 'danger' ? 'destructive' : 'default'}
          onClick={handleConfirm}
        >
          {confirmText}
        </Button>
      </div>
    </BaseModal>
  );
}
