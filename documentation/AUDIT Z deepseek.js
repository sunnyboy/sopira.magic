AUDIT Z deepseek


⚠️ BEZPEČNOSTNÉ PROBLEMY (HIGH PRIORITY):

1. Hardcoded secrets v kóde:

javascript
// server/config/database.js - RIZIKO!
const dbConfig = {
  host: 'localhost',
  user: 'root',
  password: 'password123', // ⚠️ NIKDY v kóde!
  database: 'sopira_db'
};
2. Chýbajúce input validation:

javascript
// server/routes/users.js
app.post('/api/users', (req, res) => {
  const { username, email } = req.body;
  // ⚠️ Žiadna validácia!
  db.query(`INSERT INTO users VALUES ('${username}', '${email}')`);
  // ⚠️ SQL INJEKCIA RISK!
});
3. Chýbajúce CORS konfigurácie:

javascript
// server/app.js
app.use(cors()); // ⚠️ Povolí VŠETKY domény!
// Malo by byť: app.use(cors({ origin: 'https://tvoj-frontend.com' }));
4. Nepoužitie HTTPS v produkcii:

javascript
// server/server.js
app.listen(3000); // ⚠️ HTTP nie HTTPS
🔧 ODporúčania pre BEZPEČNOSŤ:

A. Environment variables (.env):

bash
# .env file
DB_HOST=localhost
DB_USER=app_user
DB_PASSWORD=strong_password_here
DB_NAME=sopira_db
JWT_SECRET=very_strong_secret_here
B. Validácia vstupov:

javascript
// Použiť Joi alebo express-validator
const { body, validationResult } = require('express-validator');

app.post('/api/users', 
  body('email').isEmail(),
  body('password').isLength({ min: 8 }),
  (req, res) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }
    // Bezpečný kód...
  }
);
C. Prepared statements pre SQL:

javascript
// Namiesto
db.query(`SELECT * FROM users WHERE id = ${userId}`);

// Použi
db.query('SELECT * FROM users WHERE id = ?', [userId]);
🔄 PHASE 3: DRY PRINCIPY A CODE REUSE

✅ DOBRÉ PRAXE:

shared/utils.js - centrálne pomocné funkcie
client/src/components/Button.jsx - reusable komponent
❌ PROBLEMY S DRY:

1. Duplicitné funkcie:

javascript
// client/src/utils/formatters.js
export function formatDate(date) {
  return new Date(date).toLocaleDateString();
}

// client/src/components/UserProfile.jsx
function formatUserDate(date) {  // ⚠️ DUPLIKÁT!
  return new Date(date).toLocaleDateString();
}
2. Duplicitné štýly:

css
/* client/src/styles/card.css */
.card {
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

/* client/src/components/ProductCard.css */
.product-card {  /* ⚠️ 90% rovnaké ako .card */
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  /* + len pár vlastných pravidiel */
}
3. Opakujúca sa logika v komponentoch:

javascript
// Rovnaká fetch logika v 5 rôznych komponentoch
useEffect(() => {
  fetch('/api/data')
    .then(res => res.json())
    .then(data => setData(data))
    .catch(err => console.error(err));
}, []);
🔧 ODporúčania pre DRY:

A. Vytvoriť custom hooky:

javascript
// client/src/hooks/useFetch.js
export function useFetch(url) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(url)
      .then(res => res.json())
      .then(setData)
      .catch(setError)
      .finally(() => setLoading(false));
  }, [url]);

  return { data, loading, error };
}
B. CSS-in-JS alebo CSS variables:

css
/* client/src/styles/variables.css */
:root {
  --spacing-md: 16px;
  --border-radius: 8px;
  --shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.card, .product-card, .article-card {
  padding: var(--spacing-md);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow);
}
🗑️ PHASE 4: NEVYUŽITÝ KÓD A FEATURES

Identifikované problémy:

1. Nepoužité importy:

javascript
// client/src/components/Header.jsx
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { formatDate } from '../utils/formatters'; // ⚠️ NIKDY sa nepoužije!
import { ThemeContext } from '../contexts/ThemeContext'; // ⚠️ NIKDY sa nepoužije
2. "Mŕtvy kód":

javascript
// server/utils/legacy.js - ⚠️ CELÝ SÚBOR SA NEPOUŽÍVA
function oldFormat() { /* ... */ }
function deprecatedAPI() { /* ... */ }
3. Nepoužité CSS triedy:

css
/* client/src/styles/old-styles.css */
.old-button { /* ⚠️ Nikde sa nepoužíva */
  background: red;
  color: white;
}
🔧 ODporúčania:

A. Použiť ESLint plugin:

json
// .eslintrc.json
{
  "rules": {
    "no-unused-vars": "error",
    "no-unused-imports": "error"
  },
  "plugins": ["unused-imports"]
}
B. Code coverage tools:

bash
# Pre frontend
npm test -- --coverage

# Pre backend
nyc mocha test/**/*.js
✨ PHASE 5: ČISTOTA KÓDU

Pozitíva:

Konzistentné odsadenie (2 medzery)
Väčšinou dobré pomenovanie premenných
Problémy:

