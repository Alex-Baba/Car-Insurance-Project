#!/usr/bin/env sh
set -euo pipefail

# Run migrations
if [ -f /app/alembic.ini ]; then
  echo "[entrypoint] Applying migrations..."
  alembic upgrade head || { echo "Migration failed"; exit 1; }
fi

# Start Gunicorn
echo "[entrypoint] Starting Gunicorn..."
exec gunicorn -b 0.0.0.0:8000 -w 3 --threads 2 --timeout 90 'app.main:create_app()'
