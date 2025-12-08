#..............................................................
#   apps/scoping/__init__.py
#   Scoping Engine - Abstraktný scoping modul
#..............................................................

"""
Scoping Engine - Abstraktný modul pre scoping bez závislostí na konkrétnych modeloch.

Exportuje hlavné API:
- ScopingEngine: Hlavný scoping engine
- register_scope_provider: Registrácia callbacku pre získanie scope hodnôt
- register_role_provider: Registrácia callbacku pre získanie role scope_owner
- get_scope_values: Získanie scope hodnôt cez registry
- get_scope_owner_role: Získanie role scope_owner cez registry
"""

from .engine import ScopingEngine
from .registry import (
    register_scope_provider,
    register_role_provider,
    get_scope_values,
    get_scope_owner_role,
    is_registry_configured,
)
from .validation import (
    validate_scoping_rules_matrix,
    validate_rule,
    validate_registry,
    validate_all,
    validate_and_raise,
    ScopingValidationError,
)
from .metrics import (
    record_scoping_execution,
    get_metrics,
    reset_metrics,
    export_metrics,
    ScopingMetricsContext,
)
from .fallback import (
    apply_with_fallback,
    simple_fallback_filter,
    no_filter_fallback,
    should_use_fallback,
)
from .test_helpers import (
    create_mock_scope_owner,
    create_mock_scope_provider,
    create_mock_role_provider,
    create_test_rule,
    with_mock_registry,
    assert_scoping_result,
    create_test_config,
)
from .decorators import (
    apply_scoping,
    scoping_context,
)
from .serialization import (
    export_rules,
    import_rules,
    get_rules_version,
    validate_imported_rules,
)
from .presets import (
    get_factory_scoped_preset,
    get_user_scoped_preset,
    get_global_preset,
    get_hybrid_preset,
    create_custom_preset,
)
from .middleware import (
    ScopingMiddleware,
    ScopingViewSetMixin,
)

__all__ = [
    # Core
    'ScopingEngine',
    # Registry
    'register_scope_provider',
    'register_role_provider',
    'get_scope_values',
    'get_scope_owner_role',
    'is_registry_configured',
    # Validation
    'validate_scoping_rules_matrix',
    'validate_rule',
    'validate_registry',
    'validate_all',
    'validate_and_raise',
    'ScopingValidationError',
    # Metrics
    'record_scoping_execution',
    'get_metrics',
    'reset_metrics',
    'export_metrics',
    'ScopingMetricsContext',
    # Fallback
    'apply_with_fallback',
    'simple_fallback_filter',
    'no_filter_fallback',
    'should_use_fallback',
    # Test helpers
    'create_mock_scope_owner',
    'create_mock_scope_provider',
    'create_mock_role_provider',
    'create_test_rule',
    'with_mock_registry',
    'assert_scoping_result',
    'create_test_config',
    # Decorators
    'apply_scoping',
    'scoping_context',
    # Serialization
    'export_rules',
    'import_rules',
    'get_rules_version',
    'validate_imported_rules',
    # Presets
    'get_factory_scoped_preset',
    'get_user_scoped_preset',
    'get_global_preset',
    'get_hybrid_preset',
    'create_custom_preset',
    # Middleware
    'ScopingMiddleware',
    'ScopingViewSetMixin',
]