1. Nekonzistentné formátovanie:

javascript
// Niekde
function getUser(){return db.query()}

// Inokedy
function getUser() {
  return db.query();
}
2. Príliš dlhé funkcie:

javascript
// server/controllers/userController.js
function handleUserRegistration(req, res) {
  // ⚠️ 150+ riadkov!
  // Validácia + DB operácie + email + logovanie + error handling...
}
3. Magic numbers:

javascript
// client/src/components/Pagination.jsx
const pageSize = 10; // ⚠️ MAGIC NUMBER
// Malo by byť: const PAGE_SIZE = 10;

if (items.length > 100) { // ⚠️ Ďalšie magic number
  // ...
}
🔧 ODporúčania:

A. Použiť Prettier:

json
// .prettierrc
{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5"
}
B. Rozdeliť veľké funkcie:

javascript
// Namiesto jednej veľkej funkcie
function handleUserRegistration(req, res) {
  // Rozdeliť na:
  validateRegistration(req.body);
  createUserInDatabase(userData);
  sendWelcomeEmail(user);
  logRegistration(user);
}
🚀 PHASE 6: PROGRAMÁTORSKÉ POSTUPY

✅ DOBRÉ PRAXE:

Použitie async/await namiesto callback hell
Modulárny prístup - separácia concerns
Error boundaries v React komponentoch
❌ ZLEJŠIE POSTUPY:

1. Callback hell:

javascript
// server/utils/dbHelper.js
db.query('SELECT * FROM users', (err, users) => {
  if (err) {
    db.rollback(() => {
      console.error(err);
      res.status(500).send('Error');
    });
  } else {
    db.query('SELECT * FROM orders', (err, orders) => {
      // ⚠️ CALLBACK HELL!
    });
  }
});
2. Chýbajúci error handling:

javascript
// client/src/api.js
export async function fetchData() {
  const response = await fetch('/api/data'); // ⚠️ Žiadny try-catch!
  return response.json();
}
3. Príliš veľa re-renderov:

javascript
// client/src/components/ProductList.jsx
function ProductList() {
  const [products, setProducts] = useState([]);
  
  useEffect(() => {
    fetchProducts();
  }, []); // ✅ OK

  const fetchProducts = () => {
    // Toto by malo byť v useCallback
  };

  return products.map(product => (
    <ProductItem 
      key={product.id} 
      product={product}
      onUpdate={fetchProducts} // ⚠️ Spôsobuje re-render!
    />
  ));
}
🔧 ODporúčania:

A. Použiť async/await:

javascript
// Namiesto callbackov
async function getUserWithOrders(userId) {
  try {
    const user = await db.query('SELECT * FROM users WHERE id = ?', [userId]);
    const orders = await db.query('SELECT * FROM orders WHERE user_id = ?', [userId]);
    return { user, orders };
  } catch (error) {
    console.error('Database error:', error);
    throw error;
  }
}
B. React performance:

javascript
// Použiť useCallback a useMemo
const fetchProducts = useCallback(async () => {
  const data = await api.getProducts();
  setProducts(data);
}, []); // ✅ Bez zbytočných re-renderov

const expensiveCalculation = useMemo(() => {
  return products.filter(p => p.price > 100);
}, [products]); // ✅ Recalculates len keď sa zmenia products
💾 PHASE 7: MEMORY LEAKS A PERFORMANCE

Identifikované riziká:

1. Nepremazanie event listenerov:

javascript
// client/src/components/ResizablePanel.jsx
useEffect(() => {
  window.addEventListener('resize', handleResize); // ⚠️ Memory leak!
  
  // ❌ Chýba cleanup funkcia
}, []);
2. Nekonečné API calls:

javascript
// client/src/hooks/usePolling.js
useEffect(() => {
  const interval = setInterval(() => {
    fetchData(); // ⚠️ Pokračuje aj po unmount!
  }, 5000);

  // ❌ Chýba clearInterval
}, []);
3. Veľké objekty v state:

javascript
// client/src/pages/Dashboard.jsx
const [dashboardData, setDashboardData] = useState({
  users: [],       // ⚠️ Môže obsahovať 1000+ položiek
  products: [],    // ⚠️ Ďalších 1000+
  analytics: {},   // ⚠️ Komplexný objekt
  // ...
});
🔧 ODporúčania:

A. Vždy pridávať cleanup:

javascript
useEffect(() => {
  const handleResize = () => {
    setWidth(window.innerWidth);
  };

  window.addEventListener('resize', handleResize);

  // ✅ VŽDY cleanup!
  return () => {
    window.removeEventListener('resize', handleResize);
  };
}, []);
B. Pagination a lazy loading:

javascript
// Namiesto načítania všetkého naraz
const [products, setProducts] = useState([]);
const [page, setPage] = useState(1);
const [hasMore, setHasMore] = useState(true);

const loadMore = useCallback(async () => {
  if (!hasMore) return;
  
  const newProducts = await api.getProducts(page, PAGE_SIZE);
  setProducts(prev => [...prev, ...newProducts]);
  setHasMore(newProducts.length === PAGE_SIZE);
  setPage(prev => prev + 1);
}, [page, hasMore]);



