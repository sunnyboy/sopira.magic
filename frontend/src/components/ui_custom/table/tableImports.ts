/**
 * Shared imports for all table components
 * This file centralizes common dependencies to avoid repetition across table files
 */

// React core
export { useEffect, useMemo, useState, useRef, useCallback, Fragment } from "react";
export type { ReactNode } from "react";

// TanStack Table
export {
  flexRender,
  getCoreRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  useReactTable,
  createColumnHelper,
  type ColumnDef,
  type SortingState,
  type ColumnOrderState,
  type ColumnFiltersState,
} from "@tanstack/react-table";

// Framer Motion
export { motion, AnimatePresence } from "framer-motion";

// Lucide Icons - commonly used in tables
export {
  Plus,
  Download,
  Columns as ColumnsIcon,
  SlidersHorizontal,
  Trash2,
  Save,
  FileUp,
  SquarePen,
  RotateCcw,
  ChevronUp,
  ChevronDown,
  LayoutList,
  LayoutGrid,
  LineChart,
  Copy,
  CheckCircle,
  XCircle,
} from "lucide-react";

// React Hook Form
export { useForm } from "react-hook-form";
export { zodResolver } from "@hookform/resolvers/zod";

// React Portal
export { createPortal } from "react-dom";

// Custom contexts
export { useScope } from "@/contexts/ScopeContext";
export { useAuth } from "@/contexts/AuthContext";

// Custom components (non-table)
export { Graph } from "@/components/Graph";
export { TagEditor } from "@/components/TagEditor";

// Graph cell components (for table data visualization)
export { 
  coerceGraphPayload, 
  GraphHoverCell, 
  AutoGraphCell 
} from "@/components/ui_custom/table/GraphCells";

// Utilities
export { 
  useDebounced, 
  extractSearchTerms, 
  highlightText,
  buildDateRangeParams,
  buildTimeRangeParams,
  buildNumericRangeParams,
  buildTextContainsParams,
  buildTagsParams,
} from "@/utils/tableHelpers";
export { toastMessages, toasts } from "@/utils/toastMessages";

// UI Components
export { Button } from "@/components/ui_custom/button";
export { Input } from "@/components/ui_custom/input";
export { Spinner } from "@/components/ui/spinner";
export { CardContent } from "@/components/ui_custom/card";
export { Badge } from "@/components/ui/badge";

// Table components and hooks (all from our centralized table module)
export {
  TableSearch,
  useTooltip,
  Tooltip,
  useRowSelection,
  ColumnsPanel,
  ConfirmModal,
  FormModal,
  ExportModal,
  useEscapeKey,
  useExport,
  TableToolbar,
  TableActionButtons,
  ExpandedRowRenderer,
  ExpandedRowPanel,
  FilterPanel,
  FilterRow,
  FilterInput,
  FilterSelect,
  FilterCheckbox,
  FilterCheckboxGroup,
  FilterButtonGroup,
  SaveFilterModal,
  RecallFilterModal,
  useFilterState,
  useTableFilters,
  TableCard,
  TableHeader,
  TableWrapper,
  TablePanel,
  useInlineEdit,
  type SavedFilter,
  // Shadcn table components with custom borders
  Table,
  TableBody,
  TableHead,
  TableCell,
  TableRow,
  ColumnResizeHandle,
} from "@/components/ui_custom/table/index";
export { FilterDateRange } from "@/components/ui_custom/table/FilterDateRange";
export { FilterTimeRange } from "@/components/ui_custom/table/FilterTimeRange";
export { FilterTagAutocomplete } from "@/components/ui_custom/table/FilterTagAutocomplete";
export { EditableCell } from "@/components/ui_custom/table/index";

// Error handling (modals)
export { ErrorModal } from "@/components/modals/ErrorModal";
export { useErrorHandler } from "@/components/ui_custom/table/useErrorHandler";
export type { ErrorDetails } from "@/components/modals/ErrorModal";

// Optimistic updates
export { useOptimisticField } from "@/components/ui_custom/table/useOptimisticField";
export type { OptimisticFieldConfig, OptimisticFieldResult } from "@/components/ui_custom/table/useOptimisticField";

// Field factory (declarative column builder)
export { createTableColumn, createTableColumns } from "@/components/ui_custom/table/fieldFactory";
export type { 
  FieldConfig, 
  FieldFactoryContext,
  TextFieldConfig,
  NumberFieldConfig,
  TemperatureFieldConfig,
  DateFieldConfig,
  TimeFieldConfig,
  SelectFieldConfig,
  ForeignKeyFieldConfig,
  TagFieldConfig,
} from "@/components/ui_custom/table/fieldFactory";

// Form components
export {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";

// MyTable - Unified table component
export { MyTable } from "@/components/MyTable";
export type { MyTableConfig } from "@/components/MyTable";
