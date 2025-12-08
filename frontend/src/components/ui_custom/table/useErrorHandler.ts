//*........................................................
//*       www/thermal_eye_ui/src/components/ui_custom/table/useErrorHandler.ts
//*       Centralized error handler hook for all tables
//*........................................................

import { useState, useCallback } from 'react';
import { ErrorDetails } from '@/components/modals/ErrorModal';

export function useErrorHandler() {
  const [error, setError] = useState<ErrorDetails | null>(null);
  const [isErrorModalOpen, setIsErrorModalOpen] = useState(false);

  const showError = useCallback((errorDetails: ErrorDetails) => {
    setError(errorDetails);
    setIsErrorModalOpen(true);
  }, []);

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
  // Handle HTTP status codes directly
  if (err?.status === 405) {
    return 'Táto operácia nie je podporovaná. Server nepodporuje túto HTTP metódu.';
  }
  if (err?.status === 403) {
    return 'Nemáte oprávnenie na vykonanie tejto operácie.';
  }
  if (err?.status === 404) {
    return 'Záznam nebol nájdený.';
  }
  if (err?.status === 400) {
    return 'Neplatné dáta. Skontrolujte vyplnené polia.';
  }
  if (err?.status === 500) {
    return 'Chyba servera. Skúste to znova neskôr.';
  }
  
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
  
  return 'Nastala neočakávaná chyba.';
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
