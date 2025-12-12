# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Language Rules
- Jazyk komunikácie je slovenčina
- Komentáre a popis v kóde sa robia striktne v angličtine
- Každý nový súbor musí mať projektovú hlavičku a kolapsovateľný popis podľa vzoru na konci tohoto súboru

## Project Architecture

Tento projekt je **monorepo** obsahujúci:
- **Django backend** (`sopira_magic/`) - modular monolith s mikroservice architektúrou
- **React 19 + Vite + TypeScript frontend** (`frontend/`) - zrkadlí backendovú štruktúru

### Backend: Modular Monolith s Multi-Database Setup

#### Database Architecture
Projekt používa **tri PostgreSQL databázy** riadené `DatabaseRouter`:

1. **PRIMARY** (default) - Business data
   - ENV: `PRIMARY_DATABASE_URL` alebo `DATABASE_URL`
   - Apps: všetky biznis modely (user, company, factory, equipment, atď.)

2. **STATE** - UI state a user preferences
   - ENV: `STATE_DATABASE_URL`
   - Apps: `state` (table_state, saved_workspace, environment_state)

3. **LOGGING** - Application logs a audit trails
   - ENV: `LOGGING_DATABASE_URL`
   - Apps: `logging`, `audit`

#### Config-Driven Architecture (SSOT)
Projekt je postavený na princípe **Single Source of Truth**:

1. **Relation Registry** (`sopira_magic/apps/relation/`)
   - Config-driven relácie medzi modelmi
   - `RELATION_CONFIG` v `relation/config.py`
   - Dynamic relation service pre GenericForeignKey
   - Príkaz: `python manage.py init_relations`

2. **Generator System** (`sopira_magic/apps/generator/`)
   - Config-driven generovanie test dát
   - `GENERATOR_CONFIG` definuje pre každý model factory
   - Podporuje dependency resolution

3. **Base Models** (`sopira_magic/apps/core/models.py`)
   - `TimeStampedModel` - základ pre všetky modely (UUID, timestamps, active, visible)
   - `NamedWithCodeModel` - pridáva code, name, human_id, comment, note
   - `CompanyOwnedModel` - company FK (Level 1)
   - `FactoryScopedModel` - factory FK (Level 2)
   - `MeasurementRelatedModel` - measurement FK (Level 3)

#### Django Apps Structure
Všetky apps sú v `sopira_magic/apps/`:

**Core & Shared:**
- `core` - Base models a utilities
- `shared` - Shared utilities, mixins, decorators
- `security` - Security middleware a utils

**User & Auth:**
- `m_user` - User management
- `authentification` - Authentication (login, 2FA)

**Business Models (prefixované `m_`):**
- `m_company`, `m_factory`, `m_location`, `m_carrier`, `m_driver`
- `m_pot`, `m_pit`, `m_machine`, `m_camera`, `m_measurement`
- `m_productionline`, `m_utility`, `m_equipment`, `m_resource`
- `m_worker`, `m_material`, `m_process`
- `m_document`, `m_video`, `m_photo`, `m_tag`

**Services:**
- `search`, `notification`, `reporting`, `analytics`, `alarm`
- `audit`, `logging`, `file_storage`, `scheduler`
- `fk_options_cache`, `state`, `internationalization`, `impex`
- `api`, `mobileapp`, `dashboard`, `endpoint`

**SSOT & Config-driven:**
- `relation` - Dynamic relation registry
- `generator` - Data generation system
- `accessrights` - Access control config
- `scoping` - Scoping engine
- `pdfviewer` - PDF viewer

### Frontend: React 19 + Vite + TypeScript

Frontend mirrors backend structure v `frontend/src/apps/`:
- Používa **shadcn/ui** (Radix UI primitives) + Tailwind CSS
- Dev server: `http://localhost:5173`
- API proxy: `http://localhost:8000`
- Path aliases: `@/*` → `./src/*`

## Common Commands

### Backend (Django)

