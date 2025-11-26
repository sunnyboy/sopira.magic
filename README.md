# Sopira.magic

Enterprise-grade Django application with microservices architecture (modular monolith).

## Architecture

This is a modular monolith - all microservices run in a single Django project but are organized as separate Django apps. All apps share a single PostgreSQL database.

## Project Structure

```
sopira_magic/
├── manage.py
├── sopira_magic/          # Project settings
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   ├── asgi.py
│   └── security_config.py
└── apps/                  # All Django apps
    ├── core/              # Base models and utilities
    ├── user/              # User management
    ├── authentification/  # Authentication
    ├── company/           # Company management
    ├── factory/           # Factory management
    └── ...                # See full list in settings.py
```

## Setup

1. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy environment file:
```bash
cp .env.example .env
```

4. Update `.env` with your database credentials

5. Run migrations:
```bash
python manage.py migrate
```

6. Create superuser:
```bash
python manage.py createsuperuser
```

7. Run development server:
```bash
python manage.py runserver
```

## Apps

### Core Apps
- **core**: Base models (TimeStampedModel, NamedWithCodeModel)
- **shared**: Shared utilities, mixins, decorators

### User & Auth
- **user**: User management and preferences
- **authentification**: Authentication (login, signup, 2FA)

### Business Logic
- **company**: Company management
- **factory**: Factory management
- **productionline**: Production line management
- **utility**: Utility functions
- **equipment**: Equipment management
- **resource**: Resource management
- **worker**: Worker management
- **material**: Material management
- **process**: Business processes
- **endpoint**: External endpoints (cameras, sensors, IoT)
- **dashboard**: Dashboard configuration

### Services
- **search**: Search functionality (Elasticsearch ready)
- **notification**: Notifications (email, SMS, push)
- **reporting**: Reports (PDF, CSV, Excel)
- **analytics**: Analytics
- **alarm**: Alarm management
- **audit**: Audit logging
- **logging**: Application logging
- **file_storage**: File storage (S3, Local, Azure)
- **document**: Document management
- **video**: Video gallery
- **photo**: Photo gallery
- **tag**: Tag management
- **scheduler**: Task scheduling
- **caching**: Caching layer
- **state**: UI state persistence
- **internationalization**: i18n support
- **impex**: Import/Export
- **api**: API Gateway
- **mobileapp**: Mobile app configuration

### SSOT & Config-driven
- **relation**: Dynamic relation registry (config-driven)
- **generator**: Data generation (SSOT, config-driven)

## Base Models

All business models inherit from:
- `TimeStampedModel`: id (UUID), uuid, created, updated, active, visible
- `NamedWithCodeModel`: Extends TimeStampedModel with human_id, code, name, comment, note

## Database Architecture

Multi-database PostgreSQL setup:

### PRIMARY DATABASE
- **Purpose**: Hlavné business data storage
- **Tables**: user_*, company_*, factory_*, equipment_*, measurement_*, document_*, process_*
- **Environment Variable**: `PRIMARY_DATABASE_URL` or `DATABASE_URL`

### STATE DATABASE
- **Purpose**: UI state a environment state viazaný na usera
- **Tables**: table_state, saved_workspace, environment_state
- **Environment Variable**: `STATE_DATABASE_URL`
- **Apps**: `state`
- **Note**: UserPreference je v PRIMARY database (user app)

### LOGGING DATABASE
- **Purpose**: Application logs a audit trails
- **Tables**: system_log, audit_log, performance_log
- **Environment Variable**: `LOGGING_DATABASE_URL`
- **Apps**: `logging`, `audit`

### Database Router
Automatic routing via `sopira_magic.db_router.DatabaseRouter`:
- Routes models to appropriate database based on app_label
- Prevents cross-database relations
- Ensures migrations go to correct database

### Setup Databases

1. Create databases:
```bash
createdb sopira_magic
createdb sopira_magic_state
createdb sopira_magic_logging
```

2. Configure `.env` with database URLs

3. Run migrations for each database:
```bash
python manage.py migrate --database default
python manage.py migrate --database state
python manage.py migrate --database logging
```

## Development

This is a scaffold - basic structure without full functionality. Selected modules will be developed incrementally.

## License

Private project.

