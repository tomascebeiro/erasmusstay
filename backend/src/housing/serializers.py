"""
Serializers de la API REST de ErasmusStay.

Este archivo define cómo se transforman los modelos de Django en datos JSON
para que puedan ser consumidos por el frontend Vue. También valida y procesa los
datos que llegan desde el frontend antes de crear o actualizar registros en la
base de datos.

En Django REST Framework, un serializer actúa como una capa intermedia entre:

- los modelos de Django;
- las vistas o ViewSets;
- las respuestas JSON de la API;
- los datos enviados desde el frontend.

En este archivo se gestionan principalmente:

- imágenes de anuncios;
- valoraciones;
- solicitudes de contacto;
- registro de usuarios;
- creación y edición de anuncios;
- subida de imágenes mediante multipart/form-data.

La lógica más importante está en AnuncioSerializer, porque permite crear o
editar un anuncio junto con sus imágenes asociadas.
"""

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
    """
    Serializer para imágenes de anuncios.

    Convierte objetos ImagenAnuncio en JSON. Además de devolver los campos
    guardados en base de datos, calcula un campo extra llamado `url`.

    El campo `url` es el que utiliza el frontend para mostrar la imagen, ya que
    puede resolver tanto:

    - imágenes subidas al proyecto mediante ImageField;
    - imágenes antiguas o de prueba guardadas como imagen_url.
    """

    # Campo calculado manualmente mediante el método get_url.
    url = serializers.SerializerMethodField()

    class Meta:
        """
        Configuración del serializer de imágenes.

        fields indica qué campos se exponen en la API.
        read_only_fields evita que el frontend pueda modificar directamente
        ciertos valores calculados o automáticos.
        """

        model = ImagenAnuncio
        fields = ["id", "imagen", "imagen_url", "url", "orden"]
        read_only_fields = ["id", "url"]

    def get_url(self, obj):
        """
        Devuelve la URL absoluta de la imagen cuando hay request disponible.

        Funcionamiento:
        1. Obtiene la URL desde la propiedad obj.url del modelo.
        2. Si no hay URL, devuelve cadena vacía.
        3. Si la URL empieza por "/" y existe request, la convierte en URL
           absoluta.
        4. Si ya es una URL externa, la devuelve tal cual.

        Esto permite que el frontend Vue pueda cargar imágenes aunque esté
        ejecutándose en un dominio o puerto distinto al backend.
        """
        request = self.context.get("request")
        url = obj.url

        if not url:
            return ""

        if request and url.startswith("/"):
            return request.build_absolute_uri(url)

        return url


class ValoracionSerializer(serializers.ModelSerializer):
    """
    Serializer para valoraciones de anuncios.

    Permite transformar comentarios y puntuaciones en JSON. Incluye además el
    nombre del usuario como campo de solo lectura, para que el frontend pueda
    mostrar quién escribió la valoración sin hacer otra petición.
    """

    # Campo derivado del modelo User relacionado.
    usuario_nombre = serializers.CharField(source="usuario.username", read_only=True)

    class Meta:
        """
        Configuración del serializer de valoraciones.
        """

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

        # El usuario y la fecha se asignan desde el backend.
        # El frontend no debe decidir quién crea la valoración.
        read_only_fields = ["usuario", "fecha_creacion"]


