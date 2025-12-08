//*........................................................
//*       www/thermal_eye_ui/src/components/ui_custom/table/EditableCell.tsx
//*       Editable table cell with inline editing (shadcn-based)
//*........................................................

import React, { useRef, useEffect, useMemo, useState } from 'react';
import { Input } from '@/components/ui_custom/input';
import { Textarea } from '@/components/ui_custom/textarea';
import { Spinner } from '@/components/ui/spinner';
import { Popover, PopoverTrigger, PopoverContent } from '@/components/ui/popover';
import { Calendar } from '@/components/ui/calendar';
import { toIsoLocal, parseIsoLocal, toDisplayDate, fromDisplayDate } from '@/utils/date';
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from '@/components/ui/select';
import { Calendar as CalendarIcon, Clock } from 'lucide-react';
import { toastMessages } from '@/utils/toastMessages';
import { TagEditor } from '@/components/TagEditor';

interface EditableCellProps {
  value: string;
  isEditing: boolean;
  onStartEdit: () => void;
  onSave: (value: string) => void;
  onCancel: () => void;
  rowId?: string | number; // for focusing after save
  autoFocusOnSave?: boolean; // default true
  placeholder?: string;
  type?: 'text' | 'number' | 'date' | 'time' | 'select' | 'tag';
  multiline?: boolean;
  min?: number;
  max?: number;
  step?: number;
  decimals?: number; // number of decimal places for number formatting
  debounceMs?: number; // if provided, auto-save with debounce while typing
  onValidate?: (value: string) => string | null; // return error message or null
  isSaving?: boolean; // show spinner
  saveOnBlur?: boolean; // default true
  saveOnEnter?: boolean; // default true (ignored for multiline)
  options?: { value: string; label: string }[]; // for select
  selectPlaceholder?: string;
  editingAllowed?: boolean; // if false, view-only
  highlightedContent?: React.ReactNode; // rendered in view mode
  className?: string;
  // Tag-specific props
  tagValue?: string[]; // for type='tag' - array of tag strings
  tagSuggestions?: string[]; // for type='tag' - suggestions list
  onNewTag?: (tagName: string) => void; // for type='tag' - callback when new tag created
}

