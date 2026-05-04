#!/bin/sh

echo "Ejecutando migraciones..."
python manage.py migrate --noinput

echo "Creando superusuario si no existe..."
python manage.py shell << 'PYEOF'
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@erasmusstay.com', 'admin1234')
    print('Superusuario creado: admin / admin1234')
else:
    print('El superusuario ya existe')
PYEOF

echo "Arrancando servidor..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
