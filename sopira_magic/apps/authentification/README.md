# Authentication Module - ConfigDriven & SSOT

## Prehľad

Authentication modul pre sopira.magic implementovaný v duchu **ConfigDriven & SSOT** architektúry. Všetka authentification logika je riadená deklaratívnou konfiguráciou namiesto hardcoded kódu.

## Architektonické princípy

### ConfigDriven & SSOT

- **AUTH_CONFIG** - Single Source of Truth pre všetky authentification nastavenia
- **Žiadny hardcode** - všetka logika vychádza z konfigurácie
- **Abstraktný prístup** - univerzálne riešenia, nie špecifické pre konkrétny use case
- **Registry pattern** - callbacky pre custom logiku cez registry

### Integrácia s existujúcou architektúrou

- Použitie SecurityEngine pre security decisions
- Integrácia s audit modulom pre logging cez registry
- Integrácia s notification modulom pre emaily cez registry
- Integrácia s m_user modulom pre user management
- Frontend AuthContext mirror backend SSOT

## Štruktúra modulu

```
apps/authentification/
├── __init__.py              # Public API exports
├── apps.py                  # Django AppConfig
├── admin.py                 # Django admin configuration
├── models.py                # Authentication models (empty for now)
├── config.py                # AUTH_CONFIG - SSOT konfigurácia
├── types.py                 # TypedDict a Enum definície
├── registry.py              # Registry pattern pre callbacky
├── engine.py                # AuthEngine - hlavná logika
├── views.py                 # Config-driven REST API views
├── serializers.py           # Config-driven DRF serializers
├── urls.py                  # URL routing
├── backends.py              # Custom authentication backends
├── validators/              # Modulárne validátory
│   ├── __init__.py
│   ├── password.py
│   ├── username.py
│   ├── email.py
│   └── session.py
└── integration/             # Integrácia s inými modulmi
    ├── __init__.py
    ├── audit.py
    └── notification.py
```

## AUTH_CONFIG - SSOT konfigurácia

Všetky authentification nastavenia sú definované v `config.py`:

```python
from sopira_magic.apps.authentification.config import AUTH_CONFIG, get_auth_config

# Získaj konfiguráciu pre login endpoint
login_config = get_auth_config('login')
if login_config.get('enabled'):
    # Process login
```

### Konfigurovateľné endpoints

- `login`: enabled, require_csrf, session_timeout, max_attempts, lockout_duration
- `signup`: enabled, require_email_verification, default_role, auto_login
- `logout`: enabled, clear_session, invalidate_tokens
- `password_reset`: enabled, token_expiry, email_template, require_email
- `password_reset_confirm`: enabled, token_validation, min_password_length
- `verify_2fa`: enabled, provider, code_length, expiry
- `check_auth`: enabled, return_user_data, include_permissions

### Validácia

- `password`: min_length, require_uppercase, require_lowercase, require_numbers, require_special, forbidden_patterns
- `username`: min_length, max_length, allowed_chars, forbidden_patterns
- `email`: require_verification, allowed_domains, blocked_domains

### Audit & Notifications

- `audit`: audit_enabled, audit_actions, audit_fields
- `notification`: notifications_enabled, login_notification, signup_notification, password_reset_notification

## AuthEngine - hlavná logika

Všetky authentification operácie používajú `AuthEngine`:

```python
from sopira_magic.apps.authentification.engine import AuthEngine

# Authenticate user
user = AuthEngine.authenticate_user(request, username, password)

# Create user
user = AuthEngine.create_user(request, {
    'username': 'test',
    'password': 'password123',
    'email': 'test@example.com',
})

# Reset password
result = AuthEngine.reset_password(request, email)

# Check authentication
auth_status = AuthEngine.check_authentication(request)
```

## Registry Pattern

Registry pattern umožňuje host aplikácii registrovať custom callbacky:

```python
from sopira_magic.apps.authentification.registry import register_audit_logger

def my_audit_logger(action, user, **kwargs):
    # Custom audit logging
    AuditLog.objects.create(
        action=action,
        user=user,
        ip_address=kwargs.get('ip_address'),
        success=kwargs.get('success', True),
    )

register_audit_logger(my_audit_logger)
```

### Dostupné registry callbacky

- `register_audit_logger(callback)` - custom audit logging
- `register_notification_sender(callback)` - custom notification sending
- `register_user_serializer(callback)` - custom user data serialization
- `register_role_provider(callback)` - custom role management
- `register_password_validator(callback)` - custom password validation

