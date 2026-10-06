# CSEHub Backend

Django REST API for CSEHub. It provides the subject catalog, account profiles, and private notes and to-do lists for the React frontend.

## Features

- Django 6 and Django REST Framework API
- PostgreSQL storage
- Supabase JWT authentication, with local email/password authentication for development
- Public subject browsing and subject publishing endpoints
- User-owned notes and to-do items
- OpenAPI schema, Swagger UI, and ReDoc
- Docker Compose support for the backend and optional local PostgreSQL

## Requirements

- Python 3.12 or later (the production Docker image uses Python 3.12)
- PostgreSQL, or Docker Desktop for the bundled local database
- Supabase project settings for Supabase authentication

## Fork and run locally

1. Fork this repository on GitHub, then clone **your fork**:

   ```bash
   git clone https://github.com/<your-account>/<your-backend-repository>.git
   cd <your-backend-repository>
   ```

2. Configure the backend's required runtime variables using your local environment or a private, ignored local configuration file. Do not commit credentials. Required settings are:

   - `SECRET_KEY`
   - `SUPABASE_URL` and `SUPABASE_JWT_SECRET`
   - Either `DATABASE_URL` or the PostgreSQL `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, and `DB_PORT` settings

   For local development, set `DEBUG=True`. Configure `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, and `CSRF_TRUSTED_ORIGINS` for the local frontend origin `http://localhost:5173`.

3. Choose one way to run PostgreSQL and start the API.

   **Docker (recommended):** Docker Compose reads the backend's local runtime configuration. Use the optional `localdb` profile for the bundled PostgreSQL; without it, configure a reachable database with `DATABASE_URL`.

   ```bash
   docker compose --profile localdb up --build backend
   ```

   **Python:** Create a virtual environment and install dependencies:

   ```bash
   # Windows PowerShell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1

   # macOS / Linux
   python3 -m venv .venv
   source .venv/bin/activate

   python -m pip install -r requirements.txt
   python backend/manage.py migrate
   python backend/manage.py runserver
   ```

   The Python option requires PostgreSQL to be running and the required settings to be available to the process.

4. Check the API at `http://localhost:8000/api/`. API documentation is available at:

   - Swagger UI: `http://localhost:8000/api/docs/`
   - ReDoc: `http://localhost:8000/api/redoc/`
   - OpenAPI schema: `http://localhost:8000/api/schema/`
   - Django administration: `http://localhost:8000/admin/`

When using Docker, migrations run automatically at container startup. The local database is persisted in a Docker volume. To stop the stack, run `docker compose down`. Removing the volume deletes local database data.

## Configuration reference

Set configuration in the runtime environment or your deployment platform; never commit secret values.

| Setting | Purpose |
|---|---|
| `SECRET_KEY` | Django signing and security key |
| `DEBUG` | Enables development behavior; keep disabled in production |
| `SUPABASE_URL`, `SUPABASE_JWT_SECRET` | Validate Supabase-authenticated requests |
| `DATABASE_URL` | Preferred PostgreSQL connection string |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | PostgreSQL fallback when `DATABASE_URL` is not set |
| `ALLOWED_HOSTS` | Accepted host names |
| `CORS_ALLOWED_ORIGINS`, `CSRF_TRUSTED_ORIGINS` | Allowed browser origins |
| `LOCAL_AUTH_ENABLED` | Enables the local development sign-up/sign-in API |
| `DJANGO_SUPERUSER_EMAIL`, `DJANGO_SUPERUSER_USERNAME`, `DJANGO_SUPERUSER_PASSWORD` | Optional Docker startup superuser |
| `GUNICORN_WORKERS`, `GUNICORN_TIMEOUT` | Optional container Gunicorn tuning |

The Docker Compose configuration provides local CORS/host defaults. In production, configure the deployed frontend origin and database connection in the backend service settings.

## API overview

| Endpoint | Description | Access |
|---|---|---|
| `GET /api/subjects/` | List active subjects (paginated) | Public |
| `POST /api/subjects/` | Create a subject | Public in the current backend configuration |
| `GET`, `PATCH`, `DELETE /api/subjects/{id}/` | Retrieve, edit, or delete a subject | Public in the current backend configuration |
| `GET`, `PATCH /api/me/` | Read or update the authenticated profile | Authenticated |
| `GET`, `POST /api/notes/` | List or create the current user's notes | Authenticated |
| `GET`, `PATCH`, `DELETE /api/notes/{id}/` | Read, edit, or delete an owned note | Authenticated |
| `GET`, `POST /api/todos/` | List or create the current user's tasks | Authenticated |
| `GET`, `PATCH`, `DELETE /api/todos/{id}/` | Read, edit, or delete an owned task | Authenticated |
| `POST /api/auth/signup/`, `/api/auth/signin/` | Local development authentication | Local development |

**Security note:** subject write endpoints currently allow unauthenticated access. Restrict these permissions before using the API for a public production service.

The frontend is maintained separately in the CSEHub React frontend repository. Set its API base URL to the deployed backend or local API address.

## Project structure

```text
.
├── backend/
│   ├── apps/
│   │   ├── subjects/       # Subject models, API, and tests
│   │   ├── users/          # Custom user, Supabase JWT, local auth, profiles
│   │   ├── workspace/      # User-owned notes and to-do APIs
│   │   ├── problems/       # Problem-related models
│   │   ├── articles/       # Legacy app retained for migrations
│   │   └── chatbot/        # Legacy app retained for migrations
│   ├── core/               # Django settings, URLs, WSGI/ASGI
│   ├── Dockerfile
│   └── manage.py
├── docker/                 # Backend and PostgreSQL startup scripts
├── docker-compose.yml
├── requirements.txt
├── build.sh                # Render build command
└── Procfile                # Gunicorn web process
```

## Development commands

Run these from the repository root with the virtual environment activated:

```bash
python backend/manage.py test
python backend/manage.py makemigrations
python backend/manage.py migrate
python backend/manage.py collectstatic --noinput
```

The Render process command is:

```bash
gunicorn core.wsgi:application --chdir backend --bind 0.0.0.0:$PORT
```

## Contributing

Create a branch from your fork, make focused changes, and run the relevant tests before opening a pull request. Keep credentials and private runtime configuration out of commits.
