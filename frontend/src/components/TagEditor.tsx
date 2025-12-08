//*........................................................
//*       www/thermal_eye_ui/src/components/TagEditor.tsx
//*       Tag editor component with autocomplete
//*........................................................

/************************************************************************
 *  src/components/TagEditor.tsx
 *  Reusable tag editor component with autocomplete
 ************************************************************************/

import React, { useState, useMemo, useRef } from 'react';
import { createPortal } from 'react-dom';

interface TagEditorProps {
  value: string[];
  onChange: (tags: string[]) => void;
  suggestions: string[];
  onNewTag?: (name: string) => void;
}

export const TagEditor: React.FC<TagEditorProps> = ({ value, onChange, suggestions, onNewTag }) => {
  const [text, setText] = useState("");
  const [open, setOpen] = useState(false);
  const [pos, setPos] = useState({ x: 0, y: 0, width: 0 });
  const inputRef = useRef<HTMLInputElement>(null);
  
  const lower = (s: string) => s.trim().toLowerCase();
  const normalized = useMemo(() => new Set(value.map(lower)), [value]);
  
  const filtered = useMemo(() => {
    const searchText = lower(text);
    return suggestions.filter(s => !normalized.has(lower(s)) && lower(s).includes(searchText));
  }, [suggestions, normalized, text]);

  function add(tag: string) {
    const t = tag.trim();
    if (!t) return;
    if (!normalized.has(lower(t))) {
      onChange([...value, t]);
      onNewTag?.(t);
    }
    setText("");
    setOpen(false);
  }

  function remove(tag: string) {
    onChange(value.filter(v => lower(v) !== lower(tag)));
  }

  function onKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === 'Enter') {
      e.preventDefault();
      add(text);
    }
    if (e.key === 'Backspace' && !text && value.length) {
      e.preventDefault();
      onChange(value.slice(0, -1));
    }
    if (e.key === 'Escape') {
      setOpen(false);
    }
  }

  function onFocus() {
    updatePosition();
    setOpen(true);
  }

  function onBlur() {
    // Delay to allow click on suggestion item
    setTimeout(() => setOpen(false), 150);
  }

  function updatePosition() {
    if (!inputRef.current) return;
    const rect = inputRef.current.getBoundingClientRect();
    setPos({ x: rect.left, y: rect.bottom + 4, width: Math.max(160, rect.width) });
  }

  return (
    <>
      <div className="flex flex-wrap gap-1 items-center">
        {value.map((t, i) => (
          <span 
            key={i} 
            className="inline-flex items-center rounded-full bg-primary/10 px-2.5 py-0.5 text-xs font-medium text-primary border border-primary/20 gap-1"
          >
            {t}
            <button 
              type="button" 
              className="ml-0.5 inline-flex items-center justify-center w-3.5 h-3.5 rounded-full hover:bg-primary/20 text-primary/70 hover:text-primary transition-colors" 
              onClick={() => remove(t)} 
              title="Remove"
            >
              ×
            </button>
          </span>
        ))}
        <input 
          ref={inputRef} 
          className="h-6 px-2 text-xs border-0 focus:outline-none focus:ring-0 bg-transparent min-w-[80px]"
          value={text} 
          onChange={e => setText(e.target.value)} 
          onKeyDown={onKeyDown}
          onFocus={onFocus}
          onBlur={onBlur}
          placeholder="Add tag" 
        />
      </div>
      {open && filtered.length > 0 && createPortal(
        <div 
          className="fixed z-[9999] bg-popover border border-border rounded-md shadow-md min-w-[160px] max-w-[320px] max-h-[200px] overflow-y-auto"
          style={{ left: pos.x, top: pos.y, minWidth: pos.width }}
        >
          {filtered.map((s, idx) => (
            <div 
              key={idx} 
              className="px-3 py-2 text-xs cursor-pointer hover:bg-accent transition-colors border-b border-border/50 last:border-b-0" 
              onMouseDown={() => add(s)}
            >
              {s}
            </div>
          ))}
        </div>,
        document.body
      )}
    </>
  );
};
