/*........................................................
//*       www/thermal_eye_ui/src/config/modelMetadata.ts
//*       Model metadata loaded from Django backend
//*       Single source of truth for plural names & endpoints
//*........................................................

Purpose:
- Load model metadata from /api/models/metadata/ endpoint
- Django models have verbose_name_plural defined in Meta
- Frontend uses this to avoid hardcoding plurals in every table
- MyTable automatically uses this for FK field endpoints

Example metadata response from backend:
{
  "factory": {
    "model": "Factory",
    "singular": "Factory",
    "plural": "Factories",
    "endpoint": "/api/factories/"
  },
  "servicecredential": {
    "model": "ServiceCredential",
    "singular": "Service Credential",
    "plural": "Service Credentials",
    "endpoint": ""  // No API endpoint
  }
}

Usage:
import { loadModelMetadata, getModelEndpoint } from '@/config/modelMetadata';

// Load once on app initialization
await loadModelMetadata();

// Get endpoint for FK field
const endpoint = getModelEndpoint('factory'); // → '/api/factories/'
const endpoint = getModelEndpoint('credential'); // → '' (no endpoint)
*/

export interface ModelMeta {
  model: string;          // Model class name (e.g., "Factory")
  singular: string;       // Singular form (e.g., "Factory")
  plural: string;         // Plural form (e.g., "Factories")
  endpoint: string;       // API endpoint (e.g., "/api/factories/") or empty string if none
  default_ordering?: string[];  // Default ordering from VIEWS_MATRIX (e.g., ["-created"])
  ownership_field?: string | null;  // Ownership field from VIEWS_MATRIX (e.g., "factory_id", "created_by") - SSOT for scoping
}

// Cache metadata in memory (loaded once on app init)
let cachedMetadata: Record<string, ModelMeta> | null = null;
let loadingPromise: Promise<Record<string, ModelMeta>> | null = null;

/**
 * Load model metadata from backend API
 * Cached in memory after first load
 * 
 * @returns Promise with metadata for all models
 */
export async function loadModelMetadata(): Promise<Record<string, ModelMeta>> {
  // Return cached if already loaded
  if (cachedMetadata) {
    return cachedMetadata;
  }
  
  // If already loading, return existing promise (avoid duplicate requests)
  if (loadingPromise) {
    return loadingPromise;
  }
  
  // Start loading
  loadingPromise = (async () => {
    try {
      const response = await fetch('/api/models/metadata/', {
        credentials: 'include',
      });
      
      if (!response.ok) {
        console.error('Failed to load model metadata:', response.status);
        return {};
      }
      
      const metadata = await response.json();
      cachedMetadata = metadata;
      return metadata;
    } catch (error) {
      console.error('Error loading model metadata:', error);
      return {};
    } finally {
      loadingPromise = null;
    }
  })();
  
  return loadingPromise;
}

/**
 * Get cached metadata (sync)
 * Must call loadModelMetadata() first!
 * 
 * @returns Cached metadata or empty object if not loaded
 */
export function getCachedMetadata(): Record<string, ModelMeta> {
  return cachedMetadata || {};
}

/**
 * Get API endpoint for a model field name
 * 
 * @param fieldName - Field name (e.g., 'factory', 'location', 'credential')
 * @returns API endpoint URL or empty string if no endpoint exists
 * 
 * Examples:
 * - getModelEndpoint('factory') → '/api/factories/'
 * - getModelEndpoint('credential') → '' (no endpoint)
 * - getModelEndpoint('unknown') → '' (fallback for unknown models)
 */
export function getModelEndpoint(fieldName: string): string {
  const metadata = getCachedMetadata();
  const modelName = fieldName.toLowerCase();
  return metadata[modelName]?.endpoint || '';
}

/**
 * Get plural name for a model field
 * 
 * @param fieldName - Field name (e.g., 'factory', 'location')
 * @returns Plural name (e.g., 'Factories', 'Locations')
 */
export function getModelPlural(fieldName: string): string {
  const metadata = getCachedMetadata();
  const modelName = fieldName.toLowerCase();
  return metadata[modelName]?.plural || '';
}

/**
 * Get singular name for a model field
 * 
 * @param fieldName - Field name (e.g., 'factory', 'location')
 * @returns Singular name (e.g., 'Factory', 'Location')
 */
export function getModelSingular(fieldName: string): string {
  const metadata = getCachedMetadata();
  const modelName = fieldName.toLowerCase();
  return metadata[modelName]?.singular || '';
}

/**
 * Check if model has API endpoint
 * 
 * @param fieldName - Field name
 * @returns true if model has non-empty endpoint
 */
export function hasModelEndpoint(fieldName: string): boolean {
  const endpoint = getModelEndpoint(fieldName);
  return endpoint.length > 0;
}

/**
 * Get default ordering for a model field name
 * 
 * @param fieldName - Field name or storageKey (e.g., 'logentry', 'logentry-v2', 'factory')
 * @returns Default ordering array (e.g., ["-created"]) or empty array if none
 * 
 * Examples:
 * - getDefaultOrdering('logentry') → ["-created"]
 * - getDefaultOrdering('logentry-v2') → ["-created"] (strips version suffix)
 * - getDefaultOrdering('factory') → ["name"]
 * - getDefaultOrdering('unknown') → []
 * 
 * Note: Strips version suffixes (e.g., '-v2', '-v3') to match model name in metadata.
 */
export function getDefaultOrdering(fieldName: string): string[] {
  const metadata = getCachedMetadata();
  // Strip version suffix (e.g., 'logentry-v2' → 'logentry')
  const modelName = fieldName.toLowerCase().replace(/-v\d+$/, '');
  return metadata[modelName]?.default_ordering || [];
}

/**
 * Get ownership field for a model field name (SSOT for scoping)
 * 
 * @param fieldName - Field name or storageKey (e.g., 'measurement', 'camera', 'factory')
 * @returns Ownership field name (e.g., "factory_id", "created_by") or null if none
 * 
 * Examples:
 * - getOwnershipField('measurement') → "factory_id"
 * - getOwnershipField('factory') → "id"
 * - getOwnershipField('environment') → null (global entity)
 * 
 * Note: Strips version suffixes (e.g., '-v2', '-v3') to match model name in metadata.
 */
export function getOwnershipField(fieldName: string): string | null | undefined {
  const metadata = getCachedMetadata();
  // Strip version suffix (e.g., 'logentry-v2' → 'logentry')
  const modelName = fieldName.toLowerCase().replace(/-v\d+$/, '');
  return metadata[modelName]?.ownership_field;
}

