//..............................................................
//   ~/sopira.magic/version_01/frontend/src/apps/pdfviewer/usePdfCache.ts
//   usePdfCache - Hook for client-side PDF caching
//   Skeleton for caching large PDF files on the frontend
//..............................................................

/**
 * usePdfCache - client-side caching hook for PDF documents.
 *
 * This is a lightweight skeleton that defines the API surface for
 * caching large PDF files (10–20 MB) so they don't need to be
 * downloaded repeatedly. Once a real PDF engine (e.g. pdf.js) is
 * integrated, this hook can be extended to store loaded documents
 * in memory or IndexedDB.
 */

import { useMemo } from 'react'

const pdfCache = new Map<string, { lastAccess: number }>()

export function usePdfCache(documentRef: string) {
  // For now we only track that a given documentRef has been "touched".
  // Later this will hold the actual loaded PDF document instance.
  return useMemo(() => {
    const now = Date.now()
    const existing = pdfCache.get(documentRef)
    if (!existing) {
      pdfCache.set(documentRef, { lastAccess: now })
    } else {
      existing.lastAccess = now
    }

    return {
      documentRef,
      // placeholder flag; later can be used to indicate load status
      isCached: !!existing,
    }
  }, [documentRef])
}