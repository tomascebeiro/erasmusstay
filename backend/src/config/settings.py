from pathlib import Path
import os

import dj_database_url
from dotenv import load_dotenv


# ---------------------------------------------------------------------
# RUTAS BASE DEL PROYECTO
# ---------------------------------------------------------------------
# Este archivo está en:
# backend/src/config/settings.py
#
# BASE_DIR apunta a:
# backend/src
#
# ENV_DIR apunta a:
# backend
# ---------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_DIR = BASE_DIR.parent

load_dotenv(ENV_DIR / ".env")


# ---------------------------------------------------------------------
# UTILIDADES PARA LEER VARIABLES DE ENTORNO
# ---------------------------------------------------------------------

def env_bool(name, default=False):
    """
    Convierte una variable de entorno en booleano.

    Acepta:
    true, 1, yes, si, sí, on
    """
    value = os.environ.get(name)

    if value is None:
        return default

    return value.strip().lower() in ["true", "1", "yes", "si", "sí", "on"]


def env_list(name, default=""):
    """
    Convierte una variable de entorno separada por comas en una lista.

    Ejemplo:
    ALLOWED_HOSTS=localhost,127.0.0.1,.railway.app
    """
    return [
        item.strip()
        for item in os.environ.get(name, default).split(",")
        if item.strip()
    ]


# ---------------------------------------------------------------------
# CONFIGURACIÓN GENERAL
# ---------------------------------------------------------------------

SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "django-insecure-local-development-key-change-in-production",
)

DEBUG = env_bool("DEBUG", True)

ALLOWED_HOSTS = env_list(
    "ALLOWED_HOSTS",
    "localhost,127.0.0.1,.railway.app",
)


# ---------------------------------------------------------------------
# APLICACIONES INSTALADAS
# ---------------------------------------------------------------------

INSTALLED_APPS = [
    # Apps internas de Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Librerías externas
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",

    # Apps propias
    "housing",
]


# ---------------------------------------------------------------------
# MIDDLEWARE
# ---------------------------------------------------------------------
# CorsMiddleware debe ir lo más arriba posible.
# WhiteNoise debe ir justo después de SecurityMiddleware.
# WhiteNoise permite servir los archivos estáticos en producción.
# ---------------------------------------------------------------------

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",

    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


ROOT_URLCONF = "config.urls"


# ---------------------------------------------------------------------
# TEMPLATES
# ---------------------------------------------------------------------
# Aunque el frontend principal sea Vue, Django necesita templates para
# el panel de administración y algunas partes internas.
# ---------------------------------------------------------------------

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


WSGI_APPLICATION = "config.wsgi.application"


# ---------------------------------------------------------------------
# BASE DE DATOS
# ---------------------------------------------------------------------
# En local tienes dos opciones:
#
# 1) Usar PostgreSQL local con variables:
#    POSTGRES_DB=erasmusstay
#    POSTGRES_USER=postgres
#    POSTGRES_PASSWORD=abc123.
#    DB_HOST=localhost
#    DB_PORT=5432
#
# 2) Usar DATABASE_URL:
#    DATABASE_URL=postgres://postgres:abc123.@localhost:5432/erasmusstay
#
# En Railway se usará DATABASE_URL automáticamente desde PostgreSQL.
# ---------------------------------------------------------------------

DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            ssl_require=not DEBUG,
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("POSTGRES_DB", "erasmusstay"),
            "USER": os.environ.get("POSTGRES_USER", "postgres"),
            "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "abc123."),
            "HOST": os.environ.get("DB_HOST", "localhost"),
            "PORT": os.environ.get("DB_PORT", "5432"),
        }
    }


# ---------------------------------------------------------------------
# VALIDADORES DE CONTRASEÑA
# ---------------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# ---------------------------------------------------------------------
# INTERNACIONALIZACIÓN
# ---------------------------------------------------------------------

LANGUAGE_CODE = "es-es"
TIME_ZONE = "Europe/Madrid"
USE_I18N = True
USE_TZ = True


# ---------------------------------------------------------------------
# ARCHIVOS ESTÁTICOS
# ---------------------------------------------------------------------
# STATIC_URL:
# URL pública para archivos estáticos.
#
# STATIC_ROOT:
# Carpeta donde collectstatic junta todos los estáticos.
#
# STORAGES:
# Configuración moderna de Django para WhiteNoise.
# ---------------------------------------------------------------------

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}


# ---------------------------------------------------------------------
# ARCHIVOS MULTIMEDIA
# ---------------------------------------------------------------------
# En local funciona con carpeta media.
#
# En Railway, si no configuras un volumen o bucket, los archivos subidos
# pueden perderse al redesplegar. Para el TFC te puede valer, pero para
# producción real habría que usar almacenamiento persistente.
# ---------------------------------------------------------------------

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# ---------------------------------------------------------------------
# CORS Y CSRF
# ---------------------------------------------------------------------
# CORS_ALLOWED_ORIGINS:
# dominios desde los que el frontend puede llamar a la API.
#
# CSRF_TRUSTED_ORIGINS:
# dominios de confianza para peticiones seguras.
# ---------------------------------------------------------------------

CORS_ALLOWED_ORIGINS = env_list(
    "CORS_ALLOWED_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173,http://localhost:8080,http://127.0.0.1:8080",
)

CSRF_TRUSTED_ORIGINS = env_list(
    "CSRF_TRUSTED_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173,http://localhost:8000,http://127.0.0.1:8000",
)

CORS_ALLOW_CREDENTIALS = True


# ---------------------------------------------------------------------
# DJANGO REST FRAMEWORK
# ---------------------------------------------------------------------

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
}


# ---------------------------------------------------------------------
# CLAVE PRIMARIA POR DEFECTO
# ---------------------------------------------------------------------

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ---------------------------------------------------------------------
# AJUSTES DE SEGURIDAD EN PRODUCCIÓN
# ---------------------------------------------------------------------
# Solo se activan cuando DEBUG=False.
# En Railway normalmente tendrás DEBUG=False.
# ---------------------------------------------------------------------

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True