//*........................................................
//*       www/thermal_eye_ui/src/components/ui_custom/table/ErrorModal.tsx
//*       Centralized error modal for all tables
//*       Extends BaseModal for consistent UX
//*........................................................

import { BaseModal } from '@/components/modals/BaseModal';
import { Button } from '@/components/ui_custom/button';
import { AlertCircle } from 'lucide-react';

export interface ErrorDetails {
  recordId?: string | number;
  operation: 'save' | 'delete' | 'create' | 'load' | 'export';
  message: string;
  technicalDetails?: string;
  title?: string;
  details?: any;
}

interface ErrorModalProps {
  open: boolean;
  onClose: () => void;
  error: ErrorDetails | null;
}

export function ErrorModal({ open, onClose, error }: ErrorModalProps) {
  if (!error) return null;

  const operationLabels = {
    save: 'Save',
    delete: 'Delete',
    create: 'Create',
    load: 'Load',
    export: 'Export',
  };

  return (
    <BaseModal open={open} onClose={onClose} size="md">
      <div className="p-6 space-y-4">
        {/* Header with icon and title */}
        <div className="flex items-center gap-3 pb-3 border-b border-border">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-destructive/10">
            <AlertCircle className="h-5 w-5 text-destructive" />
          </div>
          <h2 className="text-xl font-semibold">
            {operationLabels[error.operation]} Failed
          </h2>
        </div>

        {/* Record ID (if present) */}
        {error.recordId && (
          <div className="bg-muted/50 p-3 rounded-md">
            <span className="text-sm font-medium">Record ID:</span>
            <code className="ml-2 text-sm font-mono bg-background px-2 py-1 rounded break-all">
              {String(error.recordId)}
            </code>
          </div>
        )}
        
        {/* Error message */}
        <div>
          <p className="text-sm font-medium mb-1 text-muted-foreground">Error:</p>
          <p className="text-sm">{error.message}</p>
        </div>

        {/* Technical details (expandable) */}
        {error.technicalDetails && (
          <details className="text-xs">
            <summary className="cursor-pointer text-muted-foreground hover:text-foreground font-medium">
              Technical details
            </summary>
            <pre className="mt-2 p-3 bg-muted/50 rounded text-[10px] overflow-x-auto max-h-48 overflow-y-auto">
              {error.technicalDetails}
            </pre>
          </details>
        )}

        {/* Close button */}
        <div className="flex justify-end gap-2 pt-4 border-t border-border">
          <Button onClick={onClose} variant="default">
            Close
          </Button>
        </div>
      </div>
    </BaseModal>
  );
}
