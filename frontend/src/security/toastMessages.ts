//*........................................................
//*       www/thermal_eye_ui/src/utils/toastMessages.ts
//*       Centralized toast messages for all tables
//*........................................................

import { toast } from 'sonner';

/**
 * Duration constants for toast messages
 */
export const durationS = 3000; // Short duration
export const durationM = 4000; // Medium duration (default)
export const durationL = 5000; // Long duration (for errors)

/**
 * Standard toast messages used across all tables
 * All UI messages in English
 */
export const toastMessages = {
  // Success messages
  changesSaved: (duration = durationM) => toast.success('Changes saved', { duration }),
  recordCreated: (duration = durationM) => toast.success('Record created', { duration }),
  recordDeleted: (count: number = 1, duration = durationM) => 
    toast.success(`${count} record${count > 1 ? 's' : ''} deleted`, { duration }),
  recordsExported: (count: number, format: string, duration = durationM) => 
    toast.success(`${count} record${count > 1 ? 's' : ''} exported as ${format.toUpperCase()}`, { duration }),
  filterSaved: (name: string, duration = durationM) => 
    toast.success(`Filter "${name}" saved`, { duration }),
  filterLoaded: (name: string, duration = durationM) => 
    toast.success(`Filter "${name}" loaded`, { duration }),
  
  // Preset operations
  presetSaved: (name: string, duration = durationM) => 
    toast.success(`Preset "${name}" saved`, { duration }),
  presetLoaded: (name: string, duration = durationM) => 
    toast.success(`Preset "${name}" loaded`, { duration }),
  presetDeleted: (duration = durationM) => 
    toast.success('Preset deleted', { duration }),
  
  // Clipboard
  copiedToClipboard: (duration = durationS) => 
    toast.success('Copied to clipboard', { duration }),
  
  // Error messages
  saveFailed: (details?: string, duration = durationL) => 
    toast.error(`Save failed${details ? `: ${details}` : ''}`, { duration }),
  deleteFailed: (details?: string, duration = durationL) => 
    toast.error(`Delete failed${details ? `: ${details}` : ''}`, { duration }),
  loadFailed: (details?: string, duration = durationL) => 
    toast.error(`Load failed${details ? `: ${details}` : ''}`, { duration }),
  exportFailed: (details?: string, duration = durationL) => 
    toast.error(`Export failed${details ? `: ${details}` : ''}`, { duration }),
  validationFailed: (field: string, reason: string, duration = durationL) => 
    toast.error(`${field}: ${reason}`, { duration }),
  
  // Preset error messages
  presetSaveFailed: (details?: string, duration = durationL) => 
    toast.error(`Failed to save preset${details ? `: ${details}` : ''}`, { duration }),
  presetLoadFailed: (details?: string, duration = durationL) => 
    toast.error(`Failed to load preset${details ? `: ${details}` : ''}`, { duration }),
  presetDeleteFailed: (duration = durationL) => 
    toast.error('Failed to delete preset', { duration }),
  
  // Warning messages
  noSelection: (duration = durationS) => 
    toast.warning('No records selected', { duration }),
  unsavedChanges: (duration = durationS) => 
    toast.warning('You have unsaved changes', { duration }),
  
  // Info messages
  processing: (action: string, duration = durationS) => 
    toast.info(`${action}...`, { duration }),
  cancelled: (action: string, duration = durationS) => 
    toast.info(`${action} cancelled`, { duration }),
  showingSelectedRecords: (count: number, duration = durationS) => 
    toast.info(`Showing ${count} selected record${count > 1 ? 's' : ''}`, { duration }),
  showingAllRecords: (duration = durationS) => 
    toast.info('Showing all records', { duration }),
};

/**
 * Shorthand for common toast patterns
 * @deprecated Use toastMessages functions instead for consistency
 */
export const toasts = {
  success: (message: string, duration = durationM) => toast.success(message, { duration }),
  error: (message: string, duration = durationL) => toast.error(message, { duration }),
  warning: (message: string, duration = durationS) => toast.warning(message, { duration }),
  info: (message: string, duration = durationS) => toast.info(message, { duration }),
};
