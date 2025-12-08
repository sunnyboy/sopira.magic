/**
 * LoadStateModal - Universal modal for loading table state presets
 * Works with any component (filters, columns, sorting, table, etc.)
 */

import React, { useState, useMemo } from 'react';
import { BaseModal } from '@/components/modals/BaseModal';
import { Button } from '@/components/ui_custom/button';
import { Input } from '@/components/ui_custom/input';
import { Trash2, Clock, Search, CheckCircle } from 'lucide-react';
import type { TableStatePreset } from '@/hooks/useSnapshot';

export interface LoadStateModalProps {
  open: boolean;
  onClose: () => void;
  presets: TableStatePreset[];
  onLoad: (preset: TableStatePreset) => void;
  onDelete: (id: number) => Promise<void>;
  title?: string;
  emptyMessage?: string;
}

export function LoadStateModal({
  open,
  onClose,
  presets,
  onLoad,
  onDelete,
  title = 'Load Preset',
  emptyMessage = 'No presets saved yet.',
}: LoadStateModalProps) {
  const [search, setSearch] = useState('');
  const [deletingIds, setDeletingIds] = useState<Set<number>>(new Set());

  // Filter presets by search
  const filteredPresets = useMemo(() => {
    const term = search.trim().toLowerCase();
    if (!term) return presets;
    
    return presets.filter(preset => 
      preset.preset_name.toLowerCase().includes(term) ||
      preset.description.toLowerCase().includes(term) ||
      preset.factory_name?.toLowerCase().includes(term)
    );
  }, [presets, search]);

  // Handle delete
  const handleDelete = async (id: number) => {
    setDeletingIds(prev => new Set(prev).add(id));
    try {
      await onDelete(id);
    } finally {
      setDeletingIds(prev => {
        const next = new Set(prev);
        next.delete(id);
        return next;
      });
    }
  };

  // Format date
  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleString('en-GB', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return dateString;
    }
  };

  return (
    <BaseModal open={open} onClose={onClose} size="md">
      {/* Header */}
      <div className="flex items-center justify-between p-6 border-b border-border">
        <h2 className="text-lg font-semibold">{title}</h2>
        <Button
          type="button"
          variant="ghost"
          size="icon"
          onClick={onClose}
          className="h-8 w-8 p-0 text-2xl hover:text-destructive"
        >
          ×
        </Button>
      </div>

      {/* Search */}
      <div className="p-4 border-b border-border">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search presets..."
            className="pl-10"
          />
        </div>
      </div>

      {/* Presets List */}
      <div className="max-h-[400px] overflow-y-auto">
        {filteredPresets.length === 0 ? (
          <div className="p-8 text-center text-sm text-muted-foreground">
            {search ? 'No matching presets found.' : emptyMessage}
          </div>
        ) : (
          <div className="divide-y divide-border">
            {filteredPresets.map((preset) => (
              <div
                key={preset.id}
                className="p-4 hover:bg-muted/50 transition-colors"
              >
                <div className="flex items-start justify-between gap-3">
                  {/* Preset Info */}
                  <div className="flex-1 min-w-0 cursor-pointer" onClick={() => onLoad(preset)}>
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-medium text-sm truncate">{preset.preset_name}</h3>
                      {preset.is_active && (
                        <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0" />
                      )}
                    </div>
                    
                    {preset.description && (
                      <p className="text-xs text-muted-foreground mb-2 line-clamp-2">
                        {preset.description}
                      </p>
                    )}
                    
                    <div className="flex items-center gap-3 text-xs text-muted-foreground">
                      <span className="flex items-center gap-1">
                        <Clock size={12} />
                        {formatDate(preset.updated)}
                      </span>
                      {preset.factory_name && (
                        <span className="truncate">
                          Factory: {preset.factory_name}
                        </span>
                      )}
                      <span className="capitalize">
                        {preset.component}
                      </span>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2 flex-shrink-0">
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => onLoad(preset)}
                      title="Load preset"
                    >
                      Load
                    </Button>
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon"
                      onClick={() => handleDelete(preset.id)}
                      disabled={deletingIds.has(preset.id)}
                      className="h-8 w-8 text-destructive hover:text-destructive hover:bg-destructive/10"
                      title="Delete preset"
                    >
                      <Trash2 size={14} />
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="flex justify-end gap-3 p-4 border-t border-border">
        <Button type="button" variant="ghost" onClick={onClose}>
          Close
        </Button>
      </div>
    </BaseModal>
  );
}


