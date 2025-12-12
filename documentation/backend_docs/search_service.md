# Search mikroservis (Elasticsearch) – setup, použitie, riziká

## Prehľad
- BE: Django + Elasticsearch (klient pinned `<9.0.0`, aktuálne 8.19.x) s config-driven mappingom z `VIEWS_MATRIX`.
- FE: MyTable vie prepínať `simple/advanced/fuzzy` a volá `/api/search/`.
- Fallback: ak ES nebeží alebo je vypnutý, používa sa DB search (param `SEARCH_ELASTIC_ENABLED=0`).

## Závislosti
- Balíky: `elasticsearch>=8.15.1,<9.0.0`, `elasticsearch-transport` (8.x).
- ES runtime: testované na Elasticsearch 8.15.1 (tarball, bundled JDK).
- TLS: lokálne self-signed CA (`config/certs/http_ca.crt`).

## Konfigurácia (env)
Používame environment-aware načítanie cez `get_elasticsearch_config()`:
- `ELASTICSEARCH_URL_LOCAL` / `ELASTICSEARCH_URL_DEV` / `ELASTICSEARCH_URL_PROD` / `ELASTICSEARCH_URL_RENDER` (fallback `ELASTICSEARCH_URL`)
  - Lokál (HTTPS, basic auth): `https://elastic:<heslo>@localhost:9200`
- `SEARCH_ELASTIC_ENABLED` (1/0) – zap/vyp ES
- `SEARCH_DEFAULT_MODE` (`simple|advanced`)
- `SEARCH_ALLOW_APPROX` (1/0) – fuzzy
- `SEARCH_INDEX_PREFIX` (napr. `idx_local`, `idx_dev`)
- `SEARCH_REQUEST_TIMEOUT` (s), `SEARCH_MAX_PAGE_SIZE`
- TLS voľby: `ELASTICSEARCH_CA_CERT` (cesta k CA), `ELASTICSEARCH_VERIFY_CERTS` (1/0)

### Lokálne nastavenie (príklad)
```
ELASTICSEARCH_URL_LOCAL=https://elastic:<heslo>@localhost:9200
SEARCH_ELASTIC_ENABLED=1
ELASTICSEARCH_CA_CERT=/Users/<user>/elasticsearch-8.15.1/config/certs/http_ca.crt
ELASTICSEARCH_VERIFY_CERTS=0   # lokálne self-signed
SEARCH_INDEX_PREFIX=idx_local
SEARCH_DEFAULT_MODE=simple
SEARCH_ALLOW_APPROX=1
SEARCH_REQUEST_TIMEOUT=5
SEARCH_MAX_PAGE_SIZE=200
```

## Workflow
1) Spustiť Elasticsearch (lokál: tarball `./bin/elasticsearch`, alebo služba).
2) Skontrolovať dostupnosť: `curl -k -I https://localhost:9200` (pri vypnutej verifikácii certu).
3) Reštartovať backend (načítanie env).
4) Reindex: `python manage.py reindex_search` (používa VIEWS_MATRIX, tvorí indexy `idx_<env>_<view>`).
5) Smoke test API:  
   - `/api/search/?view=<table>&q=test&mode=simple`  
   - `/api/search/?view=<table>&q=test&mode=advanced`  
   - `/api/search/?view=<table>&q=test&mode=simple&approx=1`
6) FE: v MyTable otestovať prepínač simple/advanced/fuzzy; ak ES vypneš (`SEARCH_ELASTIC_ENABLED=0`), FE musí fungovať (DB search).
7) Highlight: ES vracia `highlight` (fields `__fulltext`, `data.*`, `*_label`), FE číta `row.__highlight`; pri DB fallbacke FE používa lokálny substring highlight.

## API vrstva
- Endpoint: `GET /api/search/`
- Parametre:  
  - `view` (názov view z VIEWS_MATRIX) – povinné  
  - `q` – search string  
  - `mode` – `simple|advanced`  
  - `approximate` / `approx` – `1/0`  
  - `page`, `page_size`, `ordering`  
- Scoping: backend dopĺňa filtre podľa `ownership_hierarchy` (filter terms v ES).
- Fallback: ak ES nedostupný alebo vypnutý → DB search (search_fields z VIEWS_MATRIX).

## Mapping/indexovanie
- Generované z VIEWS_MATRIX: všetky polia modelu + scope polia (ownership_hierarchy) + FK labely z `fk_display_template`.
- Indexy per view: `idx_<prefix>_<view_name>`.
- Signály: post_save/post_delete → automatická indexácia.
- Full reindex: `python manage.py reindex_search` (drop & create).
- Highlight: ES dotaz obsahuje highlight blok s `<mark>` tagmi pre `__fulltext`, `data.*`, `*_label`.

## FE integrácia (MyTable)
- Prepínače: simple/advanced/fuzzy v search bare.
- Advanced: server-side parsing (client-side filter vypnutý).
- Fuzzy: `approximate=1` → ES `multi_match` s fuzziness AUTO.
- Highlight: ak ES odpoveď obsahuje `highlight`, uloží sa do `row.__highlight`; FE môže uprednostniť serverom vygenerované highlighty. Pri DB fallbacke FE používa lokálne zvýraznenie podľa query.
- Pri vypnutom ES (`SEARCH_ELASTIC_ENABLED=0`) MyTable posiela `search` param a DB search funguje.

## Nasadenie (dev/prod)
- Nastaviť príslušné `ELASTICSEARCH_URL_<ENV>` + auth (basic alebo API key podľa infra).  
- Pre HTTPS s vlastným certom: `ELASTICSEARCH_VERIFY_CERTS=1` a `ELASTICSEARCH_CA_CERT=<cesta na CA>`.  
- Pre self-signed (dev): `ELASTICSEARCH_VERIFY_CERTS=0` (dočasné).
- Po deploy: reindex na danom prostredí, skontrolovať health: `curl -k -X GET https://<host>:9200/_cluster/health`.

## Možné issues
- `Invalid media-type... Accept version must be 8 or 7` → nesúlad klienta (musí byť <9, máme pinned `<9.0.0`).
- `Remote end closed connection` → zlá URL/protokol/auth; over `ELASTICSEARCH_URL_*` a či ES počúva na HTTP/HTTPS.
- `permission denied for table django_migrations` pri migráciách → nesprávne DB role/owner (riešené grantmi a resetom DB).
- TLS varovania pri `verify_certs=0` sú očakávané lokálne; v prod povoliť verifikáciu.
- Prázdne výsledky po reindexe: DB nemá dáta (čerstvá inštalácia) – treba seed/import.

## Bottlenecks/limity
- Lokál bez dát → málo čo testovať; v prod dbať na veľkosť batchov pri reindexe (helpers.bulk).
- Fuzzy search môže byť pomalší pri veľkých indexoch; default fuzziness AUTO.
- `SEARCH_MAX_PAGE_SIZE` chráni pred veľkými page_size (default 200).
- TLS vypnutá verifikácia je riziko – iba lokálne, nie prod.

## Monitoring/logy
- ES logy: `/Users/<user>/elasticsearch-8.15.1/logs/`
- Aplikácia: `logs/sopira_magic_be.log` (ak povolené), plus stdout.
- Pri problémoch s auth/cert: test `curl -vk https://elastic:<heslo>@localhost:9200`.

