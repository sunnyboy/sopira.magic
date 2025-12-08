# PdfViewer App

PdfViewer is a cross-cutting Django application responsible for
config-driven viewing and annotation of PDF documents.

## Responsibilities
- Store focused views on PDF documents (`FocusedView`)
- Store annotations on PDF pages (`Annotation`)
- Keep all links to domain entities generic (model path + object id)
- Expose APIs that can be wired into the config-driven API gateway

## Current DEV storage model
- PDF files are stored locally in `pdfdocuments/` under this app.
- This is a provisional development-only solution and will later be
  replaced by an abstract document source (e.g. a `m_document` model
  or another document provider).

## Non-goals
- Managing low-level storage backends
- Hardcoding domain-specific logic for devices, lamps, motors, doors, etc.
