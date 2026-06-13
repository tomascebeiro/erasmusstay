"""
Modelos de datos de la aplicación ErasmusStay.

Este archivo define las entidades principales de la app `housing`. Cada clase
representa una tabla de la base de datos y describe cómo se relacionan los datos
entre sí.

Entidades principales:

- PerfilUsuario:
  amplía el modelo User nativo de Django con rol y teléfono.

- Anuncio:
  representa un alojamiento publicado por un propietario.

- ImagenAnuncio:
  guarda imágenes asociadas a un anuncio, ya sea mediante archivo subido al
  proyecto o mediante URL externa de compatibilidad.

- Valoracion:
  almacena comentarios y puntuaciones de estudiantes sobre anuncios.

- SolicitudContacto:
  registra las solicitudes de contacto que realizan los estudiantes hacia los
  propietarios de anuncios.

Estos modelos son utilizados por:
- las migraciones de Django para crear la base de datos;
- los serializers de Django REST Framework para exponer datos como JSON;
- las views y ViewSets para aplicar la lógica de la API;
- el panel de administración de Django.
"""

from django.contrib.auth.models import User
from django.db import models


class PerfilUsuario(models.Model):
    """
    Perfil extendido del usuario nativo de Django.

    Django ya incluye el modelo User, que gestiona username, email, contraseña,
    autenticación y permisos básicos. Este modelo añade información específica
    de ErasmusStay:

    - rol: define si la cuenta pertenece a un estudiante, propietario o
      administrador.
    - telefono: guarda el teléfono de contacto del usuario.

    El teléfono se guarda aquí para que pertenezca a la cuenta del propietario,
    no a cada anuncio individual. De esta forma, si el propietario cambia su
    teléfono, todos sus anuncios pueden mostrar el dato actualizado.
    """

    class Rol(models.TextChoices):
        """
        Opciones posibles para el rol de usuario.

        TextChoices permite definir valores internos estables para la base de
        datos y etiquetas legibles para formularios o paneles.
        """

        ESTUDIANTE = "estudiante", "Estudiante"
        PROPIETARIO = "propietario", "Propietario"
        ADMINISTRADOR = "administrador", "Administrador"

    # Relación uno a uno con el usuario nativo de Django.
    # Cada User tiene como máximo un PerfilUsuario y cada PerfilUsuario
    # pertenece a un único User.
    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="perfil",
    )

    # Teléfono asociado a la cuenta. Se permite vacío porque no todos los
    # usuarios necesitan mostrar teléfono, especialmente los estudiantes.
    telefono = models.CharField(max_length=20, blank=True)

    # Rol interno del usuario dentro de la aplicación.
    rol = models.CharField(
        max_length=20,
        choices=Rol.choices,
        default=Rol.ESTUDIANTE,
    )

    class Meta:
        """
        Configuración de nombres visibles en Django Admin.
        """

        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuarios"

    def __str__(self):
        """
        Devuelve una representación legible del perfil.

        Se utiliza en Django Admin y en depuración para identificar rápidamente
        a qué usuario pertenece el perfil y qué rol tiene.
        """
        return f"{self.usuario.username} - {self.rol}"


