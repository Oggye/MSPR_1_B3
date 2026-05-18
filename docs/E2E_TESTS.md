# Tests E2E Frontend ObRail (Playwright)

## Objectif

Cette suite couvre les vrais parcours frontend React avec backend FastAPI reel:

- `http://localhost:3000/interne/HomePage`
- `http://localhost:3000/externe/HomePage`
- `http://localhost:3000/externe/Trajets`
- `http://localhost:3000/externe/Map`
- `http://localhost:3000/externe/Statistique`
- `http://localhost:3000/externe/Operateur`

Elle complete les tests backend existants dans `platform/server/test/E2E` (qui restent des tests API FastAPI).

## Prerequis

- Docker + Docker Compose
- Node.js 20+
- npm

## Installation

Depuis `platform/front/app`:

```bash
npm ci
npm run e2e:install
```

## Lancement local (Docker + E2E)

Depuis la racine du projet:

```bash
docker compose up -d db api front prometheus grafana loki promtail
```

Verifier les services:

```bash
curl -f http://localhost:3000/externe/HomePage
curl -f http://localhost:8000/health
```

Puis lancer Playwright:

```bash
cd platform/front/app
npm run e2e
```

## Lancement Playwright (modes utiles)

Depuis `platform/front/app`:

```bash
npm run e2e
npm run e2e:headed
npm run e2e:ui
```

## Structure des tests

- `platform/front/app/tests/e2e/public-pages.spec.js`
  - navigation externe complete
  - interactions Trajets/Map/Statistique/Operateur
- `platform/front/app/tests/e2e/internal-admin.spec.js`
  - dashboard interne, onglets, actions UI
  - affichage erreur reseau sur `/api/internal/overview`
- `platform/front/app/tests/e2e/internal-endpoints.spec.js`
  - verification des endpoints internes FastAPI:
    - `GET /api/internal/overview`
    - `POST /api/internal/diagnostic/run`
    - `POST /api/internal/tests/run`

## CI/CD GitHub Actions

Workflow: `.github/workflows/ci-cd.yml`

Job ajoute: `frontend-e2e`

- installe Node et Playwright
- demarre les services docker necessaires
- attend la disponibilite front + API
- execute `npm run e2e`
- publie le rapport Playwright en artifact
- arrete les services

Le job `docker-build` attend maintenant aussi `frontend-e2e`.

## Debugging

1. Verifier les conteneurs:
```bash
docker compose ps
docker compose logs -f api
docker compose logs -f front
```
2. Rejouer un test:
```bash
cd platform/front/app
npx playwright test tests/e2e/public-pages.spec.js --project=desktop-chromium
```
3. Ouvrir le rapport:
```bash
npx playwright show-report
```

## Troubleshooting

- Erreur `ECONNREFUSED`:
  - verifier `front` sur `3000` et `api` sur `8000`.
- Erreur map Leaflet ou lenteur:
  - relancer avec `--headed` pour observer le rendu.
- Donnees vides:
  - les tests gerent les etats vides; verifier ensuite le chargement ETL/DB si besoin metier.
- Endpoint interne lent:
  - `POST /api/internal/tests/run` peut prendre du temps selon la charge.