## Validators

Config-driven validátory používajú AUTH_CONFIG:

```python
from sopira_magic.apps.authentification.validators import validate_password, validate_username, validate_email

# Validate password
is_valid, error = validate_password("MyPassword123")
if not is_valid:
    print(f"Password error: {error}")

# Validate username
is_valid, error = validate_username("myusername")
if not is_valid:
    print(f"Username error: {error}")

# Validate email
is_valid, error = validate_email("user@example.com")
if not is_valid:
    print(f"Email error: {error}")
```

## API Endpoints

Všetky endpoints sú config-driven a používajú AuthEngine:

- `POST /api/auth/signup/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `GET /api/auth/check/` - Check authentication status
- `GET /api/auth/csrf/` - Get CSRF token
- `POST /api/auth/forgot-password/` - Request password reset
- `POST /api/auth/reset-password/` - Confirm password reset
- `POST /api/auth/verify-2fa/` - Two-factor authentication

## Integrácia s inými modulmi

### Audit modul

```python
from sopira_magic.apps.authentification.integration.audit import register_audit_integration

def audit_logger(action, user, **kwargs):
    # Log to audit system
    pass

register_audit_integration(audit_logger)
```

### Notification modul

```python
from sopira_magic.apps.authentification.integration.notification import register_notification_integration

def notification_sender(notification_type, data):
    # Send email/SMS/push notification
    pass

register_notification_integration(notification_sender)
```

## Frontend AuthContext

Frontend používa `AuthContext` ktorý mirror backend SSOT:

```typescript
import { useAuth } from '@/contexts/AuthContext';

const { login, signup, logout, isAuthenticated, user } = useAuth();

// Login
const success = await login(username, password);

// Signup
const result = await signup(username, password, email);

// Logout
await logout();
```

## Príklady použitia

### Backend - Custom audit logging

```python
# V apps/audit/apps.py alebo apps/logging/apps.py
from sopira_magic.apps.authentification.integration.audit import register_audit_integration

def audit_logger(action, user, **kwargs):
    AuditLog.objects.create(
        action=action,
        user=user,
        ip_address=kwargs.get('ip_address'),
        user_agent=kwargs.get('user_agent'),
        success=kwargs.get('success', True),
    )

register_audit_integration(audit_logger)
```

### Backend - Custom notification sending

```python
# V apps/notification/apps.py
from sopira_magic.apps.authentification.integration.notification import register_notification_integration

def notification_sender(notification_type, data):
    if notification_type == 'login_notification':
        send_email(
            to=settings.ADMIN_EMAIL,
            subject='Login Notification',
            template='login_notification',
            context=data,
        )

register_notification_integration(notification_sender)
```

### Backend - Custom role provider

```python
# V apps/m_user/apps.py alebo apps/core/apps.py
from sopira_magic.apps.authentification.registry import register_role_provider
from sopira_magic.apps.m_user.models import UserPreference

def role_provider(user):
    role = UserPreference.role_for_user(user)
    return {
        'role': role,
        'role_display': UserPreference.UserRole(role).label,
        'role_priority': UserPreference.ROLE_PRIORITY.get(role, 0),
        'is_admin': UserPreference.user_is_admin(user),
        'is_superuser_role': UserPreference.user_is_superuser(user),
    }

register_role_provider(role_provider)
```

## Validácia

Po implementácii overiť:

1. ✅ Všetky endpoints sú config-driven (žiadny hardcode)
2. ✅ AUTH_CONFIG je SSOT pre všetky authentification nastavenia
3. ✅ AuthEngine používa konfiguráciu namiesto hardcoded logiky
4. ✅ Registry pattern funguje správne
5. ✅ Integrácia s audit modulom funguje
6. ✅ Integrácia s notification modulom funguje
7. ✅ Frontend AuthContext funguje správne
8. ✅ Všetky endpoints sú testovateľné a konfigurovateľné

## Poznámky

- **Žiadne hardcoded relations**: Všetky väzby sú riešené cez relation modul (config-driven)
- **Abstraktný prístup**: Všetky riešenia sú univerzálne, nie špecifické pre konkrétny use case
- **SSOT**: AUTH_CONFIG je single source of truth pre všetky authentification nastavenia
- **Registry pattern**: Custom logika je registrovaná cez registry, nie hardcoded

