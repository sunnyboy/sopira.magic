//*........................................................
//*       www/thermal_eye_ui/src/components/ui_custom/table/TableActionButtons.tsx
//*       Action buttons for individual table rows
//*
//*       Deployed in: MeasurementsTable, FactoriesTable (Actions column)
//*       Inheritance: Uses shadcn Button component
//*       
//*       Standard buttons:
//*       - Expand/Collapse: Toggle row details (chevron up/down)
//*       - Edit: Enter edit mode for the row
//*       - Delete: Trigger delete confirmation (danger variant)
//*       
//*       Features:
//*       - Conditional rendering based on props
//*       - Support for custom buttons slot
//*       - Consistent icon sizes (12px)
//*       - Proper spacing (gap-2)
//*........................................................

import { Button } from "@/components/ui_custom/button";
import { SquarePen, Trash2, ChevronUp, ChevronDown, Share2 } from "lucide-react";

interface TableActionButtonsProps {
  onEdit?: () => void;
  onDelete?: () => void;
  onExpand?: () => void;
  onShare?: () => void;
  isExpanded?: boolean;
  showExpand?: boolean;
  showExpandButton?: boolean; // Control visibility of expand button per table
  showShare?: boolean; // Control visibility of share button (Admin/SA only)
  customButtons?: React.ReactNode;
}

export function TableActionButtons({ 
  onEdit, 
  onDelete, 
  onExpand,
  onShare,
  isExpanded,
  showExpand = false,
  showExpandButton = true, // Default: show button
  showShare = false,
  customButtons
}: TableActionButtonsProps) {
  return (
    <div className="flex gap-2" data-component="TableActionButtons">
      {showExpand && onExpand && showExpandButton && (
        <Button
          variant="solid"
          size="sm"
          onClick={onExpand}
          title={isExpanded ? 'Collapse' : 'Expand'}
        >
          {isExpanded ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
        </Button>
      )}
      {customButtons}
      {onEdit && (
        <Button
          variant="solid"
          size="sm"
          onClick={onEdit}
          title="Edit"
        >
          <SquarePen size={12} />
        </Button>
      )}
      {showShare && onShare && (
        <Button
          variant="default"
          size="sm"
          onClick={onShare}
          title="Share"
        >
          <Share2 size={12} />
        </Button>
      )}
      {onDelete && (
        <Button
          variant="danger"
          size="sm"
          onClick={onDelete}
          title="Delete"
        >
          <Trash2 size={12} />
        </Button>
      )}
    </div>
  );
}
