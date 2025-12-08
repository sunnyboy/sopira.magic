# accessrights - ConfigDriven SSOT pre práva

Ciele:
- Jediná matica (SSOT) kto/čo môže vidieť a aké akcie (view/add/edit/delete/export/menu).
- Bez hardcodu v kóde viewsetov: DRF permission `AccessRightsPermission` číta maticu.
- FE môže použiť rovnakú maticu (menu visibility) cez budúci endpoint alebo priamo importom (ak je to bezpečné).

Súbory:
- `config.py` — `ACCESS_MATRIX` + `DEFAULT_POLICY`
- `services.py` — `can_access(view, action, user)` a `can_view_menu(menu, user)`
- `permissions.py` (v api) — `AccessRightsPermission`, `IsSuperUserPermission`

Základná matica (ukážka):
- `companies`: všetky akcie len pre `superuser`
- Default policy: view pre všetkých prihlásených, zápis len admin/superuser

Integrácia BE:
- `view_factory` pridáva `AccessRightsPermission` pre všetky viewsety (ak nie je DEV_MODE).
- Pre SA-only: v `VIEWS_MATRIX["companies"]` je `require_superuser=True` (a perm sa nastaví na `IsSuperUserPermission` + AccessRights).

Integrácia FE:
- Menu: podmienka `can_view_menu("companies", user)` (UI by malo čítať SSOT).

Ďalšie kroky (voliteľné):
- Vystaviť read-only endpoint s maticou pre FE (scoping-aware). ✅
- Rozšíriť maticu o granularitu polí/akcií podľa rolí.


## Nový endpoint

`GET /api/accessrights/matrix/` (auth)

```json
{
  "menu": {
    "companies": true,
    "factories": true,
    "...": true
  },
  "actions": {
    "companies": { "view": true, "add": true, "edit": true, "delete": true, "export": true, "menu": true },
    "factories": { "view": true, "add": true, "edit": true, "delete": true, "export": true, "menu": true }
  }
}
```

FE používa menu/actions pre:
- NavBar (zobrazenie položiek)
- MyTable (povolenie akcií add/edit/delete/export)

