//..............................................................
//   frontend/src/apps/pdfviewer/api.ts
//   API klient pre pdfviewer modul
//.............................................................

import { getMutatingHeaders } from '@/security'
import type {
  AnnotationDto,
  AnnotationsQuery,
  AssignFocusedViewPayload,
  CreateAnnotationPayload,
  FocusedViewDto,
  FocusedViewQuery,
  UpdateAnnotationPayload,
} from './types'

async function parseJson<T>(response: Response): Promise<T> {
  const text = await response.text()
  if (!text) return {} as T
  return JSON.parse(text) as T
}

function extractResults<T>(payload: { results?: T[] } | T[]): T[] {
  return Array.isArray(payload) ? payload : payload.results ?? []
}

export async function fetchFocusedViews(query: FocusedViewQuery): Promise<FocusedViewDto[]> {
  const params = new URLSearchParams({
    source_model_path: query.sourceModelPath,
    source_object_id: query.sourceObjectId,
  })

  const response = await fetch(`/api/focusedviews/?${params.toString()}`, {
    credentials: 'include',
  })

  if (!response.ok) {
    throw new Error(`Failed to load focused views (HTTP ${response.status})`)
  }

  const json = await parseJson<{ results?: FocusedViewDto[] } | FocusedViewDto[]>(response)
  return extractResults(json)
}

export async function assignFocusedView(payload: AssignFocusedViewPayload): Promise<FocusedViewDto> {
  const response = await fetch('/api/focusedviews/assign/', {
    method: 'POST',
    headers: getMutatingHeaders(),
    credentials: 'include',
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    throw new Error(`Failed to assign focused view (HTTP ${response.status})`)
  }

  return parseJson<FocusedViewDto>(response)
}

export async function fetchAnnotations(query: AnnotationsQuery): Promise<AnnotationDto[]> {
  const params = new URLSearchParams({
    document_ref: query.documentRef,
  })
  if (query.pageNumber != null) {
    params.set('page_number', String(query.pageNumber))
  }

  const response = await fetch(`/api/annotations/?${params.toString()}`, {
    credentials: 'include',
  })

  if (!response.ok) {
    throw new Error(`Failed to load annotations (HTTP ${response.status})`)
  }

  const json = await parseJson<{ results?: AnnotationDto[] } | AnnotationDto[]>(response)
  return extractResults(json)
}

export async function createAnnotation(payload: CreateAnnotationPayload): Promise<AnnotationDto> {
  const response = await fetch('/api/annotations/', {
    method: 'POST',
    headers: getMutatingHeaders(),
    credentials: 'include',
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    throw new Error(`Failed to create annotation (HTTP ${response.status})`)
  }

  return parseJson<AnnotationDto>(response)
}

export async function updateAnnotation(id: string, payload: UpdateAnnotationPayload): Promise<AnnotationDto> {
  const response = await fetch(`/api/annotations/${encodeURIComponent(id)}/`, {
    method: 'PATCH',
    headers: getMutatingHeaders(),
    credentials: 'include',
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    throw new Error(`Failed to update annotation (HTTP ${response.status})`)
  }

  return parseJson<AnnotationDto>(response)
}

export async function deleteAnnotation(id: string): Promise<void> {
  const response = await fetch(`/api/annotations/${encodeURIComponent(id)}/`, {
    method: 'DELETE',
    headers: getMutatingHeaders(),
    credentials: 'include',
  })

  if (!response.ok) {
    throw new Error(`Failed to delete annotation (HTTP ${response.status})`)
  }
}
