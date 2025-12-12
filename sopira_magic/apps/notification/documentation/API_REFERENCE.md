# Notification Microservice - API Dokumentácia

**Verzia:** 1.0.0  
**Vytvorené:** 2025-12-12

---

## 📖 Obsah

1. [NotificationEngine API](#notificationengine-api)
2. [TemplateRenderer API](#templaterenderer-api)
3. [ScopeResolver API](#scoperesolver-api)
4. [Config Helper Functions](#config-helper-functions)
5. [Models API](#models-api)
6. [Integration API](#integration-api)

---

## NotificationEngine API

**Module:** `sopira_magic.apps.notification.engine`

### `NotificationEngine.send_notification(notification_type, context)`

Hlavná metóda pre odoslanie notifikácie. Orchestruje celý flow: resolve → render → send → log.

**Parameters:**
- `notification_type` (str): Notification type identifier z NOTIFICATION_CONFIG
- `context` (dict): Context data pre template rendering a recipient resolution

**Returns:**
- `dict`: Result dictionary
  ```python
  {
      'success': bool,        # True ak aspoň 1 email bol úspešne odoslaný
      'sent_count': int,      # Počet úspešne odoslaných emailov
      'failed_count': int,    # Počet failed emailov
      'recipients': list,     # Zoznam recipient email addresses
      'errors': list         # Zoznam error messages (ak nejaké)
  }
  ```

**Raises:**
- `Exception`: Ak nastane critical error (vracané v result['errors'])

**Example:**
```python
from sopira_magic.apps.notification.engine import NotificationEngine

result = NotificationEngine.send_notification(
    notification_type='login_notification',
    context={
        'user': user_object,
        'username': 'john_doe',
        'email': 'john@example.com',
        'ip_address': '192.168.1.1',
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'timestamp': '2025-12-12 10:00:00',
        'role': 'ADMIN',
    }
)

if result['success']:
    print(f"✅ Sent to {result['sent_count']} recipients")
else:
    print(f"❌ Failed: {result['errors']}")
```

**Flow:**
1. Skontroluje či je notification enabled v config
2. Resolve recipients (NotificationMatrix + ScopeResolver)
3. Render template (TemplateRenderer)
4. Odošle email cez SMTP (send_email)
5. Zaloguje výsledok (NotificationLog)

---

### `NotificationEngine.preview_notification(notification_type, sample_context=None)`

Preview notifikácie so sample data. Užitočné pre admin interface a debugging.

**Parameters:**
- `notification_type` (str): Notification type identifier
- `sample_context` (dict, optional): Sample context data. Ak None, použijú sa defaults.

**Returns:**
- `dict`: Preview data
  ```python
  {
      'subject': str,         # Rendered subject line
      'body': str,           # Rendered body (HTML or text)
      'recipients': list,    # Resolved recipient emails
      'config': dict,        # Notification config from NOTIFICATION_CONFIG
      'enabled': bool        # Či je notification enabled
  }
  ```
  Alebo pri errore:
  ```python
  {
      'error': str  # Error message
  }
  ```

**Example:**
```python
preview = NotificationEngine.preview_notification('login_notification')

print(f"Subject: {preview['subject']}")
print(f"Recipients: {preview['recipients']}")
print(f"Body (first 200 chars): {preview['body'][:200]}")
```

---

### `NotificationEngine.resolve_recipients(notification_type, context, config)`

Resolve recipient email addresses z NotificationMatrix a scope.

**Parameters:**
- `notification_type` (str): Notification type
- `context` (dict): Context data (obsahuje user object)
- `config` (dict): Notification config z NOTIFICATION_CONFIG

**Returns:**
- `list`: List of email addresses (validated)

**Example:**
```python
config = get_notification_config('login_notification')
recipients = NotificationEngine.resolve_recipients(
    notification_type='login_notification',
    context={'user': user},
    config=config
)
# ['admin@example.com', 'security@example.com']
```

**Logic:**
1. Pokúsi sa získať recipients z NotificationMatrix
2. Ak žiadne matrix entries, použije default_recipients z config
3. Aplikuje scope filtering (ak scope_aware)
4. Odstráni duplicity
5. Validuje email addresses

---

### `NotificationEngine.render_template(notification_type, context, config)`

Renderuje notification template (subject a body).

**Parameters:**
- `notification_type` (str): Notification type
- `context` (dict): Context data pre rendering
- `config` (dict): Notification config

**Returns:**
- `tuple`: `(subject, body)` obe ako strings

**Example:**
```python
subject, body = NotificationEngine.render_template(
    notification_type='login_notification',
    context={'username': 'john_doe', 'ip_address': '192.168.1.1'},
    config=get_notification_config('login_notification')
)
```

**Fallback:** Pri errore vráti fallback text s notification_type a context.

---

### `NotificationEngine.send_email(recipient, subject, body, notification_type, context)`

Odošle single email cez Django SMTP a zaloguje výsledok.

**Parameters:**
- `recipient` (str): Recipient email address
- `subject` (str): Email subject
- `body` (str): Email body (HTML or text)
- `notification_type` (str): Pre logging
- `context` (dict): Pre logging

**Returns:**
- `dict`: `{'success': bool, 'error': str}`

**Side Effects:**
- Vytvorí `NotificationLog` entry
- Odošle email cez `django.core.mail.send_mail`

**Example:**
```python
result = NotificationEngine.send_email(
    recipient='user@example.com',
    subject='Test Email',
    body='<h1>Test</h1>',
    notification_type='test',
    context={}
)
```

---

## TemplateRenderer API

**Module:** `sopira_magic.apps.notification.template_renderer`

### `TemplateRenderer.render(template_source, template_name, context, subject_template=None)`

Renderuje template podľa source type (database alebo file).

**Parameters:**
- `template_source` (str): 'database' alebo 'file'
- `template_name` (str): Template identifier (notification_type pre DB, filename pre file)
- `context` (dict): Context variables pre rendering
- `subject_template` (str, optional): Subject template string s {variables}

**Returns:**
- `tuple`: `(subject, body)`

**Raises:**
- `ValueError`: Ak template_source je invalid
- `NotificationTemplate.DoesNotExist`: Ak DB template neexistuje
- `TemplateDoesNotExist`: Ak file template neexistuje

**Example:**
```python
from sopira_magic.apps.notification.template_renderer import TemplateRenderer

# Database template
subject, body = TemplateRenderer.render(
    template_source='database',
    template_name='login_notification',
    context={'username': 'john', 'ip_address': '192.168.1.1'},
    subject_template='Login: {username}'
)

# File template
subject, body = TemplateRenderer.render(
    template_source='file',
    template_name='signup_welcome.html',
    context={'first_name': 'John', 'login_url': 'https://example.com/login'},
    subject_template='Welcome {first_name}!'
)
```

---

### `TemplateRenderer.preview_template(template_source, template_name, sample_context=None)`

Preview template so sample data.

**Parameters:**
- `template_source` (str): 'database' alebo 'file'
- `template_name` (str): Template identifier
- `sample_context` (dict, optional): Sample context (ak None, použije defaults)

**Returns:**
- `tuple`: `(subject, body)` s rendered sample data

**Example:**
```python
subject, body = TemplateRenderer.preview_template(
    template_source='database',
    template_name='login_notification'
)
print(f"Preview Subject: {subject}")
print(f"Preview Body:\n{body}")
```

**Default sample_context:**
```python
{
    'username': 'john_doe',
    'email': 'john@example.com',
    'first_name': 'John',
    'last_name': 'Doe',
    'ip_address': '192.168.1.1',
    'user_agent': 'Mozilla/5.0',
    'timestamp': '2025-12-12 10:00:00',
    'role': 'ADMIN',
    'login_url': 'https://example.com/login',
    'reset_url': 'https://example.com/reset/token123',
    'token_expiry': '24 hours',
}
```

---

### `TemplateRenderer.validate_template(template_source, template_name, required_variables)`

Validuje že template existuje a obsahuje required variables.

**Parameters:**
- `template_source` (str): 'database' alebo 'file'
- `template_name` (str): Template identifier
- `required_variables` (list): List of required variable names

**Returns:**
- `tuple`: `(is_valid, error_message)`
  - `is_valid` (bool): True ak template je valid
  - `error_message` (str or None): Error message ak invalid

**Example:**
```python
is_valid, error = TemplateRenderer.validate_template(
    template_source='database',
    template_name='login_notification',
    required_variables=['username', 'ip_address', 'timestamp']
)

if is_valid:
    print("✅ Template is valid")
else:
    print(f"❌ Template validation failed: {error}")
```

---

## ScopeResolver API

**Module:** `sopira_magic.apps.notification.scope_resolver`

### `ScopeResolver.get_scope_admins(user)`

Získa admin email addresses v user's scope.

**Parameters:**
- `user` (User): User object (scope owner)

**Returns:**
- `list`: List of admin email addresses

**Example:**
```python
from sopira_magic.apps.notification.scope_resolver import ScopeResolver

admins = ScopeResolver.get_scope_admins(current_user)
# ['admin1@example.com', 'admin2@example.com']
```

**Note:** Zatiaľ vracia všetkých adminov. Scope filtering bude pridaný po dokončení scoping registry.

---

### `ScopeResolver.filter_by_scope(recipients, user, scope_pattern='')`

Filtruje recipients podľa scope pattern.

**Parameters:**
- `recipients` (list): List of email addresses
- `user` (User): User object (scope owner)
- `scope_pattern` (str): Scope pattern (napr. 'same_company', 'same_factory')

**Returns:**
- `list`: Filtered list of email addresses

**Example:**
```python
filtered = ScopeResolver.filter_by_scope(
    recipients=['admin1@example.com', 'admin2@example.com'],
    user=current_user,
    scope_pattern='same_company'
)
```

**Note:** Scope filtering je zatiaľ v development. Ak scope_pattern je prázdny, vráti všetkých recipients.

---

### `ScopeResolver.resolve_recipients_from_matrix(notification_type, context, user=None)`

Resolve recipients z NotificationMatrix entries pre daný notification type.

**Parameters:**
- `notification_type` (str): Notification type identifier
- `context` (dict): Context data (obsahuje user, email, atď.)
- `user` (User, optional): User object pre scope resolution

**Returns:**
- `list`: List of resolved email addresses

**Example:**
```python
recipients = ScopeResolver.resolve_recipients_from_matrix(
    notification_type='login_notification',
    context={'user': user, 'email': 'user@example.com'},
    user=user
)
```

**Logic:**
1. Získa všetky enabled matrix entries pre notification_type
2. Pre každý entry:
   - `recipient_type='admin'` → pridá ADMIN_EMAIL z settings
   - `recipient_type='user'` → pridá user email z context
   - `recipient_type='scope_admins'` → pridá scope admins
   - `recipient_type='custom'` → pridá custom email z recipient_identifier
   - `recipient_type='role'` → pridá všetkých users s danou rolou
3. Odstráni duplicity
4. Aplikuje scope filtering
5. Validuje emails

---

### `ScopeResolver.get_default_admin_email()`

Získa default admin email z settings.

**Returns:**
- `str or None`: Admin email address

**Example:**
```python
admin_email = ScopeResolver.get_default_admin_email()
# 'sopira@me.com'
```

---

### `ScopeResolver.validate_email(email)`

Validuje email address format.

**Parameters:**
- `email` (str): Email address

**Returns:**
- `bool`: True ak valid, False otherwise

**Example:**
```python
is_valid = ScopeResolver.validate_email('test@example.com')  # True
is_valid = ScopeResolver.validate_email('invalid-email')     # False
```

---

### `ScopeResolver.filter_valid_emails(emails)`

Filtruje neplatné email addresses.

**Parameters:**
- `emails` (list): List of email addresses

**Returns:**
- `list`: List of valid email addresses

**Example:**
```python
valid = ScopeResolver.filter_valid_emails([
    'valid@example.com',
    'also-valid@test.com',
    'invalid',
    'test@'
])
# ['valid@example.com', 'also-valid@test.com']
```

---

## Config Helper Functions

**Module:** `sopira_magic.apps.notification.config`

### `get_notification_config(notification_type)`

**Parameters:**
- `notification_type` (str): Notification type identifier

**Returns:**
- `dict or None`: Notification config alebo None ak neexistuje

**Example:**
```python
from sopira_magic.apps.notification.config import get_notification_config

config = get_notification_config('login_notification')
# {
#     'enabled': True,
#     'channel': 'email',
#     'template_source': 'database',
#     ...
# }
```

---

### `is_notification_enabled(notification_type)`

**Parameters:**
- `notification_type` (str)

**Returns:**
- `bool`: True ak enabled

**Example:**
```python
from sopira_magic.apps.notification.config import is_notification_enabled

if is_notification_enabled('login_notification'):
    send_notification(...)
```

---

### `get_template_config(notification_type)`

**Returns:**
- `dict or None`: Template configuration

**Example:**
```python
from sopira_magic.apps.notification.config import get_template_config

template_config = get_template_config('login_notification')
# {
#     'template_source': 'database',
#     'template_name': 'login_notification',
#     'variables': ['username', 'email', ...],
#     'subject_template': '🔐 Login Notification - {username}'
# }
```

---

### `get_default_recipients(notification_type)`

**Returns:**
- `list`: List of recipient types ['admin', 'user', atď.]

---

### `is_scope_aware(notification_type)`

**Returns:**
- `bool`: True ak notification je scope-aware

---

### `get_all_notification_types()`

**Returns:**
- `list`: List of all notification type identifiers

**Example:**
```python
all_types = get_all_notification_types()
# ['login_notification', 'signup_notification_admin', 'signup_notification_user', ...]
```

---

## Models API

**Module:** `sopira_magic.apps.notification.models`

### NotificationTemplate

**Fields:**
- `name` (CharField): Human-readable name
- `notification_type` (CharField, unique): Identifier
- `template_source` (CharField): 'database' alebo 'file'
- `subject` (CharField): Subject template
- `body` (TextField): Body template (pre database templates)
- `variables` (JSONField): List of template variables
- `scope_aware` (BooleanField): Scope-aware flag
- `enabled` (BooleanField): Enabled flag
- `created`, `updated` (DateTimeField): Timestamps

**Manager Methods:**
```python
# Get enabled templates
NotificationTemplate.objects.filter(enabled=True)

# Get by notification_type
template = NotificationTemplate.objects.get(notification_type='login_notification')
```

---

### NotificationMatrix

**Fields:**
- `notification_type` (CharField): Notification type
- `recipient_type` (CharField): 'admin', 'user', 'scope_admins', 'custom', 'role'
- `recipient_identifier` (CharField): Email alebo role name
- `scope_pattern` (CharField): Scope pattern
- `conditions` (JSONField): Additional conditions
- `enabled` (BooleanField): Enabled flag

**Manager Methods:**
```python
# Get enabled entries pre notification type
matrix = NotificationMatrix.objects.filter(
    notification_type='login_notification',
    enabled=True
)
```

---

### NotificationLog

**Fields:**
- `notification_type` (CharField): Notification type
- `recipient_email` (EmailField): Recipient
- `status` (CharField): 'sent', 'failed', 'pending'
- `error_message` (TextField): Error message
- `template_used` (CharField): Template name
- `context_data` (JSONField): Context data
- `scope_identifier` (CharField): Scope ID
- `sent_at` (DateTimeField): When sent

**Manager Methods:**
```python
# Get failed notifications
failed = NotificationLog.objects.filter(status='failed')

# Get logs for notification type
logs = NotificationLog.objects.filter(notification_type='login_notification')

# Get recent logs
recent = NotificationLog.objects.order_by('-created')[:10]
```

---

## Integration API

**Module:** `sopira_magic.apps.notification.integration`

### `notification_handler(notification_type, data)`

Callback handler pre Auth module. Automaticky registrovaný cez `apps.py`.

**Parameters:**
- `notification_type` (str): Notification type
- `data` (dict): Context data z auth module

**Usage:**
Táto funkcia je automaticky volaná Auth modulom. Netreba volať manuálne.

**Triggered by:**
- Login event → `login_notification`
- Signup event → `signup_notification_admin`, `signup_notification_user`
- Password reset → `password_reset`
- Password change → `password_reset_confirm`

---

### `register_with_auth()`

Registruje notification handler s Auth modulom. Automaticky volaná v `apps.py ready()`.

**Usage:**
```python
from sopira_magic.apps.notification.integration import register_with_auth

# Called automatically on Django startup
register_with_auth()
```

---

## Error Handling

Všetky API metódy používajú konzistentný error handling:

**Success:**
```python
{
    'success': True,
    'sent_count': 1,
    'failed_count': 0,
    'recipients': ['user@example.com'],
    'errors': []
}
```

**Partial Failure:**
```python
{
    'success': True,  # Aspoň 1 email bol úspešný
    'sent_count': 2,
    'failed_count': 1,
    'recipients': ['user1@example.com', 'user2@example.com', 'user3@example.com'],
    'errors': ['user3@example.com: SMTP connection failed']
}
```

**Complete Failure:**
```python
{
    'success': False,
    'sent_count': 0,
    'failed_count': 3,
    'recipients': ['user1@example.com', 'user2@example.com'],
    'errors': ['SMTP server not configured', 'No valid recipients']
}
```

---

**Verzia:** 1.0.0  
**Posledná aktualizácia:** 2025-12-12

