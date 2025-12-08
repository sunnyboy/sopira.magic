import React, { useState, useEffect } from 'react';
import { EditableCell } from './EditableCell';
import type { FieldFactoryContext } from './fieldFactory';
import { getOwnershipField } from '@/config/modelMetadata';

interface ScopedFKCellProps<T> {
  config: any;
  field: any;
  row: T;
  isEditing: boolean;
  context: FieldFactoryContext<T>;
  commonProps: any;
  val: string;
  displayLabel: string;
  highlighted: React.ReactNode;
  onSave: (v: string | null) => void;
}

export function ScopedFKCell<T>({
  config,
  field,
  row,
  isEditing,
  context,
  commonProps,
  val,
  displayLabel,
  highlighted,
  onSave,
}: ScopedFKCellProps<T>) {
  console.log(`[ScopedFKCell] RENDER for field: ${config.key}`, {
    isEditing,
    hasGetScopedOptions: typeof context.getScopedOptions === 'function',
    hasScopedCache: context.scopedCache !== undefined,
  });
  
  const [options, setOptions] = useState<Array<{ id: string; label: string }>>([]);
  const [isLoading, setIsLoading] = useState(false);

  // Backend automatically applies scope - no need to use factoryUuid
  // Cache key no longer includes factoryUuid - backend handles scoping
  const cacheKey = `${config.key}`;

  useEffect(() => {
    console.log(`[ScopedFKCell] useEffect triggered for field: ${config.key}`, {
      isEditing,
      hasGetScopedOptions: typeof context.getScopedOptions === 'function',
      hasScopedCache: context.scopedCache !== undefined,
      cacheKey,
    });
    
    if (!isEditing) {
      setOptions([]);
      setIsLoading(false);
      return;
    }

    if (!context.getScopedOptions) {
      console.warn(`[ScopedFKCell] Cannot load options for ${config.key}:`, {
        hasGetScopedOptions: typeof context.getScopedOptions === 'function',
      });
      setOptions([]);
      return;
    }

    // Check cache first
    if (context.scopedCache?.has(cacheKey)) {
      const cached = context.scopedCache.get(cacheKey)!;
      console.log(`[ScopedFKCell] Using cached options for ${config.key}`, cached.length);
      setOptions(cached);
      return;
    }

    // Load from API - backend automatically applies scope
    console.log(`[ScopedFKCell] Loading options from API for ${config.key} (backend applies scope automatically)`);
    setIsLoading(true);
    // Backend automatically applies scope - no need to pass factoryId
    context.getScopedOptions(config.key)
      .then(scopedList => {
        console.log(`[ScopedFKCell] Loaded ${scopedList.length} options for ${config.key}`, scopedList);
        setOptions(scopedList);
        context.scopedCache?.set(cacheKey, scopedList);
        context.onScopeCacheUpdate?.();
      })
      .catch((error) => {
        console.error(`[ScopedFKCell] Failed to load options for ${config.key}:`, error);
        setOptions([]);
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, [isEditing, config.key, cacheKey, context]);

  if (isEditing) {
    return (
      <EditableCell
        {...commonProps}
        value={val}
        isEditing={true}
        type="select"
        options={options.map(o => ({ value: o.id, label: o.label }))}
        onSave={(v) => onSave(v || null)}
        isSaving={isLoading}
        selectPlaceholder={isLoading ? 'Loading...' : '—'}
      />
    );
  }

  return (
    <EditableCell
      {...commonProps}
      value={displayLabel}
      isEditing={false}
      editingAllowed={true}
      onSave={() => {}}
      highlightedContent={highlighted}
    />
  );
}

