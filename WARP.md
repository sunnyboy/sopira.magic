# WARP Rules for sopira.magic

## Architectural principles

- This repository is a **monorepo** containing:
  - Django backend (`sopira_magic/`) as a **modular monolith** composed of many microservice-like Django apps.
  - React + Vite + TypeScript frontend (`frontend/`) that mirrors backend domains and uses shared, dynamic components.
- System is designed as **modern, scalable, enterprise-grade** platform.

## Backend architecture

- Conceptually **microservices**, implementované ako **separátne Django apps** bežiace na jednej primárnej DB (modular monolith), s doplnkovými DB pre state/logging podľa potreby.
- Architektúra je **config-driven** a **SSOT (single source of truth)**:
  - Dynamické modely, dynamické views, dynamické URLs, dynamické API.
  - Dynamický CRUD generátor.
  - Dynamická relačná konfigurácia ("relation registry" + dynamic relation service, config-driven queries).
- Existuje **plugin systém** – nové doménové moduly majú byť pridávané ako samostatné apps s minimálnou väzbou.
- **Totálny zákaz hardcodu** v zdielaných vrstvách:
  - Žiadny domain-specific hardcode v shared komponentoch, base modeloch, common views, generických službách.
  - Všetko, čo je doménovo špecifické, musí ísť cez konfiguráciu a SSOT (konfiguračné modely / registry), nie cez if/else v kóde.

## Frontend architecture

- Frontend má zodpovedať backendu:
  - Zdieľané, **dynamické komponenty** (formy, tabuľky, layouty, filtre, atď.).
  - Kanonický **SSOT** pre UI (config-driven UI, nie ručný hardcode na každú entitu).
- Komponenty majú byť znovupoužiteľné, riadené konfiguráciou (napr. schémy polí, typy entít, permisie), nie pevne napojené na konkrétny model.

## Invariants for future work

- Pri návrhu backendu aj frontendu **preferovať konfiguráciu pred hardcodom**.
- Nové features majú využívať existujúci SSOT, relation registry a dynamické generátory tam, kde je to možné.
- Ak je potrebný domain-specific kód, má byť uložený v samostatnej app (microservice-modul), nie v shared vrstvách.
- Pri návrhu API a UI vždy premýšľať, či sa dá riešenie vyjadriť konfiguračne (model/konfig tabuľka + generická vrstva), nie cez ad-hoc endpoint/komponent.
