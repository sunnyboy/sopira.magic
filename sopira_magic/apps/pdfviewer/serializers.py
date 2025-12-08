#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/pdfviewer/serializers.py
#   PdfViewer Serializers - DRF serializers for pdfviewer models
#   Serializers for FocusedView and Annotation
#..............................................................

"""
PdfViewer Serializers - DRF serializers for pdfviewer models.

These serializers provide a stable, config-driven representation of
FocusedView and Annotation instances for use by the API gateway and
frontend clients.
"""

from rest_framework import serializers

from .models import FocusedView, Annotation


class FocusedViewSerializer(serializers.ModelSerializer):
    """Serializer for FocusedView.

    This serializer is suitable both for read and write operations and
    can be wired into the config-driven API layer (VIEWS_MATRIX).
    """

    class Meta:
        model = FocusedView
        fields = (
            "id",
            "document_ref",
            "page_number",
            "x",
            "y",
            "zoom",
            "source_model_path",
            "source_object_id",
            "metadata",
            "created",
            "updated",
        )
        read_only_fields = ("id", "created", "updated")


class AnnotationSerializer(serializers.ModelSerializer):
    """Serializer for Annotation model."""

    class Meta:
        model = Annotation
        fields = (
            "id",
            "document_ref",
            "page_number",
            "x",
            "y",
            "width",
            "height",
            "annotation_type",
            "data",
            "layer_key",
            "owner_model_path",
            "owner_object_id",
            "metadata",
            "created",
            "updated",
        )
        read_only_fields = ("id", "created", "updated")
