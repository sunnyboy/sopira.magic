#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/pdfviewer/views.py
#   PdfViewer Views - DRF viewsets and endpoints
#   Endpoints for FocusedView and Annotation (if needed directly)
#..............................................................

"""
PdfViewer Views - DRF viewsets and endpoints.

In the first iteration most endpoints for pdfviewer will be wired
through the config-driven API gateway (VIEWS_MATRIX + view_factory).

This module exists as a placeholder for:
- potential specialized endpoints (e.g. assign-focused-view helpers),
- or direct registration of viewsets if needed in the future.

For now, core CRUD for FocusedView and Annotation is expected to be
provided via dynamically created viewsets in the api app.
"""

from rest_framework import viewsets, permissions

from .models import FocusedView, Annotation
from .serializers import FocusedViewSerializer, AnnotationSerializer


class FocusedViewViewSet(viewsets.ModelViewSet):
    """Optional direct ModelViewSet for FocusedView.

    This viewset is not registered by default in api/urls.py, but it
    can be used if a non-config-driven endpoint is ever required.
    """

    queryset = FocusedView.objects.all()
    serializer_class = FocusedViewSerializer
    permission_classes = [permissions.IsAuthenticated]


class AnnotationViewSet(viewsets.ModelViewSet):
    """Optional direct ModelViewSet for Annotation."""

    queryset = Annotation.objects.all()
    serializer_class = AnnotationSerializer
    permission_classes = [permissions.IsAuthenticated]
