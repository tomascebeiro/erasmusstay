from django.contrib.auth.models import User
from django.db import models


class PerfilUsuario(models.Model):
    """
    Extiende el usuario nativo de Django con rol y teléfono.

    El teléfono se guarda aquí para que pertenezca a la cuenta del propietario,
    no a cada anuncio individual. De esta forma, si el propietario cambia su
    teléfono, todos sus anuncios muestran el dato actualizado.
    """

    class Rol(models.TextChoices):
        ESTUDIANTE = "estudiante", "Estudiante"
        PROPIETARIO = "propietario", "Propietario"
        ADMINISTRADOR = "administrador", "Administrador"

    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="perfil",
    )
    telefono = models.CharField(max_length=20, blank=True)
    rol = models.CharField(
        max_length=20,
        choices=Rol.choices,
        default=Rol.ESTUDIANTE,
    )

    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuarios"

    def __str__(self):
        return f"{self.usuario.username} - {self.rol}"


class Anuncio(models.Model):
    """
    Modelo principal de alojamiento.

    El contacto telefónico se resuelve desde el perfil del propietario.
    Los campos telefono_contacto/email_contacto se mantienen por compatibilidad
    con datos antiguos, pero el frontend utilizará propietario_telefono.
    """

    class TipoVivienda(models.TextChoices):
        HABITACION = "habitacion", "Habitación"
        PISO_COMPLETO = "piso_completo", "Piso completo"
        ESTUDIO = "estudio", "Estudio"

    propietario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="anuncios",
    )
    titulo = models.CharField(max_length=150)
    descripcion = models.TextField()
    precio_mes = models.DecimalField(max_digits=8, decimal_places=2)
    localizacion = models.CharField(max_length=120)
    tipo_vivienda = models.CharField(max_length=20, choices=TipoVivienda.choices)
    duracion_min_meses = models.PositiveIntegerField(default=3)
    duracion_max_meses = models.PositiveIntegerField(default=6)

    wifi = models.BooleanField(default=False)
    terraza = models.BooleanField(default=False)
    garaje = models.BooleanField(default=False)

    # Compatibilidad con versiones antiguas. No se usará como fuente principal.
    telefono_contacto = models.CharField(max_length=20, blank=True)
    email_contacto = models.EmailField(blank=True)

    publicado = models.BooleanField(default=True)
    aprobado = models.BooleanField(default=False)

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Anuncio"
        verbose_name_plural = "Anuncios"
        ordering = ["-fecha_creacion"]

    def __str__(self):
        return self.titulo

    @property
    def telefono_propietario(self):
        try:
            return self.propietario.perfil.telefono
        except PerfilUsuario.DoesNotExist:
            return ""

    @property
    def email_propietario(self):
        return self.propietario.email


class ImagenAnuncio(models.Model):
    """
    Imagen asociada a un anuncio.

    Se soporta subida real de archivo mediante ImageField.
    imagen_url queda como compatibilidad si existían imágenes externas.
    """

    anuncio = models.ForeignKey(
        Anuncio,
        on_delete=models.CASCADE,
        related_name="imagenes",
    )
    imagen = models.ImageField(
        upload_to="anuncios/%Y/%m/%d/",
        blank=True,
        null=True,
    )
    imagen_url = models.URLField(blank=True)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Imagen del Anuncio"
        verbose_name_plural = "Imágenes de Anuncios"
        ordering = ["orden", "id"]

    def __str__(self):
        return f"Imagen de {self.anuncio.titulo}"

    @property
    def url(self):
        if self.imagen:
            return self.imagen.url
        return self.imagen_url


class Valoracion(models.Model):
    """
    Comentario y puntuación de un estudiante.

    Los comentarios quedan pendientes de aprobación para que el administrador
    pueda moderarlos antes de mostrarlos públicamente.
    """

    anuncio = models.ForeignKey(
        Anuncio,
        on_delete=models.CASCADE,
        related_name="valoraciones",
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="valoraciones",
    )
    puntuacion = models.PositiveIntegerField()
    comentario = models.TextField()
    aprobado = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Valoración"
        verbose_name_plural = "Valoraciones"
        ordering = ["-fecha_creacion"]

    def __str__(self):
        estado = "aprobada" if self.aprobado else "pendiente"
        return f"{self.usuario.username} - {self.anuncio.titulo} ({estado})"


class SolicitudContacto(models.Model):
    """
    Solicitud de contacto de un estudiante hacia el propietario de un anuncio.

    Permite crear un historial para que cada usuario pueda hacer seguimiento
    de las solicitudes realizadas y los propietarios puedan ver las recibidas.
    """

    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        RESPONDIDA = "respondida", "Respondida"
        CERRADA = "cerrada", "Cerrada"

    estudiante = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="solicitudes_realizadas",
    )
    anuncio = models.ForeignKey(
        Anuncio,
        on_delete=models.CASCADE,
        related_name="solicitudes_contacto",
    )
    mensaje = models.TextField(blank=True)
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
    )

    telefono_propietario_snapshot = models.CharField(max_length=20, blank=True)
    email_propietario_snapshot = models.EmailField(blank=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Solicitud de contacto"
        verbose_name_plural = "Solicitudes de contacto"
        ordering = ["-fecha_creacion"]

    def __str__(self):
        return f"{self.estudiante.username} → {self.anuncio.titulo} ({self.estado})"