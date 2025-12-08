//*........................................................
//*       www/thermal_eye_ui/src/components/ui_custom/table/FilterInput.tsx
//*       Text input filter component
//*........................................................

import React from 'react';
import { Input } from '@/components/ui_custom/input';
import { Button } from '@/components/ui_custom/button';
import { X } from 'lucide-react';

interface FilterInputProps {
  label: string;
  type?: 'text' | 'number' | 'range';
  // Pre text/number filtre (manuálny režim)
  value?: string | number;
  onChange?: (value: string) => void;
  placeholder?: string;
  min?: number;
  max?: number;
  // Pre range filtre (manuálny režim - backward compatibility)
  minValue?: number;
  maxValue?: number;
  onMinChange?: (value: number | undefined) => void;
  onMaxChange?: (value: number | undefined) => void;
  // Pre automatický režim s TanStack Table
  table?: any;
  columnId?: string;
}

export function FilterInput({
  label,
  type = 'text',
  value,
  onChange,
  placeholder,
  min,
  max,
  minValue,
  maxValue,
  onMinChange,
  onMaxChange,
  table,
  columnId,
}: FilterInputProps) {
  // Automatický režim - získa hodnoty z table column
  const autoMode = table && columnId;
  
  // Pre range: získaj hodnoty z column ak je auto mode
  const actualMinValue = autoMode && type === 'range'
    ? (table.getColumn(columnId)?.getFilterValue() as { min?: number, max?: number })?.min
    : minValue;
  const actualMaxValue = autoMode && type === 'range'
    ? (table.getColumn(columnId)?.getFilterValue() as { min?: number, max?: number })?.max
    : maxValue;
  
  // Pre text: získaj hodnotu z column ak je auto mode
  const actualValue = autoMode && type !== 'range'
    ? (table.getColumn(columnId)?.getFilterValue() as string) ?? ''
    : value;
  
  // Handler pre range min change
  const handleMinChange = (min: number | undefined) => {
    if (autoMode) {
      const col = table.getColumn(columnId);
      const current = (col?.getFilterValue() as { min?: number, max?: number }) || {};
      const newValue = min === undefined ? { max: current.max } : { ...current, min };
      col?.setFilterValue(Object.keys(newValue).length > 0 && Object.values(newValue).some(v => v !== undefined) ? newValue : undefined);
    } else {
      onMinChange?.(min);
    }
  };
  
  // Handler pre range max change
  const handleMaxChange = (max: number | undefined) => {
    if (autoMode) {
      const col = table.getColumn(columnId);
      const current = (col?.getFilterValue() as { min?: number, max?: number }) || {};
      const newValue = max === undefined ? { min: current.min } : { ...current, max };
      col?.setFilterValue(Object.keys(newValue).length > 0 && Object.values(newValue).some(v => v !== undefined) ? newValue : undefined);
    } else {
      onMaxChange?.(max);
    }
  };
  
  // Handler pre text/number change
  const handleChange = (val: string) => {
    if (autoMode) {
      table.getColumn(columnId)?.setFilterValue(val || undefined);
    } else {
      onChange?.(val);
    }
  };
  if (type === 'range') {
    const hasValues = actualMinValue !== undefined || actualMaxValue !== undefined;
    const handleClear = () => {
      // Vymaž celý filter naraz (nie sekvenčne)
      if (autoMode) {
        table.getColumn(columnId)?.setFilterValue(undefined);
      } else {
        onMinChange?.(undefined);
        onMaxChange?.(undefined);
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
        <div className="flex gap-1.5">
          <Input
            type="number"
            placeholder="≥ min"
            value={actualMinValue?.toString() ?? ''}
            onChange={(e) => handleMinChange(e.target.value === '' ? undefined : Number(e.target.value))}
            min={min}
            max={max}
            className="h-7 text-xs"
          />
          <Input
            type="number"
            placeholder="≤ max"
            value={actualMaxValue?.toString() ?? ''}
            onChange={(e) => handleMaxChange(e.target.value === '' ? undefined : Number(e.target.value))}
            min={min}
            max={max}
            className="h-7 text-xs"
          />
        </div>
      </div>
    );
  }

  // Text/number input s Clear buttonom
  const hasValue = actualValue !== undefined && actualValue !== '';
  const handleTextClear = () => {
    handleChange('');
  };

  return (
    <div className="flex flex-col gap-1 border rounded-md p-2 bg-card">
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium">{label}</span>
        {hasValue && (
          <Button
            size="sm"
            variant="ghost"
            onClick={handleTextClear}
            className="h-5 px-1.5 text-xs"
            title="Clear"
          >
            <X className="h-3 w-3" />
          </Button>
        )}
      </div>
      <Input
        type={type}
        value={actualValue?.toString() ?? ''}
        onChange={(e) => handleChange(e.target.value)}
        placeholder={placeholder}
        min={min}
        max={max}
        className="h-7 text-xs"
      />
    </div>
  );
}
