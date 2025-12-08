//..............................................................
//   frontend/src/apps/pdfviewer/AnnotationToolbar.tsx
//   AnnotationToolbar - skeleton toolbar pre výber nástroja
//..............................................................

import React from 'react'

import type { AnnotationTool } from './types'

export interface AnnotationToolbarProps {
  activeTool: AnnotationTool
  onToolChange: (tool: AnnotationTool) => void
}

const TOOLS: { id: AnnotationTool; label: string }[] = [
  { id: 'select', label: 'Select' },
  { id: 'text', label: 'Text' },
  { id: 'highlight', label: 'Highlight' },
  { id: 'rectangle', label: 'Rectangle' },
  { id: 'oval', label: 'Oval' },
  { id: 'line', label: 'Line' },
]

export function AnnotationToolbar({ activeTool, onToolChange }: AnnotationToolbarProps) {
  return (
    <div className="inline-flex gap-1 rounded border bg-background p-1 text-xs">
      {TOOLS.map((tool) => (
        <button
          key={tool.id}
          type="button"
          onClick={() => onToolChange(tool.id)}
          className={
            'rounded px-2 py-0.5 ' +
            (tool.id === activeTool
              ? 'bg-primary text-primary-foreground'
              : 'bg-muted text-foreground hover:bg-muted/80')
          }
        >
          {tool.label}
        </button>
      ))}
    </div>
  )
}
