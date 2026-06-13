"""
Seeder de datos iniciales para ErasmusStay.

Este archivo crea datos de prueba para que la aplicación pueda probarse sin
tener que introducir usuarios, anuncios, imágenes, valoraciones y solicitudes
manualmente desde el frontend o desde el panel de administración.

IMPORTANTE:
En esta versión del seeder, las imágenes de los anuncios se cargan mediante
URLs externas de Unsplash y se guardan en el campo `imagen_url` del modelo
ImagenAnuncio.

Esto significa que estas imágenes no se almacenan físicamente dentro del
proyecto ni dentro de MEDIA_ROOT. Sirven como imágenes de demostración para
poblar rápidamente la aplicación con anuncios visuales.

Flujo general del seeder:

1. Configura Django para poder usar modelos fuera del servidor.
2. Crea usuarios de prueba:
   - administrador;
   - propietarios;
   - estudiantes.
3. Crea o actualiza los perfiles de esos usuarios.
4. Crea anuncios de ejemplo asociados a propietarios.
5. Asocia imágenes externas de Unsplash a cada anuncio.
6. Crea valoraciones de prueba, algunas aprobadas y otra pendiente.
7. Crea solicitudes de contacto de ejemplo.
8. Imprime por consola las credenciales de prueba.

Uso:

    python create_data.py

Desde Docker:

    docker compose exec backend python create_data.py
"""

import os
import django


# Define el módulo de configuración de Django.
# Es necesario porque este archivo se ejecuta como script independiente,
# no desde manage.py directamente.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")


# Inicializa Django para poder importar modelos y trabajar con la base de datos.
django.setup()


from django.contrib.auth.models import User
from housing.models import (
    Anuncio,
    ImagenAnuncio,
    PerfilUsuario,
    SolicitudContacto,
    Valoracion,
)


def get_or_create_profile(user, rol, telefono=""):
    """
    Crea o actualiza el perfil asociado a un usuario.

    Parámetros:
    - user: usuario nativo de Django.
    - rol: tipo de usuario dentro de ErasmusStay.
    - telefono: teléfono de contacto asociado al perfil.

    Funcionamiento:
    1. Busca si el usuario ya tiene PerfilUsuario.
    2. Si no existe, lo crea con rol y teléfono.
    3. Si existe, actualiza rol y teléfono.
    4. Guarda los cambios.
    5. Devuelve el perfil.

    Se usa en el seeder para garantizar que todos los usuarios de prueba tengan
    un perfil correcto y consistente.
    """
    perfil, created = PerfilUsuario.objects.get_or_create(
        usuario=user,
        defaults={
            "rol": rol,
            "telefono": telefono,
        },
    )

    perfil.rol = rol
    perfil.telefono = telefono
    perfil.save()

    return perfil


def seed_users():
    """
    Crea los usuarios principales de prueba.

    Usuarios creados o actualizados:
    - admin: usuario administrador con permisos de staff y superusuario.
    - owner1: propietario de anuncios.
    - owner2: segundo propietario de anuncios.
    - student1: estudiante que puede solicitar contacto y valorar.
    - student2: segundo estudiante.

    La función usa get_or_create para evitar duplicar usuarios si el seeder se
    ejecuta varias veces. Si el usuario ya existe, se actualizan sus datos
    principales.

    Devuelve un diccionario con los usuarios creados para que otras funciones
    puedan reutilizarlos al crear anuncios, valoraciones y solicitudes.
    """
    admin, created = User.objects.get_or_create(
        username="admin",
        defaults={
            "email": "admin@erasmusstay.com",
            "is_staff": True,
            "is_superuser": True,
        },
    )

    # Si el usuario acaba de crearse, se asigna contraseña.
    # No se reasigna en cada ejecución para evitar pisar cambios manuales.
    if created:
        admin.set_password("admin1234")

    # Se fuerzan permisos administrativos por si el usuario ya existía.
    admin.is_staff = True
    admin.is_superuser = True
    admin.is_active = True
    admin.email = "admin@erasmusstay.com"
    admin.save()

    # Perfil extendido del administrador.
    get_or_create_profile(admin, "administrador", "+356 9900 0000")

    owner1, created = User.objects.get_or_create(
        username="owner1",
        defaults={
            "email": "owner1@ejemplo.com",
        },
    )

    if created:
        owner1.set_password("owner1234")

    owner1.email = "owner1@ejemplo.com"
    owner1.is_active = True
    owner1.save()

    # Perfil del primer propietario.
    get_or_create_profile(owner1, "propietario", "+356 9911 2233")

    owner2, created = User.objects.get_or_create(
        username="owner2",
        defaults={
            "email": "owner2@ejemplo.com",
        },
    )

    if created:
        owner2.set_password("owner1234")

    owner2.email = "owner2@ejemplo.com"
    owner2.is_active = True
    owner2.save()

    # Perfil del segundo propietario.
    get_or_create_profile(owner2, "propietario", "+356 9944 5566")

    student1, created = User.objects.get_or_create(
        username="student1",
        defaults={
            "email": "student1@ejemplo.com",
        },
    )

    if created:
        student1.set_password("student1234")

    student1.email = "student1@ejemplo.com"
    student1.is_active = True
    student1.save()

    # Perfil del primer estudiante.
    get_or_create_profile(student1, "estudiante", "+34 600 111 222")

    student2, created = User.objects.get_or_create(
        username="student2",
        defaults={
            "email": "student2@ejemplo.com",
        },
    )

    if created:
        student2.set_password("student1234")

    student2.email = "student2@ejemplo.com"
    student2.is_active = True
    student2.save()

    # Perfil del segundo estudiante.
    get_or_create_profile(student2, "estudiante", "+34 600 333 444")

    print("Usuarios creados/actualizados:")
    print("  admin / admin1234")
    print("  owner1 / owner1234")
    print("  owner2 / owner1234")
    print("  student1 / student1234")
    print("  student2 / student1234")

    return {
        "admin": admin,
        "owner1": owner1,
        "owner2": owner2,
        "student1": student1,
        "student2": student2,
    }


