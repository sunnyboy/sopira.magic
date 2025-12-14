# Signup Security Fix - Testing Guide

## Úvod

Tento dokument obsahuje podrobné testovacie kroky pre overenie opraveného signup flow a scope isolation.

## Pred Testovaním

1. **Server beží:**
   ```bash
   cd ~/sopira.magic/version_01
   source venv/bin/activate
   python manage.py runserver
   ```

2. **Frontend beží:**
   ```bash
   cd ~/sopira.magic/version_01/frontend
   npm run dev
   ```

3. **Email credentials v `.env.local`:**
   ```
   EMAIL_HOST_USER=your_email@gmail.com
   EMAIL_HOST_PASSWORD=your_app_password
   ADMIN_EMAIL=sopira@me.com
   ```

## Test 1: Nový Signup Flow

### Kroky:

1. **Odhláste sa** (ak ste prihlásený)
   - Choďte na `/login`
   - Kliknite Logout

2. **Otvorte Sign Up modal**
   - Na login stránke kliknite "Sign Up"

3. **Zaregistrujte nového používateľa:**
   ```
   Username: test_signup_user
   Password: testpass123
   Confirm Password: testpass123
   Email: your_test_email@gmail.com
   First Name: Test
   Last Name: User
   ```

4. **Kliknite "Sign Up"**

### Očakávaný výsledok:

✅ **Redirect:**
- Po úspešnom signup sa používateľ automaticky presmeruje na `/companies`

✅ **Empty State Message:**
- Vidíte: "Vitajte! Vytvorte svoju prvú spoločnosť"
- Message obsahuje jasné inštrukcie o použití +Add tlačidla

✅ **Email notifikácie:**
- **SA email (sopira@me.com):** "🆕 New User Registration - test_signup_user"
  - Obsahuje: username, email, full name, role (ADMIN), IP address
  - Action Required box: user nemá companies
- **User email (your_test_email@gmail.com):** "Welcome to Sopira Magic, Test!"
  - Obsahuje: personalized greeting, login instructions

## Test 2: Empty Scope Verification

### Kroky:

1. **Prihláste sa ako test_signup_user**

2. **Skontrolujte všetky stránky:**
   - `/companies` → prázdna tabuľka ✅
   - `/factories` → prázdna tabuľka ✅
   - `/machines` → prázdna tabuľka ✅
   - `/cameras` → prázdna tabuľka ✅
   - `/users` → vidí len seba ✅

### Očakávaný výsledok:

✅ **Všetky tabuľky sú prázdne** (okrem users, kde vidí len seba)
- NIE unfiltered queryset!
- Empty scope = Empty data

## Test 3: Create First Company

### Kroky:

1. **Prihláste sa ako test_signup_user**

2. **Choďte na `/companies`**

3. **Kliknite "+Add" tlačidlo**

4. **Vytvorte novú company:**
   ```
   Code: TESTCO
   Name: Test Company
   Human ID: TEST001
   Active: Yes
   ```

5. **Uložte**

6. **Refresh stránku**

### Očakávaný výsledok:

✅ **User vidí len svoju company:**
- Vidí: "Test Company" (TESTCO)
- Nevidí: žiadne iné companies (ak existujú)

✅ **Scope isolation funguje:**
- `/factories` → stále prázdne (žiadne factories v Test Company)
- `/machines` → stále prázdne
- User má scope obmedzený na Test Company

## Test 4: Superuser Scope Isolation

### Kroky:

1. **Odhláste sa**

2. **Prihláste sa ako sopira (superuser)**
   ```
   Username: sopira
   Password: sopirapass
   ```

3. **Vytvorte novú company:**
   ```
   Code: ADMINCO
   Name: Admin Company
   Human ID: ADMIN001
   ```

4. **Odhláste sa**

5. **Prihláste sa ako test_signup_user**

6. **Choďte na `/companies`**

### Očakávaný výsledok:

✅ **User vidí len svoju company:**
- Vidí: "Test Company" (TESTCO)
- **NEVIDÍ:** "Admin Company" (ADMINCO) ← KRITICKÉ!

## Test 5: User bez Company (Existing User)

### Kroky:

1. **Prihláste sa ako sopira**

2. **Vytvorte nového usera cez admin:**
   ```
   Username: user_no_company
   Email: test2@example.com
   Role: ADMIN
   Password: testpass123
   ```

3. **Odhláste sa**

4. **Prihláste sa ako user_no_company**

5. **Choďte na `/companies`**

### Očakávaný výsledok:

✅ **Empty state message pre existing users:**
- Vidí: "Žiadne spoločnosti"
- Message obsahuje inštrukcie pre kontaktovanie admina ALEBO vytvorenie vlastnej

## Test 6: Backend Logs Verification

### Kroky:

1. **Skontrolujte Django logs počas signup:**

```bash
# V termináli kde beží runserver, hľadajte:
[ScopingEngine] Empty scope detected for companies/admin (user=test_signup_user), returning EMPTY queryset
```

2. **Skontrolujte notification logs:**

```bash
python manage.py shell
>>> from sopira_magic.apps.notification.models import NotificationLog
>>> logs = NotificationLog.objects.filter(notification_type__contains='signup').order_by('-created')
>>> for log in logs[:5]:
...     print(f"{log.notification_type}: {log.recipient_email} - {log.status}")
```

### Očakávaný výsledok:

✅ **Log entries existujú:**
- signup_notification_admin → sopira@me.com → sent
- signup_notification_user → your_test_email@gmail.com → sent

## Známe Problémy

### Email sa neodosiela

**Príčina:** Nesprávne nastavené credentials alebo app password

**Riešenie:**
1. Overte EMAIL_HOST_USER a EMAIL_HOST_PASSWORD v `.env.local`
2. Skontrolujte Gmail App Password (nie regular password!)
3. Skúste test command:
   ```bash
   python manage.py test_notification login_notification --preview
   ```

### Empty State sa nezobrazuje

**Príčina:** Config v `companyTableConfig.ts` prepíše custom empty state

**Riešenie:**
- Empty state v `CompanyPage.tsx` má prioritu cez useMemo dependency array

### User vidí všetko namiesto prázdnej tabuľky

**Príčina:** Scoping rules nie sú správne definované

**Riešenie:**
1. Overte `sopira_magic/apps/scoping/rules.py`
2. Admin musí mať `is_assigned` condition s `scope_level: 1`
3. Restart servera po zmenách v rules

## Cleanup po Testovaní

```bash
# Vymazať test usera
python manage.py shell
>>> from sopira_magic.apps.m_user.models import User
>>> User.objects.filter(username='test_signup_user').delete()
>>> User.objects.filter(username='user_no_company').delete()

# Vymazať test companies
>>> from sopira_magic.apps.m_company.models import Company
>>> Company.objects.filter(code='TESTCO').delete()
>>> Company.objects.filter(code='ADMINCO').delete()
```

## Záver

Všetky testy musia prejsť ✅ pre potvrdenie, že:
1. Signup notifikácie fungujú (admin + user)
2. Empty scope = Empty queryset (NIE unfiltered!)
3. Scope isolation funguje korektne
4. Frontend redirect a empty state fungujú
5. Security leak je odstránený




