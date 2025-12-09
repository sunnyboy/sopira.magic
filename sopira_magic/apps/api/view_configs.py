#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/api/view_configs.py
#   ViewsMatrix - Config model for API viewsets
#   Single source of truth for config-driven API endpoints
#..............................................................

"""
ViewsMatrix Configuration for API Gateway.

Single source of truth for config-driven API viewsets. The goal is to
avoid hardcoding per-viewset logic and instead describe each endpoint
via a declarative configuration structure.

This is intentionally small in v1 and focused on the "users" endpoint,
so we can evolve a clean pattern for the new architecture without
bringing legacy complexity.
"""

from typing import TypedDict, Optional, List, Dict, Any, Type, Callable

from django.conf import settings
from django.db.models import Model
from rest_framework.permissions import AllowAny
from rest_framework.serializers import Serializer

from sopira_magic.apps.m_user.models import User
from sopira_magic.apps.m_company.models import Company
from sopira_magic.apps.m_factory.models import Factory
from sopira_magic.apps.m_location.models import Location
from sopira_magic.apps.m_carrier.models import Carrier
from sopira_magic.apps.m_driver.models import Driver
from sopira_magic.apps.m_pot.models import Pot
from sopira_magic.apps.m_pit.models import Pit
from sopira_magic.apps.m_machine.models import Machine
from sopira_magic.apps.m_camera.models import Camera
from sopira_magic.apps.m_measurement.models import Measurement
from sopira_magic.apps.pdfviewer.models import FocusedView, Annotation
from sopira_magic.apps.pdfviewer.serializers import (
    FocusedViewSerializer,
    AnnotationSerializer,
)
from .serializers import UserListSerializer


IS_LOCAL_ENV = getattr(settings, "ENV", "local") == "local"


class ViewConfig(TypedDict, total=False):
    """Configuration for a single API viewset.

    Config-driven viewset configuration inspired by Thermal Eye VIEWS_MATRIX.
    All viewsets are configured declaratively, no hardcoded logic.
    """

    # Model & serializers
    model: Type[Model]
    serializer_read: Optional[Type[Serializer]]  # None = uses MySerializer.create_serializer()
    serializer_write: Optional[Type[Serializer]]

    # Query optimization
    select_related: List[str]  # e.g., ["factory", "location"]
    prefetch_related: List[str]  # e.g., ["tags"]
    
    # Permissions & ownership
    ownership_field: Optional[str]  # e.g., "factory_id" or "created_by"
    require_superuser: bool
    require_staff: bool
    
    # Scoping hierarchy (SSOT for scoping engine)
    ownership_hierarchy: List[str]  # e.g., ["created_by", "factory_id", "location_id"]
    scope_level_metadata: Dict[int, Dict[str, str]]  # {0: {"name": "User", "field": "created_by"}, ...}
    
    # Search & Filters
    search_fields: List[str]
    filter_class: Optional[type]  # Django filter class
    ordering_fields: List[str] | str  # "__all__" or specific list
    default_ordering: List[str]
    filter_fields: List[str]  # Optional list of fields that may be filtered via query params
    
    # Features
    soft_delete: bool  # Use active=False instead of delete
    factory_scoped: bool  # Filter by user's factories
    dynamic_search: bool  # Use visible columns for search
    
    # Table state integration
    table_name: str  # For dynamic search fields
    
    # FK Display Label Template (SSOT)
    fk_display_template: Optional[str]  # e.g., "{code}-{human_id}-{name}"
    
    # FK configuration
    fk_fields: Dict[str, str]  # {'factory': 'factories', 'location': 'locations'}
    
    # Custom hooks
    before_create: Optional[Callable]
    after_create: Optional[Callable]
    before_update: Optional[Callable]
    after_update: Optional[Callable]
    
    # Include unassigned records for superuser
    include_unassigned_for_superuser: bool
    
    # Permission classes (for custom endpoints)
    permission_classes: List[type]


# -----------------------------------------------------------------------------
# VIEWS_MATRIX - Single source of truth for config-driven viewsets
# -----------------------------------------------------------------------------

