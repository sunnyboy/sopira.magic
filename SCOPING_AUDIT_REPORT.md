# SCOPING ENGINE - KOMPLEXNÝ AUDIT REPORT
**Generated:** 2025-12-12  
**Status:** 🔴 CRITICAL ISSUES FOUND

---

## Executive Summary

Scoping engine má **vážne konzistenčné problémy** medzi `VIEWS_MATRIX`, `SCOPING_RULES_MATRIX` a `core/apps.py` callbacks. Zistené boli:

- ✅ **12 modelov** má definované scoping rules
- ❌ **10+ modelov** CHÝBA v scoping rules (SECURITY LEAK!)
- ❌ **Scope level mismatch** medzi view_configs a rules
- ❌ **Core callbacks používajú absolútne levely** namiesto relatívnych indexov
- ❌ **Inconsistentný ownership_hierarchy** naprieč modelmi

---

## 1. INVENTORY: Modely v VIEWS_MATRIX

### Thermal Eye Modely (Production Data)

| Model | Table Name | Ownership Hierarchy | Scope Level Metadata | Rules Defined | Status |
|-------|------------|---------------------|---------------------|---------------|---------|
| **User** | `users` | `["id"]` | None | ✅ YES | ⚠️ PARTIAL |
| **Company** | `companies` | `["id"]` | `{1: {...}}` | ✅ YES | ❌ MISMATCH |
| **Factory** | `factories` | `["company__users", "company_id", "id"]` | `{0: {...}, 1: {...}, 2: {...}}` | ✅ YES | ⚠️ REVIEW |
| **Location** | `locations` | `["factory__company__users", "factory_id"]` | `{0: {...}, 1: {...}}` | ✅ YES | ✅ OK |
| **Carrier** | `carriers` | `["factory__company__users", "factory_id"]` | None | ✅ YES | ⚠️ NO METADATA |
| **Driver** | `drivers` | `["factory__company__users", "factory_id"]` | None | ✅ YES | ⚠️ NO METADATA |
| **Pot** | `pots` | `["factory__company__users", "factory_id"]` | None | ✅ YES | ⚠️ NO METADATA |
| **Pit** | `pits` | `["factory__company__users", "factory_id", "location_id"]` | None | ✅ YES | ⚠️ NO METADATA |
| **Machine** | `machines` | `["factory__company__users", "factory_id"]` | None | ✅ YES | ⚠️ NO METADATA |
| **Camera** | `cameras` | `["factory__company__users", "factory_id"]` | None | ✅ YES | ⚠️ NO METADATA |
| **Measurement** | `measurements` | `["factory__company__users", "factory_id"]` | None | ✅ YES | ⚠️ NO METADATA |
| **Video** | - | - | - | ❌ NO | 🔴 MISSING |
| **Photo** | - | - | - | ❌ NO | 🔴 MISSING |
| **Document** | - | - | - | ❌ NO | 🔴 MISSING |
| **Process** | - | - | - | ❌ NO | 🔴 MISSING |
| **Utility** | - | - | - | ❌ NO | 🔴 MISSING |
| **Material** | - | - | - | ❌ NO | 🔴 MISSING |
| **Resource** | - | - | - | ❌ NO | 🔴 MISSING |
| **Tag** | - | - | - | ❌ NO | 🔴 MISSING |
| **Equipment** | - | - | - | ❌ NO | 🔴 MISSING |
| **Worker** | - | - | - | ❌ NO | 🔴 MISSING |
| **ProductionLine** | - | - | - | ❌ NO | 🔴 MISSING |

### Ostatné Modely v VIEWS_MATRIX

| Model | In VIEWS_MATRIX | Rules Defined | Status |
|-------|-----------------|---------------|---------|
| **FocusedView** | ✅ YES | ❌ NO | 🔴 MISSING |
| **Annotation** | ✅ YES | ❌ NO | 🔴 MISSING |
| **Environment** | ✅ YES (empty dict) | ✅ YES (empty) | ⚠️ INTENTIONAL |
| **Logs** | NO in VIEWS_MATRIX | ✅ YES | ⚠️ ORPHAN RULE |

---

## 2. KRITICKÉ PROBLÉMY

### 🔴 PROBLEM #1: Companies Scope Level Mismatch

