# Notification Microservice - README

**ConfigDriven & SSOT Notification Mikroslužba pre Sopira Magic**

---

## 🎯 Čo je to?

Plne konfigurovateľná mikroslužba pre odosielanie emailových notifikácií s:
- ✅ Gmail SMTP integráciou
- ✅ Hybrid template system (Database + HTML files)
- ✅ Scope-aware recipient resolution
- ✅ Audit logging
- ✅ Auth module integration

---

## 🚀 Quick Start

```bash
# 1. Pridaj Gmail credentials do .env.local
EMAIL_HOST_USER=tvoj-email@gmail.com
EMAIL_HOST_PASSWORD=app-password-16-chars
ADMIN_EMAIL=sopira@me.com

# 2. Reštartuj Django server

# 3. Test
python manage.py test_notification login_notification --preview
```

**Viac info:** [`QUICKSTART.md`](QUICKSTART.md)

---

## 📚 Dokumentácia

| Dokument | Popis |
|----------|-------|
| [`QUICKSTART.md`](QUICKSTART.md) | 5-minútový quick start guide |
| [`SCOPING_QUICKREF.md`](SCOPING_QUICKREF.md) | **NOVÉ!** Quick reference card pre scoping |
| [`FAQ_AND_EXAMPLES.md`](FAQ_AND_EXAMPLES.md) | FAQ a príklady Auth integration |
| [`SCOPING_INTEGRATION.md`](SCOPING_INTEGRATION.md) | **NOVÉ!** Scoping callbacks implementácia |
| [`IMPLEMENTATION_GUIDE.md`](IMPLEMENTATION_GUIDE.md) | Kompletná implementačná príručka |
| [`API_REFERENCE.md`](API_REFERENCE.md) | API dokumentácia |
| [`ARCHITECTURE_PLAN.md`](ARCHITECTURE_PLAN.md) | Architektúra a plán |

---

## 🏗️ Architektúra

```
Config Layer (SSOT)
    ↓
Database Layer (Models)
    ↓
Service Layer (Engine, Renderer, Resolver)
    ↓
Integration Layer (Auth)
```

**Kľúčové komponenty:**
- **NotificationEngine** - orchestrátor
- **TemplateRenderer** - hybrid templates
- **ScopeResolver** - scope-aware recipients
- **NOTIFICATION_CONFIG** - SSOT konfigurácia

---

## 💻 Základné použitie

```python
from sopira_magic.apps.notification.engine import NotificationEngine

result = NotificationEngine.send_notification(
    notification_type='login_notification',
    context={
        'user': user,
        'username': user.username,
        'email': user.email,
        'ip_address': '192.168.1.1',
        'timestamp': '2025-12-12 10:00:00',
    }
)

if result['success']:
    print(f"✅ Sent to {result['sent_count']} recipients")
```

---

## 📧 Notification Types

1. **login_notification** - SA info o prihlásení (DB template, scope-aware)
2. **signup_notification_admin** - SA info o novom účte (DB template, scope-aware)
3. **signup_notification_user** - Welcome email pre usera (HTML file)
4. **password_reset** - Password reset link (HTML file)
5. **password_reset_confirm** - Potvrdenie zmeny hesla (DB template)

---

## 🛠️ Management Commands

```bash
# List notification types
python manage.py test_notification --list

# Preview
python manage.py test_notification login_notification --preview

# Test send
python manage.py test_notification login_notification --email test@example.com

# Init z config
python manage.py init_notification_templates
python manage.py init_notification_matrix
python manage.py init_database_templates
```

---

## 👨‍💼 Admin Interface

```
http://localhost:8000/admin/notification/
```

- **NotificationTemplate** - edit templates, preview, test
- **NotificationMatrix** - configure recipients
- **NotificationLog** - audit trail (read-only)

---

## 🔧 Konfigurácia

### NOTIFICATION_CONFIG (SSOT)

`sopira_magic/apps/notification/config.py`

```python
NOTIFICATION_CONFIG = {
    'notification_types': {
        'login_notification': {
            'enabled': True,
            'template_source': 'database',
            'scope_aware': True,
            'default_recipients': ['admin'],
            # ...
        },
    },
}
```

### Pridať nový notification type:

1. Pridaj do `NOTIFICATION_CONFIG`
2. Spusti `python manage.py init_notification_templates --force`
3. Vytvor template (DB alebo file)
4. Test: `python manage.py test_notification my_type --preview`

---

## 📊 Files & Structure

```
sopira_magic/apps/notification/
├── config.py              # SSOT configuration
├── engine.py              # NotificationEngine
├── template_renderer.py   # TemplateRenderer
├── scope_resolver.py      # ScopeResolver
├── integration.py         # Auth integration
├── models.py              # Database models
├── admin.py               # Admin interface
├── apps.py                # App config
├── management/commands/   # Management commands
│   ├── init_notification_templates.py
│   ├── init_notification_matrix.py
│   ├── init_database_templates.py
│   └── test_notification.py
└── documentation/         # Documentation
    ├── README.md
    ├── QUICKSTART.md
    ├── IMPLEMENTATION_GUIDE.md
    ├── API_REFERENCE.md
    └── ARCHITECTURE_PLAN.md

templates/notifications/
├── signup_welcome.html    # HTML welcome email
└── password_reset.html    # HTML reset email
```

---

## ✅ Status

**Verzia:** 1.0.0  
**Status:** ✅ Production Ready  
**Vytvorené:** 2025-12-12  
**Autor:** Michael (Sopira)

### Čo funguje:

- ✅ Gmail SMTP sending
- ✅ Database templates
- ✅ File templates (HTML)
- ✅ Recipient resolution
- ✅ Scope-aware routing (partial)
- ✅ Audit logging
- ✅ Auth integration
- ✅ Admin interface
- ✅ Management commands
- ✅ Testing tools

### V development:

- ~~🚧 Full scope integration (čaká na scoping registry callbacks)~~ → ✅ **DONE!**
- 🚧 SMS/Push notifications (budúca features)

---

## 🤝 Support

**Kontakt:** Michael (Sopira)  
**Email:** sopira@me.com  
**Projekt:** Sopira Magic  
**Path:** `/Users/sopira/sopira.magic/version_01/sopira_magic/apps/notification`

---

## 📝 License

Internal project - Sopira Magic  
© 2025 Michael (Sopira)

