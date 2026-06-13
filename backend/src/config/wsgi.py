"""
Configuración WSGI del proyecto Django.

WSGI significa Web Server Gateway Interface. Es el punto de entrada que utiliza
Django cuando la aplicación se ejecuta en servidores web tradicionales de
producción.

En este proyecto, este archivo es especialmente importante para el despliegue,
porque Gunicorn carga esta variable `application` para arrancar la aplicación
Django.

Flujo habitual en producción:

Gunicorn
    ↓
config.wsgi:application
    ↓
Django
    ↓
API REST / administración / lógica del proyecto

Más información oficial:
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application


# Define qué archivo de configuración debe utilizar Django.
# En este caso apunta a config/settings.py.
# setdefault evita sobrescribir la variable si ya está definida en el entorno,
# algo útil en producción, Docker o Railway.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")


# Crea la aplicación WSGI que usará el servidor para atender peticiones HTTP.
# Esta variable debe llamarse "application" porque es el nombre que esperan
# servidores WSGI como Gunicorn o uWSGI.
application = get_wsgi_application()