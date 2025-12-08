//*........................................................
//*       www/thermal_eye_ui/src/components/ui_custom/table/FilterButtonGroup.tsx
//*       Compact button-style checkbox filter for small option sets
//*........................................................

import React from 'react';
import { Checkbox } from '@/components/ui_custom/checkbox';

interface FilterButtonGroupProps {
  label: string;
  options: Array<{ value: string; label: string }>;
  selectedValues: string[];
  onChange: (selectedValues: string[]) => void;
}

export function FilterButtonGroup({
  label,
  options,
  selectedValues,
  onChange,
}: FilterButtonGroupProps) {
  const handleToggle = (value: string, checked: boolean) => {
    const next = checked
      ? Array.from(new Set([...selectedValues, value]))
      : selectedValues.filter((v) => v !== value);
    onChange(next);
  };

  return (
    <div className="flex flex-col gap-2">
      <span className="text-xs text-muted-foreground font-medium">{label}</span>
      <div className="flex gap-2 flex-wrap">
        {options.map((option) => (
          <label
            key={option.value}
            className="flex items-center gap-2 cursor-pointer px-3 py-1.5 rounded border border-border hover:bg-muted/50 transition-colors"
          >
            <Checkbox
              checked={selectedValues.includes(option.value)}
              onCheckedChange={(checked) => handleToggle(option.value, checked === true)}
            />
            <span className="text-sm">{option.label}</span>
          </label>
        ))}
      </div>
    </div>
  );
}
