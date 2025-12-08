//*........................................................
//*       FilterTagAutocomplete.tsx
//*       Tag filter with autocomplete dropdown (multi-select)
//*........................................................

import React, { useState, useMemo, useRef, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { Input } from '@/components/ui_custom/input';
import { Button } from '@/components/ui_custom/button';
import { X } from 'lucide-react';
import { API_BASE } from '@/config/api';

interface FilterTagAutocompleteProps {
  label: string;
  table?: any;
  columnId?: string;
  placeholder?: string;
  selectedFactories: string[]; // Factory IDs to fetch tags from
  model?: string; // Model type (default: 'measurement')
}

export function FilterTagAutocomplete({
  label,
  table,
  columnId,
  selectedFactories,
  model = 'measurement',
  placeholder = "Type to add tags..."
}: FilterTagAutocompleteProps) {
  const autoMode = table && columnId;
  
  // Get current filter value (can be array of tags or comma-separated string)
  const filterValue = autoMode 
    ? (table.getColumn(columnId)?.getFilterValue() as string | string[])
    : undefined;
  
  // Parse filter value into array of tags
  const selectedTags = useMemo(() => {
    if (!filterValue) return [];
    if (Array.isArray(filterValue)) return filterValue;
    return filterValue.split(',').map(t => t.trim()).filter(Boolean);
  }, [filterValue]);
  
  // Local state for input
  const [inputText, setInputText] = useState('');
  const [open, setOpen] = useState(false);
  const [pos, setPos] = useState({ x: 0, y: 0, width: 0 });
  const inputRef = useRef<HTMLInputElement>(null);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const tagCacheRef = useRef(new Map<string, string[]>());
  
  // Fetch tag suggestions for selected factories
  useEffect(() => {
    async function fetchTagSuggestions(factoryId: string): Promise<string[]> {
      const key = `${factoryId}:${model}`;
      if (tagCacheRef.current.has(key)) {
        return tagCacheRef.current.get(key)!;
      }
      try {
        const url = `${API_BASE}/api/tags/suggest/?factory=${factoryId}&model=${encodeURIComponent(model)}`;
        const res = await fetch(url, { credentials: 'include' });
        const json = await res.json().catch(() => ({ tags: [] }));
        const arr = Array.isArray(json.tags) ? json.tags.map(String) : [];
        tagCacheRef.current.set(key, arr);
        return arr;
      } catch {
        return [];
      }
    }
    
    if (selectedFactories.length > 0) {
      Promise.all(
        selectedFactories.map(fid => fetchTagSuggestions(fid))
      ).then(results => {
        // Merge and deduplicate all tags from all factories
        const allTags = Array.from(new Set(results.flat()));
        setSuggestions(allTags.sort());
      }).catch(() => setSuggestions([]));
    } else {
      setSuggestions([]);
    }
  }, [selectedFactories, model]);
  
  // Filter suggestions based on input
  const filtered = useMemo(() => {
    const searchText = inputText.trim().toLowerCase();
    // Exclude already selected tags
    const available = suggestions.filter(s => !selectedTags.includes(s));
    if (!searchText) return available;
    return available.filter(s => s.toLowerCase().includes(searchText));
  }, [suggestions, inputText, selectedTags]);
  
  // Update position for dropdown
  function updatePosition() {
    if (!inputRef.current) return;
    const rect = inputRef.current.getBoundingClientRect();
    setPos({ x: rect.left, y: rect.bottom + 4, width: Math.max(200, rect.width) });
  }
  
  // Handle selecting a suggestion
  function selectSuggestion(tag: string) {
    if (selectedTags.includes(tag)) return; // Already selected
    const newTags = [...selectedTags, tag];
    if (autoMode) {
      table.getColumn(columnId)?.setFilterValue(newTags.join(','));
    }
    setInputText('');
    setOpen(false);
    // Refocus input for additional tags
    inputRef.current?.focus();
  }
  
  // Handle removing a tag
  function removeTag(tagToRemove: string) {
    const newTags = selectedTags.filter(t => t !== tagToRemove);
    if (autoMode) {
      table.getColumn(columnId)?.setFilterValue(newTags.length > 0 ? newTags.join(',') : undefined);
    }
  }
  
  // Handle input change
  const handleChange = (value: string) => {
    setInputText(value);
    if (!open && value) {
      updatePosition();
      setOpen(true);
    }
  };
  
  // Handle focus
  function onFocus() {
    updatePosition();
    setOpen(true);
  }
  
  // Handle blur
  function onBlur() {
    // Delay to allow click on suggestion
    setTimeout(() => setOpen(false), 150);
  }
  
  // Clear all tags
  const handleClearAll = () => {
    if (autoMode) {
      table.getColumn(columnId)?.setFilterValue(undefined);
    }
    setInputText('');
  };
  
  const hasValue = selectedTags.length > 0;
  
  return (
    <>
      <div className="flex flex-col gap-1 border rounded-md p-2 bg-card">
        <div className="flex items-center justify-between">
          <span className="text-xs font-medium">{label}</span>
          {hasValue && (
            <Button
              size="sm"
              variant="ghost"
              onClick={handleClearAll}
              className="h-5 px-1.5 text-xs"
              title="Clear all"
            >
              <X className="h-3 w-3" />
            </Button>
          )}
        </div>
        
        {/* Selected tags as chips */}
        {selectedTags.length > 0 && (
          <div className="flex flex-wrap gap-1.5 items-center">
            {selectedTags.map((tag, idx) => (
              <span 
                key={idx} 
                className="relative inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-primary/10 text-primary border border-primary/20 text-xs"
              >
                <span>{tag}</span>
                <button
                  type="button"
                  className="flex items-center justify-center w-4 h-4 rounded-full bg-primary/20 hover:bg-primary/30 text-primary transition-colors"
                  onClick={() => removeTag(tag)}
                  title="Remove tag"
                  aria-label={`Remove ${tag}`}
                >
                  <X className="w-3 h-3" />
                </button>
              </span>
            ))}
          </div>
        )}
        
        {/* Input for adding new tags */}
        <Input
          ref={inputRef}
          type="text"
          placeholder={placeholder}
          value={inputText}
          onChange={(e) => handleChange(e.target.value)}
          onFocus={onFocus}
          onBlur={onBlur}
          className="h-7 text-xs"
        />
      </div>
      
      {open && filtered.length > 0 && createPortal(
        <div 
          className="absolute z-50 bg-card border rounded-md shadow-lg max-h-60 overflow-y-auto"
          style={{ 
            left: pos.x, 
            top: pos.y, 
            minWidth: pos.width 
          }}
        >
          {filtered.map((tag, idx) => (
            <div
              key={idx}
              className="px-3 py-2 text-sm cursor-pointer hover:bg-accent transition-colors"
              onMouseDown={() => selectSuggestion(tag)}
            >
              {tag}
            </div>
          ))}
        </div>,
        document.body
      )}
    </>
  );
}
