//*........................................................
//*       www/thermal_eye_ui/src/components/ui_custom/table/FilterTimeRange.tsx
//*       Time range filter with time pickers
//*........................................................

import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui_custom/button';
import { X, Clock } from 'lucide-react';
import { Popover, PopoverTrigger, PopoverContent } from '@/components/ui/popover';
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from '@/components/ui_custom/select';

interface FilterTimeRangeProps {
  label: string;
  table?: any;
  columnId?: string;
  // Optional custom API parameter names (for buildQuery)
  // If not provided, defaults to columnId-based names
  apiParamNames?: {
    exact: string;
    from: string;
    to: string;
  };
}

export function FilterTimeRange({
  label,
  table,
  columnId,
}: FilterTimeRangeProps) {
  const autoMode = table && columnId;
  
  // Získaj hodnoty z column
  const filterValue = autoMode 
    ? (table.getColumn(columnId)?.getFilterValue() as { from?: string, to?: string })
    : undefined;
  
  // Helpers
  const pad2 = (n: number) => String(n).padStart(2, '0');
  const clamp = (v: number, min: number, max: number) => Math.max(min, Math.min(max, v));
  const parseHM = (s?: string): { h: string; m: string } => {
    if (!s) return { h: '', m: '' };
    const [h, m] = s.split(':');
    return { h: h ?? '', m: (m ?? '').slice(0, 2) };
  };
  const toHM = (h: string, m: string) => (h && m ? `${h}:${m}` : '');

  // Local state
  const [fromH, setFromH] = useState(parseHM(filterValue?.from).h);
  const [fromM, setFromM] = useState(parseHM(filterValue?.from).m);
  const [toH, setToH] = useState(parseHM(filterValue?.to).h);
  const [toM, setToM] = useState(parseHM(filterValue?.to).m);
  const [openFrom, setOpenFrom] = useState(false);
  const [openTo, setOpenTo] = useState(false);
  
  // Sync local state with filter value when it changes externally (e.g., from recall filter)
  useEffect(() => {
    const f = parseHM(filterValue?.from);
    const t = parseHM(filterValue?.to);
    setFromH(f.h); setFromM(f.m);
    setToH(t.h); setToM(t.m);
  }, [filterValue?.from, filterValue?.to]);
  
  // Handler pre zmenu OD (from) - update local state and column filter
  const handleFromChange = (h: string, m: string) => {
    setFromH(h); setFromM(m);
    if (!autoMode) return;
    const v = toHM(h, m);
    const col = table.getColumn(columnId);
    const current = (col?.getFilterValue() as { from?: string, to?: string }) || {};
    const newValue = v ? { ...current, from: v } : (current.to ? { to: current.to } : undefined);
    col?.setFilterValue(newValue);
  };
  
  // Handler pre zmenu DO (to) - update local state and column filter
  const handleToChange = (h: string, m: string) => {
    setToH(h); setToM(m);
    if (!autoMode) return;
    const v = toHM(h, m);
    const col = table.getColumn(columnId);
    const current = (col?.getFilterValue() as { from?: string, to?: string }) || {};
    const newValue = v ? { ...current, to: v } : (current.from ? { from: current.from } : undefined);
    col?.setFilterValue(newValue);
  };
  
  // Clear button
  const hasValues = !!toHM(fromH, fromM) || !!toHM(toH, toM);
  const handleClear = () => {
    setFromH(''); setFromM(''); setToH(''); setToM('');
    if (autoMode) {
      table.getColumn(columnId)?.setFilterValue(undefined);
    }
  };

  return (
    <div className="flex flex-col gap-1 border rounded-md p-2 bg-card">
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium">{label}</span>
        {hasValues && (
          <Button
            size="sm"
            variant="ghost"
            onClick={handleClear}
            className="h-5 px-1.5 text-xs"
            title="Clear"
          >
            <X className="h-3 w-3" />
          </Button>
        )}
      </div>
      <div className="flex gap-1">
        {/* FROM time */}
        <Popover open={openFrom} onOpenChange={setOpenFrom}>
          <PopoverTrigger asChild>
            <Button variant="default" size="sm" className="h-7 text-xs w-[120px] justify-between px-2">
              <span className="truncate">{toHM(fromH, fromM) || '--:--'}</span>
              <Clock className="w-3 h-3 opacity-70" />
            </Button>
          </PopoverTrigger>
          <PopoverContent align="start" className="p-2 w-auto">
            <div className="flex items-center gap-2">
              <Select value={fromH} onValueChange={(v) => handleFromChange(v, fromM)}>
                <SelectTrigger className="h-8 w-16"><SelectValue placeholder="HH" /></SelectTrigger>
                <SelectContent>
                  {Array.from({ length: 24 }).map((_, i) => (
                    <SelectItem key={i} value={pad2(i)}>{pad2(i)}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Select value={fromM} onValueChange={(v) => handleFromChange(fromH, v)}>
                <SelectTrigger className="h-8 w-16"><SelectValue placeholder="MM" /></SelectTrigger>
                <SelectContent>
                  {Array.from({ length: 12 }).map((_, i) => {
                    const m = pad2(i * 5);
                    return <SelectItem key={m} value={m}>{m}</SelectItem>;
                  })}
                </SelectContent>
              </Select>
            </div>
          </PopoverContent>
        </Popover>

        {/* TO time */}
        <Popover open={openTo} onOpenChange={setOpenTo}>
          <PopoverTrigger asChild>
            <Button variant="default" size="sm" className="h-7 text-xs w-[120px] justify-between px-2">
              <span className="truncate">{toHM(toH, toM) || '--:--'}</span>
              <Clock className="w-3 h-3 opacity-70" />
            </Button>
          </PopoverTrigger>
          <PopoverContent align="start" className="p-2 w-auto">
            <div className="flex items-center gap-2">
              <Select value={toH} onValueChange={(v) => handleToChange(v, toM)}>
                <SelectTrigger className="h-8 w-16"><SelectValue placeholder="HH" /></SelectTrigger>
                <SelectContent>
                  {Array.from({ length: 24 }).map((_, i) => (
                    <SelectItem key={i} value={pad2(i)}>{pad2(i)}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Select value={toM} onValueChange={(v) => handleToChange(toH, v)}>
                <SelectTrigger className="h-8 w-16"><SelectValue placeholder="MM" /></SelectTrigger>
                <SelectContent>
                  {Array.from({ length: 12 }).map((_, i) => {
                    const m = pad2(i * 5);
                    return <SelectItem key={m} value={m}>{m}</SelectItem>;
                  })}
                </SelectContent>
              </Select>
            </div>
          </PopoverContent>
        </Popover>
      </div>
    </div>
  );
}
