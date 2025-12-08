//*........................................................
//*       www/thermal_eye_ui/src/components/ui_custom/table/FilterDateRange.tsx
//*       Date range filter with date pickers
//*........................................................

import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui_custom/button';
import { X, Calendar as CalendarIcon } from 'lucide-react';
import { Popover, PopoverTrigger, PopoverContent } from '@/components/ui/popover';
import { Calendar } from '@/components/ui/calendar';

interface FilterDateRangeProps {
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

export function FilterDateRange({
  label,
  table,
  columnId,
}: FilterDateRangeProps) {
  const autoMode = table && columnId;
  
  // Získaj hodnoty z column
  const filterValue = autoMode 
    ? (table.getColumn(columnId)?.getFilterValue() as { from?: string, to?: string })
    : undefined;
  
  // Helpers
  // Local date serialization to avoid timezone shift
  const toIso = (d: Date | undefined) => {
    if (!d) return '';
    const y = d.getFullYear();
    const m = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${y}-${m}-${day}`;
  };
  const parseIso = (s: string | undefined) => {
    if (!s) return undefined;
    const [y, m, d] = s.split('-').map((x) => parseInt(x, 10));
    return new Date(y, (m || 1) - 1, d || 1);
  };
  const toDdMmYyyy = (s: string | undefined) => {
    if (!s) return '';
    const [y,m,d] = s.split('-');
    return `${d}.${m}.${y}`;
  };

  // Local state as ISO strings
  const [fromIso, setFromIso] = useState<string>(filterValue?.from ?? '');
  const [toIsoStr, setToIsoStr] = useState<string>(filterValue?.to ?? '');
  const [openFrom, setOpenFrom] = useState(false);
  const [openTo, setOpenTo] = useState(false);
  
  // Sync local state with filter value when it changes externally (e.g., from recall filter)
  useEffect(() => {
    setFromIso(filterValue?.from ?? '');
    setToIsoStr(filterValue?.to ?? '');
  }, [filterValue?.from, filterValue?.to]);
  
  // Handler pre zmenu OD (from) - update local state and column filter
  const handleFromChange = (iso: string) => {
    setFromIso(iso);
    if (!autoMode) return;
    const col = table.getColumn(columnId);
    const current = (col?.getFilterValue() as { from?: string, to?: string }) || {};
    const newValue = iso ? { ...current, from: iso } : (current.to ? { to: current.to } : undefined);
    col?.setFilterValue(newValue);
  };
  
  // Handler pre zmenu DO (to) - update local state and column filter
  const handleToChange = (iso: string) => {
    setToIsoStr(iso);
    if (!autoMode) return;
    const col = table.getColumn(columnId);
    const current = (col?.getFilterValue() as { from?: string, to?: string }) || {};
    const newValue = iso ? { ...current, to: iso } : (current.from ? { from: current.from } : undefined);
    col?.setFilterValue(newValue);
  };
  
  // Clear button
  const hasValues = fromIso !== '' || toIsoStr !== '';
  const handleClear = () => {
    setFromIso('');
    setToIsoStr('');
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
        {/* From date */}
        <Popover open={openFrom} onOpenChange={setOpenFrom}>
          <PopoverTrigger asChild>
            <Button variant="default" size="sm" className="h-7 text-xs w-[140px] justify-between px-2">
              <span className="truncate">{fromIso ? toDdMmYyyy(fromIso) : 'dd.mm.rrrr'}</span>
              <CalendarIcon className="w-3 h-3 opacity-70" />
            </Button>
          </PopoverTrigger>
          <PopoverContent align="start" className="p-0 w-auto">
            <Calendar
              mode="single"
              selected={parseIso(fromIso)}
              onSelect={(d) => { setOpenFrom(false); handleFromChange(toIso(d)); }}
              captionLayout="dropdown"
            />
          </PopoverContent>
        </Popover>

        {/* To date */}
        <Popover open={openTo} onOpenChange={setOpenTo}>
          <PopoverTrigger asChild>
            <Button variant="default" size="sm" className="h-7 text-xs w-[140px] justify-between px-2">
              <span className="truncate">{toIsoStr ? toDdMmYyyy(toIsoStr) : 'dd.mm.rrrr'}</span>
              <CalendarIcon className="w-3 h-3 opacity-70" />
            </Button>
          </PopoverTrigger>
          <PopoverContent align="start" className="p-0 w-auto">
            <Calendar
              mode="single"
              selected={parseIso(toIsoStr)}
              onSelect={(d) => { setOpenTo(false); handleToChange(toIso(d)); }}
              captionLayout="dropdown"
            />
          </PopoverContent>
        </Popover>
      </div>
    </div>
  );
}
