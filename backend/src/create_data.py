import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from housing.models import Anuncio

# Crear superusuario
if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_superuser('admin', 'admin@erasmusstay.com', 'admin1234')
    print('Superusuario creado: admin / admin1234')
else:
    admin = User.objects.get(username='admin')
    print('Superusuario ya existe')

# Crear 4 anuncios de prueba
if Anuncio.objects.count() == 0:
    anuncios = [
        {
            'titulo': 'Habitacion luminosa en Sliema',
            'descripcion': 'Habitacion amplia y luminosa en el centro de Sliema. Ideal para estudiantes Erasmus. A 5 minutos del mar y bien comunicada con el resto de la isla.',
            'precio_mes': 450,
            'localizacion': 'Sliema, Malta',
            'tipo_vivienda': 'habitacion',
            'duracion_min_meses': 3,
            'duracion_max_meses': 12,
            'wifi': True,
            'terraza': False,
            'garaje': False,
            'email_contacto': 'maria@ejemplo.com',
            'publicado': True,
            'aprobado': True,
        },
        {
            'titulo': 'Estudio moderno en St. Julian',
            'descripcion': 'Estudio completamente equipado en St. Julian, zona de vida nocturna y restaurantes. Perfecto para Erasmus que buscan vivir en el centro de la accion.',
            'precio_mes': 650,
            'localizacion': "St. Julian's, Malta",
            'tipo_vivienda': 'estudio',
            'duracion_min_meses': 1,
            'duracion_max_meses': 6,
            'wifi': True,
            'terraza': True,
            'garaje': False,
            'email_contacto': 'john@ejemplo.com',
            'publicado': True,
            'aprobado': True,
        },
        {
            'titulo': 'Piso completo en Valletta',
            'descripcion': 'Precioso piso completo en la capital de Malta. Vistas al Grand Harbour. 3 habitaciones ideales para compartir entre estudiantes.',
            'precio_mes': 1200,
            'localizacion': 'Valletta, Malta',
            'tipo_vivienda': 'piso_completo',
            'duracion_min_meses': 6,
            'duracion_max_meses': 12,
            'wifi': True,
            'terraza': True,
            'garaje': True,
            'email_contacto': 'lucia@ejemplo.com',
            'publicado': True,
            'aprobado': True,
        },
        {
            'titulo': 'Habitacion en piso compartido Msida',
            'descripcion': 'Habitacion en piso compartido cerca de la Universidad de Malta. Ambiente estudiantil, a 10 minutos a pie del campus. Incluye todas las facturas.',
            'precio_mes': 380,
            'localizacion': 'Msida, Malta',
            'tipo_vivienda': 'habitacion',
            'duracion_min_meses': 3,
            'duracion_max_meses': 10,
            'wifi': True,
            'terraza': False,
            'garaje': False,
            'email_contacto': 'carlos@ejemplo.com',
            'publicado': True,
            'aprobado': True,
        },
    ]
    for data in anuncios:
        Anuncio.objects.create(propietario=admin, **data)
    print(f'{len(anuncios)} anuncios de prueba creados!')
else:
    print(f'Ya existen {Anuncio.objects.count()} anuncios en la base de datos')
