#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/pdfviewer/models.py
#   PdfViewer Models - FocusedView and Annotation
#   Config-driven models for PDF focus and annotations
#..............................................................

"""
   PdfViewer Models - FocusedView and Annotation.

   This module defines generic, config-driven models for working with
   PDF documents:

   1. FocusedView
      - Stores a focused view on a PDF document (file, page, x, y, zoom)
      - Linked generically to any source object via model path + object id
      - Used to reproduce an exact view for entities like devices, lamps,
        motors, doors, etc., without hardcoding those models here.

   2. Annotation
      - Stores annotations (text, highlight, rectangle, oval, line) on
        a PDF document page
      - Each annotation belongs to a logical annotation layer which can
        be owned by an abstract "owner" (model path + object id)
      - Layers and annotations can be shared between multiple owners

   All references to domain entities are stored as generic model path
   strings ("app_label.ModelName") and object identifiers, so the
   pdfviewer app remains fully domain-agnostic and config-driven.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _

from sopira_magic.apps.shared.models import SharedBaseModel


class AnnotationType(models.TextChoices):
    """Supported annotation types for PDF documents."""

    TEXT = "text", _("Text")
    HIGHLIGHT = "highlight", _("Highlight")
    RECTANGLE = "rectangle", _("Rectangle")
    OVAL = "oval", _("Oval")
    LINE = "line", _("Line")


class FocusedView(SharedBaseModel):
    """Focused view on a PDF document for a generic source object.

    Coordinates are stored in a normalized form (0.0 - 1.0) relative to
    the rendered page size, so the view remains resolution independent.
    """

    document_ref = models.CharField(
        max_length=1024,
        help_text=_("Relative path or identifier of the PDF document."),
    )
    page_number = models.PositiveIntegerField(
        default=1,
        help_text=_("1-based page number within the PDF document."),
    )
    x = models.FloatField(
        default=0.0,
        help_text=_("Normalized X coordinate within the page (0.0 - 1.0)."),
    )
    y = models.FloatField(
        default=0.0,
        help_text=_("Normalized Y coordinate within the page (0.0 - 1.0)."),
    )
    zoom = models.FloatField(
        default=1.0,
        help_text=_("Initial zoom level for the viewer (e.g. 1.0 = 100%)."),
    )

    source_model_path = models.CharField(
        max_length=255,
        db_index=True,
        help_text=_("Source model path in the form 'app_label.ModelName'."),
    )
    source_object_id = models.CharField(
        max_length=64,
        db_index=True,
        help_text=_("Identifier of the source object (string form)."),
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Optional extra configuration for the viewer."),
    )

    class Meta(SharedBaseModel.Meta):
        verbose_name = _("Focused view")
        verbose_name_plural = _("Focused views")
        indexes = [
            models.Index(fields=["source_model_path", "source_object_id"]),
            models.Index(fields=["document_ref", "page_number"]),
        ]

    def __str__(self) -> str:  # pragma: no cover - human-readable representation
        return f"{self.document_ref} p{self.page_number} -> {self.source_model_path}#{self.source_object_id}"


class Annotation(SharedBaseModel):
    """Annotation on a PDF document page.

    An annotation belongs to a logical annotation layer which can be
    associated with one or more abstract owners (model path + object id).
    """

    document_ref = models.CharField(
        max_length=1024,
        help_text=_("Relative path or identifier of the PDF document."),
    )
    page_number = models.PositiveIntegerField(
        default=1,
        help_text=_("1-based page number within the PDF document."),
    )

    x = models.FloatField(
        default=0.0,
        help_text=_("Normalized X coordinate within the page (0.0 - 1.0)."),
    )
    y = models.FloatField(
        default=0.0,
        help_text=_("Normalized Y coordinate within the page (0.0 - 1.0)."),
    )
    width = models.FloatField(
        default=0.0,
        help_text=_("Normalized width within the page (0.0 - 1.0)."),
    )
    height = models.FloatField(
        default=0.0,
        help_text=_("Normalized height within the page (0.0 - 1.0)."),
    )

    annotation_type = models.CharField(
        max_length=32,
        choices=AnnotationType.choices,
        default=AnnotationType.TEXT,
        help_text=_("Type of annotation (text, highlight, rectangle, oval, line)."),
    )

    data = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Annotation payload (text, style, color, etc.)."),
    )

    layer_key = models.CharField(
        max_length=128,
        blank=True,
        default="",
        help_text=_("Logical annotation layer identifier (per owner or shared)."),
    )

    owner_model_path = models.CharField(
        max_length=255,
        blank=True,
        default="",
        db_index=True,
        help_text=_("Optional owner model path 'app_label.ModelName'."),
    )
    owner_object_id = models.CharField(
        max_length=64,
        blank=True,
        default="",
        db_index=True,
        help_text=_("Optional owner object identifier (string form)."),
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Optional extra metadata for the annotation."),
    )

    class Meta(SharedBaseModel.Meta):
        verbose_name = _("Annotation")
        verbose_name_plural = _("Annotations")
        indexes = [
            models.Index(fields=["document_ref", "page_number", "layer_key"]),
            models.Index(fields=["owner_model_path", "owner_object_id"]),
        ]

    def __str__(self) -> str:  # pragma: no cover - human-readable representation
        return f"Annotation({self.annotation_type}) on {self.document_ref} p{self.page_number}"