class Anuncio(models.Model):
    """
    Modelo principal de alojamiento.

    Representa un anuncio publicado por un propietario. Guarda la información
    que el estudiante necesita para decidir si le interesa el alojamiento:

    - título;
    - descripción;
    - precio mensual;
    - localización;
    - tipo de vivienda;
    - duración mínima y máxima;
    - servicios incluidos;
    - estado de publicación y aprobación.

    El contacto telefónico se resuelve desde el perfil del propietario.
    Los campos telefono_contacto/email_contacto se mantienen por compatibilidad
    con datos antiguos, pero el frontend utilizará principalmente
    propietario_telefono y propietario_email desde el serializer.
    """

    class TipoVivienda(models.TextChoices):
        """
        Tipos de vivienda disponibles para un anuncio.
        """

        HABITACION = "habitacion", "Habitación"
        PISO_COMPLETO = "piso_completo", "Piso completo"
        ESTUDIO = "estudio", "Estudio"

    # Usuario propietario que publica el anuncio.
    # Si el propietario se elimina, también se eliminan sus anuncios.
    propietario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="anuncios",
    )

    # Datos principales del alojamiento.
    titulo = models.CharField(max_length=150)
    descripcion = models.TextField()
    precio_mes = models.DecimalField(max_digits=8, decimal_places=2)
    localizacion = models.CharField(max_length=120)
    tipo_vivienda = models.CharField(max_length=20, choices=TipoVivienda.choices)

    # Rango de duración permitido para la estancia.
    duracion_min_meses = models.PositiveIntegerField(default=3)
    duracion_max_meses = models.PositiveIntegerField(default=6)

    # Servicios básicos del alojamiento.
    wifi = models.BooleanField(default=False)
    terraza = models.BooleanField(default=False)
    garaje = models.BooleanField(default=False)

    # Compatibilidad con versiones antiguas.
    # La fuente principal de contacto debe ser el perfil del propietario.
    telefono_contacto = models.CharField(max_length=20, blank=True)
    email_contacto = models.EmailField(blank=True)

    # Control de visibilidad y moderación.
    # publicado indica si el propietario quiere que el anuncio esté activo.
    # aprobado indica si el administrador lo revisó y autorizó.
    publicado = models.BooleanField(default=True)
    aprobado = models.BooleanField(default=False)

    # Fecha automática de creación del anuncio.
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        """
        Configuración del modelo en Django.

        ordering hace que, por defecto, los anuncios más recientes aparezcan
        primero en consultas y paneles.
        """

        verbose_name = "Anuncio"
        verbose_name_plural = "Anuncios"
        ordering = ["-fecha_creacion"]

    def __str__(self):
        """
        Devuelve el título del anuncio como representación legible.

        Esto se muestra en Django Admin, relaciones y depuración.
        """
        return self.titulo

    @property
    def telefono_propietario(self):
        """
        Devuelve el teléfono del perfil del propietario.

        Se usa una propiedad para centralizar la lógica y evitar repetir accesos
        a `propietario.perfil.telefono` en serializers, views o admin.

        Si el propietario no tiene PerfilUsuario asociado, devuelve una cadena
        vacía para evitar errores.
        """
        try:
            return self.propietario.perfil.telefono
        except PerfilUsuario.DoesNotExist:
            return ""

    @property
    def email_propietario(self):
        """
        Devuelve el email del usuario propietario.

        Esta propiedad permite que serializers y vistas accedan al email de
        contacto desde un punto único.
        """
        return self.propietario.email


class ImagenAnuncio(models.Model):
    """
    Imagen asociada a un anuncio.

    Un anuncio puede tener varias imágenes. Esta clase permite dos formas de
    almacenar o referenciar la imagen:

    - imagen:
      archivo real subido al proyecto mediante ImageField. Django lo guarda en
      MEDIA_ROOT dentro de la carpeta indicada por upload_to.

    - imagen_url:
      URL externa mantenida por compatibilidad con datos antiguos o seeders que
      usan imágenes de Unsplash.

    La propiedad `url` decide qué valor debe usar el frontend.
    """

    # Anuncio al que pertenece la imagen.
    anuncio = models.ForeignKey(
        Anuncio,
        on_delete=models.CASCADE,
        related_name="imagenes",
    )

    # Archivo físico subido al proyecto.
    # upload_to organiza las imágenes en carpetas por año, mes y día.
    imagen = models.ImageField(
        upload_to="anuncios/%Y/%m/%d/",
        blank=True,
        null=True,
    )

    # URL externa opcional.
    # Se mantiene para compatibilidad con imágenes de prueba cargadas desde
    # servicios externos como Unsplash.
    imagen_url = models.URLField(blank=True)

    # Orden de aparición dentro de la galería del anuncio.
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        """
        Configuración del modelo ImagenAnuncio.

        El ordering permite mostrar primero la imagen con menor orden y, en caso
        de empate, la creada antes.
        """

        verbose_name = "Imagen del Anuncio"
        verbose_name_plural = "Imágenes de Anuncios"
        ordering = ["orden", "id"]

    def __str__(self):
        """
        Devuelve una descripción legible de la imagen.
        """
        return f"Imagen de {self.anuncio.titulo}"

    @property
    def url(self):
        """
        Devuelve la URL final que debe utilizar el frontend.

        Prioridad:
        1. Si existe una imagen subida al proyecto, devuelve su URL local.
        2. Si no existe archivo local, devuelve imagen_url.

        Esto permite que el frontend use siempre `imagen.url` sin preocuparse
        de si la imagen viene de un archivo subido o de una URL externa.
        """
        if self.imagen:
            return self.imagen.url
        return self.imagen_url


