# CSEHub

A computer-science learning platform — Django REST API + static frontend.  
Educational articles with code snippets, a per-article **RAG chatbot** (Pinecone + Gemini), and **Supabase-backed** user accounts.

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
  - [Frontend Pages](#frontend-pages)
  - [API Documentation](#api-documentation)
  - [Management Commands](#management-commands)
- [Project Structure](#project-structure)
- [API Endpoints](#api-endpoints)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

---

## Features

| Feature | Status |
|---------|--------|
| **Article library** — Browse, filter, search published articles by category/tag, with embedded code snippets | ✅ Mature |
| **AI article assistant** — Authenticated RAG chatbot (Pinecone + Gemini) scoped to a single article, with persisted conversation history | ✅ Implemented |
| **Supabase Auth** — JWT authentication; the API auto-provisions a local `User` from a valid Bearer token | ✅ Implemented |
| **User profile** — `GET`/`PATCH /api/me/` for display name, username, and avatar | ✅ Implemented |
| **Static frontend** — HTML/CSS/JS client (home, articles, article + chat, login, profile) | ✅ Implemented |
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
| **RAG Pipeline**   | LangChain + Pinecone (vector DB) + Google Gemini |
| **Backend deploy** | Render (Gunicorn + WhiteNoise)                   |
| **Frontend**       | Static HTML/CSS/JS + Nginx (Docker) or Vercel    |
| **Containerisation** | Docker Compose (PostgreSQL + Backend + Frontend) |

---

## Getting Started

### Option A — Docker (Recommended)

> **Only requirement:** [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed.  
> No Python, no PostgreSQL, no Node.js needed.

```bash
# 1. Clone
git clone https://github.com/captain-07/CSEHub.git
cd CSEHub

# 2. Create env file and fill in your secrets (see Environment Variables below)
cp backend/.env.example backend/.env

# 3a. Using a CLOUD database — DATABASE_URL is set in backend/.env
docker compose up --build

# 3b. Using the bundled LOCAL PostgreSQL — leave DATABASE_URL blank
docker compose --profile localdb up --build
```

**Which one runs is decided by `DATABASE_URL` in `backend/.env`, not by a flag:**

| `DATABASE_URL` | Database used | `db` container | Command |
|----------------|---------------|----------------|---------|
| set (e.g. Supabase) | cloud Postgres | **not started** | `docker compose up --build` |
| empty / whitespace | bundled Postgres 16 | started | `docker compose --profile localdb up --build` |

This matches `backend/core/settings.py` exactly — an empty or whitespace-only
`DATABASE_URL` counts as "not set", so the `DB_*` fallback takes over. The
backend logs which one it picked on every start, and the local `db` service sits
behind the `localdb` profile so a cloud run never boots an unused container.

> If you already run Postgres on port 5432, set `DB_PUBLISHED_PORT` in
> `backend/.env` to a free port (e.g. `5433`).

| URL | What |
|-----|------|
| http://localhost:3000 | **Frontend** (main site, proxies `/api/` and `/admin/`) |
| http://localhost:3000/api/docs/ | Swagger API docs (via the frontend proxy) |
| http://localhost:8000/api/docs/ | Swagger API docs (direct to backend) |
| http://localhost:8000/admin/ | Django admin panel |

**What happens automatically:** backend starts → resolves the database → waits
for it to accept connections → runs migrations → seeds sample data → starts
Gunicorn → Nginx serves the frontend and proxies `/api/` to the backend.

```bash
# Useful Docker commands
docker compose up --build -d     # Run in background (cloud DB)
docker compose logs -f backend   # Follow backend logs
docker compose down              # Stop everything
docker compose down -v           # Stop + delete the local database volume (full reset)

# Run Django management commands inside the container
docker compose exec backend python backend/manage.py shell
docker compose exec backend python backend/manage.py makemigrations
docker compose exec backend python backend/manage.py migrate

# Rebuild the Pinecone index for the chatbot (opt-in; costs embedding credits)
docker compose exec backend python backend/manage.py ingest_articles

# Access the local PostgreSQL directly (only with --profile localdb)
docker compose --profile localdb exec db psql -U postgres -d csehub_db
```

#### Docker Architecture

```
Browser (localhost:3000)
  └─→ Nginx (frontend container)
        ├── Static files (HTML/CSS/JS)
        ├── /api/*   ─┐
        ├── /admin/*  ─┼→ proxy → Gunicorn (backend container)
        └── /static/* ─┘              │
                                       └──→ DATABASE_URL if set (cloud)
                                           otherwise → PostgreSQL (db container,
                                                       --profile localdb)
```

---

### Option B — Manual Setup

**Prerequisites:** Python 3.11+, PostgreSQL (local or remote), Supabase project, Pinecone index, Gemini API key.

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

# Run migrations and seed data
python backend/manage.py migrate
python backend/manage.py seed

# Start the backend
python backend/manage.py runserver
```

For the frontend, serve it with any static file server:

```bash
python -m http.server 3000 --directory frontend
```

Open http://localhost:3000. The frontend auto-detects `localhost` and proxies API calls to the backend.

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
| `PINECONE_API_KEY` | Yes | Pinecone API key |
| `PINECONE_INDEX_NAME` | Yes | Pinecone index for article embeddings |
| `GEMINI_API_KEY` | Yes | Google Gemini API key |
| `CLOUDINARY_*` | No | Cloudinary credentials (for media uploads) |
| `CORS_ALLOWED_ORIGINS` | No | Frontend origins (default: `http://localhost:3000`) |
| `CSRF_TRUSTED_ORIGINS` | No | CSRF trusted origins (default: `http://localhost:3000`) |
| `DJANGO_SUPERUSER_*` | No | Auto-create superuser during build |
| `DJANGO_COLLECTSTATIC` | No | Re-run `collectstatic` on container start (default: `False`; static is baked into the image) |
| `DJANGO_INGEST_ARTICLES` | No | Re-embed published articles into Pinecone on container start (default: `False`) |
| `GUNICORN_WORKERS`, `GUNICORN_TIMEOUT` | No | Gunicorn tuning for the Docker backend (defaults: `3`, `120`) |

*Either `DATABASE_URL` or the individual `DB_*` variables must be provided.*

> **Note:** When using Docker, `DB_HOST`, `DB_PORT`, `ALLOWED_HOSTS`, `CORS/CSRF` origins, and `DEBUG` are automatically overridden by `docker-compose.yml`. Just fill in the secrets.

---

## Usage

### Frontend Pages

| File | Route | Description |
|------|-------|-------------|
| `index.html` | `/` | Home / landing page |
| `articles.html` | `/articles` | Article library with search and filters |
| `article.html` | `/article` | Article detail + RAG chat sidebar |
| `login.html` | `/login` | Sign in / sign up (Supabase) |
| `profile.html` | `/profile` | Current user profile |

### API Documentation

Once the server is running:

- **Swagger UI** — http://localhost:8000/api/docs/
- **ReDoc** — http://localhost:8000/api/redoc/
- **OpenAPI Schema** — http://localhost:8000/api/schema/

### Management Commands

```bash
# Apply database migrations
python backend/manage.py migrate

# Seed sample categories, tags, and articles (idempotent)
python backend/manage.py seed

# Ingest all published articles into Pinecone (embeddings for RAG)
python backend/manage.py ingest_articles

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
│   │   ├── articles/              # Article CRUD (mature)
│   │   │   ├── management/commands/seed.py
│   │   │   ├── models.py          # Category, Tag, Article, CodeSnippet
│   │   │   ├── serializers.py
│   │   │   ├── urls.py
│   │   │   └── views.py
│   │   ├── chatbot/               # RAG chatbot (implemented)
│   │   │   ├── management/commands/ingest_articles.py
│   │   │   ├── ingestion.py       # Pinecone embeddings
│   │   │   ├── rag_chat.py        # Gemini grounded answers
│   │   │   ├── signals.py         # Re-ingest on article save
│   │   │   ├── models.py          # Conversation, Message
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
├── frontend/
│   ├── index.html
│   ├── articles.html
│   ├── article.html
│   ├── login.html
│   ├── profile.html
│   ├── css/
│   ├── js/
│   ├── Dockerfile
│   └── vercel.json
├── docker/
│   ├── nginx.conf                 # Frontend Nginx config + API proxy
│   ├── backend-entrypoint.sh      # Resolve DB → wait → migrate → seed → start
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
| `GET` | `/api/articles/` | List published articles | Public |
| `GET` | `/api/articles/{id}/` | Article detail with content and snippets | Public |
| `POST` | `/api/articles/` | Create article | Admin |
| `PUT`/`PATCH` | `/api/articles/{id}/` | Update article | Admin |
| `DELETE` | `/api/articles/{id}/` | Delete article | Admin |
| `GET` | `/api/categories/` | List categories | Public |
| `GET` | `/api/categories/{id}/` | Category detail | Public |
| `GET` | `/api/tags/` | List tags | Public |
| `GET` | `/api/tags/{id}/` | Tag detail | Public |
| `GET` | `/api/me/` | Current user profile | Authenticated |
| `PATCH` | `/api/me/` | Update profile | Authenticated |
| `POST` | `/api/articles/{slug}/ask/` | Ask a question about an article (RAG) | Authenticated |
| `GET` | `/api/articles/{slug}/conversation/` | Load conversation for an article | Authenticated |
| `GET` | `/api/docs/` | Swagger UI | Public |
| `GET` | `/api/redoc/` | ReDoc | Public |
| `GET` | `/api/schema/` | OpenAPI schema (JSON) | Public |
| — | `/admin/` | Django admin | Staff |

**Filtering & search** on `/api/articles/`:
- Filter by `category__slug`, `tags__slug`
- Search on `title`, `content`
- Order by `created_at` (default: newest first)
- Page-number pagination (page size: 20)

**Auth:** Send `Authorization: Bearer <supabase-access-token>`. A valid JWT auto-creates/updates the matching `User` row.

---

## Deployment

### Render (Production)

The backend is deployed on Render. The frontend is a static Vercel site.

```bash
# Full build (install → collectstatic → migrate → seed → ingest)
bash build.sh

# Gunicorn (as defined in Procfile)
gunicorn core.wsgi:application --chdir backend --bind 0.0.0.0:${PORT:-8000}
```

**Required production env vars:** `SECRET_KEY`, `DATABASE_URL`, `SUPABASE_JWT_SECRET`, `SUPABASE_URL`, `PINECONE_API_KEY`, `PINECONE_INDEX_NAME`, `GEMINI_API_KEY`, `CORS_ALLOWED_ORIGINS`.

### Docker (Local / Staging)

See [Option A — Docker](#option-a--docker-recommended) above.

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

Distributed under the MIT License. See `LICENSE` for more information.