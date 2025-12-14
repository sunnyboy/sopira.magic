//*........................................................
//*       frontend/src/utils/toastConfig.ts
//*       Toast Messages Configuration - SSOT
//*       Centrálny config pre všetky toast hlásenia
//*........................................................

/**
 * Toast Messages Configuration - SSOT
 * 
 * Centrálny config pre všetky toast hlásenia v aplikácii.
 * Pripravené pre budúcu internacionalizáciu.
 * 
 * ConfigDriven & SSOT - všetky texty na jednom mieste.
 */

export type ToastType = 'success' | 'error' | 'warning' | 'info';
export type DurationType = 'short' | 'medium' | 'long';

export interface ToastMessageConfig {
  type: ToastType;
  text: string | ((...args: any[]) => string);
  duration: DurationType;
}

/**
 * SSOT - Single Source of Truth for all toast messages
 */
export const TOAST_CONFIG: Record<string, ToastMessageConfig> = {
  // Success messages
  changesSaved: {
    type: 'success',
    text: 'Changes saved',
    duration: 'medium',
  },
  recordCreated: {
    type: 'success',
    text: 'Record created',
    duration: 'medium',
  },
  recordDeleted: {
    type: 'success',
    text: (count: number) => `${count} record${count > 1 ? 's' : ''} deleted`,
    duration: 'medium',
  },
  recordsExported: {
    type: 'success',
    text: (count: number, format: string) => 
      `${count} record${count > 1 ? 's' : ''} exported as ${format.toUpperCase()}`,
    duration: 'medium',
  },
  filterSaved: {
    type: 'success',
    text: (name: string) => `Filter "${name}" saved`,
    duration: 'medium',
  },
  filterLoaded: {
    type: 'success',
    text: (name: string) => `Filter "${name}" loaded`,
    duration: 'medium',
  },
  presetSaved: {
    type: 'success',
    text: (name: string) => `Preset "${name}" saved`,
    duration: 'medium',
  },
  presetLoaded: {
    type: 'success',
    text: (name: string) => `Preset "${name}" loaded`,
    duration: 'medium',
  },
  presetDeleted: {
    type: 'success',
    text: 'Preset deleted',
    duration: 'medium',
  },
  copiedToClipboard: {
    type: 'success',
    text: 'Copied to clipboard',
    duration: 'short',
  },

  // Error messages
  saveFailed: {
    type: 'error',
    text: (details?: string) => `Save failed${details ? `: ${details}` : ''}`,
    duration: 'long',
  },
  deleteFailed: {
    type: 'error',
    text: (details?: string) => `Delete failed${details ? `: ${details}` : ''}`,
    duration: 'long',
  },
  loadFailed: {
    type: 'error',
    text: (details?: string) => `Load failed${details ? `: ${details}` : ''}`,
    duration: 'long',
  },
  exportFailed: {
    type: 'error',
    text: (details?: string) => `Export failed${details ? `: ${details}` : ''}`,
    duration: 'long',
  },
  validationFailed: {
    type: 'error',
    text: (field: string, reason: string) => `${field}: ${reason}`,
    duration: 'long',
  },
  presetSaveFailed: {
    type: 'error',
    text: (details?: string) => `Failed to save preset${details ? `: ${details}` : ''}`,
    duration: 'long',
  },
  presetLoadFailed: {
    type: 'error',
    text: (details?: string) => `Failed to load preset${details ? `: ${details}` : ''}`,
    duration: 'long',
  },
  presetDeleteFailed: {
    type: 'error',
    text: 'Failed to delete preset',
    duration: 'long',
  },

  // Warning messages
  noSelection: {
    type: 'warning',
    text: 'No records selected',
    duration: 'short',
  },
  unsavedChanges: {
    type: 'warning',
    text: 'You have unsaved changes',
    duration: 'short',
  },

  // Info messages
  processing: {
    type: 'info',
    text: (action: string) => `${action}...`,
    duration: 'short',
  },
  cancelled: {
    type: 'info',
    text: (action: string) => `${action} cancelled`,
    duration: 'short',
  },
  showingSelectedRecords: {
    type: 'info',
    text: (count: number) => `Showing ${count} selected record${count > 1 ? 's' : ''}`,
    duration: 'short',
  },
  showingAllRecords: {
    type: 'info',
    text: 'Showing all records',
    duration: 'short',
  },
};

// Duration mappings (ms)
export const DURATION_MAP = {
  short: 3000,
  medium: 4000,
  long: 5000,
} as const;

