//*........................................................
//*       www/thermal_eye_ui/src/components/ui_custom/table/FilterCheckbox.tsx
//*       Checkbox filter component
//*........................................................

import React from 'react';
import { Checkbox } from '@/components/ui_custom/checkbox';

interface FilterCheckboxProps {
  label: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
}

export function FilterCheckbox({ label, checked, onChange }: FilterCheckboxProps) {
  return (
    <label className="flex items-center gap-2 cursor-pointer">
      <Checkbox
        checked={checked}
        onCheckedChange={(checked) => onChange(checked === true)}
      />
      <span className="text-sm">{label}</span>
    </label>
  );
}
