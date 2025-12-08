#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/pdfviewer/apps.py
#   PdfViewer App Config - Django app configuration
#   PDF viewer and annotation application configuration
#..............................................................

"""
   PdfViewer App Config - Django App Configuration.

   Django AppConfig for pdfviewer application.
   Provides PDF viewing and annotation services in a
   config-driven, domain-agnostic way.

   Configuration:
   - App name: sopira_magic.apps.pdfviewer
   - App label: pdfviewer
   - Verbose name: PDF Viewer
   - Default auto field: BigAutoField

   Important:
   - NO HARDCODING: All solutions must be universal and config-driven
   - No model-specific or app-specific hardcoded logic
"""

from django.apps import AppConfig


class PdfViewerConfig(AppConfig):
    """Django AppConfig for the pdfviewer application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "sopira_magic.apps.pdfviewer"
    label = "pdfviewer"
    verbose_name = "PDF Viewer"
