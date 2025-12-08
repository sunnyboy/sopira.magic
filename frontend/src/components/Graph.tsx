//*........................................................
//*       www/thermal_eye_ui/src/components/Graph.tsx
//*       Graph visualization component for thermal data
//*........................................................

//*........................................................
//*       www/thermal_eye_ui/src/components/Graph.tsx
//*       Reusable SVG graph renderer for ROC/TEMP payloads
//*........................................................

import React, { useMemo, useRef, useState } from 'react';

export type GraphHeader = {
  title: string;
  xLabel: string;
  yLabel: string;
  xUnit: string;
  yUnit: string;
  tooltip: string; // template: e.g. "t={t}s • ROC={v}°C"
  serialLabels?: string[]; // legend labels for series (order-matched)
};

export type GraphPoint = { t: number; v: number };
export type GraphSeries = { name: string; color?: string; data: GraphPoint[] };
export type GraphPayload = { header: GraphHeader; series: GraphSeries[] };

export type GraphProps = {
  payload: GraphPayload;
  width?: number;
  height?: number;
  color?: string;          // stroke color
  strokeWidth?: number;
  spark?: boolean;         // sparkline mode (no axes/title)
  showDots?: boolean;      // draw dots on points
  className?: string;
  style?: React.CSSProperties;
};

const defaultColor = 'var(--te-primary, #2563eb)';
const palette = ['#2563eb', '#10b981', '#ef4444', '#f59e0b', '#8b5cf6'];

function formatTooltip(tpl: string, t: number, v: number, xUnit: string, yUnit: string) {
  // Replace placeholders; if units are already in tpl, leave as is
  return tpl
    .replace('{t}', String(t))
    .replace('{v}', String(v))
    .replace('{xUnit}', xUnit)
    .replace('{yUnit}', yUnit);
}

