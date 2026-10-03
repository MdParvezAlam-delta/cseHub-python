#!/usr/bin/env bash
#
# Container entrypoint for the Django backend.
#
# Database priority mirrors backend/core/settings.py exactly:
#   1. DATABASE_URL present -> cloud Postgres, nothing local is started.
#   2. DATABASE_URL blank   -> the local `db` compose service (--profile localdb).
#
set -euo pipefail

cd /app/backend

# `docker compose run backend <cmd...>` and `docker compose exec` pass arguments
# through the entrypoint. Run them verbatim instead of booting the server, so
# one-off management commands don't trigger migrate/seed as a side effect.
if [ "$#" -gt 0 ]; then
    exec "$@"
fi

# Same normalisation as backend/core/settings.py:
#   str.strip() -> str.strip('\'"') -> str.strip()
# `docker compose`'s env_file passes quotes through untouched while
# python-environ removes them, so both paths must be reduced to one value here.
# DATABASE_URL=  and  DATABASE_URL="  "  therefore both count as unset.
trim() {
    local s="$1"
    s="${s#"${s%%[![:space:]]*}"}"
    s="${s%"${s##*[![:space:]]}"}"
    while [[ "$s" == \'* || "$s" == \"* ]]; do s="${s:1}"; done
    while [[ "$s" == *\' || "$s" == *\" ]]; do s="${s%?}"; done
    s="${s#"${s%%[![:space:]]*}"}"
    s="${s%"${s##*[![:space:]]}"}"
    printf '%s' "$s"
}

db_url="$(trim "${DATABASE_URL:-}")"

if [ -n "$db_url" ]; then
    # Never echo the full URL — it carries the password.
    echo "==> DATABASE_URL is set — using the cloud database."
else
    echo "==> DATABASE_URL is not set — using the local PostgreSQL at ${DB_HOST:-db}:${DB_PORT:-5432}."
    echo "    (Start it with: docker compose --profile localdb up --build)"
    for i in $(seq 1 30); do
        if python - <<'PY'
import os
import sys

import psycopg

try:
    psycopg.connect(
        dbname=os.environ.get('DB_NAME', 'csehub_db'),
        user=os.environ.get('DB_USER', 'postgres'),
        password=os.environ.get('DB_PASSWORD', 'postgres'),
        host=os.environ.get('DB_HOST', 'db'),
        port=os.environ.get('DB_PORT', '5432'),
        connect_timeout=3,
    ).close()
except Exception:
    sys.exit(1)
PY
        then
            echo "==> PostgreSQL is ready."
            break
        fi
        if [ "$i" -eq 30 ]; then
            echo "==> ERROR: PostgreSQL unreachable after 60s." >&2
            echo "    If DATABASE_URL is empty, is the db service running?" >&2
            echo "    Start it with: docker compose --profile localdb up" >&2
            exit 1
        fi
        echo "    waiting for DB... ($i/30)"
        sleep 2
    done
fi

# Static files are baked into the image; opt out only if someone mounts an
# empty volume over /app/backend/staticfiles.
if [ "${DJANGO_COLLECTSTATIC:-False}" = "True" ]; then
    echo "==> Collecting static files..."
    python manage.py collectstatic --noinput
fi

echo "==> Running migrations..."
python manage.py migrate --noinput

echo "==> Seeding database..."
python manage.py seed || echo "    Seed skipped or already seeded."

# Opt-in: re-indexing every published article into Pinecone is slow and costs
# embedding credits, so it never runs implicitly on container start.
if [ "${DJANGO_INGEST_ARTICLES:-False}" = "True" ]; then
    echo "==> Ingesting articles into Pinecone..."
    python manage.py ingest_articles || echo "    Ingestion failed; skipping."
fi

if [ -n "${DJANGO_SUPERUSER_EMAIL:-}" ] && [ -n "${DJANGO_SUPERUSER_USERNAME:-}" ] && [ -n "${DJANGO_SUPERUSER_PASSWORD:-}" ]; then
    echo "==> Creating superuser..."
    python manage.py createsuperuser \
        --noinput \
        --email "$DJANGO_SUPERUSER_EMAIL" \
        --username "$DJANGO_SUPERUSER_USERNAME" \
        2>/dev/null || echo "    Superuser already exists, skipping."
fi

echo "==> Starting Gunicorn on 0.0.0.0:8000 ..."
exec gunicorn core.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers "${GUNICORN_WORKERS:-3}" \
    --timeout "${GUNICORN_TIMEOUT:-120}" \
    --access-logfile - \
    --error-logfile -
