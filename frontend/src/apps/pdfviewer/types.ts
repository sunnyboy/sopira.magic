//..............................................................
//   frontend/src/apps/pdfviewer/types.ts
//   Typy pre pdfviewer FE modul
//..............................................................

export interface FocusedViewDto {
  id: string
  document_ref: string
  page_number: number
  x: number
  y: number
  zoom: number
  source_model_path: string
  source_object_id: string
  metadata: Record<string, unknown>
}

export interface AnnotationDto {
  id: string
  document_ref: string
  page_number: number
  x: number
  y: number
  width: number
  height: number
  annotation_type: string
  data: Record<string, unknown>
  layer_key?: string
  owner_model_path?: string
  owner_object_id?: string
  metadata?: Record<string, unknown>
}

export interface FocusedViewQuery {
  sourceModelPath: string
  sourceObjectId: string
}

export interface AssignFocusedViewPayload {
  source_model_path: string
  source_object_id: string
  document_ref: string
  page_number: number
  x: number
  y: number
  zoom?: number
  metadata?: Record<string, unknown>
}

export interface AnnotationsQuery {
  documentRef: string
  pageNumber?: number
}

export type AnnotationTool = 'select' | 'text' | 'highlight' | 'rectangle' | 'oval' | 'line'

export interface CreateAnnotationPayload {
  document_ref: string
  page_number: number
  x: number
  y: number
  width: number
  height: number
  annotation_type: string
  data?: Record<string, unknown>
  layer_key?: string
  owner_model_path?: string
  owner_object_id?: string
  metadata?: Record<string, unknown>
}

export interface UpdateAnnotationPayload {
  id: string
  data?: Record<string, unknown>
  layer_key?: string
  metadata?: Record<string, unknown>
}
