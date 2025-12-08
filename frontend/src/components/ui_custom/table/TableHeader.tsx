//*........................................................
//*       www/thermal_eye_ui/src/components/ui_custom/table/TableHeader.tsx
//*       Table header with title, stats, and pagination
//*........................................................

import { CardHeader } from "@/components/ui_custom/card";
import { Button } from "@/components/ui_custom/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui_custom/select";
import { ReactNode } from "react";

interface TableHeaderProps {
  title: string;
  selectedCount: number;
  visibleCount: number;
  totalCount: number;
  pageIndex: number;
  pageSize: number;
  pageSizeOptions?: number[]; // Available page sizes for dropdown (default: [10, 25, 50, 100, 250, 500])
  onPageChange: (page: number) => void;
  onPageSizeChange: (size: number) => void;
  canPreviousPage: boolean;
  canNextPage: boolean;
  onSelectedCountClick?: () => void; // NEW: Callback when clicking on selected count
  children?: ReactNode; // For search + toolbar (right side of second row)
  className?: string; // For custom styling
}

export function TableHeader({
  title,
  selectedCount,
  visibleCount,
  totalCount,
  pageIndex,
  pageSize,
  pageSizeOptions = [10, 25, 50, 100, 250, 500], // Default page size options
  onPageChange,
  onPageSizeChange,
  canPreviousPage,
  canNextPage,
  onSelectedCountClick,
  children,
  className = "p-4 border-b",
}: TableHeaderProps) {
  const totalPages = Math.max(1, Math.ceil(totalCount / pageSize));

  return (
    <CardHeader className={className}>
      {/* First row: Title left, Pagination center, Stats right */}
      <div className="flex items-center justify-between gap-4 mb-4">
        {/* Left: Title */}
        <h1 className="text-3xl font-extrabold tracking-wide opacity-90">{title}</h1>
        
        {/* Center: Pagination */}
        <div className="flex items-center gap-3 text-sm text-muted-foreground">
          <div>
            Page <b>{pageIndex + 1}</b> / {totalPages} ·
            Total <b>{totalCount}</b>
          </div>
          <div className="flex items-center gap-2">
            <Button
              size="sm"
              variant="ghost"
              onClick={() => onPageChange(pageIndex - 1)}
              disabled={!canPreviousPage}
              aria-label="Previous page"
              className="h-8 w-8 p-0"
            >
              &lt;
            </Button>
            <Button
              size="sm"
              variant="ghost"
              onClick={() => onPageChange(pageIndex + 1)}
              disabled={!canNextPage}
              aria-label="Next page"
              className="h-8 w-8 p-0"
            >
              &gt;
            </Button>
            <Select value={String(pageSize)} onValueChange={(val) => onPageSizeChange(Number(val))}>
              <SelectTrigger className="h-8 w-[100px] text-xs">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {pageSizeOptions.map((s) => (
                  <SelectItem key={s} value={String(s)}>
                    {s} / page
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>
        
        {/* Right: Stats */}
        <div className="text-sm text-muted-foreground">
          <span 
            className={`${selectedCount > 0 ? 'text-primary font-semibold cursor-pointer hover:underline' : ''}`}
            onClick={selectedCount > 0 && onSelectedCountClick ? () => onSelectedCountClick() : undefined}
            title={selectedCount > 0 ? 'Click to show only selected records' : undefined}
            role={selectedCount > 0 && onSelectedCountClick ? 'button' : undefined}
            tabIndex={selectedCount > 0 && onSelectedCountClick ? 0 : undefined}
          >
            {selectedCount}
          </span>
          {' of '}
          <span>{visibleCount}</span>
          {' of '}
          <span>{totalCount}</span>
          {' Records'}
        </div>
      </div>
      
      {/* Second row: Search + Toolbar right */}
      <div className="flex items-center justify-end gap-4 flex-wrap">
        {/* Right side: Search + Toolbar passed as children */}
        {children}
      </div>
    </CardHeader>
  );
}
