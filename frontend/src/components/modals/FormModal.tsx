//*........................................................
//*       www/thermal_eye_ui/src/components/ui_custom/table/FormModal.tsx
//*       Generic form modal wrapper for Add/Edit operations
//*
//*       Primary use: Adding new records via "Add" button
//*       Secondary use: Editing records in modal (not inline)
//*       
//*       Inheritance: Extends BaseModal (parent component)
//*       Deployment: Should be used by AddFactoryModal, EditFactoryModal, etc.
//*       
//*       Features:
//*       - Four size variants: sm, md (default), lg, xl
//*       - Scrollable content area with max height
//*       - Form submit handling
//*       - Customizable submit/cancel text
//*       - Children slot for form fields
//*       - Blue border (inherited from BaseModal)
//*........................................................

import React from 'react';
import { Button } from '@/components/ui_custom/button';
import { BaseModal } from '@/components/modals/BaseModal';

interface FormModalProps {
  open: boolean;
  title: string | React.ReactNode;  // Allow ReactNode for styled titles
  onClose: () => void;
  onSubmit: (e: React.FormEvent) => void;
  children: React.ReactNode;
  beforeFormContent?: React.ReactNode;
  submitText?: string;
  cancelText?: string;
  /** Disable the submit button */
  submitDisabled?: boolean;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
  initialFocusRef?: React.RefObject<HTMLElement | null>;
  scrollResetDeps?: React.DependencyList;
}

export function FormModal({
  open,
  title,
  onClose,
  onSubmit,
  children,
  beforeFormContent,
  submitText = 'Save',
  cancelText = 'Cancel',
  submitDisabled = false,
  size = 'md',
  className,
  initialFocusRef,
  scrollResetDeps = [],
}: FormModalProps) {
  const scrollContainerRef = React.useRef<HTMLDivElement | null>(null);

  React.useEffect(() => {
    if (!open) return;
    const container = scrollContainerRef.current;
    if (!container) return;
    const raf = requestAnimationFrame(() => {
      container.scrollTo({ top: 0, behavior: 'smooth' });
      const target = initialFocusRef?.current;
      if (target && typeof target.focus === 'function') {
        target.focus({ preventScroll: true } as any);
      }
    });
    return () => cancelAnimationFrame(raf);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open, initialFocusRef, ...scrollResetDeps]);

  return (
    <BaseModal
      open={open}
      onClose={onClose}
      size={size}
      borderColor=""
      className={className}
    >
      <div className="flex items-center justify-between p-6 border-b border-border">
        <div className="text-lg font-semibold">{title}</div>
        <Button
          type="button"
          variant="ghost"
          size="icon"
          onClick={onClose}
          className="h-8 w-8 p-0 text-2xl hover:text-destructive"
        >
          ×
        </Button>
      </div>

      <form onSubmit={onSubmit}>
        <div
          ref={scrollContainerRef}
          className="p-6 max-h-[calc(100vh-16rem)] overflow-y-auto"
        >
          {beforeFormContent}
          {children}
        </div>

        <div className="flex justify-end gap-3 p-6 pt-0 border-t border-border">
          <Button type="button" variant="ghost" onClick={onClose}>
            {cancelText}
          </Button>
          <Button type="submit" disabled={submitDisabled}>
            {submitText}
          </Button>
        </div>
      </form>
    </BaseModal>
  );
}
