#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/pdfviewer/services.py
#   PdfViewer Services - FocusedView and Annotation helpers
#   Generic services for managing PDF focus and annotations
#..............................................................

"""
PdfViewer Services - Generic helpers for FocusedView and Annotation.

This module provides small, domain-agnostic services for working with
FocusedView and Annotation models in a config-driven way.

Key responsibilities:
- Create/update a focused view for a given source object
- Retrieve the focused view for a given source object (if any)
- List and manage annotations for a given document/page/layer/owner

All APIs work with generic identifiers (model path + object id) and
never depend on concrete domain models like device, lamp, motor, etc.
"""

from __future__ import annotations

from typing import Iterable, Optional

from django.db import transaction

from .models import FocusedView, Annotation, AnnotationType
from .config import DEFAULT_PDF_ZOOM


class PdfViewerService:
    """Service layer for pdfviewer models.

    This service hides common CRUD/update-or-create patterns and keeps
    higher layers free from ORM details.
    """

    # ------------------------------------------------------------------
    # FocusedView helpers
    # ------------------------------------------------------------------

    @staticmethod
    def get_focused_view(
        source_model_path: str,
        source_object_id: str,
    ) -> Optional[FocusedView]:
        """Return the focused view for a given source, if it exists."""

        return (
            FocusedView.objects.filter(
                source_model_path=source_model_path,
                source_object_id=str(source_object_id),
            )
            .order_by("-updated")
            .first()
        )

    @staticmethod
    @transaction.atomic
    def set_focused_view(
        *,
        source_model_path: str,
        source_object_id: str,
        document_ref: str,
        page_number: int,
        x: float,
        y: float,
        zoom: float | None = None,
        metadata: Optional[dict] = None,
    ) -> FocusedView:
        """Create or update a focused view for a given source.

        This method uses update_or_create so callers do not need to
        distinguish between "create" and "update" semantics.
        """

        if zoom is None:
            zoom = DEFAULT_PDF_ZOOM

        if metadata is None:
            metadata = {}

        focused_view, _ = FocusedView.objects.update_or_create(
            source_model_path=source_model_path,
            source_object_id=str(source_object_id),
            defaults={
                "document_ref": document_ref,
                "page_number": page_number,
                "x": x,
                "y": y,
                "zoom": zoom,
                "metadata": metadata,
            },
        )
        return focused_view

    # ------------------------------------------------------------------
    # Annotation helpers
    # ------------------------------------------------------------------

    @staticmethod
    def list_annotations(
        *,
        document_ref: str,
        page_number: Optional[int] = None,
        layer_key: str | None = None,
        owner_model_path: str | None = None,
        owner_object_id: str | None = None,
    ) -> Iterable[Annotation]:
        """Return annotations filtered by document, page, layer and/or owner."""

        qs = Annotation.objects.filter(document_ref=document_ref)
        if page_number is not None:
            qs = qs.filter(page_number=page_number)
        if layer_key:
            qs = qs.filter(layer_key=layer_key)
        if owner_model_path:
            qs = qs.filter(owner_model_path=owner_model_path)
        if owner_object_id:
            qs = qs.filter(owner_object_id=str(owner_object_id))
        return qs.order_by("page_number", "created")

    @staticmethod
    @transaction.atomic
    def create_annotation(
        *,
        document_ref: str,
        page_number: int,
        x: float,
        y: float,
        width: float,
        height: float,
        annotation_type: str,
        data: Optional[dict] = None,
        layer_key: str = "",
        owner_model_path: str = "",
        owner_object_id: str = "",
        metadata: Optional[dict] = None,
    ) -> Annotation:
        """Create a new annotation in a generic way."""

        if data is None:
            data = {}
        if metadata is None:
            metadata = {}

        if annotation_type not in AnnotationType.values:
            raise ValueError(f"Unsupported annotation_type: {annotation_type!r}")

        return Annotation.objects.create(
            document_ref=document_ref,
            page_number=page_number,
            x=x,
            y=y,
            width=width,
            height=height,
            annotation_type=annotation_type,
            data=data,
            layer_key=layer_key,
            owner_model_path=owner_model_path,
            owner_object_id=str(owner_object_id) if owner_object_id else "",
            metadata=metadata,
        )

    @staticmethod
    @transaction.atomic
    def update_annotation(annotation: Annotation, **fields: object) -> Annotation:
        """Update an existing annotation with the given fields."""

        for key, value in fields.items():
            setattr(annotation, key, value)
        annotation.save()
        return annotation

    @staticmethod
    @transaction.atomic
    def delete_annotation(annotation: Annotation) -> None:
        """Delete a single annotation instance."""

        annotation.delete()

    @staticmethod
    @transaction.atomic
    def delete_annotations_for_owner(
        *, owner_model_path: str, owner_object_id: str
    ) -> int:
        """Delete all annotations for a given owner.

        Returns the number of deleted records.
        """

        qs = Annotation.objects.filter(
            owner_model_path=owner_model_path,
            owner_object_id=str(owner_object_id),
        )
        deleted, _ = qs.delete()
        return deleted
