from django.contrib.auth.models import User
from rest_framework import serializers

from .models import (
    Anuncio,
    ImagenAnuncio,
    PerfilUsuario,
    SolicitudContacto,
    Valoracion,
)


class ImagenAnuncioSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = ImagenAnuncio
        fields = ["id", "imagen", "imagen_url", "url", "orden"]
        read_only_fields = ["id", "url"]

    def get_url(self, obj):
        """
        Devuelve URL absoluta cuando hay request disponible.
        Soporta tanto ImageField como imagen_url antigua.
        """
        request = self.context.get("request")
        url = obj.url

        if not url:
            return ""

        if request and url.startswith("/"):
            return request.build_absolute_uri(url)

        return url


class ValoracionSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source="usuario.username", read_only=True)

    class Meta:
        model = Valoracion
        fields = [
            "id",
            "anuncio",
            "usuario",
            "usuario_nombre",
            "puntuacion",
            "comentario",
            "aprobado",
            "fecha_creacion",
        ]
        read_only_fields = ["usuario", "fecha_creacion"]


class SolicitudContactoSerializer(serializers.ModelSerializer):
    estudiante_nombre = serializers.CharField(source="estudiante.username", read_only=True)
    anuncio_titulo = serializers.CharField(source="anuncio.titulo", read_only=True)
    anuncio_localizacion = serializers.CharField(source="anuncio.localizacion", read_only=True)
    propietario_nombre = serializers.CharField(source="anuncio.propietario.username", read_only=True)

    class Meta:
        model = SolicitudContacto
        fields = [
            "id",
            "estudiante",
            "estudiante_nombre",
            "anuncio",
            "anuncio_titulo",
            "anuncio_localizacion",
            "propietario_nombre",
            "mensaje",
            "estado",
            "telefono_propietario_snapshot",
            "email_propietario_snapshot",
            "fecha_creacion",
            "fecha_actualizacion",
        ]
        read_only_fields = [
            "estudiante",
            "estudiante_nombre",
            "anuncio_titulo",
            "anuncio_localizacion",
            "propietario_nombre",
            "telefono_propietario_snapshot",
            "email_propietario_snapshot",
            "fecha_creacion",
            "fecha_actualizacion",
        ]


class UserRegistrationSerializer(serializers.ModelSerializer):
    rol = serializers.ChoiceField(
        choices=PerfilUsuario.Rol.choices,
        default=PerfilUsuario.Rol.ESTUDIANTE,
        write_only=True,
    )
    telefono = serializers.CharField(required=False, allow_blank=True, write_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "rol", "telefono"]
        extra_kwargs = {
            "password": {"write_only": True},
            "email": {"required": True},
        }

    def create(self, validated_data):
        role = validated_data.pop("rol", PerfilUsuario.Rol.ESTUDIANTE)
        telefono = validated_data.pop("telefono", "")
        password = validated_data.pop("password")

        user = User.objects.create_user(**validated_data, password=password)

        PerfilUsuario.objects.create(
            usuario=user,
            rol=role,
            telefono=telefono,
        )

        return user


class AnuncioSerializer(serializers.ModelSerializer):
    imagenes = ImagenAnuncioSerializer(many=True, read_only=True)
    valoraciones = serializers.SerializerMethodField()

    propietario_nombre = serializers.CharField(source="propietario.username", read_only=True)
    propietario_telefono = serializers.CharField(source="telefono_propietario", read_only=True)
    propietario_email = serializers.EmailField(source="email_propietario", read_only=True)

    uploaded_images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False,
        allow_empty=True,
    )

    class Meta:
        model = Anuncio
        fields = [
            "id",
            "propietario",
            "propietario_nombre",
            "propietario_telefono",
            "propietario_email",
            "titulo",
            "descripcion",
            "precio_mes",
            "localizacion",
            "tipo_vivienda",
            "duracion_min_meses",
            "duracion_max_meses",
            "wifi",
            "terraza",
            "garaje",
            "telefono_contacto",
            "email_contacto",
            "publicado",
            "aprobado",
            "fecha_creacion",
            "imagenes",
            "valoraciones",
            "uploaded_images",
        ]
        read_only_fields = [
            "propietario",
            "propietario_nombre",
            "propietario_telefono",
            "propietario_email",
            "telefono_contacto",
            "email_contacto",
            "aprobado",
            "fecha_creacion",
        ]

    def get_valoraciones(self, obj):
        """
        El público solo recibe comentarios aprobados.
        El administrador recibe todos desde el endpoint /valoraciones/.
        """
        valoraciones = obj.valoraciones.filter(aprobado=True).order_by("-fecha_creacion")
        return ValoracionSerializer(valoraciones, many=True, context=self.context).data

    def _crear_imagenes(self, anuncio, imagenes):
        for orden, imagen in enumerate(imagenes):
            ImagenAnuncio.objects.create(
                anuncio=anuncio,
                imagen=imagen,
                orden=orden,
            )

    def create(self, validated_data):
        imagenes = validated_data.pop("uploaded_images", [])

        anuncio = Anuncio.objects.create(**validated_data)

        # Compatibilidad con campos antiguos de contacto.
        anuncio.telefono_contacto = anuncio.telefono_propietario
        anuncio.email_contacto = anuncio.email_propietario
        anuncio.save(update_fields=["telefono_contacto", "email_contacto"])

        self._crear_imagenes(anuncio, imagenes)
        return anuncio

    def update(self, instance, validated_data):
        imagenes = validated_data.pop("uploaded_images", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.telefono_contacto = instance.telefono_propietario
        instance.email_contacto = instance.email_propietario
        instance.save()

        # Si se envían imágenes nuevas en edición, sustituimos la galería.
        if imagenes is not None:
            instance.imagenes.all().delete()
            self._crear_imagenes(instance, imagenes)

        return instance