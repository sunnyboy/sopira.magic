//*........................................................
//*       www/thermal_eye_ui/src/components/ui_custom/table/FilterPanel.tsx
//*       Container panel for filter components
//*
//*       Inheritance: Extends TablePanel with grid layout
//*       Uses: TablePanel (base) + grid layout for filters
//*........................................................

import React from 'react';
import { TablePanel } from './TablePanel';

interface FilterPanelProps {
  title?: string;
  icon?: React.ReactNode;
  children: React.ReactNode;
  activePresetName?: string | null;
  onSet?: () => void;
  onReset?: () => void;
  onRecall?: () => void;
  onClose?: () => void;
}

export function FilterPanel({
  title = 'Filters',
  icon,
  children,
  activePresetName,
  onSet,
  onReset,
  onRecall,
  onClose,
}: FilterPanelProps) {
  return (
    <TablePanel
      open={true}
      title={title}
      icon={icon}
      activePresetName={activePresetName}
      onSet={onSet}
      onReset={onReset}
      onRecall={onRecall}
      onClose={onClose}
    >
      {/* Flexibilný grid layout - každé dieťa sa zobrazí ako samostatný prvok */}
      <div className="flex flex-col gap-3">
        {children}
      </div>
    </TablePanel>
  );
}
