# Audit Report – sopira-magic

- Files scanned: **902**



## Security (7)
- `/mnt/data/repo_extract_fast/sopira.magic-main/frontend/src/components/ui/chart.tsx` — dangerouslySetInnerHTML
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/api/view_configs.py` — DRF AllowAny
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/api/view_factory.py` — DRF AllowAny
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/api/views.py` — DRF AllowAny
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/api/views.py` — csrf_exempt present
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/authentification/views.py` — DRF AllowAny
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/authentification/views.py` — csrf_exempt present

## DRY / Duplicates (3)
- `/mnt/data/repo_extract_fast/sopira.magic-main/frontend/src/security/date.ts; /mnt/data/repo_extract_fast/sopira.magic-main/frontend/src/utils/date.ts` — Duplicate-or-near-identical files
- `/mnt/data/repo_extract_fast/sopira.magic-main/frontend/src/security/tableHelpers.ts; /mnt/data/repo_extract_fast/sopira.magic-main/frontend/src/utils/tableHelpers.ts` — Duplicate-or-near-identical files
- `/mnt/data/repo_extract_fast/sopira.magic-main/frontend/src/security/toastMessages.ts; /mnt/data/repo_extract_fast/sopira.magic-main/frontend/src/utils/toastMessages.ts` — Duplicate-or-near-identical files

