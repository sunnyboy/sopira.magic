//*........................................................
//*       www/thermal_eye_ui/src/components/ui_custom/table/FilterCheckboxGroup.tsx
//*       Multi-select checkbox group filter component
//*........................................................

import React, { useState } from 'react';
import { Checkbox } from '@/components/ui_custom/checkbox';
import { Button } from '@/components/ui_custom/button';
import { Input } from '@/components/ui_custom/input';
import { Search, CheckSquare, Square } from 'lucide-react';

interface FilterCheckboxGroupProps {
  label: string;
  options: Array<{ id: string; label: string }>;
  selectedIds: string[];
  onChange: (selectedIds: string[]) => void;
}

export function FilterCheckboxGroup({
  label,
  options,
  selectedIds,
  onChange,
}: FilterCheckboxGroupProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [showSearch, setShowSearch] = useState(false);

  // Filter options based on search query (must be defined before handlers)
  const filteredOptions = options.filter(option =>
    option.label.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleToggle = (id: string, checked: boolean) => {
    const next = checked
      ? Array.from(new Set([...selectedIds, id]))
      : selectedIds.filter((v) => v !== id);
    onChange(next.length ? next : []);
  };

  const handleSelectAll = () => {
    // Select all currently visible (filtered) options
    const allFilteredIds = filteredOptions.map(opt => opt.id);
    // Merge with already selected (to keep selections that are not currently visible)
    const merged = Array.from(new Set([...selectedIds, ...allFilteredIds]));
    onChange(merged);
  };

  const handleDeselectAll = () => {
    // Deselect all currently visible (filtered) options
    const filteredIds = new Set(filteredOptions.map(opt => opt.id));
    const remaining = selectedIds.filter(id => !filteredIds.has(id));
    onChange(remaining);
  };

  const selectedCount = selectedIds.length;
  const totalCount = options.length;
  const allSelected = selectedCount === totalCount && totalCount > 0;

  return (
    <div className="flex flex-col gap-2 border rounded-md p-3 bg-card">
      {/* Header */}
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2 flex-1 min-w-0">
          <span className="text-sm font-medium truncate">{label}</span>
          <span className="text-xs text-muted-foreground whitespace-nowrap">
            {selectedCount}/{totalCount}
          </span>
        </div>
        <div className="flex items-center gap-1">
          <Button
            size="sm"
            variant="ghost"
            onClick={allSelected ? handleDeselectAll : handleSelectAll}
            className="h-7 px-2 text-xs"
            title={allSelected ? 'Deselect All' : 'Select All'}
          >
            {allSelected ? <Square className="h-3 w-3" /> : <CheckSquare className="h-3 w-3" />}
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => setShowSearch(!showSearch)}
            className="h-7 px-2"
            title="Search"
          >
            <Search className="h-3 w-3" />
          </Button>
        </div>
      </div>

      {/* Search field (collapsible) */}
      {showSearch && (
        <Input
          type="text"
          placeholder="Search..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="h-8 text-sm"
          autoFocus
        />
      )}

      {/* Options list - kompaktnejší: 4 riadky, menšie medzery */}
      <div className="flex flex-col gap-0.5 max-h-[96px] overflow-y-auto">
        {filteredOptions.length === 0 ? (
          <p className="text-xs text-muted-foreground text-center py-2">No options found</p>
        ) : (
          filteredOptions.map((option) => (
          <label key={option.id} className="flex items-center gap-1.5 cursor-pointer hover:bg-muted/50 px-1 py-0.5 rounded">
            <Checkbox
              checked={selectedIds.includes(option.id)}
              onCheckedChange={(checked) => handleToggle(option.id, checked === true)}
              className="h-3.5 w-3.5"
            />
            <span className="text-xs leading-tight truncate" title={option.label}>{option.label}</span>
          </label>
        ))
        )}
      </div>
    </div>
  );
}
