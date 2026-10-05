# CSEHub

A computer-science learning platform — Django REST API for the separate React frontend.
Admin-managed subject cards, user profiles, and **Supabase-backed** user accounts.

![Python](https://img.shields.io/badge/python-3.11+-blue?logo=python)
![Django](https://img.shields.io/badge/django-6.0.3-092E20?logo=django)
![DRF](https://img.shields.io/badge/djangorestframework-3.16.0-red?logo=django)
![License](https://img.shields.io/badge/license-MIT-green)
![Render](https://img.shields.io/badge/deployed%20on-Render-46E3B7?logo=render)

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
  - [Option A — Docker (Recommended)](#option-a--docker-recommended)
  - [Option B — Manual Setup](#option-b--manual-setup)
- [Environment Variables](#environment-variables)
- [Usage](#usage)
  - [API Documentation](#api-documentation)
  - [Management Commands](#management-commands)
- [Project Structure](#project-structure)
- [API Endpoints](#api-endpoints)
- [Deployment](#deployment)
- [Contributing](#contributing)
  - [1. Fork the Repository](#1-fork-the-repository)
  - [2. Clone Your Fork](#2-clone-your-fork)
  - [3. Add the Upstream Remote](#3-add-the-upstream-remote)
  - [4. Set Up Your Local Environment](#4-set-up-your-local-environment)
  - [5. Keep Your Fork in Sync](#5-keep-your-fork-in-sync)
  - [6. Create a Feature Branch](#6-create-a-feature-branch)
  - [7. Make Your Changes](#7-make-your-changes)
  - [8. Run the Tests](#8-run-the-tests)
  - [9. Push to Your Fork](#9-push-to-your-fork)
  - [10. Open a Pull Request](#10-open-a-pull-request)
- [License](#license)

---

## Features

| Feature | Status |
|---------|--------|
| **Subject catalog** — Admin-managed subject cards with public listing | ✅ Implemented |
| **Supabase Auth** — JWT authentication; the API auto-provisions a local `User` from a valid Bearer token | ✅ Implemented |
| **User profile** — `GET`/`PATCH /api/me/` for display name, username, and avatar | ✅ Implemented |
| **API documentation** — Auto-generated OpenAPI schema with Swagger UI and ReDoc | ✅ Implemented |
| **Coding problems** — Problem / TestCase / Submission models defined | 🚧 Models only |

---

## Tech Stack

| Layer              | Technology                                       |
| ------------------ | ------------------------------------------------ |
| **Backend**        | Django 6.0.3 + Django REST Framework 3.16.0      |
| **Database**       | PostgreSQL                                       |
| **Authentication** | Supabase Auth (JWT)                              |
| **API Docs**       | drf-spectacular (OpenAPI 3.0, Swagger, ReDoc)    |
| **Backend deploy** | Render (Gunicorn + WhiteNoise)                   |
| **Frontend**       | Separate React application                        |
| **Containerisation** | Docker Compose (PostgreSQL + Backend)           |

---

## Getting Started

### Option A — Docker (Recommended)

> **Backend requirement:** [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed.

```bash
# 1. Clone
git clone https://github.com/captain-07/CSEHub.git
cd CSEHub

# 2. Create env file and fill in your secrets (see Environment Variables below)
cp backend/.env.example backend/.env

# 3a. Using a CLOUD database — DATABASE_URL is set in backend/.env
docker compose up --build backend

# 3b. Using the bundled LOCAL PostgreSQL — leave DATABASE_URL blank
docker compose --profile localdb up --build backend
```

**Which one runs is decided by `DATABASE_URL` in `backend/.env`, not by a flag:**

| `DATABASE_URL` | Database used | `db` container | Command |
|----------------|---------------|----------------|---------|
| set (e.g. Supabase) | cloud Postgres | **not started** | `docker compose up --build backend` |
| empty / whitespace | bundled Postgres 16 | started | `docker compose --profile localdb up --build backend` |

This matches `backend/core/settings.py` exactly — an empty or whitespace-only
`DATABASE_URL` counts as "not set", so the `DB_*` fallback takes over. The
backend logs which one it picked on every start, and the local `db` service sits
behind the `localdb` profile so a cloud run never boots an unused container.

> If you already run Postgres on port 5432, set `DB_PUBLISHED_PORT` in
> `backend/.env` to a free port (e.g. `5433`).

| URL | What |
|-----|------|
| http://localhost:8000/api/docs/ | Swagger API docs (direct to backend) |
| http://localhost:8000/admin/ | Django admin panel |

**What happens automatically:** backend starts → resolves the database → waits
for it to accept connections → runs migrations → starts
Gunicorn. The React frontend runs separately and connects to
`http://localhost:8000/api`.

The cleanup migration removes the old article, category, tag, and chatbot database
tables and their contents. Subject cards start empty and are created from the
staff-only `/admin` subject manager.

```bash
# Useful Docker commands
docker compose up --build -d backend # Run backend in background (cloud DB)
docker compose logs -f backend   # Follow backend logs
docker compose down              # Stop the backend
docker compose down -v           # Stop + delete the local database volume (full reset)

# Run Django management commands inside the container
docker compose exec backend python backend/manage.py shell
docker compose exec backend python backend/manage.py makemigrations
docker compose exec backend python backend/manage.py migrate

# Access the local PostgreSQL directly (only with --profile localdb)
docker compose --profile localdb exec db psql -U postgres -d csehub_db
```

#### Docker Architecture

```
React frontend (localhost:5173) → Django backend (localhost:8000)
                                      └──→ DATABASE_URL if set (cloud)
                                           otherwise → PostgreSQL (db container,
                                                       --profile localdb)
```

---

### Option B — Manual Setup

**Prerequisites:** Python 3.11+, PostgreSQL (local or remote), Supabase project.

```bash
# Clone
git clone https://github.com/captain-07/CSEHub.git
cd CSEHub

# Virtual environment
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create env file and fill in values
cp backend/.env.example backend/.env

# Run migrations
python backend/manage.py migrate

# Start the backend
python backend/manage.py runserver
```

The React frontend is maintained separately from this backend repository.

---

## Environment Variables

Copy `backend/.env.example` → `backend/.env` and fill in:

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | Yes | Django secret key |
| `DEBUG` | No | `True` for local dev (default: `False`) |
| `ALLOWED_HOSTS` | No | Comma-separated hosts (default: `127.0.0.1,localhost`) |
| `DATABASE_URL` | Yes* | PostgreSQL connection string. **Takes priority** — blank/whitespace falls back to `DB_*` |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | Yes* | Fallback, only used when `DATABASE_URL` is empty |
| `DB_PUBLISHED_PORT` | No | Host port the Docker `db` service publishes to (default: `5432`) |
| `SUPABASE_JWT_SECRET` | Yes | Supabase project JWT secret |
| `SUPABASE_URL` | Yes | Supabase project URL |
| `CLOUDINARY_*` | No | Cloudinary credentials (for media uploads) |
| `CORS_ALLOWED_ORIGINS` | No | Frontend origins (include `http://localhost:5173` for Vite) |
| `CSRF_TRUSTED_ORIGINS` | No | CSRF trusted origins (include `http://localhost:5173` for Vite) |
| `DJANGO_SUPERUSER_*` | No | Auto-create superuser during build |
| `DJANGO_COLLECTSTATIC` | No | Re-run `collectstatic` on container start (default: `False`; static is baked into the image) |
| `GUNICORN_WORKERS`, `GUNICORN_TIMEOUT` | No | Gunicorn tuning for the Docker backend (defaults: `3`, `120`) |

*Either `DATABASE_URL` or the individual `DB_*` variables must be provided.*

> **Note:** When using Docker, `DB_HOST`, `DB_PORT`, `ALLOWED_HOSTS`, `CORS/CSRF` origins, and `DEBUG` are automatically overridden by `docker-compose.yml`. Just fill in the secrets.

---

## Usage

### API Documentation

Once the server is running:

- **Swagger UI** — http://localhost:8000/api/docs/
- **ReDoc** — http://localhost:8000/api/redoc/
- **OpenAPI Schema** — http://localhost:8000/api/schema/

### Management Commands

```bash
# Apply database migrations
python backend/manage.py migrate

# Create migrations after model changes
python backend/manage.py makemigrations

# Collect static files (WhiteNoise)
python backend/manage.py collectstatic --noinput
```

---

## Project Structure

```
CSEHub/
├── backend/
│   ├── apps/
│   │   ├── subjects/              # Admin-managed subject cards
│   │   │   ├── models.py
│   │   │   ├── serializers.py
│   │   │   ├── urls.py
│   │   │   └── views.py
│   │   ├── problems/              # Coding problems (models only)
│   │   │   └── models.py          # Problem, TestCase, Submission
│   │   └── users/                 # Custom user + JWT auth
│   │       ├── authentication.py  # SupabaseJWTAuthentication
│   │       ├── models.py          # Custom User (email as USERNAME_FIELD)
│   │       ├── urls.py
│   │       └── views.py           # GET/PATCH /api/me/
│   ├── core/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   ├── .env.example
│   ├── Dockerfile
│   └── manage.py
├── docker/
│   ├── backend-entrypoint.sh      # Resolve DB → wait → migrate → start
│   └── postgres-entrypoint.sh     # Maps DB_* → POSTGRES_* for the db service
├── docker-compose.yml
├── build.sh                       # Production build script (Render)
├── Procfile                       # Render process declaration
├── .dockerignore
└── requirements.txt
```

---

## API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/api/subjects/` | List subject cards | Public |
| `GET/POST` | `/api/notes/` | List or create the signed-in user's notes | Authenticated |
| `GET/PATCH/DELETE` | `/api/notes/{id}/` | Read, update, or delete an owned note | Authenticated |
| `GET/POST` | `/api/todos/` | List or create the signed-in user's tasks | Authenticated |
| `GET/PATCH/DELETE` | `/api/todos/{id}/` | Read, update, or delete an owned task | Authenticated |
| `POST` | `/api/subjects/` | Create a subject card | Public (temporary) |
| `PATCH` | `/api/subjects/{id}/` | Update a subject card | Public (temporary) |
| `DELETE` | `/api/subjects/{id}/` | Delete a subject card | Public (temporary) |
| `GET` | `/api/me/` | Current user profile | Authenticated |
| `PATCH` | `/api/me/` | Update profile | Authenticated |
| `GET` | `/api/docs/` | Swagger UI | Public |
| `GET` | `/api/redoc/` | ReDoc | Public |
| `GET` | `/api/schema/` | OpenAPI schema (JSON) | Public |
| — | `/admin/` | Django admin | Staff |

Subject cards are listed alphabetically and use page-number pagination (page size: 20).
Each subject stores a domain, title, author, publish date, subtitle, Markdown
content, and language-tagged code snippets. Inactive drafts are hidden from public
listing. Subject write operations currently require no authentication; anyone who can
reach the API can create, update, or delete subject records.
Notebook entries and tasks are persisted separately in `workspace_notes` and
`workspace_todos`, and each is scoped to the authenticated user.

**Auth:** Send `Authorization: Bearer <supabase-access-token>`. A valid JWT auto-creates/updates the matching `User` row.

---

## Deployment

### Render (Production)

The backend is deployed on Render. The separate React frontend is deployed independently.

```bash
# Full build (install → collectstatic → migrate)
bash build.sh

# Gunicorn (as defined in Procfile)
gunicorn core.wsgi:application --chdir backend --bind 0.0.0.0:${PORT:-8000}
```

**Required production env vars:** `SECRET_KEY`, `DATABASE_URL`, `SUPABASE_JWT_SECRET`, `SUPABASE_URL`, `CORS_ALLOWED_ORIGINS`.

### Docker (Local / Staging)

See [Option A — Docker](#option-a--docker-recommended) above.

---

## Contributing

We welcome contributions! Please follow the steps below to get started.

### 1. Fork the Repository

Click the **Fork** button at the top-right of the [CSEHub repo page](https://github.com/captain-07/CSEHub) to create your own copy under your GitHub account.

### 2. Clone Your Fork

```bash
git clone https://github.com/<your-username>/CSEHub.git
cd CSEHub
```

### 3. Add the Upstream Remote

This lets you pull future changes from the original repo:

```bash
git remote add upstream https://github.com/captain-07/CSEHub.git
git remote -v
# You should see:
#   origin    https://github.com/<your-username>/CSEHub.git (fetch/push)
#   upstream  https://github.com/captain-07/CSEHub.git    (fetch/push)
```

### 4. Set Up Your Local Environment

```bash
# Create and activate a virtual environment
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy the env template and fill in your secrets (see Environment Variables above)
cp backend/.env.example backend/.env
# Set DEBUG=True for local development

# Run migrations
python backend/manage.py migrate

# Start the dev server — verify everything works
python backend/manage.py runserver
```

> **Using Docker instead?** See [Option A — Docker](#option-a--docker-recommended) above — the same setup, just inside a container.

### 5. Keep Your Fork in Sync

Before starting new work, always sync with upstream:

```bash
git checkout dev
git fetch upstream
git merge upstream/dev
git push origin dev
```

### 6. Create a Feature Branch

Always branch off `dev` (not `main`). Use the naming convention below:

```bash
git checkout dev
git checkout -b <type>/<short-description>
```

| Prefix | Use for |
|--------|---------|
| `feature/` | New features (`feature/problem-submissions`) |
| `fix/` | Bug fixes (`fix/subject-search`) |
| `docs/` | Documentation only (`docs/update-api-endpoints`) |
| `refactor/` | Code restructuring (`refactor/serializer-cleanup`) |
| `test/` | Adding or updating tests (`test/subject-viewset`) |
| `chore/` | Build, CI, tooling changes (`chore/docker-healthcheck`) |

### 7. Make Your Changes

- Keep commits focused and atomic — one logical change per commit.
- **Do not** modify `backend/.env` (it's gitignored). Edit `.env.example` if you add new variables.
- Preserve existing comments and docstrings that are unrelated to your changes.

#### Commit Message Format

```
<type>: <short summary in imperative mood>

# Examples:
feat: add submission endpoint for coding problems
fix: handle empty subject search query
docs: add API auth section to README
test: add viewset tests for categories
refactor: simplify subject catalog
```

### 8. Run the Tests

Make sure all tests pass before pushing:

```bash
python backend/manage.py test
```

If you added new functionality, **write tests** for it. Tests use Django's built-in `TestCase` (not pytest).

### 9. Push to Your Fork

```bash
git push origin <type>/<short-description>
```

### 10. Open a Pull Request

1. Go to your fork on GitHub.
2. Click **"Compare & pull request"**.
3. Set the base branch to **`captain-07/CSEHub` → `dev`** (not `main`).
4. Fill in the PR template:
   - **What** does this PR do?
   - **Why** is this change needed?
   - **How** can a reviewer test it?
   - Link any related issues (e.g., `Closes #42`).
5. Request a review from a maintainer.

> **Important:** PRs should target the `dev` branch. The `main` branch is for production releases only.

### Ground Rules

- Be respectful and constructive in code reviews and discussions.
- Keep PRs small and focused — it's easier to review and merge.
- If you're working on something big, open an issue first to discuss the approach.
- Don't push directly to `main` or `dev` on the upstream repo.

---

## License

Distributed under the MIT License. See `LICENSE` for more information.