# Notification Microservice - FAQ & Integration Examples

**Verzia:** 2.0.0  
**Vytvorené:** 2025-12-12  
**Updated:** 2025-12-12 - Scoping callbacks COMPLETE

---

## ❓ FAQ - Často Kladené Otázky

### 1. Scope Integration - Čo chýba pre plnú funkcionalitu?

**Otázka:** *"Píšeš že scope integration je pripravená, ale plná implementácia bude po dokončení scoping registry callbacks. Čo stojí v ceste dokončiť registry callbacks?"*

**Odpoveď:** ✅ **DOKONČENÉ!** (2025-12-12)

Scoping registry callbacks sú **plne implementované** v `sopira_magic/apps/core/apps.py`.

#### ✅ Čo je implementované:

1. **`role_provider`** - Mapovanie User.role → scoping roles
   - SUPERADMIN → superuser (full access)
   - ADMIN → admin (company scope)  
   - STAFF → staff (factory scope)
   - EDITOR/READER/ADHOC → príslušné roles

2. **`scope_provider`** - Resolution scope values pre 3 levely:
   - Level 0: User (user.id) 
   - Level 1: Company (company.id) via relation system
   - Level 2: Factory (factory.id) via company hierarchy

3. **Helper functions** - get_all_scope_values, get_selected_scope, get_accessible_scope, etc.

4. **Integration** s mystate SavedState (selected scope) a relation system (accessible scope)

#### 📖 Dokumentácia:

Pre detailnú dokumentáciu pozri: [`SCOPING_INTEGRATION.md`](SCOPING_INTEGRATION.md)

#### ✅ Verifikácia:

```bash
python manage.py check

# Expected output:
# [INFO] ✅ Scoping registry callbacks registered (FULL IMPLEMENTATION)
# [INFO] Scoping engine validation completed
# System check identified no issues (0 silenced).
```

**Status:** PRODUCTION READY 🚀

---

### 2. Auth Integration - Automatické notifikácie

**Otázka:** *"Píšeš že Auth integration je automatická - stačí použiť auth endpoints a notifikácie sa odosielajú samy. Uveď mi na to príklad."*

**Odpoveď:** ✅ **Plne funkčné!**

Auth integration využíva **registry pattern** - Auth modul "volá" notification modul cez callback.

#### Ako to funguje:

```
User Login (Auth endpoint)
    ↓
Auth modul trigger event: 'login_notification'
    ↓
Notification registry callback: notification_handler()
    ↓
NotificationEngine.send_notification()
    ↓
Email sent ✅
```

---

## 🔌 Integration Examples

### Example 1: Login Notification (AUTOMATICKÉ)

**User sa prihlási:**

```bash
POST /api/auth/login/
{
  "username": "john_doe",
  "password": "secret123"
}
```

**Čo sa deje:**

1. `authentification` modul overí credentials
2. Auth modul zavolá `trigger_notification('login_notification', data)`
3. Notification registry callback sa spustí
4. `NotificationEngine.send_notification()` odošle email
5. Admin dostane email: "🔐 User john_doe sa prihlásil"

**Kód (Auth modul):**

```python
# sopira_magic/apps/authentification/views.py

from .integration.notification import trigger_notification

class LoginView(APIView):
    def post(self, request):
        # ... authenticate user ...
        
        # Trigger notification automatically
        trigger_notification('login_notification', {
            'user': user,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'timestamp': timezone.now(),
            'ip_address': request.META.get('REMOTE_ADDR', 'unknown'),
        })
        
        return Response({'token': token})
```

**Notification modul (listener):**

```python
# sopira_magic/apps/notification/integration.py

def notification_handler(notification_type: str, data: Dict):
    """Callback called by Auth module."""
    from .engine import NotificationEngine
    NotificationEngine.send_notification(notification_type, data)

# Registered in apps.py ready()
register_with_auth()  # Registers notification_handler with auth registry
```

**Výsledok:**

✅ Email odoslaný na `ADMIN_EMAIL` (sopira@me.com)  
✅ Log v `NotificationLog`  
✅ Zero hardcoding - plne config-driven

---

### Example 2: Signup Notification (AUTOMATICKÉ)

**Admin vytvorí nový account:**

```bash
POST /api/auth/signup/
{
  "username": "new_user",
  "email": "new@example.com",
  "password": "pass123",
  "first_name": "New",
  "last_name": "User"
}
```

**Čo sa deje:**

1. User je vytvorený
2. Auth modul trigger 2 notifikácie:
   - `signup_notification_admin` → email pre SA
   - `signup_notification_user` → welcome email pre usera
3. Obe sa odošlú automaticky

**Kód:**

```python
# sopira_magic/apps/authentification/views.py

class SignupView(APIView):
    def post(self, request):
        user = User.objects.create_user(...)
        
        # Notify admin
        trigger_notification('signup_notification_admin', {
            'user': user,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'created_at': user.date_joined,
        })
        
        # Notify user (welcome email)
        trigger_notification('signup_notification_user', {
            'user': user,
            'first_name': user.first_name,
            'username': user.username,
            'email': user.email,
            'login_url': f"{settings.FRONTEND_URL}/login",
        })
        
        return Response({'success': True})
```