#### Setup & Migrations
```bash
# Aktivovať virtual environment
source venv/bin/activate  # alebo: source .venv/bin/activate

# Migrácie pre všetky databázy
python manage.py migrate --database default
python manage.py migrate --database state
python manage.py migrate --database logging

# Vytvoriť superusera
python manage.py createsuperuser
```

#### Development Server
```bash
# Spustiť Django dev server
python manage.py runserver

# Poznámka: User preferuje príkaz 'resetall' na štart serverov (ak existuje)
```

#### Testing
```bash
# Spustiť všetky testy
pytest

# Spustiť testy konkrétnej app
pytest sopira_magic/apps/core/

# Spustiť konkrétny test súbor
pytest sopira_magic/apps/core/tests/test_models.py

# Spustiť s coverage
pytest --cov=sopira_magic --cov-report=html

# Spustiť iba unit testy (vynechať pomalé)
pytest -m "not slow"
```

#### Data Generation (SSOT)
```bash
# Inicializovať relation registry z config
python manage.py init_relations

# Generovať seed data pre všetky modely (respects dependencies)
python manage.py generate_all_data

# Generovať data pre konkrétny model
python manage.py generate_data company --count 10
python manage.py generate_data factory --count 20 --user sopira

# Vymazať všetky business data (ponecháva users)
python manage.py clear_all_data

# Vymazať data konkrétneho modelu
python manage.py generate_data company --clear

# Overiť relačnú integritu
python manage.py verify_relations
```

### Frontend (React + Vite)

```bash
cd frontend

# Inštalácia dependencies
npm install

# Dev server (hot reload)
npm run dev

# Production build
npm run build

# Preview production build
npm run preview

# Lint check
npm run lint
```

## Development Workflow

### Git Workflow
- Main branch: `main` (protected)
- Feature branches:
  - `feat/<description>` - nové features
  - `fix/<description>` - bugfixy
  - `chore/<description>` - non-functional changes

### Pre-commit Checks
Pred otvorením pull requestu:
```bash
# Backend
pytest                    # všetky testy musia prejsť

# Frontend
cd frontend
npm run lint             # žiadne lint errory
npm run build            # build musí prejsť
```

### CI Pipeline (GitHub Actions)
- Backend: pytest + multi-database setup
- Frontend: lint + build
- PostgreSQL 16 service container

## File Header Template

Každý nový súbor musí obsahovať:

```python
#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/<app>/<file>.py
#   <Title> - <Short description>
#   <Purpose description>
#..............................................................

"""
   <Title> - <Full Description>.

   <Detailed description of the module, its purpose, and usage.>
   <Include key features, configuration, and important notes.>

   Usage:
   ```python
   # Example code
   ```

   Important:
   - NO HARDCODING: All solutions must be universal and config-driven
   - No model-specific or app-specific hardcoded logic
"""
```

## Architecture Invariants

### Config-Driven Development
- **ZAKÁZANÉ**: Hardcode v shared komponentoch, base modeloch, common views
- **POVINNÉ**: Všetko doménovo špecifické cez konfiguráciu a SSOT
- Používaj `RELATION_CONFIG`, `GENERATOR_CONFIG`, `VIEWS_MATRIX`
- Nové features využívajú existujúci relation registry a generátory

### Domain Isolation
- Domain-specific kód patrí do samostatnej app (microservice-modul)
- Shared vrstvy musia zostať generické
- Žiadne if/else podmienky na konkrétne modely v shared kóde

### Base Model Inheritance
Všetky business modely dedia z:
- `TimeStampedModel` - ak nepotrebuješ code/name
- `NamedWithCodeModel` - štandardná voľba
- `CompanyOwnedModel` - ak je owned by company
- `FactoryScopedModel` - ak je scoped to factory
- `MeasurementRelatedModel` - pre media attached to measurements

### Multi-Database Routing
- Models sú automaticky routované do správnej DB cez `DatabaseRouter`
- Nepoužívaj cross-database ForeignKeys (zabránené routerom)
- Migrations musia ísť do správnej DB (--database flag)
