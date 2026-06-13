"""
Configuración ASGI del proyecto Django.

ASGI significa Asynchronous Server Gateway Interface. Es el punto de entrada que
usa Django cuando la aplicación se ejecuta en servidores compatibles con ASGI.

Este archivo permite que el proyecto pueda trabajar con servidores modernos y
soportar, si en el futuro se necesitase, funcionalidades asíncronas como:

- WebSockets;
- tareas en tiempo real;
- notificaciones instantáneas;
- conexiones persistentes.

En esta versión del proyecto, la aplicación funciona principalmente como API
REST tradicional, pero Django mantiene este archivo como parte estándar de la
configuración del proyecto.

Más información oficial:
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application


# Define qué archivo de configuración debe utilizar Django.
# En este caso apunta a config/settings.py.
# setdefault evita sobrescribir la variable si ya está definida en el entorno,
# algo útil en producción, Docker o Railway.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")


# Crea la aplicación ASGI que usará el servidor para atender peticiones.
# Esta variable debe llamarse "application" porque es el nombre que esperan
# servidores ASGI como Daphne, Uvicorn o Hypercorn.
application = get_asgi_application()