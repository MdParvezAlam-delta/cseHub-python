FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# psycopg[binary] ships its own libpq, so no build toolchain is needed.

# Copy requirements first (Docker layer caching)
COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy the backend source code
COPY backend/ /app/backend/
COPY docker/backend-entrypoint.sh /app/backend-entrypoint.sh

# Bake the static manifest into the image so container start-up doesn't have to
# run collectstatic. The placeholder secrets below are build-time only — they
# never reach the runtime environment (real values come from backend/.env via
# docker-compose `env_file`) and do not affect the generated manifest.
RUN SECRET_KEY=build-only-not-a-secret \
    DEBUG=False \
    SUPABASE_JWT_SECRET=build-only \
    SUPABASE_URL=https://build.invalid \
    PINECONE_API_KEY=build-only \
    PINECONE_INDEX_NAME=build-only \
    GEMINI_API_KEY=build-only \
    python backend/manage.py collectstatic --noinput

# Run as an unprivileged user
RUN chmod +x /app/backend-entrypoint.sh \
    && useradd --create-home --uid 1000 --shell /usr/sbin/nologin appuser \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

ENTRYPOINT ["/app/backend-entrypoint.sh"]
