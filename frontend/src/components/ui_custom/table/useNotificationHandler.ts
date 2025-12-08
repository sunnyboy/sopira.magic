//*........................................................
//*       www/thermal_eye_ui/src/components/ui_custom/table/useNotificationHandler.ts
//*       Centralized notification handler hook for all tables
//*       Extends useErrorHandler with sonner toast integration
//*........................................................

import { useState, useCallback } from 'react';
import { toast } from 'sonner';
import { ErrorDetails } from './ErrorModal';

export function useNotificationHandler() {
  const [error, setError] = useState<ErrorDetails | null>(null);
  const [isErrorModalOpen, setIsErrorModalOpen] = useState(false);

  // Success notifications (always use toast)
  const showSuccess = useCallback((message: string, duration = 4000) => {
    toast.success(message, { duration });
  }, []);

  // Warning notifications (always use toast)
  const showWarning = useCallback((message: string, duration = 3000) => {
    toast.warning(message, { duration });
  }, []);

  // Info notifications (always use toast)
  const showInfo = useCallback((message: string, duration = 2000) => {
    toast.info(message, { duration });
  }, []);

  // Error notifications (use modal for complex errors, toast for simple ones)
  const showError = useCallback((errorDetails: ErrorDetails | string) => {
    // If string provided, convert to ErrorDetails
    if (typeof errorDetails === 'string') {
      toast.error(errorDetails, { duration: 5000 });
      return;
    }

    // If has technical details, use modal for better UX
    if (errorDetails.technicalDetails) {
      setError(errorDetails);
      setIsErrorModalOpen(true);
    } else {
      // Simple error - use toast
      toast.error(errorDetails.message, { duration: 5000 });
    }
  }, []);

  // Convenience handlers for specific operations
  const handleSaveError = useCallback((recordId: string | number, err: any) => {
    showError({
      recordId,
      operation: 'save',
      message: extractErrorMessage(err),
      technicalDetails: extractTechnicalDetails(err),
    });
  }, [showError]);

  const handleDeleteError = useCallback((recordId: string | number, err: any) => {
    showError({
      recordId,
      operation: 'delete',
      message: extractErrorMessage(err),
      technicalDetails: extractTechnicalDetails(err),
    });
  }, [showError]);

  const handleCreateError = useCallback((err: any) => {
    showError({
      operation: 'create',
      message: extractErrorMessage(err),
      technicalDetails: extractTechnicalDetails(err),
    });
  }, [showError]);

  const handleLoadError = useCallback((err: any) => {
    showError({
      operation: 'load',
      message: extractErrorMessage(err),
      technicalDetails: extractTechnicalDetails(err),
    });
  }, [showError]);

  const handleExportError = useCallback((err: any) => {
    showError({
      operation: 'export',
      message: extractErrorMessage(err),
      technicalDetails: extractTechnicalDetails(err),
    });
  }, [showError]);

  const closeErrorModal = useCallback(() => {
    setIsErrorModalOpen(false);
    // Clear error after animation
    setTimeout(() => setError(null), 300);
  }, []);

  return {
    // Toast notifications
    showSuccess,
    showWarning,
    showInfo,
    // Error handling (modal or toast)
    error,
    isErrorModalOpen,
    showError,
    handleSaveError,
    handleDeleteError,
    handleCreateError,
    handleLoadError,
    handleExportError,
    closeErrorModal,
  };
}

/**
 * Extract user-friendly error message from various error types
 */
function extractErrorMessage(err: any): string {
  if (typeof err === 'string') return err;
  if (err?.message) return err.message;
  if (err?.error) return err.error;
  if (err?.detail) return err.detail;
  
  // Django REST Framework error format
  if (err?.response?.data) {
    const data = err.response.data;
    if (typeof data === 'string') return data;
    if (data.detail) return data.detail;
    
    // Field-specific errors
    const fieldErrors = Object.entries(data)
      .filter(([key]) => key !== 'detail')
      .map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(', ') : String(value)}`)
      .join(' | ');
    
    if (fieldErrors) return fieldErrors;
  }
  
  return 'An unexpected error occurred';
}

/**
 * Extract technical details for debugging
 */
function extractTechnicalDetails(err: any): string | undefined {
  try {
    return JSON.stringify(err, null, 2);
  } catch {
    return String(err);
  }
}