export const Graph: React.FC<GraphProps> = ({
  payload,
  width = 300,
  height = 180,
  color = defaultColor,
  strokeWidth = 2,
  spark = false,
  showDots = false,
  className,
  style,
}) => {
  const { header } = (payload || {}) as GraphPayload;
  // Normalize to array of series (accept legacy payloads with data[])
  const series: GraphSeries[] = useMemo(() => {
    if (!payload) return [];
    let s: GraphSeries[] = [];
    const anyPayload: any = payload as any;
    if (Array.isArray(anyPayload.series) && anyPayload.series.length) {
      s = anyPayload.series as GraphSeries[];
    } else if (Array.isArray(anyPayload.data)) {
      s = [{ name: header?.serialLabels?.[0] || header?.title || 'Series', color: undefined, data: anyPayload.data }];
    }
    // Apply serialLabels and colors if missing
    s = s.map((ss, idx) => ({
      name: header?.serialLabels?.[idx] || ss.name || `Series ${idx + 1}`,
      color: ss.color || palette[idx % palette.length],
      data: ss.data || [],
    }));
    return s;
  }, [payload, header]);
  const containerRef = useRef<HTMLDivElement>(null);
  const [hoverIdx, setHoverIdx] = useState<number | null>(null);

const pad = spark ? { top: 6, right: 6, bottom: 6, left: 6 } : { top: 22, right: 12, bottom: 44, left: 40 };
  const innerW = Math.max(1, width - pad.left - pad.right);
  const innerH = Math.max(1, height - pad.top - pad.bottom);

  const { paths, xScale, yScale, minT, maxT, minV, maxV } = useMemo(() => {
    if (!series.length || !series[0].data?.length) {
      return {
        paths: [] as { d: string; color?: string; name: string }[],
        xScale: (t: number) => 0,
        yScale: (v: number) => 0,
        minT: 0,
        maxT: 1,
        minV: 0,
        maxV: 1,
      };
    }
    const allT = series.flatMap(s => s.data.map(p => p.t));
    const allV = series.flatMap(s => s.data.map(p => p.v));
    const minT = Math.min(...allT);
    const maxT = Math.max(...allT);
    const minV = Math.min(...allV);
    const maxV = Math.max(...allV);
    const xt = (t: number) => {
      if (maxT === minT) return 0;
      return ((t - minT) / (maxT - minT)) * innerW;
    };
    const yv = (v: number) => {
      if (maxV === minV) return innerH / 2;
      return innerH - ((v - minV) / (maxV - minV)) * innerH;
    };
    const paths = series.map((s) => ({
      d: (s.data || []).map((p, i) => `${i === 0 ? 'M' : 'L'} ${xt(p.t)} ${yv(p.v)}`).join(' '),
      color: s.color,
      name: s.name,
    }));
    return { paths, xScale: xt, yScale: yv, minT, maxT, minV, maxV };
  }, [series, innerW, innerH]);

  const onMouseMove: React.MouseEventHandler<SVGRectElement> = (e) => {
    if (!series.length || !series[0].data?.length) return;
    const svg = e.currentTarget.ownerSVGElement;
    if (!svg) return;
    const pt = svg.createSVGPoint();
    pt.x = e.clientX; pt.y = e.clientY;
    const cursor = pt.matrixTransform(svg.getScreenCTM()?.inverse());
    // Find nearest point by x
    let nearest = 0;
    let best = Infinity;
    const base = series[0].data;
    for (let i = 0; i < base.length; i++) {
      const xi = xScale(base[i].t);
      const dx = Math.abs(xi - cursor.x + pad.left);
      if (dx < best) { best = dx; nearest = i; }
    }
    setHoverIdx(nearest);
  };

  const onLeave = () => setHoverIdx(null);

  // Render
return (
    <div ref={containerRef} className={className} style={{ position: 'relative', width, height, background: 'var(--te-bg,#f5f7fb)', borderRadius: 8, ...style }}>
      <svg width={width} height={height} role="img" aria-label={header?.title || 'Graph'}>
        {!spark && (
          <g transform={`translate(${pad.left}, ${pad.top})`}>
            {/* Title centered */}
            <text x={innerW / 2} y={-8} textAnchor="middle" fill="var(--te-text,#0f172a)" fontSize={12} fontWeight={600}>
              {header?.title || ''}
            </text>
          </g>
        )}
        {/* Plot area */}
        <g transform={`translate(${pad.left}, ${pad.top})`}>
          {/* Axes (minimal ticks + axis/grid lines) */}
          {!spark && (
            <>
              {/* Axis base lines */}
              <line x1={0} y1={innerH} x2={innerW} y2={innerH} stroke="var(--te-border,#e5e7eb)" />
              <line x1={0} y1={0} x2={0} y2={innerH} stroke="var(--te-border,#e5e7eb)" />
              {/* X axis ticks */}
              {Array.from({ length: 5 }).map((_, i) => {
                const tVal = minT + (i / 4) * (maxT - minT);
                const x = xScale(tVal);
                return (
                  <g key={`xt-${i}`}>
                    {/* grid line */}
                    <line x1={x} y1={0} x2={x} y2={innerH} stroke="rgba(2,6,23,0.06)" />
                    {/* tick */}
                    <line x1={x} y1={innerH} x2={x} y2={innerH + 4} stroke="var(--te-border,#e5e7eb)" />
                    <text x={x} y={innerH + 16} textAnchor="middle" fill="var(--te-muted,#6b7280)" fontSize={9}>{tVal.toFixed(1)}</text>
                  </g>
                );
              })}
              {/* Y axis ticks */}
              {Array.from({ length: 5 }).map((_, i) => {
                const vVal = minV + (i / 4) * (maxV - minV);
                const y = yScale(vVal);
                return (
                  <g key={`yt-${i}`}>
                    {/* grid line */}
                    <line x1={0} y1={y} x2={innerW} y2={y} stroke="rgba(2,6,23,0.06)" />
                    {/* tick */}
                    <line x1={-4} y1={y} x2={0} y2={y} stroke="var(--te-border,#e5e7eb)" />
                    <text x={-6} y={y + 3} textAnchor="end" fill="var(--te-muted,#6b7280)" fontSize={9}>{vVal.toFixed(1)}</text>
                  </g>
                );
              })}
              {/* X axis label */}
              <text x={innerW / 2} y={innerH + 28} textAnchor="middle" fill="var(--te-muted,#6b7280)" fontSize={10}>
                {header?.xLabel}{header?.xUnit ? ` (${header.xUnit})` : ''}
              </text>
              {/* Y axis label (rotated) */}
              <text transform={`translate(${-32}, ${innerH / 2}) rotate(-90)`} textAnchor="middle" fill="var(--te-muted,#6b7280)" fontSize={10}>
                {header?.yLabel}{header?.yUnit ? ` (${header.yUnit})` : ''}
              </text>
              {/* Legend (top right) */}
              <g transform={`translate(${innerW - 90}, 0)`}>
                {series.map((s, idx) => (
                  <g key={`leg-${idx}`} transform={`translate(0, ${idx * 14})`}>
                    <rect x={0} y={-8} width={12} height={2} fill={s.color || defaultColor} />
                    <text x={16} y={-7} fill="var(--te-text,#0f172a)" fontSize={10}>{s.name}</text>
                  </g>
                ))}
              </g>
            </>
          )}

          {/* Data paths */}
          {paths.length ? (
            paths.map((p, idx) => (
              <path key={idx} d={p.d} fill="none" stroke={p.color || color} strokeWidth={strokeWidth} vectorEffect="non-scaling-stroke" />
            ))
          ) : (
            <text x={innerW / 2} y={innerH / 2} textAnchor="middle" fill="var(--te-muted,#6b7280)" fontSize={12}>
              No data
            </text>
          )}

          {/* Dots */}
          {showDots && series.length && series[0].data && series[0].data.map((p, i) => (
            <circle key={i} cx={xScale(p.t)} cy={yScale(p.v)} r={2.2} fill={color} />
          ))}

          {/* Hover capture */}
          <rect x={0} y={0} width={innerW} height={innerH} fill="transparent" onMouseMove={onMouseMove} onMouseLeave={onLeave} />

          {/* Hover marker */}
          {hoverIdx !== null && series.length && series[0].data && series[0].data[hoverIdx] && (
            <>
              <line x1={xScale(series[0].data[hoverIdx].t)} x2={xScale(series[0].data[hoverIdx].t)} y1={0} y2={innerH} stroke="rgba(0,0,0,0.1)" />
              <circle cx={xScale(series[0].data[hoverIdx].t)} cy={yScale(series[0].data[hoverIdx].v)} r={3.5} fill="#fff" stroke={color} strokeWidth={2} />
            </>
          )}
        </g>
      </svg>

      {/* Floating tooltip */}
      {hoverIdx !== null && series.length && series[0].data && series[0].data[hoverIdx] && (
        <div
          style={{
            position: 'absolute',
            left: pad.left + xScale(series[0].data[hoverIdx].t) + 8,
            top: pad.top + yScale(series[0].data[hoverIdx].v) - 28,
            background: 'var(--te-surface,#fff)',
            color: 'var(--te-text,#0f172a)',
            border: '1px solid var(--te-border,#e5e7eb)',
            borderRadius: 8,
            padding: '4px 8px',
            fontSize: 11,
            boxShadow: '0 6px 16px rgba(2,6,23,0.08)',
            pointerEvents: 'none',
            whiteSpace: 'nowrap',
          }}
        >
          {/* Multi-series tooltip: show all series at index */}
          <div>
            <div style={{ fontWeight: 600, marginBottom: 4 }}>{header?.title || 'Graph'}</div>
            {series.map((s, idx) => (
              <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <span style={{ width: 10, height: 2, background: s.color || color, display: 'inline-block' }} />
                <span>{s.name}: {formatTooltip(header?.tooltip || 't={t}{xUnit} • v={v}{yUnit}', series[0].data[hoverIdx].t, s.data?.[hoverIdx]?.v ?? NaN, header?.xUnit || '', header?.yUnit || '')}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default Graph;