VIEWS_MATRIX: Dict[str, ViewConfig] = {
    # Users admin endpoint
    "users": {
        "model": User,
        "serializer_read": UserListSerializer,
        # No implicit filters; permissions + scoping control visibility
        "base_filters": {},
        # Ownership hierarchy for scoping engine
        # scope_level 0 = owner (user.id - UUID)
        "ownership_hierarchy": ["id"],
        "search_fields": ["username", "email", "first_name", "last_name"],
        "ordering_fields": [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "date_joined",
        ],
        "default_ordering": ["username"],
    },
    
    # =====================================================================
    # Thermal Eye Models (migrated)
    # =====================================================================
    
    # Companies - Superuser-only access
    "companies": {
        "model": Company,
        "serializer_read": None,
        "serializer_write": None,
        "base_filters": {"active": True},
        # Scoping: Superuser only in this iteration
        "ownership_hierarchy": ["users"],
        "search_fields": ["name", "code", "human_id"],
        "ordering_fields": "__all__",
        "default_ordering": ["name"],
        "soft_delete": True,
        "factory_scoped": False,
        "dynamic_search": True,
        "table_name": "companies",
        "fk_display_template": "{code}-{name}",
        "select_related": [],
        "require_superuser": True,
    },
    
    # Factories - Company-owned
    "factories": {
        "model": Factory,
        "serializer_read": None,
        "serializer_write": None,
        "base_filters": {"active": True},
        # Scoping: User → Company → Factory
        "ownership_hierarchy": ["company__users", "company_id", "id"],
        "scope_level_metadata": {
            0: {"name": "User (via Company)", "field": "company__users"},
            1: {"name": "Company", "field": "company_id"},
            2: {"name": "Factory", "field": "id"},
        },
        "search_fields": ["name", "code", "address", "company__name"],
        "ordering_fields": "__all__",
        "default_ordering": ["name"],
        "soft_delete": True,
        "factory_scoped": False,  # Factories are company-scoped, not factory-scoped
        "dynamic_search": True,
        "table_name": "factories",
        "fk_display_template": "{code}-{human_id}-{name}",
        # FK configuration
        "fk_fields": {"company": "companies"},
        "select_related": ["company"],
    },
    
    # Locations - Factory-scoped lookup entity
    "locations": {
        "model": Location,
        "serializer_read": None,
        "serializer_write": None,
        "base_filters": {"active": True},
        # Scoping: User → Company → Factory → Location
        "ownership_hierarchy": ["factory__company__users", "factory_id"],
        "scope_level_metadata": {
            0: {"name": "User (via Company)", "field": "factory__company__users"},
            1: {"name": "Factory", "field": "factory_id"},
        },
        "search_fields": ["name", "code", "factory__name"],
        "ordering_fields": "__all__",
        "default_ordering": ["name"],
        "soft_delete": True,
        "factory_scoped": True,
        "dynamic_search": True,
        "table_name": "locations",
        "fk_display_template": "{code} - {name}",
        "fk_fields": {"factory": "factories"},
        "select_related": ["factory"],
    },
    
    # Carriers - Factory-scoped lookup entity
    "carriers": {
        "model": Carrier,
        "serializer_read": None,
        "serializer_write": None,
        "base_filters": {"active": True},
        "ownership_hierarchy": ["factory__company__users", "factory_id"],
        "search_fields": ["name", "code", "factory__name"],
        "ordering_fields": "__all__",
        "default_ordering": ["name"],
        "soft_delete": True,
        "factory_scoped": True,
        "table_name": "carriers",
        "fk_display_template": "{code} - {name}",
        "fk_fields": {"factory": "factories"},
        "select_related": ["factory"],
    },
    
    # Drivers - Factory-scoped lookup entity
    "drivers": {
        "model": Driver,
        "serializer_read": None,
        "serializer_write": None,
        "base_filters": {"active": True},
        "ownership_hierarchy": ["factory__company__users", "factory_id"],
        "search_fields": ["name", "code", "factory__name"],
        "ordering_fields": "__all__",
        "default_ordering": ["name"],
        "soft_delete": True,
        "factory_scoped": True,
        "table_name": "drivers",
        "fk_display_template": "{code} - {name}",
        "fk_fields": {"factory": "factories"},
        "select_related": ["factory"],
    },
    
    # Pots - Factory-scoped lookup entity
    "pots": {
        "model": Pot,
        "serializer_read": None,
        "serializer_write": None,
        "base_filters": {"active": True},
        "ownership_hierarchy": ["factory__company__users", "factory_id"],
        "search_fields": ["name", "code", "factory__name"],
        "ordering_fields": "__all__",
        "default_ordering": ["name"],
        "soft_delete": True,
        "factory_scoped": True,
        "table_name": "pots",
        "fk_display_template": "{code} - {name}",
        "fk_fields": {"factory": "factories"},
        "select_related": ["factory"],
    },
    
    # Pits - Factory-scoped with optional Location
    "pits": {
        "model": Pit,
        "serializer_read": None,
        "serializer_write": None,
        "base_filters": {"active": True},
        "ownership_hierarchy": ["factory__company__users", "factory_id", "location_id"],
        "search_fields": ["name", "code", "factory__name", "location__name"],
        "ordering_fields": "__all__",
        "default_ordering": ["name"],
        "soft_delete": True,
        "factory_scoped": True,
        "table_name": "pits",
        "fk_display_template": "{code} - {name}",
        "fk_fields": {"factory": "factories", "location": "locations"},
        "select_related": ["factory", "location"],
    },
    
    # Machines - Factory-scoped
    "machines": {
        "model": Machine,
        "serializer_read": None,
        "serializer_write": None,
        "base_filters": {"active": True},
        "ownership_hierarchy": ["factory__company__users", "factory_id"],
        "search_fields": ["name", "code", "machine_uuid", "factory__name"],
        "ordering_fields": "__all__",
        "default_ordering": ["name"],
        "soft_delete": True,
        "factory_scoped": True,
        "table_name": "machines",
        "fk_display_template": "{code} - {name}",
        "fk_fields": {"factory": "factories"},
        "select_related": ["factory"],
    },
    
    # Cameras - Factory-scoped with optional Location
    "cameras": {
        "model": Camera,
        "serializer_read": None,
        "serializer_write": None,
        "base_filters": {"active": True},
        "ownership_hierarchy": ["factory__company__users", "factory_id"],
        "search_fields": ["name", "code", "ip", "camera_sn", "manufacturer", "factory__name"],
        "ordering_fields": "__all__",
        "default_ordering": ["name"],
        "soft_delete": True,
        "factory_scoped": True,
        "table_name": "cameras",
        "fk_display_template": "{code} - {name}",
        "fk_fields": {"factory": "factories", "location": "locations"},
        "select_related": ["factory", "location"],
        "include_unassigned_for_superuser": True,
    },
    
    # Measurements - Complex FK relationships
    "measurements": {
        "model": Measurement,
        "serializer_read": None,
        "serializer_write": None,
        "base_filters": {},
        "ownership_hierarchy": ["factory__company__users", "factory_id"],
        "search_fields": [
            "id", "comment", "note",
            "factory__name", "factory__code",
            "location__name", "carrier__name", "carrier__code",
            "driver__name", "driver__code", "pot__name", "pot__code",
            "pit__name", "pit__code", "machine__name", "machine__code",
        ],
        "ordering_fields": "__all__",
        "default_ordering": ["-dump_date", "-dump_time"],
        "soft_delete": False,
        "factory_scoped": True,
        "table_name": "measurements",
        "fk_fields": {
            "factory": "factories",
            "location": "locations",
            "carrier": "carriers",
            "driver": "drivers",
            "pot": "pots",
            "pit": "pits",
            "machine": "machines",
        },
        "select_related": ["factory", "location", "carrier", "driver", "pot", "pit", "machine"],
    },
    # PdfViewer focused views endpoint
    "focusedviews": {
        "model": FocusedView,
        "serializer_read": FocusedViewSerializer,
        "base_filters": {},
        "search_fields": [
            "document_ref",
            "source_model_path",
            "source_object_id",
        ],
        "ordering_fields": [
            "created",
            "updated",
            "document_ref",
            "page_number",
        ],
        "default_ordering": ["-updated"],
        "filter_fields": [
            "document_ref",
            "source_model_path",
            "source_object_id",
        ],
        # In local development we allow anonymous access so the pdfviewer
        # demo can work without a full frontend auth flow.
        **({"permission_classes": [AllowAny]} if IS_LOCAL_ENV else {}),
    },
    # PdfViewer annotations endpoint
    "annotations": {
        "model": Annotation,
        "serializer_read": AnnotationSerializer,
        "base_filters": {},
        "search_fields": [
            "document_ref",
            "layer_key",
            "owner_model_path",
            "owner_object_id",
        ],
        "ordering_fields": [
            "document_ref",
            "page_number",
            "created",
        ],
        "default_ordering": ["document_ref", "page_number", "created"],
        "filter_fields": [
            "document_ref",
            "page_number",
            "layer_key",
            "owner_model_path",
            "owner_object_id",
        ],
        **({"permission_classes": [AllowAny]} if IS_LOCAL_ENV else {}),
    },
}


