//..............................................................
//   ~/sopira.magic/version_01/frontend/src/apps/pdfviewer/PdfViewerPage.tsx
//   PdfViewerPage - Page wrapper for PdfViewer
//   Demonstrates config-driven focused view wiring
//..............................................................

/**
 * PdfViewerPage - simple page that renders the PdfViewer component.
 *
 * In v1 this page uses a static placeholder FocusedView configuration
 * so that the routing and component contract can be verified end-to-end
 * before real backend integration and PDF rendering are implemented.
 */

import React, { useEffect, useState } from 'react'

import { PdfViewer } from '@/components/PdfViewer'

import { useFocusedView } from './hooks/useFocusedView'
import { useAnnotations } from './hooks/useAnnotations'
import { AnnotationToolbar } from './AnnotationToolbar'
import type { AnnotationTool, AssignFocusedViewPayload } from './types'

// Temporary hardcoded source context and document for demo purposes.
const DEMO_SOURCE_MODEL_PATH = 'device.Device'
const DEMO_SOURCE_ID = '1'
const DEMO_DOCUMENT_REF =
  '79564 DW-E30-001_1 Location Plan - Dewatering - Side View.pdf'

export function PdfViewerPage() {
  const [activeTool, setActiveTool] = useState<AnnotationTool>('select')

  const {
    focusedView,
    isLoading,
    error,
    assign,
  } = useFocusedView({
    sourceModelPath: DEMO_SOURCE_MODEL_PATH,
    sourceObjectId: DEMO_SOURCE_ID,
  })

  const effectiveView =
    focusedView ?? ({
      document_ref: DEMO_DOCUMENT_REF,
      page_number: 1,
      x: 0.25,
      y: 0.25,
      zoom: 1.0,
      id: '',
      source_model_path: DEMO_SOURCE_MODEL_PATH,
      source_object_id: DEMO_SOURCE_ID,
      metadata: {},
    } as const)

  const {
    annotations,
    createForCurrentView,
    deleteById,
  } = useAnnotations({
    documentRef: effectiveView.document_ref,
    pageNumber: effectiveView.page_number,
  })

  // Rezervované miesto pre budúce cross-cutting efekty (napr. logging)
  useEffect(() => {
    // zatiaľ nič
  }, [])

  const handleAssignView = async () => {
    const payload: AssignFocusedViewPayload = {
      source_model_path: DEMO_SOURCE_MODEL_PATH,
      source_object_id: DEMO_SOURCE_ID,
      document_ref: effectiveView.document_ref,
      page_number: effectiveView.page_number,
      x: effectiveView.x,
      y: effectiveView.y,
      zoom: effectiveView.zoom,
      metadata: effectiveView.metadata,
    }

    await assign(payload)
  }

  const handleAddDummyAnnotation = async () => {
    await createForCurrentView({
      x: 0.4,
      y: 0.4,
      width: 0.2,
      height: 0.1,
      annotation_type: 'rectangle',
      data: { label: 'Demo annotation' },
    })
  }

  const handleDeleteFirstAnnotation = async () => {
    const first = annotations[0]
    if (!first) return
    await deleteById(first.id)
  }

  return (
    <div className="p-4 space-y-4">
      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="text-sm font-semibold">PDF Viewer demo</div>
          <AnnotationToolbar activeTool={activeTool} onToolChange={setActiveTool} />
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={handleAddDummyAnnotation}
            className="rounded border px-3 py-1 text-xs font-medium hover:bg-muted"
          >
            Add demo annotation
          </button>
          <button
            type="button"
            onClick={handleDeleteFirstAnnotation}
            className="rounded border px-3 py-1 text-xs font-medium hover:bg-muted"
          >
            Delete first annotation
          </button>
          <button
            type="button"
            onClick={handleAssignView}
            className="rounded bg-primary px-3 py-1 text-xs font-medium text-primary-foreground hover:bg-primary/90"
          >
            Assign view to demo source
          </button>
        </div>
      </div>

      {error && <div className="text-xs text-destructive">{error}</div>}
      {isLoading && <div className="text-xs text-muted-foreground">Loading focused view...</div>}

      <PdfViewer
        documentRef={effectiveView.document_ref}
        initialPage={effectiveView.page_number}
        initialX={effectiveView.x}
        initialY={effectiveView.y}
        initialZoom={effectiveView.zoom}
        annotations={annotations}
      />
    </div>
  )
}
