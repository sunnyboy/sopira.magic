//*........................................................
//*       www/thermal_eye_ui/src/components/ui_custom/table/TablePanel.tsx
//*       Collapsible panel wrapper for tables
//*
//*       Inheritance: Custom component (no shadcn parent)
//*       Uses: framer-motion (AnimatePresence + motion.div)
//*       Purpose: Animated collapsible panels for filters/columns
//*........................................................

import { motion, AnimatePresence } from "framer-motion";
import { ReactNode } from "react";
import { PanelHeader } from "./PanelHeader";

interface TablePanelProps {
  open: boolean;
  title: string;
  icon?: ReactNode;
  children: ReactNode;
  activePresetName?: string | null;
  isModified?: boolean;
  onRevertToPreset?: () => void;
  onSaveModification?: () => void;
  isSaving?: boolean;
  onSet?: () => void;
  onReset?: () => void;
  onRecall?: () => void;
  onClose?: () => void;
  onToggleDebug?: () => void;
  showDebug?: boolean;
  onSelectAll?: () => void;
  onDeselectAll?: () => void;
}

export function TablePanel({ 
  open, 
  title, 
  icon, 
  children, 
  activePresetName, 
  isModified,
  onRevertToPreset,
  onSaveModification,
  isSaving,
  onSet, 
  onReset, 
  onRecall, 
  onClose, 
  onToggleDebug, 
  showDebug, 
  onSelectAll, 
  onDeselectAll 
}: TablePanelProps) {
  return (
    <AnimatePresence>
      {open && (
        <motion.div 
          initial={{ height: 0, opacity: 0 }} 
          animate={{ height: 'auto', opacity: 1 }} 
          exit={{ height: 0, opacity: 0 }}
          className="p-4 mx-4 my-2 border border-border rounded-xl bg-card"
          data-component="TablePanel"
        >
          <PanelHeader
            title={title}
            icon={icon}
            activePresetName={activePresetName}
            isModified={isModified}
            onRevertToPreset={onRevertToPreset}
            onSaveModification={onSaveModification}
            isSaving={isSaving}
            onSet={onSet}
            onReset={onReset}
            onRecall={onRecall}
            onClose={onClose}
            onToggleDebug={onToggleDebug}
            showDebug={showDebug}
            onSelectAll={onSelectAll}
            onDeselectAll={onDeselectAll}
          />
          {children}
        </motion.div>
      )}
    </AnimatePresence>
  );
}
