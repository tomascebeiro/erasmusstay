import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from housing.models import Anuncio, PerfilUsuario

def seed_data():
    # 1. Crear Administrador
    if not User.objects.filter(username='admin').exists():
        admin = User.objects.create_superuser('admin', 'admin@erasmusstay.com', 'admin1234')
        PerfilUsuario.objects.create(usuario=admin, rol='administrador')
        print('Admin creado: admin / admin1234')
    else:
        admin = User.objects.get(username='admin')

    # 2. Crear Propietario
    if not User.objects.filter(username='owner1').exists():
        owner = User.objects.create_user('owner1', 'owner@ejemplo.com', 'owner1234')
        PerfilUsuario.objects.create(usuario=owner, rol='propietario')
        print('Propietario creado: owner1 / owner1234')
    else:
        owner = User.objects.get(username='owner1')

    # 3. Crear Estudiante
    if not User.objects.filter(username='student1').exists():
        student = User.objects.create_user('student1', 'student@ejemplo.com', 'student1234')
        PerfilUsuario.objects.create(usuario=student, rol='estudiante')
        print('Estudiante creado: student1 / student1234')

    # 4. Crear Anuncios (Asignados al Propietario)
    if Anuncio.objects.count() == 0:
        anuncios = [
            {
                'titulo': 'Bright Room in Sliema',
                'descripcion': 'Bright and spacious room in Sliema center. Close to the sea.',
                'precio_mes': 450,
                'localizacion': 'Sliema, Malta',
                'tipo_vivienda': 'habitacion',
                'duracion_min_meses': 3,
                'duracion_max_meses': 12,
                'wifi': True,
                'aprobado': True,
            },
            {
                'titulo': 'Modern Studio in St. Julian',
                'descripcion': 'Perfect studio for Erasmus students in the heart of St. Julian.',
                'precio_mes': 650,
                'localizacion': "St. Julian's, Malta",
                'tipo_vivienda': 'estudio',
                'duracion_min_meses': 1,
                'duracion_max_meses': 6,
                'wifi': True,
                'terraza': True,
                'aprobado': True,
            }
        ]
        for data in anuncios:
            Anuncio.objects.create(propietario=owner, **data)
        print('Anuncios de prueba creados!')

if __name__ == '__main__':
    seed_data()