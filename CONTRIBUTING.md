# Contributing to sopira.magic

This repository is a monorepo containing a **Django backend** (`sopira_magic/`) and a **React 19 + Vite + TypeScript frontend** (`frontend/`).

The goal of this guide is to make it easy to get started, run tests, and open pull requests in a consistent way.

## 1. Prerequisites

- **Python**: 3.12 (or 3.11+)
- **Node.js**: 20.x (LTS) recommended
- **PostgreSQL**: 15+ (local instance)
- Git + GitHub account

## 2. Backend setup (Django)

From the repository root:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Update .env with your database URLs (PRIMARY, STATE, LOGGING)

# Run migrations (all databases)
python manage.py migrate --database default
python manage.py migrate --database state
python manage.py migrate --database logging

# Run development server
python manage.py runserver
```

For details, see `README.md` in the root.

## 3. Frontend setup (Vite + React + TS)

From the repository root:

```bash
cd frontend
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

For details, see `frontend/README.md`.

## 4. Running tests & checks locally

### Backend tests

From the repository root with venv activated:

```bash
pytest
```

This uses `pytest` + `pytest-django` with the Django settings module `sopira_magic.settings` and multi-database configuration.

### Frontend lint & build

From `frontend/`:

```bash
npm run lint
npm run build
```

Please run these commands before opening a pull request.

## 5. Git workflow

- The default branch is **`main`** and is **protected**.
- Never commit directly to `main`.
- Create feature branches from `main`:
  - `feat/<short-description>` for new features
  - `fix/<short-description>` for bugfixes
  - `chore/<short-description>` for non-functional changes (docs, tooling, etc.)

Example:

```bash
git checkout -b feat/user-preferences-ui
```

## 6. Commit messages

Use clear, meaningful commit messages. Recommended (not strictly enforced):

- `feat: add user preferences API`
- `fix: handle missing factory relation`
- `chore: update CI workflow`

Try to keep one logical change per commit when possible.

## 7. Pull requests

When opening a PR:

1. Make sure backend tests and frontend lint/build pass locally.
2. Keep PRs as small and focused as possible.
3. Provide a clear description:
   - What was changed
   - Why it was changed
   - How it was tested
4. If relevant, add screenshots (mainly for frontend changes).

CI (GitHub Actions) will run automatically on every push and pull request to validate:

- **Backend**: `pytest`
- **Frontend**: `npm run lint` + `npm run build`

## 8. Code owners & reviews

- `CODEOWNERS` defines who is responsible for reviewing changes in different parts of the repo.
- Pull requests touching `sopira_magic/` or `frontend/` will automatically request review from the appropriate owners.

At least one approval from a code owner is recommended before merging (and will be required on protected branches).

## 9. Merging

- Use **Squash and merge** or **Rebase and merge** to keep history clean.
- Ensure all required checks (CI jobs) are green before merging.
