//=======================================================
//  thermal_eye_ui/src/services/fkCacheService.ts
//=======================================================
/**
 * Service for loading FK options from backend cache.
 * Uses /api/fk-options-cache/ endpoint for fast loading.
 */

export interface FKOption {
  id: string;
  label: string;
  code?: string;
  name?: string;
  human_id?: string;
  [key: string]: any; // Allow additional fields for template string support
}

export interface FKCacheResponse {
  field: string;
  options: FKOption[];
  count: number;
  cache_age: string | null;
  factories_count: number;
}

/**
 * Load FK options from backend cache for specific field.
 * 
 * Backend automatically applies scope based on active scope (Dashboard selection).
 * Frontend does NOT send factory_ids[] - backend handles scoping automatically.
 * 
 * @param field - FK field name (e.g., 'location', 'carrier', 'driver', 'pot', 'pit', 'machine')
 * @param factoryIds - DEPRECATED: Backend automatically applies scope, this parameter is ignored
 * @returns Promise<FKOption[]>
 */
export async function loadFKOptionsFromCache(
  field: string,
  factoryIds: string[] = [] // DEPRECATED: Backend automatically applies scope
): Promise<FKOption[]> {
  try {
    // Build query params - backend automatically applies scope
    const params = new URLSearchParams();
    params.set('field', field);
    // Note: factory_ids[] parameter removed - backend automatically applies scope
    
    const url = `/api/fk-options-cache/?${params.toString()}`;
    
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
    });
    
    if (!response.ok) {
      console.error(`[FK Cache] Failed to load ${field} options:`, response.statusText);
      return [];
    }
    
    const data: FKCacheResponse = await response.json();
    
    console.log(`[FK Cache] Loaded ${field}: ${data.count} options (cache age: ${data.cache_age}, factories_count: ${data.factories_count})`);
    
    return data.options;
  } catch (error) {
    console.error(`[FK Cache] Error loading ${field} options:`, error);
    return [];
  }
}

/**
 * Load multiple FK fields in parallel.
 * 
 * Backend automatically applies scope - frontend does NOT send factory_ids[].
 * 
 * @param fields - Array of FK field names
 * @param factoryIds - DEPRECATED: Backend automatically applies scope, this parameter is ignored
 * @returns Promise<Record<string, FKOption[]>>
 */
export async function loadMultipleFKOptionsFromCache(
  fields: string[],
  factoryIds: string[] = [] // DEPRECATED: Backend automatically applies scope
): Promise<Record<string, FKOption[]>> {
  const promises = fields.map(field => 
    loadFKOptionsFromCache(field, factoryIds) // factoryIds ignored - backend handles scoping
      .then(options => ({ field, options }))
  );
  
  const results = await Promise.all(promises);
  
  const optionsMap: Record<string, FKOption[]> = {};
  results.forEach(({ field, options }) => {
    optionsMap[field] = options;
  });
  
  return optionsMap;
}

/**
 * Manually trigger cache rebuild for specific field/factory.
 * 
 * @param field - FK field name
 * @param factoryId - Factory UUID (optional)
 */
export async function rebuildFKCache(
  field: string,
  factoryId?: string
): Promise<void> {
  try {
    const response = await fetch('/api/fk-options-cache/rebuild/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({
        field,
        factory_id: factoryId,
      }),
    });
    
    if (!response.ok) {
      throw new Error(`Rebuild failed: ${response.statusText}`);
    }
    
    const data = await response.json();
    console.log(`[FK Cache] Rebuild complete:`, data);
  } catch (error) {
    console.error(`[FK Cache] Rebuild error:`, error);
    throw error;
  }
}