**View Config:**
```python
"companies": {
    "ownership_hierarchy": ["id"],  # Index 0 = company.id
    "scope_level_metadata": {
        1: {"name": "Company", "field": "id"},  # ❌ Hovorí level 1!
    }
}
```

**Scoping Rules:**
```python
"companies": {
    "admin": [{
        "params": {"scope_level": 0, "scope_type": "accessible"}  # ✅ Používa index 0
    }]
}
```

**Core Callback:**
```python
def get_accessible_scope(user, scope_level, request=None):
    if scope_level == 1:  # ❌ Hardcoded "1 = company"!
        return get_user_companies(user)
```

**KONFLIKT:**
- `scope_level_metadata` hovorí level **1**
- `ownership_hierarchy` má len **1 element** (index 0)
- Scoping rules používajú **index 0**
- Core callback očakáva **level 1**

**Dôsledok:**  
- Pri `scope_level=0` v rules sa volá `get_accessible_scope(user, 0, ...)`
- Core callback má hardcoded `if scope_level == 1` pre companies
- **VRÁTI PRÁZDNE POLE** → User nevidí svoje companies! ❌

---

### 🔴 PROBLEM #2: Factories má 3 levely, ale používa len 1

**View Config:**
```python
"factories": {
    "ownership_hierarchy": ["company__users", "company_id", "id"],
    # Index 0 = company__users (User cez company)
    # Index 1 = company_id (Company FK)
    # Index 2 = id (Factory.id)
    "scope_level_metadata": {
        0: {"name": "User (via Company)", "field": "company__users"},
        1: {"name": "Company", "field": "company_id"},
        2: {"name": "Factory", "field": "id"},
    }
}
```

**Scoping Rules:**
```python
"factories": {
    "admin": [{
        "params": {"scope_level": 1, "scope_type": "accessible"}  # Používa index 1
    }]
}
```

**Core Callback:**
```python
def get_accessible_scope(user, scope_level, request=None):
    if scope_level == 1:  # Toto vracia COMPANY IDs
        return get_user_companies(user)
    elif scope_level == 2:  # Toto vracia FACTORY IDs
        return get_user_factories(user)
```

**KONFLIKT:**
- Rules volajú `scope_level=1` (index 1 v hierarchy)
- Callback interpretuje `scope_level=1` ako "Company IDs"
- Ale factories očakávajú **company_id** (FK field), nie Company IDs? ❌

**Otázka:** 
- Má callback vracať **company IDs** (pre filter `company_id__in=[...]`)?
- Alebo má vracať **factory IDs** (pre filter `id__in=[...]`)?

---

### 🔴 PROBLEM #3: Chýbajúce scope_level_metadata

Väčšina modelov **NEMÁ** definované `scope_level_metadata`, len `ownership_hierarchy`.

**Príklad - Cameras:**
```python
"cameras": {
    "ownership_hierarchy": ["factory__company__users", "factory_id"],
    # NO scope_level_metadata!
}
```

**Dôsledok:**
- `ScopingEngine.get_scope_level_metadata(config)` vráti **prázdny dict**
- Debug metadata sú neúplné
- Nejasné aký field sa má použiť pre scope_level

---

### 🔴 PROBLEM #4: Chýbajúce Scoping Rules (Security Leak!)

**Tieto modely sú v databáze, ale NEMAJÚ scoping rules:**
- Video
- Photo
- Document
- Process
- Utility
- Material
- Resource
- Tag
- Equipment
- Worker
- ProductionLine
- FocusedView (v VIEWS_MATRIX)
- Annotation (v VIEWS_MATRIX)

**Dôsledok:**
- `ScopingEngine.apply_rules()` nenájde rules → vráti **UNFILTERED queryset**
- **VŠETCI užívatelia vidia VŠETKY data** z týchto tabuliek! 🚨

---

## 3. KONCEPTUÁLNY PROBLÉM: Relatívne vs Absolútne Levely

**Máme 2 možné interpretácie:**

### A) Relatívne Indexy (Current Implementation)

`scope_level` = **index do ownership_hierarchy**

**Príklad:**
```python
# Companies
"ownership_hierarchy": ["id"]
scope_level 0 → company.id

# Factories
"ownership_hierarchy": ["company__users", "company_id", "id"]
scope_level 0 → company__users
scope_level 1 → company_id
scope_level 2 → id
```

