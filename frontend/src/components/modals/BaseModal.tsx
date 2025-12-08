//*........................................................
//*       www/thermal_eye_ui/src/components/ui_custom/table/BaseModal.tsx
//*       Base modal component - parent of all modals (DRY principle)
//*
//*       Purpose: Shared modal logic for all modal types
//*       
//*       Children modals (use BaseModal or FormModal):
//*       - FormModal (form with Submit/Cancel) 
//*         → SaveFilterModal, SaveStateModal, ShareFactoryModal
//*       - ConfirmModal (yes/no confirmation for dangerous operations)
//*       - ErrorModal (error display with technical details)
//*       - ExportModal (export options with progress tracking)
//*       - LoadStateModal (load saved table states)
//*       - RecallFilterModal (load saved filters)
//*       - FactorySelectionModal (multi-select factories)
//*       - UserSelectionModal (multi-select users)
//*       
//*       Inheritance: Uses Framer Motion + cn utility
//*       
//*       Shared Features:
//*       - ESC key handling
//*       - Click outside to close
//*       - Body scroll lock
//*       - AnimatePresence animations
//*       - Backdrop blur overlay
//*       - Customizable size and styling
//*........................................................

import React, { useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '@/lib/utils';

interface BaseModalProps {
  open: boolean;
  onClose: () => void;
  children: React.ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
  borderColor?: string; // e.g. "border-green-200 dark:border-green-800"
}

const sizeClasses = {
  sm: 'max-w-md',
  md: 'max-w-lg',
  lg: 'max-w-2xl',
  xl: 'max-w-4xl',
};

export function BaseModal({
  open,
  onClose,
  children,
  size = 'md',
  className,
  borderColor = 'border-border',
}: BaseModalProps) {
  // Handle ESC key to close modal
  useEffect(() => {
    if (!open) return;

    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [open, onClose]);

  // Prevent body scroll when modal is open
  useEffect(() => {
    if (open) {
      document.body.style.overflow = 'hidden';
      return () => {
        document.body.style.overflow = '';
      };
    }
  }, [open]);

  return (
    <AnimatePresence>
      {open && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4"
          onClick={(e) => {
            if (e.target === e.currentTarget) onClose();
          }}
        >
          <motion.div
            initial={{ scale: 0.95, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.95, opacity: 0 }}
            transition={{ duration: 0.15 }}
            className={cn(
              "bg-background rounded-lg shadow-xl border w-full",
              sizeClasses[size],
              borderColor,
              className
            )}
          >
            {children}
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}
