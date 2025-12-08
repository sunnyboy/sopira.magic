#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/pdfviewer/config.py
#   PdfViewer Config - SSOT for PDF viewer behavior
#   Configuration for PDF storage, zoom and annotation types
#..............................................................

"""
PdfViewer Config - Single Source of Truth for pdfviewer settings.

This module centralizes configuration for the pdfviewer app so that
no magic constants are scattered in models, services or views.

Current (DEV) behavior:
- PDF files are stored locally under the pdfviewer app in the
  `pdfdocuments/` directory. This is a provisional development-only
  solution and will later be replaced by an abstract document source
  (e.g. integration with m_document or another storage backend).

Planned future behavior:
- Replace direct filesystem storage with a config-driven document
  provider (e.g. model-based document registry).
- Keep the same FocusedView + Annotation data structures so that
  migration to m_document does not require changing consumers.
"""

from pathlib import Path
from django.conf import settings

# Root directory for PDF documents in DEV mode
PDF_DEV_ROOT: Path = (
    Path(settings.BASE_DIR)
    / "sopira_magic"
    / "apps"
    / "pdfviewer"
    / "pdfdocuments"
)

# Default zoom level for newly created focused views
DEFAULT_PDF_ZOOM: float = 1.0

# Allowed annotation types (must match AnnotationType choices)
ALLOWED_ANNOTATION_TYPES = [
    "text",
    "highlight",
    "rectangle",
    "oval",
    "line",
]
