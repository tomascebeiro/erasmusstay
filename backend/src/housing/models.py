from django.db import models
from django.contrib.auth.models import User

class PerfilUsuario(models.Model):
    """
    Extensión del modelo User nativo de Django para almacenar el rol
    y datos adicionales del usuario dentro de la plataforma ErasmusStay.
    """
    class Rol(models.TextChoices):
        ESTUDIANTE = "estudiante", "Estudiante"
        PROPIETARIO = "propietario", "Propietario"
        ADMINISTRADOR = "administrador", "Administrador"

    # related_name="perfil" es vital para acceder desde el User: usuario.perfil
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name="perfil")
    telefono = models.CharField(max_length=20, blank=True)
    rol = models.CharField(max_length=20, choices=Rol.choices, default=Rol.ESTUDIANTE)

    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuarios"

    def __str__(self):
        return f"{self.usuario.username} - {self.rol}"


class Anuncio(models.Model):
    """
    Modelo principal de negocio que representa un inmueble en alquiler.
    Contiene la validación de moderación (aprobado/publicado).
    """
    class TipoVivienda(models.TextChoices):
        HABITACION = "habitacion", "Habitación"
        PISO_COMPLETO = "piso_completo", "Piso completo"
        ESTUDIO = "estudio", "Estudio"

    propietario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="anuncios")
    titulo = models.CharField(max_length=150)
    descripcion = models.TextField()
    precio_mes = models.DecimalField(max_digits=8, decimal_places=2)
    localizacion = models.CharField(max_length=120)
    tipo_vivienda = models.CharField(max_length=20, choices=TipoVivienda.choices)
    duracion_min_meses = models.PositiveIntegerField(default=3)
    duracion_max_meses = models.PositiveIntegerField(default=6)

    # Servicios booleanos
    wifi = models.BooleanField(default=False)
    terraza = models.BooleanField(default=False)
    garaje = models.BooleanField(default=False)

    # Contacto específico para este anuncio
    telefono_contacto = models.CharField(max_length=20, blank=True)
    email_contacto = models.EmailField(blank=True)

    # Flags de estado y moderación
    publicado = models.BooleanField(default=True)
    aprobado = models.BooleanField(default=False)

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Anuncio"
        verbose_name_plural = "Anuncios"
        ordering = ['-fecha_creacion']

    def __str__(self):
        return self.titulo


class ImagenAnuncio(models.Model):
    """
    Modelo para gestionar múltiples imágenes por anuncio (Vía URLs externas)
    """
    anuncio = models.ForeignKey(Anuncio, on_delete=models.CASCADE, related_name="imagenes")
    imagen_url = models.URLField(blank=True)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Imagen del Anuncio"
        verbose_name_plural = "Imágenes de Anuncios"
        ordering = ['orden']

    def __str__(self):
        return f"Imagen de {self.anuncio.titulo}"


class Valoracion(models.Model):
    """
    Feedback de los estudiantes sobre las estancias. 
    Protegido por lógica de negocio en views.py para evitar fraude.
    """
    anuncio = models.ForeignKey(Anuncio, on_delete=models.CASCADE, related_name="valoraciones")
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="valoraciones")
    puntuacion = models.PositiveIntegerField()
    comentario = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Valoración"
        verbose_name_plural = "Valoraciones"
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.usuario.username} - {self.anuncio.titulo} ({self.puntuacion})"