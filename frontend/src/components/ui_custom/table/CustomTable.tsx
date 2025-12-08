//*........................................................
//*       www/thermal_eye_ui/src/components/ui_custom/table/CustomTable.tsx
//*       Custom table components extending shadcn/ui table
//*       Adds vertical borders to cells
//*........................................................

import * as React from "react"
import { cn } from "@/lib/utils"
import {
  Table as BaseTable,
  TableHeader as BaseTableHeader,
  TableBody as BaseTableBody,
  TableFooter as BaseTableFooter,
  TableRow as BaseTableRow,
  TableCaption as BaseTableCaption,
  TableHead as BaseTableHead,
  TableCell as BaseTableCell,
} from "@/components/ui/table"

// Re-export base components that don't need customization
export const Table = BaseTable
export const TableHeader = BaseTableHeader
export const TableBody = BaseTableBody
export const TableFooter = BaseTableFooter
export const TableRow = BaseTableRow
export const TableCaption = BaseTableCaption

// Custom TableHead with horizontal border and minimal horizontal padding
export const TableHead = React.forwardRef<
  HTMLTableCellElement,
  React.ThHTMLAttributes<HTMLTableCellElement>
>(({ className, ...props }, ref) => (
  <BaseTableHead
    ref={ref}
    className={cn("border-b px-0.5 py-1", className)}
    {...props}
  />
))
TableHead.displayName = "TableHead"

// Custom TableCell with horizontal border and minimal horizontal padding
// Note: max-height and overflow are applied to read-only content, not to editing fields
export const TableCell = React.forwardRef<
  HTMLTableCellElement,
  React.TdHTMLAttributes<HTMLTableCellElement>
>(({ className, ...props }, ref) => (
  <BaseTableCell
    ref={ref}
    className={cn("border-b px-0.5 py-1", className)}
    {...props}
  />
))
TableCell.displayName = "TableCell"
