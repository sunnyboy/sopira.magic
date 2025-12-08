//..............................................................
//   ~/sopira.magic/version_01/frontend/src/components/PdfViewer/PdfViewer.tsx
//   PdfViewer - Config-driven PDF viewer and annotation shell
//   Placeholder viewer component for PDF focus and annotations
//..............................................................

/**
 * PdfViewer - Config-driven PDF viewer and annotation shell.
 *
 * This component is intentionally minimal in v1 and acts as a
 * placeholder/wrapper for future integration with a real PDF engine
 * (e.g. pdf.js). It is designed to be driven entirely by props so
 * that the caller can provide FocusedView/Annotation data coming
 * from the backend.
 */

import React, { useEffect, useState } from 'react'

export interface PdfViewerAnnotation {
  id: string
  pageNumber: number
  x: number
  y: number
  width: number
  height: number
  annotationType: string
  data: Record<string, unknown>
  layerKey?: string
}

export interface PdfViewerProps {
  documentRef: string
  initialPage: number
  initialX: number
  initialY: number
  initialZoom: number
  annotations?: PdfViewerAnnotation[]
}

export function PdfViewer({
  documentRef,
  initialPage,
  initialX,
  initialY,
  initialZoom,
  annotations = [],
}: PdfViewerProps) {
  // Local view state for page navigation and zoom controls.
  const [page, setPage] = useState(initialPage)
  const [zoom, setZoom] = useState(initialZoom)

  // Reset local state when the focused view from backend changes.
  useEffect(() => {
    setPage(initialPage)
    setZoom(initialZoom)
  }, [documentRef, initialPage, initialZoom])

  const handlePrevPage = () => {
    setPage((current) => Math.max(1, current - 1))
  }

  const handleNextPage = () => {
    setPage((current) => current + 1)
  }

  const handleZoomOut = () => {
    setZoom((current) => Math.max(0.1, Number((current - 0.1).toFixed(2))))
  }

  const handleZoomIn = () => {
    setZoom((current) => Math.min(5, Number((current + 0.1).toFixed(2))))
  }

  const pdfUrl = `/pdfdev/${encodeURIComponent(documentRef)}`

  return (
    <div className="rounded-md border bg-background p-4 text-sm">
      <div className="mb-2 font-semibold">PDF Viewer</div>
      <div className="mb-1 text-xs text-muted-foreground">documentRef: {documentRef}</div>
      <div className="mb-2 flex items-center gap-2 text-xs text-muted-foreground">
        <button
          type="button"
          onClick={handlePrevPage}
          className="rounded border px-2 py-0.5 text-[10px] font-medium hover:bg-muted"
        >
          ◀
        </button>
        <span>page: {page}</span>
        <button
          type="button"
          onClick={handleNextPage}
          className="rounded border px-2 py-0.5 text-[10px] font-medium hover:bg-muted"
        >
          ▶
        </button>
        <span className="ml-4">zoom: {zoom.toFixed(2)}</span>
        <button
          type="button"
          onClick={handleZoomOut}
          className="ml-2 rounded border px-2 py-0.5 text-[10px] font-medium hover:bg-muted"
        >
          -
        </button>
        <button
          type="button"
          onClick={handleZoomIn}
          className="rounded border px-2 py-0.5 text-[10px] font-medium hover:bg-muted"
        >
          +
        </button>
        <span className="ml-auto text-xs text-muted-foreground">
          annotations: {annotations.length}
        </span>
      </div>
      <div className="mt-2 rounded border bg-muted/30">
        <iframe
          key={pdfUrl}
          src={pdfUrl}
          title={`PDF document ${documentRef}`}
          className="h-[70vh] w-full rounded border-0"
        />
      </div>
    </div>
  )
}
