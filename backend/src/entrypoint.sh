#!/bin/sh
set -e

echo " Esperando a PostgreSQL..."
until python -c "
import os, psycopg2
psycopg2.connect(
    dbname=os.environ['POSTGRES_DB'],
    user=os.environ['POSTGRES_USER'],
    password=os.environ['POSTGRES_PASSWORD'],
    host=os.environ.get('DB_HOST', 'db'),
    port=os.environ.get('DB_PORT', '5432')
)
" 2>/dev/null; do
  echo "   BD no disponible, reintentando en 2s..."
  sleep 2
done

echo " PostgreSQL listo"

echo " Aplicando migraciones..."
python manage.py migrate --noinput

echo " Recolectando estáticos..."
python manage.py collectstatic --noinput --clear

echo " Seeding base de datos..."
python create_data.py

echo " Arrancando Gunicorn..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -