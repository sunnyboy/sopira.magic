//*........................................................
//*       www/thermal_eye_ui/src/components/TableModals.tsx
//*       Modal components for table operations
//*........................................................

/************************************************************************
 *  src/components/TableModals.tsx
 *  Reusable modal components for table CRUD operations
 ************************************************************************/

import React from 'react';
import { motion } from 'framer-motion';

interface ConfirmDialogProps {
  open: boolean;
  title: string;
  message: string;
  onConfirm: () => void;
  onCancel: () => void;
}

export const ConfirmDialog: React.FC<ConfirmDialogProps> = ({
  open,
  title,
  message,
  onConfirm,
  onCancel,
}) => {
  if (!open) return null;

  return (
    <div className="te-modal-overlay">
      <motion.div
        initial={{ scale: 0.95, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        className="te-modal-content"
      >
        <div className="te-modal-header">
          <h2 className="te-modal-title">{title}</h2>
          <button className="te-modal-close" onClick={onCancel}>
            ×
          </button>
        </div>
        <div className="te-modal-body">{message}</div>
        <div className="te-modal-actions">
          <button className="te-btn ghost" onClick={onCancel}>
            Cancel
          </button>
          <button className="te-btn danger" onClick={onConfirm}>
            Delete
          </button>
        </div>
      </motion.div>
    </div>
  );
};
