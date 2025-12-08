//..............................................................
//   frontend/src/apps/pdfviewer/hooks/useFocusedView.ts
//   Hook pre načítanie FocusedView
//..............................................................

import { useCallback, useEffect, useState } from 'react'

import { fetchFocusedViews, assignFocusedView } from '../api'
import type { AssignFocusedViewPayload, FocusedViewDto, FocusedViewQuery } from '../types'

interface UseFocusedViewOptions {
  autoLoad?: boolean
}

interface UseFocusedViewResult {
  focusedView: FocusedViewDto | null
  isLoading: boolean
  error: string | null
  reload: () => Promise<void>
  assign: (payload: AssignFocusedViewPayload) => Promise<void>
}

export function useFocusedView(
  query: FocusedViewQuery,
  options: UseFocusedViewOptions = { autoLoad: true },
): UseFocusedViewResult {
  const [focusedView, setFocusedView] = useState<FocusedViewDto | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const { sourceModelPath, sourceObjectId } = query

  const load = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      const items = await fetchFocusedViews({
        sourceModelPath,
        sourceObjectId,
      })
      setFocusedView(items[0] ?? null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error while loading focused view')
    } finally {
      setIsLoading(false)
    }
  }, [sourceModelPath, sourceObjectId])

  const assign = useCallback(async (payload: AssignFocusedViewPayload) => {
    setError(null)
    try {
      const updated = await assignFocusedView(payload)
      setFocusedView(updated)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error while assigning focused view')
    }
  }, [])

  useEffect(() => {
    if (options.autoLoad) {
      void load()
    }
  }, [load, options.autoLoad])

  return {
    focusedView,
    isLoading,
    error,
    reload: load,
    assign,
  }
}
