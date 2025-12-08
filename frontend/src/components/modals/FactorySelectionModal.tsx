//*........................................................
//*       www/thermal_eye_ui/src/components/FactorySelectionModal.tsx
//*       Reusable modal for factory selection (DRY)
//*........................................................

import React, { useState, useMemo, useEffect } from 'react';
import { BaseModal } from '@/components/modals/BaseModal';
import { Button } from '@/components/ui_custom/button';
import { Checkbox } from '@/components/ui_custom/checkbox';
import { TableSearch } from '@/components/ui_custom/table/TableSearch';
import { X, CheckSquare, Square } from 'lucide-react';
import { API_BASE } from '@/config/api';

interface FactoryOption {
  id: string;
  label: string;
}

interface FactorySelectionModalProps {
  open: boolean;
  onClose: () => void;
  onSave: (selectedIds: string[]) => void;
  initialSelection?: string[];
  title?: string;
  description?: string;
}

export function FactorySelectionModal({
  open,
  onClose,
  onSave,
  initialSelection = [],
  title = 'Select Factories',
  description = 'Choose factories to include in your selection',
}: FactorySelectionModalProps) {
  const [factories, setFactories] = useState<FactoryOption[]>([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [selectedIds, setSelectedIds] = useState<string[]>(initialSelection);

  // Load factories
  useEffect(() => {
    if (open) {
      setLoading(true);
      fetch(`${API_BASE}/api/factories/?page=1&page_size=500`, { credentials: 'include' })
        .then(res => res.json())
        .then(json => {
          const results = Array.isArray(json) ? json : (json.results || []);
          setFactories(results.map((o: any) => ({
            id: String(o.id),
            label: `${o.name}${o.code ? ` (${o.code})` : ''}`,
          })));
        })
        .catch(err => {
          console.error('Failed to load factories:', err);
        })
        .finally(() => setLoading(false));
    }
  }, [open]);

  // Reset selection when modal opens
  useEffect(() => {
    if (open) {
      setSelectedIds(initialSelection);
      setSearch('');
    }
  }, [open, initialSelection]);

  // Filter factories by search
  const filteredFactories = useMemo(() => {
    if (!search.trim()) return factories;
    const searchLower = search.toLowerCase();
    return factories.filter(f =>
      f.label.toLowerCase().includes(searchLower) ||
      f.id.toLowerCase().includes(searchLower)
    );
  }, [factories, search]);

  const toggleFactory = (id: string, checked: boolean) => {
    setSelectedIds(prev =>
      checked
        ? Array.from(new Set([...prev, id]))
        : prev.filter(x => x !== id)
    );
  };

  const selectAll = () => {
    setSelectedIds(filteredFactories.map(f => f.id));
  };

  const selectNone = () => {
    setSelectedIds([]);
  };

  const handleSave = () => {
    onSave(selectedIds);
    onClose();
  };

  return (
    <BaseModal
      open={open}
      onClose={onClose}
      title={title}
      size="md"
    >
      <div className="flex flex-col gap-4 p-4">
        {description && (
          <p className="text-sm text-muted-foreground">{description}</p>
        )}

        {/* Search Field */}
        <div>
          <TableSearch
            value={search}
            onChange={setSearch}
            placeholder="Search factories..."
          />
        </div>

        {/* Select All/None Buttons */}
        <div className="flex gap-2">
          <Button
            variant="default"
            size="sm"
            onClick={selectAll}
            className="flex-1"
          >
            <CheckSquare className="w-4 h-4 mr-1" />
            Select All
          </Button>
          <Button
            variant="default"
            size="sm"
            onClick={selectNone}
            className="flex-1"
          >
            <Square className="w-4 h-4 mr-1" />
            Select None
          </Button>
        </div>

        {/* Factories List */}
        <div className="flex-1 overflow-auto max-h-64 border border-border rounded-md p-2 space-y-1">
          {loading ? (
            <div className="text-sm text-muted-foreground text-center py-4">
              Loading factories...
            </div>
          ) : filteredFactories.length === 0 ? (
            <div className="text-sm text-muted-foreground text-center py-4">
              {factories.length === 0 ? 'No factories available' : 'No factories found'}
            </div>
          ) : (
            filteredFactories.map(f => (
              <label
                key={f.id}
                className="flex items-center gap-2 text-xs cursor-pointer hover:bg-muted/50 px-2 py-1 rounded transition-colors"
              >
                <Checkbox
                  checked={selectedIds.includes(f.id)}
                  onCheckedChange={(checked) => toggleFactory(f.id, checked === true)}
                  className="shrink-0"
                />
                <span className="flex-1 truncate" title={f.label}>{f.label}</span>
              </label>
            ))
          )}
        </div>

        {/* Selected Count */}
        <div className="text-xs text-muted-foreground border-t border-border pt-2">
          {selectedIds.length > 0
            ? `${selectedIds.length} factory${selectedIds.length !== 1 ? 'ies' : ''} selected`
            : 'No factories selected'}
        </div>

        {/* Action Buttons */}
        <div className="flex gap-2 pt-2 border-t border-border">
          <Button
            variant="default"
            size="sm"
            onClick={onClose}
            className="flex-1"
          >
            Cancel
          </Button>
          <Button
            variant="solid"
            size="sm"
            onClick={handleSave}
            className="flex-1"
          >
            Save
          </Button>
        </div>
      </div>
    </BaseModal>
  );
}

