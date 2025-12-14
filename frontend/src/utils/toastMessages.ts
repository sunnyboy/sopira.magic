//*........................................................
//*       frontend/src/utils/toastMessages.ts
//*       Toast Messages Engine - ConfigDriven & SSOT
//*       Univerzálny engine pre zobrazovanie toast notifikácií
//*........................................................

/**
 * Toast Messages Engine - ConfigDriven & SSOT
 * 
 * Univerzálny engine pre zobrazovanie toast notifikácií.
 * Všetky messages sú definované v toastConfig.ts (SSOT).
 * 
 * Usage:
 * - Predefined: toastMessages.recordCreated()
 * - Custom: toastMessages.displayMessage('warning', 'Custom text')
 */

import { toast } from 'sonner';
import { TOAST_CONFIG, DURATION_MAP, type ToastType, type DurationType } from './toastConfig';

/**
 * Create typed toast function from config
 */
function createToastFunction(configKey: string) {
  const config = TOAST_CONFIG[configKey];
  if (!config) {
    console.warn(`[toastMessages] Unknown config key: ${configKey}`);
    return () => {};
  }

  const duration = DURATION_MAP[config.duration];

  // If text is a function, return a function that accepts arguments
  if (typeof config.text === 'function') {
    return (...args: any[]) => {
      const message = (config.text as (...args: any[]) => string)(...args);
      toast[config.type](message, { duration });
    };
  }

  // If text is a string, return a simple function
  return () => {
    toast[config.type](config.text as string, { duration });
  };
}

/**
 * ConfigDriven toast messages object
 * All functions are dynamically generated from TOAST_CONFIG
 */
export const toastMessages = {
  // Success messages
  changesSaved: createToastFunction('changesSaved'),
  recordCreated: createToastFunction('recordCreated'),
  recordDeleted: createToastFunction('recordDeleted') as (count: number) => void,
  recordsExported: createToastFunction('recordsExported') as (count: number, format: string) => void,
  filterSaved: createToastFunction('filterSaved') as (name: string) => void,
  filterLoaded: createToastFunction('filterLoaded') as (name: string) => void,
  
  // Preset operations
  presetSaved: createToastFunction('presetSaved') as (name: string) => void,
  presetLoaded: createToastFunction('presetLoaded') as (name: string) => void,
  presetDeleted: createToastFunction('presetDeleted'),
  
  // Clipboard
  copiedToClipboard: createToastFunction('copiedToClipboard'),
  
  // Error messages
  saveFailed: createToastFunction('saveFailed') as (details?: string) => void,
  deleteFailed: createToastFunction('deleteFailed') as (details?: string) => void,
  loadFailed: createToastFunction('loadFailed') as (details?: string) => void,
  exportFailed: createToastFunction('exportFailed') as (details?: string) => void,
  validationFailed: createToastFunction('validationFailed') as (field: string, reason: string) => void,
  
  // Preset error messages
  presetSaveFailed: createToastFunction('presetSaveFailed') as (details?: string) => void,
  presetLoadFailed: createToastFunction('presetLoadFailed') as (details?: string) => void,
  presetDeleteFailed: createToastFunction('presetDeleteFailed'),
  
  // Warning messages
  noSelection: createToastFunction('noSelection'),
  unsavedChanges: createToastFunction('unsavedChanges'),
  
  // Info messages
  processing: createToastFunction('processing') as (action: string) => void,
  cancelled: createToastFunction('cancelled') as (action: string) => void,
  showingSelectedRecords: createToastFunction('showingSelectedRecords') as (count: number) => void,
  showingAllRecords: createToastFunction('showingAllRecords'),

  /**
   * Universal function for displaying custom messages (e.g., from backend)
   * ConfigDriven - accepts any type and message
   */
  displayMessage: (type: ToastType, message: string, customDuration?: DurationType) => {
    const duration = customDuration ? DURATION_MAP[customDuration] : DURATION_MAP[
      type === 'error' ? 'long' : (type === 'info' ? 'short' : 'medium')
    ];
    toast[type](message, { duration });
  },
};

// Re-export duration constants for backward compatibility
export const durationS = DURATION_MAP.short;
export const durationM = DURATION_MAP.medium;
export const durationL = DURATION_MAP.long;
