//*........................................................
//*       www/thermal_eye_ui/src/components/ui_custom/table/useExport.ts
//*       Reusable export hook for all tables
//*........................................................

import { useState } from 'react';
import * as XLSX from 'xlsx';
import type { Table } from '@tanstack/react-table';
import type { ExportScope } from './ExportModal';

export interface ExportProgress {
  isExporting: boolean;
  current: number;
  total: number;
  cancelled: boolean;
  completed: boolean;
  exportedCount: number;
}

export interface UseExportOptions<T> {
  /** Current page data */
  data: T[];
  /** TanStack table instance */
  table: Table<T>;
  /** API endpoint for fetching all records */
  apiEndpoint: string;
  /** Function to build query params (includes filters, search, sorting) */
  buildQueryParams: () => URLSearchParams;
  /** Selected row IDs */
  selectedRows: Set<string>;
  /** File name prefix for export (e.g., "factories", "measurements") */
  fileNamePrefix: string;
}

export function useExport<T extends Record<string, any>>(options: UseExportOptions<T>) {
  const {
    data,
    table,
    apiEndpoint,
    buildQueryParams,
    selectedRows,
    fileNamePrefix,
  } = options;

  const [exportProgress, setExportProgress] = useState<ExportProgress>({
    isExporting: false,
    current: 0,
    total: 0,
    cancelled: false,
    completed: false,
    exportedCount: 0,
  });

  const handleExport = async (scope: ExportScope, format: 'csv' | 'xlsx') => {
    setExportProgress({
      isExporting: true,
      current: 0,
      total: 100,
      cancelled: false,
      completed: false,
      exportedCount: 0,
    });

    try {
      let exportData: T[] = [];

      if (scope === 'selected') {
        // Export selected records
        if (selectedRows.size === 0) {
          alert('No records selected for export');
          return;
        }
        exportData = data.filter((row) => selectedRows.has(String(row.id)));
      } else if (scope === 'visible') {
        // Export currently visible records (current page)
        exportData = data;
      } else if (scope === 'all') {
        // Fetch all records from server with pagination using same filters as table
        setExportProgress({
          isExporting: true,
          current: 0,
          total: 0,
          cancelled: false,
          completed: false,
          exportedCount: 0,
        });

        let allRecords: T[] = [];
        let page = 1;
        let hasMore = true;
        const pageSize = 500; // Use larger page size for export

        while (hasMore) {
          const params = buildQueryParams();
          params.set('page', String(page));
          params.set('page_size', String(pageSize));

          const response = await fetch(`${apiEndpoint}?${params.toString()}`, {
            credentials: 'include',
          });

          if (!response.ok) {
            throw new Error(
              `Failed to fetch records (page ${page}): ${response.status}`
            );
          }

          const result = await response.json();
          const records = result.results || [];
          const totalAvailable = result.count || 0;

          if (records.length === 0) {
            hasMore = false;
          } else {
            allRecords.push(...records);

            // Update progress
            setExportProgress({
              isExporting: true,
              current: allRecords.length,
              total: totalAvailable,
              cancelled: false,
              completed: false,
              exportedCount: 0,
            });

            if (
              allRecords.length >= totalAvailable ||
              records.length < pageSize
            ) {
              hasMore = false;
            } else {
              page++;
            }
          }
        }

        exportData = allRecords;
        console.log(`Successfully fetched ${allRecords.length} records for export`);
      }

      if (!exportData.length) {
        alert('No data to export');
        return;
      }

      // Get visible columns in their current order
      const visibleColumns = table
        .getVisibleLeafColumns()
        .filter((col) => col.id !== 'select' && col.id !== 'actions');
      const columnIds = visibleColumns.map((col) => col.id);
      const headers = visibleColumns.map((col) => {
        const header = col.columnDef.header;
        return typeof header === 'string' ? header : col.id;
      });

      // Filter data to only include visible columns
      const filteredData = exportData.map((row) => {
        const filteredRow: any = {};
        columnIds.forEach((colId, index) => {
          const val = row[colId];
          // Handle arrays (e.g., tags)
          if (Array.isArray(val)) {
            filteredRow[headers[index]] = val.join(format === 'csv' ? '; ' : ', ');
          } else {
            filteredRow[headers[index]] = val ?? '';
          }
        });
        return filteredRow;
      });

      const timestamp = new Date().toISOString().slice(0, 10);
      const filename = `${fileNamePrefix}_${scope}_${timestamp}`;

      if (format === 'csv') {
        // CSV Export
        const escape = (v: any) => {
          const s = String(v ?? '');
          if (s.includes(',') || s.includes('\n') || s.includes('"'))
            return '"' + s.replace(/"/g, '""') + '"';
          return s;
        };

        const csv = [
          headers.join(','),
          ...filteredData.map((r) => headers.map((h) => escape(r[h])).join(',')),
        ].join('\n');

        const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${filename}.csv`;
        a.click();
        URL.revokeObjectURL(url);
      } else if (format === 'xlsx') {
        // XLSX Export
        const ws = XLSX.utils.json_to_sheet(filteredData);
        const wb = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(wb, ws, fileNamePrefix);
        XLSX.writeFile(wb, `${filename}.xlsx`);
      }

      // Set success state
      setExportProgress({
        isExporting: false,
        current: filteredData.length,
        total: filteredData.length,
        cancelled: false,
        completed: true,
        exportedCount: filteredData.length,
      });
    } catch (error) {
      console.error('Export error:', error);
      alert(`Export failed: ${error}`);
      setExportProgress({
        isExporting: false,
        current: 0,
        total: 0,
        cancelled: false,
        completed: false,
        exportedCount: 0,
      });
    }
  };

  const resetExportProgress = () => {
    setExportProgress({
      isExporting: false,
      current: 0,
      total: 0,
      cancelled: false,
      completed: false,
      exportedCount: 0,
    });
  };

  const cancelExport = () => {
    setExportProgress((prev) => ({ ...prev, cancelled: true }));
  };

  return {
    exportProgress,
    handleExport,
    resetExportProgress,
    cancelExport,
  };
}