class Valoracion(models.Model):
    """
    Comentario y puntuación de un estudiante.

    Cada valoración pertenece a un anuncio y a un usuario. El campo aprobado
    permite moderar los comentarios antes de que sean visibles públicamente.

    Esto evita que aparezcan comentarios ofensivos, falsos o irrelevantes sin
    revisión previa.
    """

    # Anuncio valorado.
    anuncio = models.ForeignKey(
        Anuncio,
        on_delete=models.CASCADE,
        related_name="valoraciones",
    )

    # Usuario que realiza la valoración.
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="valoraciones",
    )

    # Puntuación numérica del alojamiento.
    puntuacion = models.PositiveIntegerField()

    # Texto libre del comentario.
    comentario = models.TextField()

    # Estado de moderación del comentario.
    aprobado = models.BooleanField(default=False)

    # Fecha automática de creación.
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        """
        Configuración del modelo Valoracion.
        """

        verbose_name = "Valoración"
        verbose_name_plural = "Valoraciones"
        ordering = ["-fecha_creacion"]

    def __str__(self):
        """
        Devuelve una representación legible de la valoración.

        Incluye usuario, anuncio y estado de moderación.
        """
        estado = "aprobada" if self.aprobado else "pendiente"
        return f"{self.usuario.username} - {self.anuncio.titulo} ({estado})"


class SolicitudContacto(models.Model):
    """
    Solicitud de contacto de un estudiante hacia el propietario de un anuncio.

    Permite crear un historial para que:
    - cada estudiante pueda hacer seguimiento de las solicitudes realizadas;
    - cada propietario pueda consultar las solicitudes recibidas;
    - el administrador pueda supervisar el flujo completo.

    Además, guarda una copia del teléfono y email del propietario en el momento
    de la solicitud. Esto mantiene trazabilidad aunque el propietario cambie sus
    datos de perfil en el futuro.
    """

    class Estado(models.TextChoices):
        """
        Estados posibles de una solicitud de contacto.
        """

        PENDIENTE = "pendiente", "Pendiente"
        RESPONDIDA = "respondida", "Respondida"
        CERRADA = "cerrada", "Cerrada"

    # Estudiante que realiza la solicitud.
    estudiante = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="solicitudes_realizadas",
    )

    # Anuncio sobre el que se solicita contacto.
    anuncio = models.ForeignKey(
        Anuncio,
        on_delete=models.CASCADE,
        related_name="solicitudes_contacto",
    )

    # Mensaje opcional del estudiante.
    mensaje = models.TextField(blank=True)

    # Estado actual de la solicitud.
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
    )

    # Copia del contacto del propietario en el momento de crear la solicitud.
    telefono_propietario_snapshot = models.CharField(max_length=20, blank=True)
    email_propietario_snapshot = models.EmailField(blank=True)

    # Fechas automáticas de creación y última actualización.
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        """
        Configuración del modelo SolicitudContacto.
        """

        verbose_name = "Solicitud de contacto"
        verbose_name_plural = "Solicitudes de contacto"
        ordering = ["-fecha_creacion"]

    def __str__(self):
        """
        Devuelve una representación legible de la solicitud.
        """
        return f"{self.estudiante.username} → {self.anuncio.titulo} ({self.estado})"