**Problém:**
- Core callback **nemôže hardcode** `if scope_level == 1: return companies`
- Lebo pre companies je level **0**, pre factories je level **1**
- Callback potrebuje vedieť **"pre tento model, čo znamená level X?"**

### B) Absolútne Konceptuálne Levely

`scope_level` = **konceptuálny level v celom systéme**

**Definícia:**
```python
SCOPE_LEVELS = {
    0: "user",      # User ownership
    1: "company",   # Company membership
    2: "factory",   # Factory
    3: "location",  # Location
}
```

**Príklad:**
```python
# Companies - filter by company.id
"ownership_hierarchy": ["id"]
"scope_level_mapping": {1: 0}  # Level 1 (company) → index 0

# Factories - filter by company_id (FK)
"ownership_hierarchy": ["company__users", "company_id", "id"]
"scope_level_mapping": {
    0: 0,  # Level 0 (user) → index 0
    1: 1,  # Level 1 (company) → index 1
    2: 2   # Level 2 (factory) → index 2
}
```

**Core callback:**
```python
def scope_provider(scope_level, scope_owner, scope_type, request=None):
    # scope_level je KONCEPTUÁLNY (0=user, 1=company, 2=factory)
    if scope_level == 0:
        return [str(scope_owner.id)]
    elif scope_level == 1:
        return get_user_companies(scope_owner)
    elif scope_level == 2:
        return get_user_factories(scope_owner)
```

**Výhoda:**
- ✅ Jasná sémantika
- ✅ Callback je **generický**
- ✅ Konzistentné naprieč modelmi

**Nevýhoda:**
- ❌ Veľká refaktorizácia
- ❌ Potreba pridať `scope_level_mapping` do všetkých configs

---

## 4. OWNERSHIP_HIERARCHY PATTERNS

### Pattern 1: Self-owned (scope by own ID)
```python
"users": ["id"]
"companies": ["id"]
```
**Scope:** Filtruj podľa vlastného ID (for company: company.id, for user: user.id)

### Pattern 2: Factory-owned (most common)
```python
"cameras": ["factory__company__users", "factory_id"]
"machines": ["factory__company__users", "factory_id"]
"locations": ["factory__company__users", "factory_id"]
```
**Scope:** Filtruj podľa factory_id FK

### Pattern 3: Multi-level hierarchy
```python
"factories": ["company__users", "company_id", "id"]
"pits": ["factory__company__users", "factory_id", "location_id"]
```
**Scope:** Viacúrovňová hierarchia

---

## 5. RECOMMENDATIONS

### Option A: Quick Fix (Minimálna zmena)

**1. Oprav Companies mismatch:**
```python
# view_configs.py
"companies": {
    "ownership_hierarchy": ["id"],
    "scope_level_metadata": {
        0: {"name": "Company", "field": "id"},  # ✅ Index 0
    }
}
```

**2. Fix Core callback - add context:**
```python
def scope_provider(scope_level, scope_owner, scope_type, request=None, config=None):
    # Zisti field name z ownership_hierarchy
    ownership_hierarchy = config.get("ownership_hierarchy", [])
    if scope_level >= len(ownership_hierarchy):
        return []
    
    field_name = ownership_hierarchy[scope_level]
    
    # Mapuj field name → scope values
    if "company" in field_name.lower() or field_name == "id" (for companies):
        return get_user_companies(scope_owner)
    elif "factory" in field_name.lower():
        return get_user_factories(scope_owner)
    # ...
```

**3. Pridaj chýbajúce rules:**
- Systematic pridanie rules pre všetky chýbajúce modely

**Pros:**
- ✅ Rýchle riešenie
- ✅ Minimálna zmena
- ✅ Backward compatible

**Cons:**
- ❌ Hack (heuristics based on field name)
- ❌ Nie clean design
- ❌ Stále relatívne indexy

---

### Option B: Clean Refactor (Absolútne levely)

**1. Definuj SCOPE_LEVELS:**
```python
# scoping/levels.py
SCOPE_LEVELS = {
    0: {"name": "user", "description": "User ownership"},
    1: {"name": "company", "description": "Company membership"},
    2: {"name": "factory", "description": "Factory scope"},
    3: {"name": "location", "description": "Location scope"},
}
```

