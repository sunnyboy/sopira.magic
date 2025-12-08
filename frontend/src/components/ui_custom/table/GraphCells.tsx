//*........................................................
//*       www/thermal_eye_ui/src/components/ui_custom/table/GraphCells.tsx
//*       Reusable graph cell components for table data visualization
//*       
//*       Purpose: Generic graph rendering components for all tables
//*       Components:
//*         - coerceGraphPayload: Normalizes various graph data formats
//*         - GraphHoverCell: Inline icon with hover tooltip graph
//*         - AutoGraphCell: Auto-sizing graph for expanded rows
//*........................................................

import { useState, useRef, useMemo, useEffect } from 'react';
import { LineChart } from 'lucide-react';
import { Graph } from '@/components/Graph';

/**
 * Coerce graph payload to unified {header, series[]} shape
 * Handles multiple payload formats for backward compatibility
 * 
 * Supported formats:
 * 1. Unified format: { header: {...}, series: [...] }
 * 2. Legacy format: { header: {...}, data: [...] }
 * 3. Plain array: [{ t: number, v: number }, ...]
 * 
 * @param raw - Raw graph data from API (can be various formats)
 * @returns Unified graph payload or null if invalid
 * 
 * @example
 * // Unified format (preferred)
 * coerceGraphPayload({
 *   header: { title: "ROC", xLabel: "Time", yLabel: "Value", xUnit: "s", yUnit: "°C", tooltip: "..." },
 *   series: [{ name: "Series 1", data: [{ t: 0, v: 100 }, ...] }]
 * });
 * 
 * @example
 * // Legacy format (converts to unified)
 * coerceGraphPayload({
 *   header: { title: "Temperature", ... },
 *   data: [{ t: 0, v: 25 }, { t: 1, v: 26 }]
 * });
 * 
 * @example
 * // Plain array (creates default header)
 * coerceGraphPayload([{ t: 0, v: 100 }, { t: 1, v: 102 }]);
 */
export function coerceGraphPayload(raw: any): any | null {
  if (!raw) return null;
  
  // If already unified format: { header, series[] }
  if (raw.header && Array.isArray(raw.series)) {
    return raw;
  }
  
  // If legacy format: { header, data[] } -> wrap into single series
  if (raw.header && Array.isArray(raw.data)) {
    const name = (raw.header.serialLabels && raw.header.serialLabels[0]) || raw.header.title || 'Series';
    return { 
      header: raw.header, 
      series: [{ name, data: raw.data }] 
    };
  }
  
  // Legacy plain array of points -> build default header + series
  if (Array.isArray(raw)) {
    return {
      header: {
        title: "Graph",
        xLabel: "Time",
        yLabel: "Value",
        xUnit: "s",
        yUnit: "",
        tooltip: "t={t}{xUnit} • v={v}{yUnit}",
      },
      series: [{ name: "Series", data: raw }],
    };
  }
  
  return null;
}

/**
 * GraphHoverCell Component
 * 
 * Displays a small LineChart icon in table cell.
 * On hover, shows a floating tooltip with full graph visualization.
 * 
 * Perfect for compact table cells where you want to show graph data
 * without taking up too much space.
 * 
 * @param payload - Graph data (any format, will be normalized by coerceGraphPayload)
 * 
 * @example
 * // In table column definition:
 * {
 *   key: 'graph_roc',
 *   header: 'ROC',
 *   cell: (row) => <GraphHoverCell payload={row.graph_roc} />
 * }
 */
export function GraphHoverCell({ payload }: { payload: any }) {
  const [open, setOpen] = useState(false);
  const [pos, setPos] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const wrapperRef = useRef<HTMLSpanElement>(null);
  const tooltipRef = useRef<HTMLDivElement>(null);
  const coerced = useMemo(() => coerceGraphPayload(payload), [payload]);

  const handleEnter = () => {
    const el = wrapperRef.current;
    if (!el) return;
    
    const iconRect = el.getBoundingClientRect();
    const tooltipWidth = 420 + 16; // width + padding
    const tooltipHeight = 200 + 16; // height + padding
    const gap = 6; // spacing from icon
    
    // Get viewport dimensions
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;
    
    // Calculate initial position (below icon, left-aligned)
    let x = iconRect.left;
    let y = iconRect.bottom + gap;
    
    // Adjust X position if tooltip would overflow right edge
    if (x + tooltipWidth > viewportWidth) {
      x = viewportWidth - tooltipWidth - 10; // 10px margin from edge
    }
    
    // Adjust X position if tooltip would overflow left edge
    if (x < 10) {
      x = 10; // 10px margin from edge
    }
    
    // Adjust Y position if tooltip would overflow bottom edge
    if (y + tooltipHeight > viewportHeight) {
      // Try to show above icon instead
      const yAbove = iconRect.top - tooltipHeight - gap;
      if (yAbove >= 10) {
        y = yAbove;
      } else {
        // If neither below nor above fits, position at bottom with margin
        y = viewportHeight - tooltipHeight - 10;
      }
    }
    
    // Ensure tooltip doesn't go above viewport
    if (y < 10) {
      y = 10;
    }
    
    setPos({ x: Math.round(x), y: Math.round(y) });
    setOpen(true);
  };

  const handleLeave = () => setOpen(false);

  // Don't render anything if no valid data
  if (!coerced) return null;

  return (
    <span
      ref={wrapperRef}
      onMouseEnter={handleEnter}
      onMouseLeave={handleLeave}
      className="cursor-pointer inline-flex items-center text-muted-foreground hover:text-foreground transition-colors"
    >
      <LineChart size={16} />
      {open && coerced && (
        <div
          ref={tooltipRef}
          className="fixed z-[9999] bg-popover border border-border rounded-lg shadow-lg p-2"
          style={{ left: pos.x, top: pos.y }}
        >
          <Graph payload={coerced} width={420} height={200} style={{ background: 'transparent' }} />
        </div>
      )}
    </span>
  );
}

/**
 * AutoGraphCell Component
 * 
 * Renders a full-width graph that automatically resizes to fit its container.
 * Uses ResizeObserver to track container width changes.
 * 
 * Perfect for expanded table rows or detail panels where you want
 * the graph to take full available width.
 * 
 * @param payload - Graph data (any format, will be normalized by coerceGraphPayload)
 * @param height - Graph height in pixels (default: 200)
 * 
 * @example
 * // In expanded row renderer:
 * customRenderers={{
 *   graph_roc: (row) => <AutoGraphCell payload={row.graph_roc} height={250} />,
 *   graph_temp: (row) => <AutoGraphCell payload={row.graph_temp} height={250} />
 * }}
 */
export function AutoGraphCell({ payload, height = 200 }: { payload: any; height?: number }) {
  const ref = useRef<HTMLDivElement>(null);
  const [w, setW] = useState(300);
  const coerced = useMemo(() => coerceGraphPayload(payload), [payload]);

  useEffect(() => {
    if (!ref.current) return;
    const ro = new ResizeObserver((entries) => {
      for (const e of entries) {
        const cw = Math.max(100, Math.floor(e.contentRect.width));
        setW(cw);
      }
    });
    ro.observe(ref.current);
    return () => ro.disconnect();
  }, []);

  // Don't render anything if no valid data
  if (!coerced) return null;

  return (
    <div ref={ref} className="w-full">
      <Graph payload={coerced} width={w} height={height} />
    </div>
  );
}

