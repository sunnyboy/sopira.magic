# Notification Microservice - Quick Start Guide

**Začni tu!** 🚀

---

## 5-minútový Quick Start

### 1️⃣ Gmail Setup (2 minúty)

1. **Vytvor App Password:**
   - Choď na: https://myaccount.google.com/apppasswords
   - Zvol "Mail" → "Other (Custom name)" → "Sopira Magic"
   - Klikni "Generate"
   - Skopíruj 16-znakové heslo (napr. `abcdefghijklmnop`)

2. **Pridaj do `.env.local`:**
   ```bash
   # Email Configuration (Gmail SMTP)
   EMAIL_HOST_USER=tvoj-email@gmail.com
   EMAIL_HOST_PASSWORD=abcdefghijklmnop
   ADMIN_EMAIL=sopira@me.com
   ```

3. **Reštartuj Django server** (Ctrl+C a znovu spusti)

---

### 2️⃣ Test (3 minúty)

```bash
cd /Users/sopira/sopira.magic/version_01
source venv/bin/activate

# Preview test (bez odoslania)
python manage.py test_notification login_notification --preview

# Real send test
python manage.py test_notification login_notification --email tvoj-email@gmail.com
```

**Hotovo!** ✅ Ak dostaneš email, všetko funguje!

---

## Základné použitie

### Odoslať notifikáciu z kódu:

```python
from sopira_magic.apps.notification.engine import NotificationEngine

# Login notification
NotificationEngine.send_notification(
    notification_type='login_notification',
    context={
        'user': user,
        'username': user.username,
        'email': user.email,
        'ip_address': request.META.get('REMOTE_ADDR'),
        'user_agent': request.META.get('HTTP_USER_AGENT'),
        'timestamp': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
        'role': user.role,
    }
)
```

---

## Dostupné notification types:

1. **`login_notification`** - SA dostane info o prihlásení
2. **`signup_notification_admin`** - SA dostane info o novom účte
3. **`signup_notification_user`** - User dostane welcome email
4. **`password_reset`** - User dostane reset link
5. **`password_reset_confirm`** - User dostane potvrdenie zmeny hesla

---

## Management Commands

```bash
# List všetkých notification types
python manage.py test_notification --list

# Preview notification
python manage.py test_notification signup_notification_user --preview

# Test send
python manage.py test_notification login_notification --email test@example.com

# Init templates/matrix z config
python manage.py init_notification_templates
python manage.py init_notification_matrix
python manage.py init_database_templates
```

---

## Admin Interface

```
http://localhost:8000/admin/notification/
```

- **NotificationTemplate** - upraviť templates, preview, test send
- **NotificationMatrix** - nastaviť kto dostane aké notifikácie
- **NotificationLog** - audit trail (read-only)

---

## Troubleshooting

### Email sa neodosiela?

1. **Over credentials:**
   ```bash
   cat .env.local | grep EMAIL
   ```

2. **Reštartuj server** (aby načítal .env.local)

3. **Over Gmail App Password** (nie normálne heslo!)

4. **Test SMTP connection:**
   ```bash
   python manage.py shell
   >>> from django.core.mail import send_mail
   >>> send_mail('Test', 'Body', 'from@gmail.com', ['to@gmail.com'])
   ```

---

### Template not found?

```bash
# Over že templates existujú
ls -la /Users/sopira/sopira.magic/version_01/templates/notifications/

# Reštartuj server
```

---

### No recipients?

```bash
# Over že ADMIN_EMAIL je v .env.local
cat .env.local | grep ADMIN_EMAIL

# Over NotificationMatrix entries
python manage.py shell
>>> from sopira_magic.apps.notification.models import NotificationMatrix
>>> NotificationMatrix.objects.filter(enabled=True)
```

---

## Ďalšie kroky

📖 **Kompletná dokumentácia:**
- `IMPLEMENTATION_GUIDE.md` - Detailný implementation guide
- `API_REFERENCE.md` - API dokumentácia
- `ARCHITECTURE_PLAN.md` - Architektúra a plán

---

**Need help?** Michael (sopira@me.com)  
**Status:** ✅ Production Ready