# =============================================================================
# CUSTOM ENDPOINTS CONFIGURATION
# =============================================================================

class CustomEndpointConfig(TypedDict, total=False):
    """Configuration for a custom API endpoint.
    
    Used for non-CRUD endpoints like authentication, file uploads, etc.
    """
    path: str  # URL path (e.g., "auth/login/")
    view_function: str  # Import path to view function
    name: str  # URL name (e.g., "auth-login")
    methods: List[str]  # HTTP methods (e.g., ["POST"])
    permission_classes: List[str]  # Permission classes (e.g., ["AllowAny"])
    path_params: Optional[Dict[str, str]]  # Path parameters (e.g., {"uidb64": "str"})
    cors_enabled: bool  # Whether CORS headers should be set


CUSTOM_ENDPOINTS: Dict[str, CustomEndpointConfig] = {
    # =========================================================================
    # Authentication Endpoints
    # =========================================================================
    
    "auth-login": {
        "path": "auth/login/",
        "view_function": "sopira_magic.apps.authentification.views.login_view",
        "name": "auth-login",
        "methods": ["POST"],
        "permission_classes": ["AllowAny"],
        "cors_enabled": True,
    },
    "auth-logout": {
        "path": "auth/logout/",
        "view_function": "sopira_magic.apps.authentification.views.logout_view",
        "name": "auth-logout",
        "methods": ["POST"],
        "permission_classes": ["IsAuthenticated"],
        "cors_enabled": True,
    },
    "auth-signup": {
        "path": "auth/signup/",
        "view_function": "sopira_magic.apps.authentification.views.signup_view",
        "name": "auth-signup",
        "methods": ["POST"],
        "permission_classes": ["AllowAny"],
        "cors_enabled": True,
    },
    "auth-check": {
        "path": "auth/check/",
        "view_function": "sopira_magic.apps.authentification.views.check_auth_view",
        "name": "auth-check",
        "methods": ["GET"],
        "permission_classes": ["AllowAny"],
        "cors_enabled": True,
    },
    "auth-csrf": {
        "path": "auth/csrf/",
        "view_function": "sopira_magic.apps.authentification.views.csrf_token_view",
        "name": "csrf-token",
        "methods": ["GET"],
        "permission_classes": ["AllowAny"],
        "cors_enabled": True,
    },
    "auth-forgot-password": {
        "path": "auth/forgot-password/",
        "view_function": "sopira_magic.apps.authentification.views.forgot_password_view",
        "name": "auth-forgot-password",
        "methods": ["POST"],
        "permission_classes": ["AllowAny"],
        "cors_enabled": True,
    },
    "auth-reset-password": {
        "path": "auth/reset-password/<str:uidb64>/<str:token>/",
        "view_function": "sopira_magic.apps.authentification.views.reset_password_view",
        "name": "auth-reset-password",
        "methods": ["POST"],
        "permission_classes": ["AllowAny"],
        "path_params": {"uidb64": "str", "token": "str"},
        "cors_enabled": True,
    },
    
    # =========================================================================
    # PDF Viewer Endpoints
    # =========================================================================
    
    "focusedviews-assign": {
        "path": "focusedviews/assign/",
        "view_function": "sopira_magic.apps.api.views.assign_focused_view",
        "name": "assign-focused-view",
        "methods": ["POST"],
        "permission_classes": ["AllowAny"] if IS_LOCAL_ENV else ["IsAuthenticated"],
        "cors_enabled": True,
    },
    
    # =========================================================================
    # API Key Management (existing endpoints, now config-driven)
    # =========================================================================
    
    # Note: APIKey and APIVersion viewsets are registered separately
    # as they use custom ViewSet classes, not config-driven ones
    
    # =========================================================================
    # User Management Endpoints
    # =========================================================================
    
    "user-preferences": {
        "path": "user/preferences/",
        "view_function": "sopira_magic.apps.api.views.user_preferences_view",
        "name": "user-preferences",
        "methods": ["GET", "POST", "PUT"],
        "permission_classes": ["IsAuthenticated"],
        "cors_enabled": True,
    },
    "user-filters": {
        "path": "user/filters/",
        "view_function": "sopira_magic.apps.api.views.user_filters_view",
        "name": "user-filters",
        "methods": ["GET", "POST", "DELETE"],
        "permission_classes": ["IsAuthenticated"],
        "cors_enabled": True,
    },
    
    # =========================================================================
    # Access Rights Endpoints
    # =========================================================================
    
    "accessrights-matrix": {
        "path": "accessrights/matrix/",
        "view_function": "sopira_magic.apps.api.views.accessrights_matrix_view",
        "name": "accessrights-matrix",
        "methods": ["GET"],
        "permission_classes": ["IsAuthenticated"],
        "cors_enabled": True,
    },
    
    # =========================================================================
    # Models Metadata Endpoints
    # =========================================================================
    
    "models-metadata": {
        "path": "models/metadata/",
        "view_function": "sopira_magic.apps.api.views.models_metadata_view",
        "name": "models-metadata",
        "methods": ["GET"],
        "permission_classes": ["IsAuthenticated"],
        "cors_enabled": True,
    },
    
    # =========================================================================
    # Table State Presets Endpoints
    # =========================================================================
    
    "table-state-presets": {
        "path": "table-state-presets/",
        "view_function": "sopira_magic.apps.api.views.table_state_presets_view",
        "name": "table-state-presets",
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "permission_classes": ["IsAuthenticated"],
        "cors_enabled": True,
    },
}
