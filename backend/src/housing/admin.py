from django.contrib import admin

from .models import (
    Anuncio,
    ImagenAnuncio,
    PerfilUsuario,
    SolicitudContacto,
    Valoracion,
)


# Define un inline para que las imágenes relacionadas con un anuncio se puedan
# editar dentro de la misma página de admin del anuncio.
# `extra = 2` añade dos formularios vacíos adicionales para subir nuevas imágenes.
class ImagenAnuncioInline(admin.TabularInline):
    model = ImagenAnuncio
    extra = 2
    fields = ("imagen", "imagen_url", "orden")


@admin.register(Anuncio)
class AnuncioAdmin(admin.ModelAdmin):
    # Campos visibles en la lista de anuncios dentro del admin.
    # Esto facilita ver rápidamente el título, propietario y estado.
    list_display = (
        "titulo",
        "propietario",
        "tipo_vivienda",
        "localizacion",
        "precio_mes",
        "publicado",
        "aprobado",
        "fecha_creacion",
    )

    # Filtros rápidos en la barra lateral para segmentar anuncios.
    # Sirve para revisar anuncios publicados/no publicados o con ciertas características.
    list_filter = (
        "tipo_vivienda",
        "publicado",
        "aprobado",
        "wifi",
        "terraza",
        "garaje",
    )

    # Permite buscar anuncios por campos clave y por datos del propietario.
    search_fields = (
        "titulo",
        "descripcion",
        "localizacion",
        "propietario__username",
        "propietario__email",
    )

    # Los campos list_editable se pueden cambiar directamente desde la lista.
    # Útil para aprobar anuncios o marcar su publicación rápidamente.
    list_editable = ("publicado", "aprobado")

    # Ordena los anuncios por fecha de creación descendente.
    ordering = ("-fecha_creacion",)

    # Incluye las imágenes relacionadas directamente en el formulario del anuncio.
    inlines = [ImagenAnuncioInline]

    # Organiza el formulario de edición en secciones para mayor claridad.
    fieldsets = (
        ("Información principal", {
            "fields": ("propietario", "titulo", "descripcion", "tipo_vivienda")
        }),
        ("Ubicación y precio", {
            "fields": ("localizacion", "precio_mes", "duracion_min_meses", "duracion_max_meses")
        }),
        ("Características", {
            "fields": ("wifi", "terraza", "garaje")
        }),
        ("Estado", {
            "fields": ("publicado", "aprobado")
        }),
    )

    def save_model(self, request, obj, form, change):
        # Si se crea un anuncio desde el admin y no tiene propietario asignado,
        # se establece automáticamente el usuario que está guardando el registro.
        if not obj.pk and not obj.propietario_id:
            obj.propietario = request.user

        # Copia los datos de contacto del propietario al propio anuncio.
        # Esto asegura que la información quede almacenada incluso si cambia el perfil.
        obj.telefono_contacto = obj.telefono_propietario
        obj.email_contacto = obj.email_propietario

        super().save_model(request, obj, form, change)


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    # Configuración del admin para el perfil de usuario.
    # Muestra nombre, rol y teléfono en la lista.
    list_display = ("usuario", "rol", "telefono")
    # Permite filtrar perfiles por rol. Ej: estudiante, propietario, admin.
    list_filter = ("rol",)
    # Busca perfiles por usuario, email o teléfono, útil para asistencia.
    search_fields = ("usuario__username", "usuario__email", "telefono")


@admin.register(ImagenAnuncio)
class ImagenAnuncioAdmin(admin.ModelAdmin):
    # Configuración del admin para las imágenes de anuncios.
    # Permite ver el anuncio asociado, el archivo y el orden de la imagen.
    list_display = ("anuncio", "imagen", "imagen_url", "orden")
    list_filter = ("anuncio",)
    search_fields = ("anuncio__titulo",)


@admin.register(Valoracion)
class ValoracionAdmin(admin.ModelAdmin):
    # Configuración del admin de valoraciones.
    # Muestra el anuncio, el usuario y si la valoración fue aprobada.
    list_display = ("anuncio", "usuario", "puntuacion", "aprobado", "fecha_creacion")
    list_filter = ("puntuacion", "aprobado")
    search_fields = ("comentario", "usuario__username", "anuncio__titulo")
    # Permite aprobar/desaprobar valoraciones sin abrir el registro.
    list_editable = ("aprobado",)


@admin.register(SolicitudContacto)
class SolicitudContactoAdmin(admin.ModelAdmin):
    # Configuración del admin de solicitudes de contacto.
    # Permite ver qué estudiante ha solicitado información y en qué anuncio.
    list_display = (
        "anuncio",
        "estudiante",
        "estado",
        "telefono_propietario_snapshot",
        "fecha_creacion",
    )
    # Filtra por el estado de la solicitud para revisar pendientes o aceptadas.
    list_filter = ("estado",)
    # Busca solicitudes por anuncio, estudiante, mensaje o teléfono guardado.
    search_fields = (
        "anuncio__titulo",
        "estudiante__username",
        "mensaje",
        "telefono_propietario_snapshot",
    )
    # Permite cambiar el estado desde la lista sin abrir el registro.
    list_editable = ("estado",)


# Personaliza los textos del panel de administración para ayudar a identificar
# esta aplicación cuando se accede a /admin/.
admin.site.site_header = "ErasmusStay - Panel de Administración"
admin.site.site_title = "ErasmusStay Admin"
admin.site.index_title = "Gestión de Alojamientos"