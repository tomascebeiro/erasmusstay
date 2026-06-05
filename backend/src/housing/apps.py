from django.apps import AppConfig


# Configuración básica de la aplicación Django 'housing'.
# Se registra en el proyecto principal para poder usar los modelos,
# vistas y señales de este módulo.
class HousingConfig(AppConfig):
    # Define el tipo de campo primario que Django usará por defecto.
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'housing'
