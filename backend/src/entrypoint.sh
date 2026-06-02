#!/bin/sh
set -e

echo "Iniciando backend de ErasmusStay..."

echo "Comprobando conexión con la base de datos..."
python - <<'PY'
import os
import time
import psycopg2
import dj_database_url

database_url = os.environ.get("DATABASE_URL")

if database_url:
    config = dj_database_url.parse(database_url)
    dbname = config.get("NAME")
    user = config.get("USER")
    password = config.get("PASSWORD")
    host = config.get("HOST")
    port = config.get("PORT") or 5432
else:
    dbname = os.environ.get("POSTGRES_DB", "erasmusstay")
    user = os.environ.get("POSTGRES_USER", "postgres")
    password = os.environ.get("POSTGRES_PASSWORD", "abc123.")
    host = os.environ.get("DB_HOST", "localhost")
    port = os.environ.get("DB_PORT", "5432")

for intento in range(30):
    try:
        psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port,
        ).close()
        print("Base de datos disponible.")
        break
    except Exception as exc:
        print(f"Base de datos no disponible todavía. Reintento {intento + 1}/30...")
        time.sleep(2)
else:
    raise RuntimeError("No se pudo conectar con la base de datos.")
PY

echo "Aplicando migraciones..."
python manage.py migrate --noinput

echo "Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

if [ "$RUN_SEED" = "true" ]; then
    echo "Cargando datos iniciales..."
    python create_data.py
else
    echo "Seed desactivado. Para activarlo, usa RUN_SEED=true una sola vez."
fi

echo "Arrancando Gunicorn..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers ${WEB_CONCURRENCY:-2} \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -