//*........................................................
//*       www/thermal_eye_ui/src/components/ui_custom/table/FilterRow.tsx
//*       Grid row wrapper for filter components
//*........................................................

import React from 'react';

interface FilterRowProps {
  children: React.ReactNode;
  cols?: 2 | 3 | 4;
}

export function FilterRow({ children, cols = 4 }: FilterRowProps) {
  // Use grid-template-columns with minmax to ensure minimum width of 100px
  // This creates a responsive grid that maintains readable filter cards
  const gridStyle = {
    display: 'grid',
    gridTemplateColumns: `repeat(auto-fit, minmax(max(230px, ${80 / cols}%), 1fr))`,
    gap: '0.75rem', // gap-3
  };

  return (
    <div style={gridStyle}>
      {children}
    </div>
  );
}