**2. Pridaj scope_level_mapping do VŠETKÝCH configs:**
```python
"companies": {
    "ownership_hierarchy": ["id"],
    "scope_level_mapping": {1: 0},  # Company level → index 0
}

"factories": {
    "ownership_hierarchy": ["company__users", "company_id", "id"],
    "scope_level_mapping": {
        0: 0,  # User level → index 0
        1: 1,  # Company level → index 1
        2: 2,  # Factory level → index 2
    }
}
```

**3. Update ScopingEngine:**
```python
# engine.py
def _evaluate_condition(cls, condition, scope_owner, request, params, config):
    conceptual_level = params.get("scope_level")
    
    # Map conceptual level → ownership_hierarchy index
    mapping = config.get("scope_level_mapping", {})
    hierarchy_index = mapping.get(conceptual_level)
    
    if hierarchy_index is None:
        return Q()  # No mapping defined
    
    # Get field name from hierarchy
    field_name = config["ownership_hierarchy"][hierarchy_index]
    
    # Call scope_provider with CONCEPTUAL level
    scope_values = cls._get_scope_values(
        scope_owner,
        conceptual_level,  # ← Conceptual (0/1/2)
        scope_type,
        request
    )
```

**4. Update Core callback:**
```python
def scope_provider(conceptual_level, scope_owner, scope_type, request=None):
    # conceptual_level je 0/1/2 (user/company/factory)
    if conceptual_level == 0:
        return [str(scope_owner.id)]
    elif conceptual_level == 1:
        return get_user_companies(scope_owner)
    elif conceptual_level == 2:
        return get_user_factories(scope_owner)
```

**Pros:**
- ✅ Clean design
- ✅ Jasná sémantika
- ✅ Maintainable
- ✅ Scalable

**Cons:**
- ❌ Veľká zmena
- ❌ Breaking change
- ❌ Potreba migrácie všetkých rules

---

### Option C: Hybrid (RECOMMENDED)

**Postup:**
1. **Phase 1:** Quick fix companies (Option A style)
2. **Phase 2:** Pridaj chýbajúce rules systematicky
3. **Phase 3:** Dokumentuj current approach
4. **Phase 4:** (Budúcnosť) Refactor na absolútne levely (Option B)

**Reasoning:**
- Teraz fix critical security issues
- Potom systematicky dokumentuj a test
- Neskôr clean refactor keď máme stabilný základ

---

## 6. NEXT STEPS

**Immediate (CRITICAL):**
1. ✅ Fix companies scope level mismatch
2. 🔴 Pridaj scoping rules pre Video, Photo, Document, Process, etc.
3. 🔴 Test miso user - overit empty scope behavior

**Short Term:**
1. Pridaj `scope_level_metadata` pre všetky modely
2. Systematicky test všetky modely s empty/populated scope
3. Dokumentuj ownership_hierarchy patterns

**Long Term:**
1. Consider refactor na absolútne scope levels
2. Add validation pri startupe (check rules ↔ configs consistency)
3. Add scoping engine debug UI

---

## 7. TESTING MATRIX

| Model | Admin (0 companies) | Admin (1 company) | Admin (2 companies) | Superuser |
|-------|---------------------|-------------------|---------------------|-----------|
| companies | EMPTY ✅ | 1 ✅ | 2 ✅ | ALL ✅ |
| factories | EMPTY ❓ | company's ❓ | both companies' ❓ | ALL ❓ |
| cameras | EMPTY ❓ | company's factories' ❓ | both companies' ❓ | scope selected ❓ |
| machines | EMPTY ❓ | company's factories' ❓ | both companies' ❓ | scope selected ❓ |
| videos | EMPTY ❓ | ??? ❓ | ??? ❓ | ALL ❓ |

**Legend:**
- ✅ Tested & working
- ❓ Not tested yet
- ❌ Known issue

---

## CONCLUSION

Scoping engine má **vážne konceptuálne problémy** medzi relatívnymi indexmi a absolútnymi levelmi. 

**Odporúčam:**
1. **TERAZ:** Quick fix companies + pridaj chýbajúce rules
2. **POTOM:** Systematický audit a testing
3. **BUDÚCNOSŤ:** Clean refactor na absolútne levely

**Čo preferuješ?**
- Option A (quick fix)?
- Option B (clean refactor)?
- Option C (hybrid)?