class SolicitudContactoSerializer(serializers.ModelSerializer):
    """
    Serializer para solicitudes de contacto.

    Además de los campos propios de SolicitudContacto, añade datos relacionados
    del estudiante, del anuncio y del propietario.

    Esto simplifica el frontend, porque permite mostrar un historial completo de
    solicitudes sin tener que hacer varias llamadas a la API.
    """

    # Datos calculados a partir de relaciones.
    estudiante_nombre = serializers.CharField(source="estudiante.username", read_only=True)
    anuncio_titulo = serializers.CharField(source="anuncio.titulo", read_only=True)
    anuncio_localizacion = serializers.CharField(source="anuncio.localizacion", read_only=True)
    propietario_nombre = serializers.CharField(source="anuncio.propietario.username", read_only=True)

    class Meta:
        """
        Configuración del serializer de solicitudes de contacto.
        """

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

        # Estos campos se calculan o se asignan desde el backend.
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
    """
    Serializer para el registro de usuarios.

    Recibe los datos del formulario de registro del frontend y crea:

    1. Un usuario nativo de Django.
    2. Un PerfilUsuario asociado con rol y teléfono.

    El password se define como write_only para que nunca se devuelva en las
    respuestas JSON.
    """

    # Rol elegido en el registro. Solo se usa para crear el perfil.
    rol = serializers.ChoiceField(
        choices=PerfilUsuario.Rol.choices,
        default=PerfilUsuario.Rol.ESTUDIANTE,
        write_only=True,
    )

    # Teléfono opcional. Es especialmente importante para propietarios.
    telefono = serializers.CharField(required=False, allow_blank=True, write_only=True)

    class Meta:
        """
        Configuración del serializer de registro.
        """

        model = User
        fields = ["id", "username", "email", "password", "rol", "telefono"]
        extra_kwargs = {
            # La contraseña solo entra desde el frontend, nunca se devuelve.
            "password": {"write_only": True},

            # El email se exige para poder identificar y contactar usuarios.
            "email": {"required": True},
        }

    def create(self, validated_data):
        """
        Crea el usuario y su perfil asociado.

        Funcionamiento:
        1. Extrae rol, teléfono y password de los datos validados.
        2. Crea el usuario mediante create_user, para que la contraseña se
           almacene cifrada.
        3. Crea el PerfilUsuario relacionado.
        4. Devuelve el usuario creado.

        Es importante usar create_user y no User.objects.create, porque
        create_user aplica correctamente el hash de contraseña.
        """
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
    """
    Serializer principal de anuncios.

    Se utiliza para:

    - listar anuncios;
    - mostrar el detalle de un anuncio;
    - crear anuncios;
    - editar anuncios.

    Además de los campos propios del modelo Anuncio, añade:

    - imágenes asociadas;
    - valoraciones aprobadas;
    - nombre del propietario;
    - teléfono del propietario;
    - email del propietario;
    - campo uploaded_images para recibir imágenes desde el frontend.

    El campo uploaded_images no existe en el modelo. Es un campo auxiliar que se
    usa solo para recibir archivos en peticiones multipart/form-data.
    """

    # Galería de imágenes asociadas al anuncio.
    imagenes = ImagenAnuncioSerializer(many=True, read_only=True)

    # Campo calculado manualmente para devolver solo comentarios aprobados.
    valoraciones = serializers.SerializerMethodField()

    # Datos del propietario obtenidos desde relaciones o propiedades del modelo.
    propietario_nombre = serializers.CharField(source="propietario.username", read_only=True)
    propietario_telefono = serializers.CharField(source="telefono_propietario", read_only=True)
    propietario_email = serializers.EmailField(source="email_propietario", read_only=True)

    # Campo auxiliar para recibir varias imágenes desde el frontend.
    # write_only=True significa que se puede enviar, pero no aparece en la respuesta.
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False,
        allow_empty=True,
    )

    class Meta:
        """
        Configuración del serializer de anuncios.
        """

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

        # Campos controlados por backend.
        # El frontend no puede elegir propietario, aprobación ni datos derivados.
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
        Devuelve únicamente las valoraciones aprobadas del anuncio.

        El público solo debe recibir comentarios moderados y aprobados.
        El administrador puede consultar todas las valoraciones desde el endpoint
        específico /valoraciones/.

        Esto separa la vista pública de la gestión administrativa.
        """
        valoraciones = obj.valoraciones.filter(aprobado=True).order_by("-fecha_creacion")
        return ValoracionSerializer(valoraciones, many=True, context=self.context).data

    def _crear_imagenes(self, anuncio, imagenes):
        """
        Crea las imágenes asociadas a un anuncio.

        Parámetros:
        - anuncio: instancia de Anuncio ya creada o actualizada.
        - imagenes: lista de archivos recibidos desde el frontend.

        Funcionamiento:
        1. Recorre la lista de imágenes.
        2. Crea un objeto ImagenAnuncio por cada archivo.
        3. Asigna el orden según la posición en la lista.

        El guardado físico del archivo lo gestiona Django mediante ImageField.
        """
        for orden, imagen in enumerate(imagenes):
            ImagenAnuncio.objects.create(
                anuncio=anuncio,
                imagen=imagen,
                orden=orden,
            )

    def create(self, validated_data):
        """
        Crea un nuevo anuncio junto con sus imágenes.

        Flujo:
        1. Extrae uploaded_images de los datos validados.
        2. Crea el anuncio con el resto de campos.
        3. Sincroniza los campos antiguos de contacto por compatibilidad.
        4. Crea las imágenes asociadas.
        5. Devuelve el anuncio creado.

        El propietario no se asigna aquí directamente porque normalmente se
        asigna desde el ViewSet en perform_create.
        """
        imagenes = validated_data.pop("uploaded_images", [])

        anuncio = Anuncio.objects.create(**validated_data)

        # Compatibilidad con campos antiguos de contacto.
        # La fuente real es el perfil del propietario, pero estos campos se
        # mantienen sincronizados para no romper código anterior.
        anuncio.telefono_contacto = anuncio.telefono_propietario
        anuncio.email_contacto = anuncio.email_propietario
        anuncio.save(update_fields=["telefono_contacto", "email_contacto"])

        self._crear_imagenes(anuncio, imagenes)
        return anuncio

    def update(self, instance, validated_data):
        """
        Actualiza un anuncio existente.

        Flujo:
        1. Extrae uploaded_images si el frontend envió imágenes nuevas.
        2. Actualiza los atributos normales del anuncio.
        3. Sincroniza teléfono y email de contacto.
        4. Guarda el anuncio.
        5. Si llegaron imágenes nuevas, elimina la galería anterior y crea la
           nueva galería.

        Si no se envía uploaded_images, las imágenes existentes se mantienen.
        """
        imagenes = validated_data.pop("uploaded_images", None)

        # Actualiza dinámicamente cada campo recibido.
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Mantiene compatibilidad con los campos antiguos de contacto.
        instance.telefono_contacto = instance.telefono_propietario
        instance.email_contacto = instance.email_propietario
        instance.save()

        # Si se envían imágenes nuevas en edición, sustituimos la galería.
        if imagenes is not None:
            instance.imagenes.all().delete()
            self._crear_imagenes(instance, imagenes)

        return instance