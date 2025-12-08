//*........................................................
//*       www/thermal_eye_ui/src/components/ui_custom/table/RecallFilterModal.tsx
//*       Modal for selecting from saved filters
//*........................................................

import React, { useState } from 'react';
import { BaseModal } from '@/components/modals/BaseModal';
import { Button } from '@/components/ui_custom/button';
import { Input } from '@/components/ui_custom/input';
import { Trash2, Clock, Search } from 'lucide-react';

export interface SavedFilter {
  name: string;
  timestamp: number;
  state: any;
}

interface RecallFilterModalProps {
  open: boolean;
  onClose: () => void;
  savedFilters: SavedFilter[];
  onRecall: (filter: SavedFilter) => void;
  onDelete: (filterName: string) => void;
}

export function RecallFilterModal({
  open,
  onClose,
  savedFilters,
  onRecall,
  onDelete,
}: RecallFilterModalProps) {
  const [searchQuery, setSearchQuery] = useState('');

  const formatDate = (timestamp: number) => {
    return new Date(timestamp).toLocaleString('sk-SK', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  // Filter saved filters based on search query
  const filteredFilters = savedFilters.filter(filter =>
    filter.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <BaseModal
      open={open}
      title="Recall Saved Filter"
      onClose={onClose}
      size="md"
    >
      {/* Search input */}
      {savedFilters.length > 0 && (
        <div className="relative mb-3">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            type="text"
            placeholder="Search filters..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9"
          />
        </div>
      )}

      <div className="flex flex-col gap-3 max-h-96 overflow-y-auto">
        {filteredFilters.length === 0 && savedFilters.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            <Clock size={48} className="mx-auto mb-3 opacity-30" />
            <p className="font-medium">No saved filters</p>
            <p className="text-sm mt-1">First create some using the Set button.</p>
          </div>
        ) : filteredFilters.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            <Search size={48} className="mx-auto mb-3 opacity-30" />
            <p className="font-medium">No filters found</p>
            <p className="text-sm mt-1">Try a different search term.</p>
          </div>
        ) : (
          filteredFilters.map((filter) => (
            <div
              key={filter.name}
              className="flex items-center justify-between p-3 border rounded hover:bg-muted/50 transition-colors"
            >
              <div className="flex-1">
                <p className="font-medium">{filter.name}</p>
                <p className="text-xs text-muted-foreground">
                  Saved: {formatDate(filter.timestamp)}
                </p>
              </div>
              <div className="flex gap-2">
                <Button
                  size="sm"
                  variant="solid"
                  onClick={() => {
                    onRecall(filter);
                    onClose();
                  }}
                >
                  Load
                </Button>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => onDelete(filter.name)}
                  title="Delete this filter"
                >
                  <Trash2 size={14} />
                </Button>
              </div>
            </div>
          ))
        )}
      </div>
      <div className="flex justify-end gap-2 mt-4 pt-4 border-t">
        <Button variant="ghost" onClick={onClose}>
          Close
        </Button>
      </div>
    </BaseModal>
  );
}