def create_anuncio(owner, data, image_urls):
    """
    Crea o actualiza un anuncio de ejemplo.

    Parámetros:
    - owner: usuario propietario del anuncio.
    - data: diccionario con los datos principales del anuncio.
    - image_urls: lista de URLs externas de Unsplash.

    Funcionamiento:
    1. Busca un anuncio existente por título y propietario.
    2. Si existe, actualiza sus datos.
    3. Si no existe, lo crea.
    4. Copia teléfono y email del propietario en los campos de contacto.
    5. Elimina las imágenes anteriores del anuncio.
    6. Crea nuevas imágenes asociadas usando `imagen_url`.

    La eliminación previa de imágenes evita duplicados cuando el seeder se
    ejecuta más de una vez.
    """
    anuncio, created = Anuncio.objects.update_or_create(
        titulo=data["titulo"],
        propietario=owner,
        defaults={
            "descripcion": data["descripcion"],
            "precio_mes": data["precio_mes"],
            "localizacion": data["localizacion"],
            "tipo_vivienda": data["tipo_vivienda"],
            "duracion_min_meses": data["duracion_min_meses"],
            "duracion_max_meses": data["duracion_max_meses"],
            "wifi": data.get("wifi", False),
            "terraza": data.get("terraza", False),
            "garaje": data.get("garaje", False),
            "publicado": data.get("publicado", True),
            "aprobado": data.get("aprobado", True),
            "telefono_contacto": owner.perfil.telefono,
            "email_contacto": owner.email,
        },
    )

    # Se borran las imágenes previas para que el seeder sea idempotente.
    # Así, ejecutar el script varias veces no genera imágenes duplicadas.
    anuncio.imagenes.all().delete()

    # En esta versión se crean imágenes usando URLs externas de Unsplash.
    # No se descarga el archivo ni se guarda en MEDIA_ROOT.
    for index, url in enumerate(image_urls):
        ImagenAnuncio.objects.create(
            anuncio=anuncio,
            imagen_url=url,
            orden=index,
        )

    return anuncio


def seed_anuncios(users):
    """
    Crea los anuncios iniciales de la aplicación.

    Recibe el diccionario de usuarios creado por seed_users y usa owner1/owner2
    como propietarios de los alojamientos.

    La lista anuncios_data contiene:
    - propietario del anuncio;
    - datos principales;
    - imágenes externas de Unsplash.

    Se incluye un anuncio pendiente de aprobación para poder probar la moderación
    desde el panel de administrador.
    """
    anuncios_data = [
        {
            "owner": users["owner1"],
            "data": {
                "titulo": "Bright Room in Sliema",
                "descripcion": "Habitación luminosa y amplia en el centro de Sliema. Cerca del paseo marítimo, supermercados y paradas de bus.",
                "precio_mes": 450,
                "localizacion": "Sliema, Malta",
                "tipo_vivienda": "habitacion",
                "duracion_min_meses": 3,
                "duracion_max_meses": 12,
                "wifi": True,
                "terraza": False,
                "garaje": False,
                "aprobado": True,
                "publicado": True,
            },
            "images": [
                "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267",
                "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85",
            ],
        },
        {
            "owner": users["owner1"],
            "data": {
                "titulo": "Modern Studio in St. Julian's",
                "descripcion": "Estudio moderno para estudiantes Erasmus. Buena conexión con Paceville, universidad y zonas de ocio.",
                "precio_mes": 650,
                "localizacion": "St. Julian's, Malta",
                "tipo_vivienda": "estudio",
                "duracion_min_meses": 1,
                "duracion_max_meses": 6,
                "wifi": True,
                "terraza": True,
                "garaje": False,
                "aprobado": True,
                "publicado": True,
            },
            "images": [
                "https://images.unsplash.com/photo-1493809842364-78817add7ffb",
                "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85",
            ],
        },
        {
            "owner": users["owner2"],
            "data": {
                "titulo": "Shared Flat near University",
                "descripcion": "Piso compartido cerca de la universidad. Ideal para estudiantes que buscan estancia de varios meses.",
                "precio_mes": 380,
                "localizacion": "Msida, Malta",
                "tipo_vivienda": "habitacion",
                "duracion_min_meses": 3,
                "duracion_max_meses": 9,
                "wifi": True,
                "terraza": False,
                "garaje": False,
                "aprobado": True,
                "publicado": True,
            },
            "images": [
                "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2",
                "https://images.unsplash.com/photo-1560448075-bb485b067938",
            ],
        },
        {
            "owner": users["owner2"],
            "data": {
                "titulo": "Pending Apartment in Valletta",
                "descripcion": "Anuncio pendiente de revisión por parte del administrador. Sirve para probar la moderación.",
                "precio_mes": 720,
                "localizacion": "Valletta, Malta",
                "tipo_vivienda": "piso_completo",
                "duracion_min_meses": 2,
                "duracion_max_meses": 8,
                "wifi": True,
                "terraza": True,
                "garaje": True,
                "aprobado": False,
                "publicado": True,
            },
            "images": [
                "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688",
            ],
        },
    ]

    anuncios = []

    # Se recorre la lista de datos y se crea/actualiza cada anuncio.
    for item in anuncios_data:
        anuncio = create_anuncio(
            owner=item["owner"],
            data=item["data"],
            image_urls=item["images"],
        )
        anuncios.append(anuncio)

    print(f"Anuncios creados/actualizados: {len(anuncios)}")

    return anuncios


