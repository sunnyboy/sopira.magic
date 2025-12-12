# Scoping Integration - Quick Reference Card

**Status:** ✅ PRODUCTION READY  
**Verzia:** 1.0.0  
**Dátum:** 2025-12-12

---

## 🎯 TL;DR

**Scope integration je PLNE IMPLEMENTOVANÁ a FUNKČNÁ!**

- ✅ Role mapping: User.role → scoping roles
- ✅ Scope resolution: User → Companies → Factories  
- ✅ Integration: mystate + relation system
- ✅ Notification service: Plne scope-aware
- ✅ Validácia: Zero warnings

---

## 🚀 Quick Start

### Verifikácia

```bash
python manage.py check
# Expected: ✅ Scoping registry callbacks registered (FULL IMPLEMENTATION)
```

### Test Notifikácie

```bash
python manage.py test_notification login_notification --preview
# Expected: Recipients podľa scope
```

### Test v Shell

```python
python manage.py shell

from sopira_magic.apps.scoping import get_scope_values, get_scope_owner_role
from sopira_magic.apps.m_user.models import User

user = User.objects.get(username='sopira')
role = get_scope_owner_role(user)
companies = get_scope_values(1, user, 'accessible')
factories = get_scope_values(2, user, 'accessible')

print(f"Role: {role}")
print(f"Companies: {companies}")
print(f"Factories: {factories}")
```

---

## 📊 Role Mapping

| User.role | Scoping Role | Access Level |
|-----------|--------------|--------------|
| SUPERADMIN | superuser | Everything |
| ADMIN | admin | Company scope |
| STAFF | staff | Factory scope |
| EDITOR | editor | Limited |
| READER | reader | Own records |
| ADHOC | adhoc | Limited |

---

## 🔍 Scope Levels

| Level | Entity | Example |
|-------|--------|---------|
| 0 | User | `['uuid-user-123']` |
| 1 | Company | `['uuid-comp-1', 'uuid-comp-2']` |
| 2 | Factory | `['uuid-fact-1', 'uuid-fact-2', ...]` |

---

## 🔧 API Usage

### Get User Role

```python
from sopira_magic.apps.scoping import get_scope_owner_role

role = get_scope_owner_role(user)
# Returns: 'superuser', 'admin', 'staff', etc.
```

### Get Scope Values

```python
from sopira_magic.apps.scoping import get_scope_values

# Get accessible companies
companies = get_scope_values(
    scope_level=1,           # Level 1 = Company
    scope_owner=user,
    scope_type='accessible'  # or 'selected'
)

# Get accessible factories
factories = get_scope_values(
    scope_level=2,           # Level 2 = Factory
    scope_owner=user,
    scope_type='accessible'
)
```

---

## 📖 Dokumentácia

| Dokument | Účel |
|----------|------|
| `SCOPING_INTEGRATION.md` | **Detailná implementácia** |
| `FAQ_AND_EXAMPLES.md` | FAQ + príklady |
| `IMPLEMENTATION_GUIDE.md` | Setup guide |
| `API_REFERENCE.md` | API docs |

---

## 🐛 Troubleshooting

### Problem: Scoping validation warning

```bash
# Check that core app is in INSTALLED_APPS
grep "sopira_magic.apps.core" sopira_magic/settings.py

# Restart server
resetall
```

### Problem: Empty scope values

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Check logs for errors
tail -f logs/*.txt | grep -i scope
```

---

## ✅ Production Checklist

- [x] Scoping callbacks registered
- [x] No validation warnings  
- [x] System check passes
- [x] Notification scope filtering works
- [x] Fallback strategies tested
- [x] Error logging configured

---

## 🎯 Key Files

```
sopira_magic/apps/core/apps.py          # Main implementation
sopira_magic/apps/scoping/              # Scoping engine
sopira_magic/apps/notification/         # Notification service
```

---

**Ready to use!** 🚀

