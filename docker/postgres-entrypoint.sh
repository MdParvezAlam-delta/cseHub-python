#!/usr/bin/env bash
# Maps the backend's DB_* settings (backend/.env) onto the POSTGRES_* variables
# the official image expects, so the local-fallback database and the Django
# container can never end up with mismatched credentials.
set -e

export POSTGRES_DB="${DB_NAME:-csehub_db}"
export POSTGRES_USER="${DB_USER:-postgres}"
export POSTGRES_PASSWORD="${DB_PASSWORD:-postgres}"

exec /usr/local/bin/docker-entrypoint.sh postgres