def seed_valoraciones(users, anuncios):
    """
    Crea valoraciones de ejemplo.

    Funcionamiento:
    1. Elimina valoraciones anteriores para evitar duplicados.
    2. Crea comentarios aprobados visibles públicamente.
    3. Crea un comentario pendiente para probar la moderación.

    Las valoraciones permiten comprobar el flujo de comentarios en la ficha de
    un anuncio y la revisión por parte del administrador.
    """
    Valoracion.objects.all().delete()

    Valoracion.objects.create(
        anuncio=anuncios[0],
        usuario=users["student1"],
        puntuacion=5,
        comentario="Muy buena ubicación y propietario atento. Recomendable para Erasmus.",
        aprobado=True,
    )

    Valoracion.objects.create(
        anuncio=anuncios[1],
        usuario=users["student2"],
        puntuacion=4,
        comentario="El estudio está bien situado y tiene buena conexión con transporte.",
        aprobado=True,
    )

    Valoracion.objects.create(
        anuncio=anuncios[2],
        usuario=users["student1"],
        puntuacion=3,
        comentario="Comentario pendiente de moderación para probar el panel de administrador.",
        aprobado=False,
    )

    print("Valoraciones creadas.")


def seed_solicitudes(users, anuncios):
    """
    Crea solicitudes de contacto de ejemplo.

    Funcionamiento:
    1. Elimina solicitudes anteriores para evitar duplicados.
    2. Crea una solicitud pendiente.
    3. Crea una solicitud respondida.

    Cada solicitud guarda una copia del teléfono y email del propietario en el
    momento de la creación. Esto permite mantener historial aunque el propietario
    cambie sus datos más adelante.
    """
    SolicitudContacto.objects.all().delete()

    SolicitudContacto.objects.create(
        estudiante=users["student1"],
        anuncio=anuncios[0],
        mensaje="Hola, estoy interesado en la habitación. Llegaría a Malta en septiembre.",
        estado="pendiente",
        telefono_propietario_snapshot=anuncios[0].telefono_propietario,
        email_propietario_snapshot=anuncios[0].email_propietario,
    )

    SolicitudContacto.objects.create(
        estudiante=users["student2"],
        anuncio=anuncios[1],
        mensaje="Me gustaría saber si el estudio está disponible durante 4 meses.",
        estado="respondida",
        telefono_propietario_snapshot=anuncios[1].telefono_propietario,
        email_propietario_snapshot=anuncios[1].email_propietario,
    )

    print("Solicitudes de contacto creadas.")


def seed_data():
    """
    Ejecuta la carga completa de datos iniciales.

    Orden de ejecución:
    1. Crear usuarios y perfiles.
    2. Crear anuncios e imágenes.
    3. Crear valoraciones.
    4. Crear solicitudes de contacto.

    Este orden es importante porque anuncios, valoraciones y solicitudes dependen
    de que los usuarios ya existan.
    """
    users = seed_users()
    anuncios = seed_anuncios(users)
    seed_valoraciones(users, anuncios)
    seed_solicitudes(users, anuncios)

    print("")
    print("Seed completado correctamente.")


# Punto de entrada del script.
# Solo se ejecuta seed_data si este archivo se lanza directamente con:
# python create_data.py
if __name__ == "__main__":
    seed_data()