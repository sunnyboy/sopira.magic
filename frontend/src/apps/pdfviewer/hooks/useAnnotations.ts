//..............................................................
//   frontend/src/apps/pdfviewer/hooks/useAnnotations.ts
//   Hook pre načítanie anotácií
//..............................................................

import { useCallback, useEffect, useState } from 'react'

import { fetchAnnotations, createAnnotation as apiCreateAnnotation, updateAnnotation as apiUpdateAnnotation, deleteAnnotation as apiDeleteAnnotation } from '../api'
import type { AnnotationDto, UpdateAnnotationPayload } from '../types'
import type { PdfViewerAnnotation } from '@/components/PdfViewer'

interface UseAnnotationsArgs {
  documentRef: string
  pageNumber?: number
}

interface UseAnnotationsResult {
  annotations: PdfViewerAnnotation[]
  isLoading: boolean
  error: string | null
  reload: () => Promise<void>
  createForCurrentView: (input: {
    x: number
    y: number
    width: number
    height: number
    annotation_type: string
    data?: Record<string, unknown>
  }) => Promise<void>
  updateById: (id: string, changes: UpdateAnnotationPayload) => Promise<void>
  deleteById: (id: string) => Promise<void>
}

export function useAnnotations({ documentRef, pageNumber }: UseAnnotationsArgs): UseAnnotationsResult {
  const [annotations, setAnnotations] = useState<PdfViewerAnnotation[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      const items = await fetchAnnotations({ documentRef, pageNumber })
      const mapped: PdfViewerAnnotation[] = items.map((a: AnnotationDto) => ({
        id: String(a.id),
        pageNumber: a.page_number,
        x: a.x,
        y: a.y,
        width: a.width,
        height: a.height,
        annotationType: a.annotation_type,
        data: a.data ?? {},
        layerKey: a.layer_key ?? undefined,
      }))
      setAnnotations(mapped)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error while loading annotations')
    } finally {
      setIsLoading(false)
    }
  }, [documentRef, pageNumber])

  useEffect(() => {
    void load()
  }, [load])

  const createForCurrentView = useCallback(
    async (input: {
      x: number
      y: number
      width: number
      height: number
      annotation_type: string
      data?: Record<string, unknown>
    }) => {
      const page = pageNumber ?? 1
      await apiCreateAnnotation({
        document_ref: documentRef,
        page_number: page,
        ...input,
      })
      await load()
    },
    [documentRef, pageNumber, load],
  )

  const updateById = useCallback(
    async (id: string, changes: UpdateAnnotationPayload) => {
      await apiUpdateAnnotation(id, changes)
      await load()
    },
    [load],
  )

  const deleteById = useCallback(
    async (id: string) => {
      await apiDeleteAnnotation(id)
      await load()
    },
    [load],
  )

  return {
    annotations,
    isLoading,
    error,
    reload: load,
    createForCurrentView,
    updateById,
    deleteById,
  }
}
