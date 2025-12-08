//*........................................................
//*       www/thermal_eye_ui/src/components/ui_custom/table/TableSearch.tsx
//*       Universal search component for tables with advanced syntax support
//*
//*       Inheritance: Custom component using shadcn Input
//*       Uses: Input (shadcn) + Filter icon + advanced search syntax
//*       Features: AND/OR/NOT operators, quoted phrases, parentheses
//*........................................................

import { Input } from "@/components/ui_custom/input";
import { Filter, X } from "lucide-react";
import { Button } from "@/components/ui_custom/button";

interface TableSearchProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  className?: string;
}

export function TableSearch({ 
  value, 
  onChange, 
  placeholder = 'Search… (Try: "exact phrase" AND (term1 OR term2))',
  className = ''
}: TableSearchProps) {
  const helpText = 
    'Advanced Search Syntax:\n\n' +
    '• Quoted phrases: "exact match" (exact phrase)\n' +
    '• AND (default): term1 term2 = term1 AND term2\n' +
    '• OR operator: term1 OR term2\n' +
    '• NOT operator: term1 NOT term2\n' +
    '• Parentheses: "phrase" AND (term1 OR term2)\n' +
    '• Complex: (term1 OR term2) AND NOT term3\n\n' +
    'Searches across all visible fields in the table';

  const handleClear = () => {
    onChange('');
  };

  return (
    <div 
      className={`flex items-center gap-2 border border-input rounded-xl px-3 py-2 ${className}`}
      data-component="TableSearch"
    >
      <Filter size={16} className="text-muted-foreground shrink-0" />
      <Input
        placeholder={placeholder}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        title={helpText}
        className="border-0 h-auto p-0 min-w-[260px] focus-visible:ring-0 focus-visible:ring-offset-0 bg-transparent flex-1"
      />
      {value && (
        <Button
          type="button"
          variant="ghost"
          size="sm"
          onClick={handleClear}
          className="h-6 w-6 p-0 shrink-0 hover:bg-muted"
          title="Clear search"
        >
          <X size={14} className="text-muted-foreground" />
        </Button>
      )}
    </div>
  );
}