export function EditableCell({
  value,
  isEditing,
  onStartEdit,
  onSave,
  onCancel,
  placeholder = '',
  type = 'text',
  multiline = false,
  min,
  max,
  step,
  decimals,
  debounceMs,
  onValidate,
  isSaving = false,
  saveOnBlur = true,
  saveOnEnter = true,
  options,
  selectPlaceholder = '—',
  editingAllowed = true,
  highlightedContent,
  className = '',
  rowId,
  autoFocusOnSave = true,
  tagValue = [],
  tagSuggestions = [],
  onNewTag,
}: EditableCellProps) {
  const inputRef = useRef<HTMLInputElement | HTMLTextAreaElement>(null);
  const popoverContentRef = useRef<HTMLDivElement | null>(null);
  const wrapperRef = useRef<HTMLDivElement | null>(null);
  const [local, setLocal] = useState<string>(value ?? '');
  const [timer, setTimer] = useState<number | null>(null);
  const [inlineError, setInlineError] = useState<string | null>(null);
  const [pickerOpen, setPickerOpen] = useState(false);
  const clearTimer = () => { if (timer) { window.clearTimeout(timer); setTimer(null); } };

  useEffect(() => {
    if (isEditing) {
      if (type === 'date') {
        const disp = toDisplayDate(value);
        setLocal(disp);
      } else if (type === 'number' || type === 'temperature') {
        // Format number to 1 decimal place in edit mode
        if (value && value !== '') {
          const numValue = Number(value);
          if (!isNaN(numValue)) {
            const decimalPlaces = decimals ?? 1;
            setLocal(numValue.toFixed(decimalPlaces));
          } else {
            setLocal(value ?? '');
          }
        } else {
          setLocal('');
        }
      } else {
        setLocal(value ?? '');
      }
    }
  }, [isEditing, value, type, decimals]);

  useEffect(() => {
    if (isEditing && inputRef.current) {
      inputRef.current.focus();
      // select only for text/number
      if (!multiline && 'select' in inputRef.current) {
        try { (inputRef.current as HTMLInputElement).select(); } catch {}
      }
    }
  }, [isEditing, multiline]);

  const numberError = useMemo(() => {
    if (type !== 'number') return null;
    if (local === '') return null;
    const n = Number(local);
    if (Number.isNaN(n)) return 'Invalid number';
    if (min !== undefined && n < min) return `Min ${min}`;
    if (max !== undefined && n > max) return `Max ${max}`;
    return null;
  }, [type, local, min, max]);

  const customError = useMemo(() => (onValidate ? onValidate(local) : null), [local, onValidate]);
  const error = numberError || customError || inlineError;

  const triggerSave = async (val: string) => {
    if (error) return; // do not save invalid value
    await onSave(val);
    // Note: Toast is shown by parent/hook on successful save
  };

  const handleChange = (val: string) => {
    setLocal(val);
    if (debounceMs && debounceMs > 0) {
      clearTimer();
      const t = window.setTimeout(() => triggerSave(val), debounceMs);
      setTimer(t);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !multiline && saveOnEnter) {
      e.preventDefault();
      clearTimer();
      triggerSave((e.target as HTMLInputElement).value);
    } else if (e.key === 'Escape') {
      e.preventDefault();
      clearTimer();
      onCancel();
    }
  };

  if (isEditing && editingAllowed) {
    const commonProps = {
      ref: inputRef as any,
      value: local,
      onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => handleChange(e.target.value),
      onBlur: saveOnBlur
        ? (e: React.FocusEvent<HTMLInputElement | HTMLTextAreaElement>) => { clearTimer(); triggerSave(e.target.value); }
        : undefined,
      onKeyDown: handleKeyDown,
      placeholder,
      className: `${className} ${error ? 'border-destructive ring-destructive/50' : ''}`,
    } as const;

    // Specialized shadcn pickers for date/time
    if (type === 'date') {
      const handleManualSave = async (raw: string) => {
        const norm = fromDisplayDate(raw);
        if (norm === null) { setInlineError('Invalid date'); return; }
        setInlineError(null);
        setLocal(toDisplayDate(norm));
        await onSave(norm);
        // Note: Toast is shown by parent/hook on successful save
      };

      return (
        <div className="rounded px-1 py-0.5 relative min-w-[220px]">
          <div className="relative" ref={wrapperRef}>
            <Input
              ref={inputRef as any}
              value={local}
              onChange={(e) => { setInlineError(null); setLocal(e.target.value); }}
              onBlur={saveOnBlur ? (e) => {
                clearTimer();
                const rt = e.relatedTarget as Node | null;
                if (rt && (wrapperRef.current?.contains(rt) || popoverContentRef.current?.contains(rt as Node))) {
                  return; // ignore blur when moving into trigger or popover
                }
                handleManualSave(e.target.value);
              } : undefined}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !multiline && saveOnEnter) { e.preventDefault(); clearTimer(); handleManualSave((e.target as HTMLInputElement).value); }
                else if (e.key === 'Escape') { e.preventDefault(); clearTimer(); onCancel(); }
              }}
              placeholder="DD.MM.YYYY"
              className={`${className} pr-8 ${error ? 'border-destructive ring-destructive/50' : ''}`}
              inputMode="numeric"
            />
            <Popover open={pickerOpen} onOpenChange={(o) => { setPickerOpen(o); if (!o) { handleManualSave(local); } }}>
              <PopoverTrigger asChild>
                <button
                  type="button"
                  className="absolute right-1 top-1/2 -translate-y-1/2 p-1 text-muted-foreground hover:text-foreground"
                  aria-label="Open date picker"
                  onMouseDown={(e) => { e.preventDefault(); e.stopPropagation(); }}
                  onClick={(e) => { e.preventDefault(); e.stopPropagation(); setPickerOpen(true); }}
                >
                  <CalendarIcon className="w-4 h-4" />
                </button>
              </PopoverTrigger>
              <PopoverContent ref={(el) => { popoverContentRef.current = el; }} align="start" className="p-0 w-auto">
                <Calendar
                  mode="single"
                  selected={parseIsoLocal(fromDisplayDate(local) || value || '')}
                  defaultMonth={parseIsoLocal(fromDisplayDate(local) || value || '')}
                  captionLayout="dropdown"
                  onSelect={async (d) => {
                    const iso = toIsoLocal(d);
                    setLocal(toDisplayDate(iso));
                    setInlineError(null);
                    if (iso) {
                      await onSave(iso);
                      // Note: Toast is shown by parent/hook on successful save
                    }
                  }}
                />
              </PopoverContent>
            </Popover>
          </div>
          {isSaving && (
            <span className="absolute right-6 top-1/2 -translate-y-1/2">
              <Spinner className="w-4 h-4" />
            </span>
          )}
          {error && (
            <div className="text-[11px] text-destructive mt-1 px-0.5">{error}</div>
          )}
        </div>
      );
    }

    if (type === 'time') {
      const pad2 = (n: number) => String(n).padStart(2,'0');
      const normalizeTimeInput = (s: string): string | null => {
        const t = (s || '').trim();
        if (!t) return '';
        const m = t.match(/^(\d{1,2})[:.]?(\d{2})$/);
        if (!m) return null;
        let hh = parseInt(m[1], 10);
        let mm = parseInt(m[2], 10);
        if (hh < 0 || hh > 23 || mm < 0 || mm > 59) return null;
        return `${pad2(hh)}:${pad2(mm)}`;
      };
      const [hh, mm] = (() => {
        const m = normalizeTimeInput(local);
        if (!m) return ['', ''];
        const [H, M] = m.split(':');
        return [H, M];
      })();

      const handleManualSave = (raw: string) => {
        const norm = normalizeTimeInput(raw);
        if (norm === null) { setInlineError('Invalid time'); return; }
        setInlineError(null);
        setLocal(norm);
        triggerSave(norm);
      };

      return (
        <div className="rounded px-1 py-0.5 relative min-w-[200px]">
          <div className="relative" ref={wrapperRef}>
            <Input
              ref={inputRef as any}
              value={local}
              onChange={(e) => { setInlineError(null); setLocal(e.target.value); }}
              onBlur={saveOnBlur ? (e) => {
                clearTimer();
                const rt = e.relatedTarget as Node | null;
                if (rt && (wrapperRef.current?.contains(rt) || popoverContentRef.current?.contains(rt as Node))) {
                  return; // ignore blur when moving into trigger or popover
                }
                handleManualSave(e.target.value);
              } : undefined}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !multiline && saveOnEnter) { e.preventDefault(); clearTimer(); handleManualSave((e.target as HTMLInputElement).value); }
                else if (e.key === 'Escape') { e.preventDefault(); clearTimer(); onCancel(); }
              }}
              placeholder="HH:MM"
              className={`${className} pr-8 ${error ? 'border-destructive ring-destructive/50' : ''}`}
              inputMode="numeric"
            />
            <Popover open={pickerOpen} onOpenChange={setPickerOpen}>
              <PopoverTrigger asChild>
                <button
                  type="button"
                  className="absolute right-1 top-1/2 -translate-y-1/2 p-1 text-muted-foreground hover:text-foreground"
                  aria-label="Open time picker"
                  onMouseDown={(e) => { e.preventDefault(); e.stopPropagation(); }}
                  onClick={(e) => { e.preventDefault(); e.stopPropagation(); setPickerOpen(true); }}
                >
                  <Clock className="w-4 h-4" />
                </button>
              </PopoverTrigger>
              <PopoverContent ref={(el) => { popoverContentRef.current = el; }} align="start" className="p-2 w-auto">
                <div className="flex items-center gap-2">
                  <Select
                    value={hh}
                    onValueChange={(v) => {
                      const next = v && mm ? `${v}:${mm}` : v ? `${v}:00` : '';
                      setLocal(next);
                      setInlineError(null);
                      if (v) triggerSave(next);
                    }}
                  >
                    <SelectTrigger className="h-8 w-16"><SelectValue placeholder="HH" /></SelectTrigger>
                    <SelectContent>
                      {Array.from({length:24}).map((_,i)=>(<SelectItem key={i} value={pad2(i)}>{pad2(i)}</SelectItem>))}
                    </SelectContent>
                  </Select>
                  <Select
                    value={mm}
                    onValueChange={(v) => {
                      const next = hh ? `${hh}:${v}` : v ? `00:${v}` : '';
                      setLocal(next);
                      setInlineError(null);
                      if (v) triggerSave(next);
                    }}
                  >
                    <SelectTrigger className="h-8 w-16"><SelectValue placeholder="MM" /></SelectTrigger>
                    <SelectContent>
                      {Array.from({length:60}).map((_,i)=>{ const m=pad2(i); return (<SelectItem key={m} value={m}>{m}</SelectItem>); })}
                    </SelectContent>
                  </Select>
                </div>
              </PopoverContent>
            </Popover>
          </div>
          {isSaving && (
            <span className="absolute right-6 top-1/2 -translate-y-1/2">
              <Spinner className="w-4 h-4" />
            </span>
          )}
          {error && (
            <div className="text-[11px] text-destructive mt-1 px-0.5">{error}</div>
          )}
        </div>
      );
    }

    if (type === 'tag') {
      return (
        <div className="relative min-w-[200px]">
          <TagEditor
            value={tagValue}
            onChange={async (newTags) => {
              try {
                // Convert tags array to string for onSave (expects string)
                await onSave(JSON.stringify(newTags));
                showSaveToast();
              } catch (err) {
                // Error already handled by parent
              }
            }}
            suggestions={tagSuggestions}
            onNewTag={onNewTag}
          />
          {isSaving && (
            <span className="absolute right-1 top-1/2 -translate-y-1/2">
              <Spinner className="w-4 h-4" />
            </span>
          )}
        </div>
      );
    }

    return (
      <div className="rounded px-1 py-0.5 relative min-w-[160px]">
        {multiline ? (
          <Textarea {...commonProps} rows={2} />
        ) : type === 'select' ? (
          <Select
            value={local || undefined}
            onValueChange={(val) => { 
              const newVal = val || '';
              setLocal(newVal); 
              triggerSave(newVal); 
            }}
          >
            <SelectTrigger 
              className={`h-7 text-xs w-full ${className}`}
            >
              <SelectValue placeholder={selectPlaceholder} />
            </SelectTrigger>
            <SelectContent>
              {(options || []).map(opt => (
                <SelectItem key={opt.value} value={opt.value}>
                  {opt.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        ) : (
          <Input 
            {...commonProps} 
            type={type} 
            min={min} 
            max={max} 
            step={step}
            className={commonProps.className}
          />
        )}
        {isSaving && (
          <span className="absolute right-1 top-1/2 -translate-y-1/2">
            <Spinner className="w-4 h-4" />
          </span>
        )}
        {error && (
          <div className="text-[11px] text-destructive mt-1 px-0.5">{error}</div>
        )}
      </div>
    );
  }

  // Format number values for display (1 decimal place for temperature/weight)
  const formatDisplayValue = (val: string): string => {
    if ((type === 'number' || type === 'temperature') && val && val !== '') {
      const numValue = Number(val);
      if (!isNaN(numValue)) {
        // Use decimals prop if provided, otherwise default to 1
        const decimalPlaces = decimals ?? 1;
        return numValue.toFixed(decimalPlaces);
      }
    }
    return val;
  };

  const displayValue = formatDisplayValue(value);
  const displayTitle = highlightedContent ? String(highlightedContent) : (displayValue || '—');

  return (
    <div
      className={`cursor-pointer hover:bg-muted/70 px-2 py-1 rounded bg-muted/50 border border-border overflow-hidden text-xs whitespace-nowrap text-ellipsis flex items-center ${className}`}
      style={{ maxHeight: '1.5rem', height: '1.5rem' }}
      onDoubleClick={onStartEdit}
      title={displayTitle}
    >
      {highlightedContent || displayValue || <span className="text-muted-foreground">—</span>}
    </div>
  );
}
