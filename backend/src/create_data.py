import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
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
    admin, created = User.objects.get_or_create(
        username="admin",
        defaults={
            "email": "admin@erasmusstay.com",
            "is_staff": True,
            "is_superuser": True,
        },
    )

    if created:
        admin.set_password("admin1234")
    admin.is_staff = True
    admin.is_superuser = True
    admin.is_active = True
    admin.email = "admin@erasmusstay.com"
    admin.save()
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

    anuncio.imagenes.all().delete()

    for index, url in enumerate(image_urls):
        ImagenAnuncio.objects.create(
            anuncio=anuncio,
            imagen_url=url,
            orden=index,
        )

    return anuncio


def seed_anuncios(users):
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
    users = seed_users()
    anuncios = seed_anuncios(users)
    seed_valoraciones(users, anuncios)
    seed_solicitudes(users, anuncios)

    print("")
    print("Seed completado correctamente.")


if __name__ == "__main__":
    seed_data()