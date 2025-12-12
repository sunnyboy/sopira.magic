# Notification Microservice - Implementačná Príručka

**Vytvorené:** 2025-12-12  
**Autor:** Michael (Sopira)  
**Status:** Production Ready  
**Verzia:** 1.0.0

---

## 📋 Obsah

1. [Úvod](#úvod)
2. [Architektúra](#architektúra)
3. [Inštalácia a Setup](#inštalácia-a-setup)
4. [Konfigurácia](#konfigurácia)
5. [Používanie](#používanie)
6. [API Reference](#api-reference)
7. [Management Commands](#management-commands)
8. [Admin Interface](#admin-interface)
9. [Troubleshooting](#troubleshooting)
10. [Best Practices](#best-practices)

---

## 🎯 Úvod

Notification Microservice je plne **ConfigDriven & SSOT (Single Source of Truth)** mikroslužba pre odosielanie emailových notifikácií v sopira.magic projekte.

### Kľúčové vlastnosti:

- ✅ **ConfigDriven** - všetko vychádza z `NOTIFICATION_CONFIG` (žiadny hardcode)
- ✅ **Hybrid Templates** - Database templates pre simple, File templates pre complex HTML
- ✅ **Scope-Aware** - integrácia so scoping modulom pre hierarchické permissions
- ✅ **Audit Trail** - každá notifikácia sa loguje do `NotificationLog`
- ✅ **Registry Pattern** - loose coupling s Auth modulom
- ✅ **Gmail SMTP** - production-ready email sending

### Podporované notification types:

1. **login_notification** - SA dostane info o prihlásení (scope-aware)
2. **signup_notification_admin** - SA dostane info o novom účte (scope-aware)
3. **signup_notification_user** - Nový user dostane welcome email (HTML)
4. **password_reset** - User dostane reset link (HTML)
5. **password_reset_confirm** - User dostane potvrdenie o zmene hesla

---

## 🏗️ Architektúra

### Vrstvy systému:

```
┌─────────────────────────────────────────────────────────────┐
│                     CONFIG LAYER (SSOT)                      │
│  NOTIFICATION_CONFIG - Single source of truth                │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                     DATABASE LAYER                           │
│  NotificationTemplate │ NotificationMatrix │ NotificationLog │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                     SERVICE LAYER                            │
│  NotificationEngine │ TemplateRenderer │ ScopeResolver       │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   INTEGRATION LAYER                          │
│  Auth Integration (Registry Callback)                        │
└─────────────────────────────────────────────────────────────┘
```

### Flow diagram:

```
Auth Module
    ↓
Registry Callback
    ↓
NotificationEngine.send_notification()
    ↓
┌───────────────────┐
│ 1. Check Config   │ → NOTIFICATION_CONFIG
│ 2. Resolve        │ → NotificationMatrix + ScopeResolver
│ 3. Render         │ → TemplateRenderer (DB or File)
│ 4. Send           │ → Gmail SMTP
│ 5. Log            │ → NotificationLog
└───────────────────┘
```

---

## 🚀 Inštalácia a Setup

### 1. Migrations

```bash
cd /Users/sopira/sopira.magic/version_01
source venv/bin/activate

# Vytvor migrations
python manage.py makemigrations notification

# Aplikuj migrations
python manage.py migrate notification
```

### 2. Inicializácia templates a matrix

```bash
# Vytvor NotificationTemplate objekty z config
python manage.py init_notification_templates

# Vytvor NotificationMatrix entries z config
python manage.py init_notification_matrix

# Vyplň database template content
python manage.py init_database_templates
```

### 3. Gmail SMTP Configuration

Pridaj do `.env.local`:

```bash
# Email Configuration (Gmail SMTP)
EMAIL_HOST_USER=tvoj-email@gmail.com
EMAIL_HOST_PASSWORD=tvoje-app-password-tu
ADMIN_EMAIL=sopira@me.com
```

**Ako získať Gmail App Password:**

1. Zapni 2-Step Verification: https://myaccount.google.com/security
2. Vytvor App Password: https://myaccount.google.com/apppasswords
3. Zvol "Mail" → "Other" → "Sopira Magic"
4. Skopíruj 16-znakové heslo (bez medzier)

### 4. Reštart Django servera

```bash
# Zastaviť existujúci server (Ctrl+C)
# Spustiť znovu (načíta nové env vars)
python manage.py runserver
```

### 5. Verifikácia

```bash
# Test preview (bez odoslania)
python manage.py test_notification login_notification --preview

# Test real send
python manage.py test_notification login_notification --email test@example.com
```

---

## ⚙️ Konfigurácia

### NOTIFICATION_CONFIG (SSOT)

Umiestnenie: `sopira_magic/apps/notification/config.py`

```python
NOTIFICATION_CONFIG = {
    'smtp': {
        'backend': 'smtp',
        'enabled': True,
    },
    'notification_types': {
        'login_notification': {
            'enabled': True,
            'channel': 'email',
            'template_source': 'database',
            'template_name': 'login_notification',
            'scope_aware': True,
            'default_recipients': ['admin'],
            'subject_template': '🔐 Login Notification - {username}',
            'variables': ['username', 'email', 'ip_address', 'user_agent', 'timestamp', 'role'],
        },
        # ... ďalšie notification types
    },
}
```

### Pridanie nového notification type:

1. **Pridaj do `NOTIFICATION_CONFIG`:**

```python
'my_new_notification': {
    'enabled': True,
    'channel': 'email',
    'template_source': 'database',  # alebo 'file'
    'template_name': 'my_new_notification',
    'scope_aware': False,
    'default_recipients': ['user'],
    'subject_template': 'My Subject - {variable}',
    'variables': ['variable', 'another_variable'],
},
```

2. **Spusti init commands:**

```bash
python manage.py init_notification_templates --force
python manage.py init_notification_matrix --force
```

3. **Ak je `template_source: 'database'`, vyplň body:**

Cez Django admin alebo cez management command.

4. **Ak je `template_source: 'file'`, vytvor HTML template:**

```bash
# Vytvor súbor:
templates/notifications/my_new_notification.html
```

---

## 💻 Používanie

### Základné použitie:

```python
from sopira_magic.apps.notification.engine import NotificationEngine

# Odoslať notifikáciu
result = NotificationEngine.send_notification(
    notification_type='login_notification',
    context={
        'user': user_object,
        'username': 'john_doe',
        'email': 'john@example.com',
        'ip_address': '192.168.1.1',
        'user_agent': 'Mozilla/5.0',
        'timestamp': '2025-12-12 10:00:00',
        'role': 'ADMIN',
    }
)

# Výsledok
print(result)
# {
#     'success': True,
#     'sent_count': 1,
#     'failed_count': 0,
#     'recipients': ['admin@example.com'],
#     'errors': []
# }
```

### Preview notifikácie:

```python
from sopira_magic.apps.notification.engine import NotificationEngine

preview = NotificationEngine.preview_notification(
    notification_type='login_notification',
    sample_context={'username': 'test_user'}
)

print(preview['subject'])  # Subject line
print(preview['body'])     # Rendered body
print(preview['recipients'])  # Resolved recipients
```

### Manuálne odoslanie emailu:

```python
from sopira_magic.apps.notification.engine import NotificationEngine

result = NotificationEngine.send_email(
    recipient='user@example.com',
    subject='Test Subject',
    body='<h1>Test Body</h1>',
    notification_type='test',
    context={}
)
```

---

## 📚 API Reference

### NotificationEngine

**Hlavné metódy:**

#### `send_notification(notification_type, context)`

Odošle notifikáciu.

**Args:**
- `notification_type` (str): Notification type z NOTIFICATION_CONFIG
- `context` (dict): Context data pre template rendering

**Returns:**
- dict: `{'success': bool, 'sent_count': int, 'failed_count': int, 'recipients': list, 'errors': list}`

**Example:**
```python
result = NotificationEngine.send_notification(
    notification_type='signup_notification_user',
    context={
        'user': user,
        'first_name': 'John',
        'username': 'john_doe',
        'email': 'john@example.com',
        'login_url': 'https://example.com/login'
    }
)
```

#### `preview_notification(notification_type, sample_context=None)`

Preview notifikácie so sample data.

**Args:**
- `notification_type` (str): Notification type
- `sample_context` (dict, optional): Sample context data

**Returns:**
- dict: `{'subject': str, 'body': str, 'recipients': list, 'config': dict, 'enabled': bool}`

#### `resolve_recipients(notification_type, context, config)`

Resolve recipients z matrix a scope.

**Returns:**
- list: Email addresses

#### `render_template(notification_type, context, config)`

Renderuje template.

**Returns:**
- tuple: `(subject, body)`

#### `send_email(recipient, subject, body, notification_type, context)`

Odošle single email a zaloguje.

**Returns:**
- dict: `{'success': bool, 'error': str}`

---

### TemplateRenderer

**Hlavné metódy:**

#### `render(template_source, template_name, context, subject_template=None)`

Renderuje template podľa source type.

**Args:**
- `template_source` (str): 'database' alebo 'file'
- `template_name` (str): Template name/identifier
- `context` (dict): Context data
- `subject_template` (str, optional): Subject template string

**Returns:**
- tuple: `(subject, body)`

**Example:**
```python
from sopira_magic.apps.notification.template_renderer import TemplateRenderer

subject, body = TemplateRenderer.render(
    template_source='database',
    template_name='login_notification',
    context={'username': 'john'},
    subject_template='Login: {username}'
)
```

#### `preview_template(template_source, template_name, sample_context=None)`

Preview template so sample data.

#### `validate_template(template_source, template_name, required_variables)`

Validuje template.

**Returns:**
- tuple: `(is_valid, error_message)`

---

### ScopeResolver

**Hlavné metódy:**

#### `get_scope_admins(user)`

Získa admin emails v user scope.

**Returns:**
- list: Admin email addresses

#### `filter_by_scope(recipients, user, scope_pattern='')`

Filtruje recipients podľa scope.

#### `resolve_recipients_from_matrix(notification_type, context, user=None)`

Resolve recipients z NotificationMatrix.

**Returns:**
- list: Email addresses

#### `filter_valid_emails(emails)`

Filtruje neplatné email addresses.

**Returns:**
- list: Valid email addresses

---

### Config Helper Functions

```python
from sopira_magic.apps.notification.config import (
    get_notification_config,
    is_notification_enabled,
    get_template_config,
    get_default_recipients,
    is_scope_aware,
    get_all_notification_types,
)

# Získať config pre notification type
config = get_notification_config('login_notification')

# Skontrolovať či je enabled
if is_notification_enabled('login_notification'):
    # Send notification
    pass

# Získať template config
template_config = get_template_config('login_notification')

# Získať default recipients
recipients = get_default_recipients('login_notification')  # ['admin']

# Skontrolovať scope-aware
if is_scope_aware('login_notification'):
    # Apply scope filtering
    pass

# Zoznam všetkých notification types
all_types = get_all_notification_types()
```

---

## 🛠️ Management Commands

### init_notification_templates

Inicializuje NotificationTemplate objekty z NOTIFICATION_CONFIG.

```bash
# Vytvor nové templates
python manage.py init_notification_templates

# Force update existujúcich
python manage.py init_notification_templates --force
```

### init_notification_matrix

Inicializuje NotificationMatrix entries z NOTIFICATION_CONFIG.

```bash
# Vytvor nové matrix entries
python manage.py init_notification_matrix

# Force recreate existujúcich
python manage.py init_notification_matrix --force
```

### init_database_templates

Vyplní body content pre database templates.

```bash
# Vyplň template content
python manage.py init_database_templates

# Force overwrite existujúceho
python manage.py init_database_templates --force
```

### test_notification

Testuje odosielanie notifikácií.

```bash
# List všetkých notification types
python manage.py test_notification --list

# Preview notification (bez odoslania)
python manage.py test_notification login_notification --preview

# Send test notification
python manage.py test_notification login_notification

# Send na vlastný email
python manage.py test_notification login_notification --email test@example.com
```

---

## 👨‍💼 Admin Interface

### Prístup:

```
http://localhost:8000/admin/notification/
```

### NotificationTemplate Admin

**Features:**
- Preview template s sample data
- Test send (preview only)
- Enable/disable templates
- Edit template content (pre database templates)

**Actions:**
- Preview selected templates
- Test send
- Enable selected templates
- Disable selected templates

### NotificationMatrix Admin

**Features:**
- Manage communication matrix
- Define kto dostane aké notifikácie
- Scope patterns
- Conditions (JSON)

**Actions:**
- Enable selected entries
- Disable selected entries

### NotificationLog Admin

**Features:**
- View audit trail
- Filter by notification type, status, date
- Search by recipient email
- **Read-only** (cannot add/delete)

**Filters:**
- Notification type
- Status (sent, failed, pending)
- Created date

---

## 🐛 Troubleshooting

### Problém: Email sa neodosiela

**Symptóm:** `test_notification` zlyhá s SMTP errorom.

**Riešenie:**
1. Over EMAIL credentials v `.env.local`:
   ```bash
   echo $EMAIL_HOST_USER
   echo $EMAIL_HOST_PASSWORD
   ```
2. Reštartuj Django server (aby načítal env vars)
3. Over Gmail App Password (nie normálne heslo!)
4. Skontroluj firewall/network connection

**Debug:**
```bash
# Test SMTP connection
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Test body', 'from@example.com', ['to@example.com'])
```

---

### Problém: Template not found

**Symptóm:** `TemplateDoesNotExist: notifications/signup_welcome.html`

**Riešenie:**
1. Over že template existuje:
   ```bash
   ls -la /Users/sopira/sopira.magic/version_01/templates/notifications/
   ```
2. Over `TEMPLATES['DIRS']` v `settings.py`:
   ```python
   TEMPLATES = [{
       'DIRS': [BASE_DIR / 'templates'],
   }]
   ```
3. Reštartuj Django server

---

### Problém: No recipients found

**Symptóm:** Notifikácia sa neodošle, `recipients: []`

**Riešenie:**
1. Over NotificationMatrix entries:
   ```bash
   python manage.py shell
   >>> from sopira_magic.apps.notification.models import NotificationMatrix
   >>> NotificationMatrix.objects.filter(notification_type='login_notification', enabled=True)
   ```
2. Over že ADMIN_EMAIL je nastavený v `.env.local`
3. Pre user notifications over že user má email:
   ```python
   >>> user.email  # Nesmie byť prázdne
   ```

---

### Problém: Template rendering failed

**Symptóm:** Database template sa nezobrazi správne.

**Riešenie:**
1. Over že template má vyplnený `body`:
   ```bash
   python manage.py shell
   >>> from sopira_magic.apps.notification.models import NotificationTemplate
   >>> t = NotificationTemplate.objects.get(notification_type='login_notification')
   >>> print(t.body)
   ```
2. Spusti `init_database_templates`:
   ```bash
   python manage.py init_database_templates --force
   ```
3. Over template syntax (Django template tags):
   ```django
   {{ username }} ✓
   {username} ✗
   ```

---

### Problém: Scope-aware nefunguje

**Symptóm:** Scope admins nedostávajú notifikácie.

**Riešenie:**
1. Over že notification type má `scope_aware: True` v NOTIFICATION_CONFIG
2. Over že matrix entry má `scope_pattern` vyplnený
3. Scope integration je zatiaľ v development fáze - používa sa fallback na všetkých adminov

---

## ✨ Best Practices

### 1. ConfigDriven Development

**DO:**
```python
# Všetko cez config
config = get_notification_config('my_notification')
if config.get('enabled'):
    send_notification(...)
```

**DON'T:**
```python
# Hardcoded logic
if notification_type == 'login_notification':
    send_to_admin(...)
```

---

### 2. Error Handling

**DO:**
```python
try:
    result = NotificationEngine.send_notification(...)
    if not result['success']:
        logger.error(f"Notification failed: {result['errors']}")
except Exception as e:
    logger.error(f"Critical error: {e}")
```

**DON'T:**
```python
# Silent failures
NotificationEngine.send_notification(...)
```

---

### 3. Context Data

**DO:**
```python
context = {
    'user': user,  # Include user object
    'username': user.username,  # Include all template variables
    'email': user.email,
    'timestamp': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
}
```

**DON'T:**
```python
context = {
    'user': user  # Missing template variables
}
```

---

### 4. Template Variables

**DO:**
```python
# Define všetky variables v NOTIFICATION_CONFIG
'variables': ['username', 'email', 'ip_address', 'timestamp']

# Use v template
{{ username }} - {{ email }}
```

**DON'T:**
```python
# Použiť nedeklarované variables
{{ undefined_variable }}  # Crashes
```

---

### 5. Testing

**DO:**
```bash
# Vždy najprv preview
python manage.py test_notification my_notification --preview

# Potom test send
python manage.py test_notification my_notification --email test@example.com
```

**DON'T:**
```bash
# Send priamo do production bez testovania
```

---

### 6. Security

**DO:**
```bash
# Používaj App Password, nie regular password
EMAIL_HOST_PASSWORD=app-password-16-chars

# Never commit credentials
# Add to .gitignore: .env.local
```

**DON'T:**
```bash
# Hardcoded credentials v kóde
EMAIL_HOST_PASSWORD="mypassword123"  # ✗
```

---

### 7. Audit Logging

**DO:**
```python
# NotificationLog sa vytvára automaticky
# Používaj na debugging:
from sopira_magic.apps.notification.models import NotificationLog
logs = NotificationLog.objects.filter(status='failed')
```

**DON'T:**
```python
# Ignorovať failed notifications
```

---

### 8. HTML Templates

**DO:**
```html
<!-- Responsive design -->
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<!-- Inline CSS (email clients) -->
<style>body { font-family: sans-serif; }</style>
```

**DON'T:**
```html
<!-- External CSS (nefunguje v email clients) -->
<link rel="stylesheet" href="style.css">
```

---

## 📞 Support

**Kontakt:** Michael (Sopira)  
**Email:** sopira@me.com  
**Projekt:** Sopira Magic  
**Repository:** ~/sopira.magic/version_01

---

**Verzia dokumentácie:** 1.0.0  
**Posledná aktualizácia:** 2025-12-12  
**Status:** ✅ Production Ready

