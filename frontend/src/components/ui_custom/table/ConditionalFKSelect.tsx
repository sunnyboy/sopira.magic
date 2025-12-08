//*........................................................
//*       www/thermal_eye_ui/src/components/ui_custom/table/ConditionalFKSelect.tsx
//*       Conditional FK Select - zobrazí read-only field ak je len 1 možnosť a field je required
//*
//*       Purpose: Univerzálny komponent pre FK fields
//*       Dedičnosť: Používa komponenty z /components/ui_custom (nie /components/ui)
//*       
//*       Features:
//*       - Ak je len 1 možnosť a field je required → read-only field
//*       - Ak je autoSetValue a field je required → read-only field
//*       - Inak → Select dropdown
//*........................................................

import { useEffect } from 'react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui_custom/select';
import { Input } from '@/components/ui_custom/input';

type Option = { id: string; label: string };

interface ConditionalFKSelectProps {
  options: Option[];
  value: string | null;
  onChange: (value: string | null) => void;
  isLoading: boolean;
  disabled: boolean;
  placeholder: string;
  required: boolean;
  autoSetValue?: string | null;
}

/**
 * Conditional FK Select Component
 * 
 * Univerzálny komponent pre FK fields, ktorý automaticky zobrazí read-only field
 * ak je len jeden výber a field je povinný (required), inak zobrazí dropdown.
 * 
 * Použitie:
 * - Pre factory field: ak je len 1 factory vybratá v Dashboard, zobrazí read-only field
 * - Pre ostatné FK fields: ak je len 1 možnosť v options a field je required, zobrazí read-only field
 * - Inak: zobrazí štandardný Select dropdown
 */
export function ConditionalFKSelect({
  options,
  value,
  onChange,
  isLoading,
  disabled,
  placeholder,
  required,
  autoSetValue,
}: ConditionalFKSelectProps) {
  // Automaticky nastaviť hodnotu ak je len 1 možnosť a field je required
  useEffect(() => {
    if (required && !value) {
      if (options.length === 1) {
        onChange(options[0].id);
      } else if (autoSetValue) {
        onChange(autoSetValue);
      }
    }
  }, [options, required, value, autoSetValue, onChange]);

  // Ak je len 1 možnosť a field je required, zobraziť read-only field
  if (required && options.length === 1 && !isLoading) {
    const displayValue = options[0].label;
    return (
      <Input
        value={displayValue}
        disabled={true}
        readOnly
        className="bg-muted cursor-not-allowed"
      />
    );
  }

  // Ak je autoSetValue a field je required, zobraziť read-only field
  // Zobrazíme aj počas loading, ak už máme autoSetValue
  if (required && autoSetValue) {
    // Počkáme na načítanie options, aby sme mohli zobraziť správny label
    if (isLoading) {
      return (
        <Input
          value="Loading..."
          disabled={true}
          readOnly
          className="bg-muted cursor-not-allowed"
        />
      );
    }
    // Skúsime nájsť label v options
    const displayValue = options.find(opt => opt.id === autoSetValue)?.label;
    // Ak sme našli label, zobrazíme read-only field
    if (displayValue) {
      return (
        <Input
          value={displayValue}
          disabled={true}
          readOnly
          className="bg-muted cursor-not-allowed"
        />
      );
    }
    // Ak sme nenašli label, ale máme options, možno je problém s matching
    // V tomto prípade zobrazíme read-only field s UUID (fallback)
    // Alebo ak options sú prázdne, zobrazíme read-only field s UUID (fallback)
    // Vždy zobrazíme read-only field ak je autoSetValue nastavená
    return (
      <Input
        value={displayValue || autoSetValue}
        disabled={true}
        readOnly
        className="bg-muted cursor-not-allowed"
      />
    );
  }

  // Inak zobraziť Select dropdown (štandardné správanie)
  // Radix UI Select neumožňuje prázdny string ako hodnotu, používame špeciálnu hodnotu
  const EMPTY_VALUE = '__empty__';
  
  return (
    <Select
      value={value || EMPTY_VALUE}
      onValueChange={(val) => onChange(val === EMPTY_VALUE ? null : val)}
      disabled={disabled || isLoading}
    >
      <SelectTrigger>
        <SelectValue placeholder={isLoading ? 'Loading...' : placeholder} />
      </SelectTrigger>
      <SelectContent>
        {!required && <SelectItem value={EMPTY_VALUE}>—</SelectItem>}
        {options.map((opt) => (
          <SelectItem key={opt.id} value={opt.id}>
            {opt.label}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}