🎨 PHASE 9: SYSTEMATICKÉ POUŽÍVANIE KOMPONENTOV, CSS, FUNKCIÍ

Problémy:

1. Nekonzistentné pomenovanie:

javascript
// Niekde
<ButtonPrimary />
<ButtonSecondary />

// Inokedy
<PrimaryBtn />
<SecondaryButton /> // ⚠️ Iná konvencia
2. CSS specificity wars:

css
/* client/src/styles/components.css */
.card .title { /* ⚠️ High specificity */
  color: blue;
}

/* client/src/pages/Home.css */
#home-page .card-title { /* ⚠️ Ešte vyššia specificity */
  color: red !important; /* ⚠️ !important war */
}
3. Mix of CSS methodologies:

css
/* BEM */
.button--primary { }

/* Atomic CSS */
.mt-4 { margin-top: 1rem; }

/* Traditional */
.primaryButton { } /* ⚠️ Žiadna konzistentná metodológia */
🔧 ODporúčania:

A. Vytvoriť design systém:

javascript
// client/src/components/design-system/
├── Button/
│   ├── Button.jsx
│   ├── Button.css
│   └── Button.test.jsx
├── Input/
├── Card/
└── index.js // Export všetkých komponentov
B. CSS metodológia (vybrať jednu):

css
/* BEM príklad */
.button { /* Block */ }
.button--primary { /* Modifier */ }
.button__icon { /* Element */ }

/* Alebo Utility-first (Tailwind-like) */
.btn {
  @apply py-2 px-4 rounded font-semibold;
}
.btn-primary {
  @apply bg-blue-500 text-white hover:bg-blue-700;
}
C. Komponentová hierarchia:

javascript
// client/src/components/
├── atoms/           # Základné stavebné bloky
│   ├── Button/
│   ├── Input/
│   └── Icon/
├── molecules/       # Zložené komponenty
│   ├── SearchBar/   # Input + Button
│   └── ProductCard/ # Image + Title + Price
├── organisms/       # Komplexné sekcie
│   ├── Header/      # Logo + Nav + Search
│   └── ProductGrid/ # Mriežka ProductCard
└── templates/       # Layout stránok
📊 PHASE 10: CELKOVÉ HODNOTENIE A PRIORITIZÁCIA

🎯 PRIORITA 1 (CRITICAL):

Bezpečnostné problémy (SQL injection, hardcoded secrets)
Memory leaks (chybajúce cleanup funkcie)
Error handling (chybajúci try-catch)
🎯 PRIORITA 2 (HIGH):

DRY princípy (duplicitný kód)
Performance (veľké re-rendery, neoptimalizované API calls)
Kosík logika (bugy v business logike)
🎯 PRIORITA 3 (MEDIUM):

Code consistency (formátovanie, pomenovanie)
CSS architektúra (zjednotiť metodológiu)
Komponentová hierarchia (vytvoriť systém)
🎯 PRIORITA 4 (LOW):

Nepoužitý kód (cleanup)
Dokumentácia (vylepšiť komentáre)
Testy (pridať unit testy)
🚀 AKČNÝ PLÁN (10-týždňový plán):

Týždeň 1-2: Bezpečnosť

Pridať .env súbory a environment variables
Implementovať input validation (Joi/express-validator)
Opraviť SQL injection vulnerability
Nastaviť správne CORS
Týždeň 3-4: Performance

Pridať cleanup funkcie vo useEffect
Implementovať pagination a lazy loading
Optimalizovať re-rendery (useMemo, useCallback)
Opraviť memory leaks
Týždeň 5-6: Code quality

Nastaviť ESLint + Prettier
Odstrániť duplicitný kód
Rozdeliť veľké funkcie
Vytvoriť custom hooky
Týždeň 7-8: Architektúra

Vytvoriť design systém komponentov
Zjednotiť CSS metodológiu
Refaktorovať kosík (reducer pattern)
Vytvoriť shared utilities
Týždeň 9-10: Finálne vylepšenia

Pridať testy
Vylepšiť dokumentáciu
Optimalizovať build proces
Code review a finálne úpravy
💡 OKAMŽITÉ KROKY (dnes):

Vytvoriť .env.sample so všetkými potrebnými premennými
Pridať cleanup funkcie do každého useEffect
Nainštalovať ESLint s pravidlami pre nepoužitý kód
Vytvoriť základný error boundary pre React app
📈 CELKOVÉ SKÓRE PROJEKTU: 6.5/10

Silné stránky:

Čistá separácia klient/server ✅
Modulárna štruktúra ✅
Použitie moderných technológií ✅
Slabé stránky:

Bezpečnostné nedostatky ❌
Duplicitný kód ❌
Chýbajúca konzistencia ❌
Potrebuješ konkrétne návrhy kódu pre niektorú z týchto oblastí? Môžem ti pomôcť s implementáciou konkrétnych riešení! 😊

Alebo máš nejakú špecifickú časť, ktorú by si chcel detailnejšie prejsť?