## Unused (heuristic) (63)
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/api/view_configs.py` — Possibly unused import 'Any'
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/api/views.py` — Possibly unused import 'RateLimitConfig'
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/api/views.py` — Possibly unused import 'timezone'
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/audit/models.py` — Possibly unused import 'TimeStampedModel'
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/audit/models.py` — Possibly unused import '_'
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/authentification/models.py` — Possibly unused import 'NamedWithCodeModel'
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/authentification/models.py` — Possibly unused import 'TimeStampedModel'
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/authentification/serializers.py` — Possibly unused import 'get_validation_config'
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/authentification/types.py` — Possibly unused import 'Optional'
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/authentification/validators/email.py` — Possibly unused import 're'
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/caching/services.py` — Possibly unused import 'hashlib'
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/core/models.py` — Possibly unused import 'settings'
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/generator/datasets.py` — Possibly unused import 'List'
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/generator/management/commands/clear_all_data.py` — Possibly unused import 'CommandError'
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/generator/management/commands/clear_all_data.py` — Possibly unused import 'transaction'
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/generator/management/commands/verify_relations.py` — Possibly unused import 'ContentType'
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/generator/tests/conftest.py` — Possibly unused import 'Factory'
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/generator/tests/conftest.py` — Possibly unused import 'Photo'
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/generator/tests/conftest.py` — Possibly unused import 'ProductionLine'
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/generator/tests/test_config.py` — Possibly unused import 'pytest'
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/generator/tests/test_datasets.py` — Possibly unused import 'pytest'
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/generator/tests/test_datasets.py` — Possibly unused import 're'
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/generator/tests/test_field_generators.py` — Possibly unused import 'pytest'
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/generator/tests/test_field_generators.py` — Possibly unused import 'time'
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/generator/tests/test_generate_data.py` — Possibly unused import 'Company'
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/generator/tests/test_models.py` — Possibly unused import 'ValidationError'
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/generator/tests/test_services.py` — Possibly unused import 'Factory'
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/generator/tests/test_services.py` — Possibly unused import 'Photo'
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/generator/tests/test_services.py` — Possibly unused import 'ProductionLine'
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/generator/tests/test_verify_relations.py` — Possibly unused import 'RelationRegistry'
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/m_camera/models.py` — Possibly unused import 'uuid'
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/relation/services.py` — Possibly unused import 'List'
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/scoping/engine.py` — Possibly unused import 'List'
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/scoping/engine.py` — Possibly unused import 'ScopingMatrix'
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/scoping/engine.py` — Possibly unused import 'ScopingRule'
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/scoping/engine.py` — Possibly unused import 'UserRole'
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/scoping/fallback.py` — Possibly unused import 'Q'
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/scoping/management/commands/scoping_presets.py` — Possibly unused import 'export_rules'
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/scoping/metrics.py` — Possibly unused import 'List'
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/scoping/metrics.py` — Possibly unused import 'Optional'
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/scoping/metrics.py` — Possibly unused import 'timedelta'
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/scoping/presets.py` — Possibly unused import 'Any'
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/scoping/rules.py` — Possibly unused import 'Dict'
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/scoping/serialization.py` — Possibly unused import 'validate_scoping_rules_matrix'
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/scoping/validation.py` — Possibly unused import 'settings'
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/security/engine.py` — Possibly unused import 'settings'
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/security/monitoring.py` — Possibly unused import 'SECURITY_CONFIG_MATRIX'
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/security/tests/factories.py` — Possibly unused import 'List'
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/security/tests/test_config.py` — Possibly unused import 'Dict'
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/security/tests/test_config.py` — Possibly unused import 'EnvironmentConfig'
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/security/tests/test_config.py` — Possibly unused import 'List'
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/security/tests/test_config.py` — Possibly unused import 'copy'
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/security/tests/test_engine.py` — Possibly unused import 'HttpRequest'
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/security/tests/test_registry.py` — Possibly unused import 'os'
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/security/tests/test_registry.py` — Possibly unused import 'pytest'
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/security/tests/test_validators/test_csrf.py` — Possibly unused import 'SimpleNamespace'
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/security/tests/test_validators/test_ssl.py` — Possibly unused import 'pytest'
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/security/types.py` — Possibly unused import 'Any'
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/security/types.py` — Possibly unused import 'Dict'
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/security/types.py` — Possibly unused import 'Optional'
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/shared/utils.py` — Possibly unused import 'Dict'
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/shared/utils.py` — Possibly unused import 'Optional'
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/shared/utils.py` — Possibly unused import 'models'

## Cleanliness (24)
- `/mnt/data/repo_extract_fast/sopira.magic-main/frontend/src/components/MyTable/MyTable.tsx` — console.* present
- `/mnt/data/repo_extract_fast/sopira.magic-main/frontend/src/components/MyTable/useMyTableData.ts` — console.* present
- `/mnt/data/repo_extract_fast/sopira.magic-main/frontend/src/components/NavBar.tsx` — console.* present
- `/mnt/data/repo_extract_fast/sopira.magic-main/frontend/src/components/modals/AddRecordModal.tsx` — console.* present
- `/mnt/data/repo_extract_fast/sopira.magic-main/frontend/src/components/modals/EditRecordModal.tsx` — console.* present
- `/mnt/data/repo_extract_fast/sopira.magic-main/frontend/src/components/modals/FactorySelectionModal.tsx` — console.* present
- `/mnt/data/repo_extract_fast/sopira.magic-main/frontend/src/components/modals/UserSelectionModal.tsx` — console.* present
- `/mnt/data/repo_extract_fast/sopira.magic-main/frontend/src/components/ui_custom/table/ScopedFKCell.tsx` — console.* present
- `/mnt/data/repo_extract_fast/sopira.magic-main/frontend/src/components/ui_custom/table/fieldFactory.tsx` — console.* present
- `/mnt/data/repo_extract_fast/sopira.magic-main/frontend/src/components/ui_custom/table/useColumnPresetsState.ts` — console.* present
- `/mnt/data/repo_extract_fast/sopira.magic-main/frontend/src/components/ui_custom/table/useExport.ts` — console.* present
- `/mnt/data/repo_extract_fast/sopira.magic-main/frontend/src/components/ui_custom/table/useFilterState.ts` — console.* present
- `/mnt/data/repo_extract_fast/sopira.magic-main/frontend/src/components/ui_custom/table/useOptimisticField.ts` — console.* present
- `/mnt/data/repo_extract_fast/sopira.magic-main/frontend/src/config/api.ts` — console.* present
- `/mnt/data/repo_extract_fast/sopira.magic-main/frontend/src/config/modelMetadata.ts` — console.* present
- `/mnt/data/repo_extract_fast/sopira.magic-main/frontend/src/contexts/AuthContext.tsx` — console.* present
- `/mnt/data/repo_extract_fast/sopira.magic-main/frontend/src/contexts/ScopeContext.tsx` — console.* present
- `/mnt/data/repo_extract_fast/sopira.magic-main/frontend/src/hooks/useSnapshot.tsx` — console.* present
- `/mnt/data/repo_extract_fast/sopira.magic-main/frontend/src/pages/Home.tsx` — console.* present
- `/mnt/data/repo_extract_fast/sopira.magic-main/frontend/src/services/fkCacheService.ts` — console.* present
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/authentification/validators/email.py` — print() present
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/authentification/validators/password.py` — print() present
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/authentification/validators/username.py` — print() present
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/generator/services.py` — print() present

## Memory-leak risks (React) (5)
- `/mnt/data/repo_extract_fast/sopira.magic-main/frontend/src/components/MyTable/MyTable.tsx:1542` — useEffect with timers/listeners without cleanup
- `/mnt/data/repo_extract_fast/sopira.magic-main/frontend/src/components/MyTable/MyTable.tsx:1543` — useEffect with timers/listeners without cleanup
- `/mnt/data/repo_extract_fast/sopira.magic-main/frontend/src/components/MyTable/MyTable.tsx:1546` — useEffect with timers/listeners without cleanup
- `/mnt/data/repo_extract_fast/sopira.magic-main/frontend/src/components/MyTable/MyTable.tsx:1547` — useEffect with timers/listeners without cleanup
- `/mnt/data/repo_extract_fast/sopira.magic-main/frontend/src/components/ui_custom/table/EditableCell.tsx:111` — useEffect with timers/listeners without cleanup

## Trash/Legacy/TODO (6)
- `/mnt/data/repo_extract_fast/sopira.magic-main/documentation/thermal-eye-to-magic-migration.md` — Has TODO/FIXME/XXX/HACK
- `/mnt/data/repo_extract_fast/sopira.magic-main/frontend/src/components/MyTable/README.md` — Has TODO/FIXME/XXX/HACK
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/api/views.py` — Has TODO/FIXME/XXX/HACK
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/authentification/engine.py` — Has TODO/FIXME/XXX/HACK
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/caching/services.py` — Has TODO/FIXME/XXX/HACK
- `/mnt/data/repo_extract_fast/sopira.magic-main/sopira_magic/apps/m_measurement/models.py` — Has TODO/FIXME/XXX/HACK

## Systematic usage (components/CSS/tokens) (7)
- `/mnt/data/repo_extract_fast/sopira.magic-main/frontend/src/components/Graph.tsx` — Hardcoded color literals
- `/mnt/data/repo_extract_fast/sopira.magic-main/frontend/src/components/ui/chart.tsx` — Hardcoded color literals
- `/mnt/data/repo_extract_fast/sopira.magic-main/frontend/src/components/ui_custom/table/GraphCells.tsx` — Inline style objects in JSX
- `/mnt/data/repo_extract_fast/sopira.magic-main/frontend/src/index.css` — CSS !important used
- `/mnt/data/repo_extract_fast/sopira.magic-main/frontend/src/index.css` — Hardcoded color literals
- `/mnt/data/repo_extract_fast/sopira.magic-main/frontend/src/security/tableHelpers.ts` — Hardcoded color literals
- `/mnt/data/repo_extract_fast/sopira.magic-main/frontend/src/utils/tableHelpers.ts` — Hardcoded color literals