**Výsledok:**

✅ Admin dostane notifikáciu: "📢 Nový account vytvorený: new_user"  
✅ User dostane welcome email s login URL  
✅ Všetko scope-aware - notifikácie idú len relevantným adminom

---

### Example 3: Password Reset (AUTOMATICKÉ)

**User zabudol heslo:**

```bash
POST /api/auth/password-reset/
{
  "email": "john@example.com"
}
```

**Čo sa deje:**

1. Auth modul vygeneruje reset token
2. Trigger `password_reset` notifikáciu
3. User dostane email s reset linkom

**Kód:**

```python
# sopira_magic/apps/authentification/views.py

class PasswordResetView(APIView):
    def post(self, request):
        user = User.objects.get(email=request.data['email'])
        token = generate_reset_token(user)
        
        # Trigger notification
        trigger_notification('password_reset', {
            'user': user,
            'username': user.username,
            'email': user.email,
            'reset_url': f"{settings.FRONTEND_URL}/reset-password?token={token}",
            'token_expiry': '24 hours',
        })
        
        return Response({'success': True})
```

**Výsledok:**

✅ User dostane email: "🔑 Reset Password - Click here: [link]"  
✅ Token expiry info v emaile  
✅ Professional HTML email template

---

## 🔧 Ako to funguje pod kapotou?

### Registry Pattern

```python
# sopira_magic/apps/authentification/integration/notification.py

# Registry (storage pre callback)
_notification_callback = None

def register_notification_integration(callback):
    """Register notification callback."""
    global _notification_callback
    _notification_callback = callback
    logger.info("Notification sender registered")

def trigger_notification(notification_type: str, data: Dict):
    """Trigger notification via registered callback."""
    if _notification_callback:
        _notification_callback(notification_type, data)
    else:
        logger.warning(f"No notification callback registered for: {notification_type}")
```

```python
# sopira_magic/apps/notification/integration.py

def notification_handler(notification_type: str, data: Dict):
    """Handle notification trigger from auth module."""
    from .engine import NotificationEngine
    NotificationEngine.send_notification(notification_type, data)

def register_with_auth():
    """Register notification handler with auth module."""
    from sopira_magic.apps.authentification.integration.notification import register_notification_integration
    register_notification_integration(notification_handler)
```

```python
# sopira_magic/apps/notification/apps.py

class NotificationConfig(AppConfig):
    def ready(self):
        # Auto-register on Django startup
        from .integration import register_with_auth
        register_with_auth()
```

### Flow Diagram

```
Django Startup
    ↓
NotificationConfig.ready()
    ↓
register_with_auth()
    ↓
Auth registry stores notification_handler callback
    ↓
─────────────────────────────────────────────────────────
Runtime - User Login
    ↓
Auth endpoint called
    ↓
trigger_notification('login_notification', data)
    ↓
_notification_callback(notification_type, data)  ← calls registered handler
    ↓
notification_handler() in Notification module
    ↓
NotificationEngine.send_notification()
    ↓
1. Check config (enabled?)
2. Resolve recipients (matrix + scope)
3. Render template
4. Send email via SMTP
5. Log result
    ↓
✅ Email delivered
```

---

## ✅ Verifikácia

### Test 1: Check Registry

```bash
python manage.py shell

from sopira_magic.apps.authentification.integration.notification import trigger_notification

# Test trigger
trigger_notification('login_notification', {
    'username': 'test',
    'email': 'test@example.com'
})

# Check logs:
# [INFO] Notification integration registered
# [INFO] Sending notification: login_notification
```

### Test 2: Test Management Command

```bash
python manage.py test_notification login_notification --preview

# Expected:
# ✓ Enabled: True
# ✓ Recipients: ['sopira@me.com']
# ✓ Subject: 🔐 Login Notification - test_user
# Body preview: ...
```

### Test 3: Real Auth Endpoint

```bash
# Start server
python manage.py runserver

# Login via API
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "sopira", "password": "sopirapass"}'

# Check email inbox (sopira@me.com)
# → Should receive "🔐 Login Notification"
```

---

## 🎯 Summary

### ✅ Čo funguje automaticky:

1. **Login notification** - Každý login → email pre SA
2. **Signup notification** - Nový account → 2 emaily (SA + user)
3. **Password reset** - Forgot password → email s reset linkom

### 🔑 Key Features:

- **Zero Configuration** - Auto-registrácia pri Django startup
- **Scope-Aware** - Notifikácie len pre relevantných adminov
- **Config-Driven** - Všetko cez `NOTIFICATION_CONFIG`
- **Template System** - Database + File templates
- **Auditing** - Všetko logované v `NotificationLog`
- **Robust** - Fallback strategies, error handling

### 📖 Related Docs:

- [`SCOPING_INTEGRATION.md`](SCOPING_INTEGRATION.md) - Scoping callbacks
- [`IMPLEMENTATION_GUIDE.md`](IMPLEMENTATION_GUIDE.md) - Setup guide
- [`API_REFERENCE.md`](API_REFERENCE.md) - API docs

---

**Verzia:** 2.0.0  
**Status:** ✅ PRODUCTION READY 🚀  
**Last Updated:** 2025-12-12
