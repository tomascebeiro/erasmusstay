"""
Configuración del panel de administración de Django para la app housing.

Este archivo registra los modelos principales de ErasmusStay en el panel interno
de Django Admin, accesible desde /admin/.

Aunque la aplicación cuenta con un frontend propio en Vue para usuarios,
propietarios y administración, el admin de Django sigue siendo útil como panel
técnico de mantenimiento. Desde aquí se pueden revisar y modificar directamente:

- anuncios publicados por propietarios;
- imágenes asociadas a cada anuncio;
- perfiles de usuario y roles;
- valoraciones y comentarios;
- solicitudes de contacto.

El objetivo de este archivo no es definir la lógica principal de negocio, sino
configurar cómo se muestran y editan los modelos dentro del panel de Django.
"""

from django.contrib import admin

from .models import (
    Anuncio,
    ImagenAnuncio,
    PerfilUsuario,
    SolicitudContacto,
    Valoracion,
)


class ImagenAnuncioInline(admin.TabularInline):
    """
    Inline de imágenes dentro del formulario de un anuncio.

    Permite añadir, editar o eliminar imágenes asociadas a un anuncio sin tener
    que salir de la pantalla de edición del propio anuncio.

    Se usa TabularInline para mostrar las imágenes en formato tabla, ocupando
    menos espacio que un StackedInline.
    """

    # Modelo que se editará como elemento dependiente del anuncio.
    model = ImagenAnuncio

    # Número de formularios vacíos que aparecen por defecto para añadir imágenes.
    extra = 2

    # Campos visibles dentro del inline.
    # - imagen: archivo subido al proyecto.
    # - imagen_url: URL externa usada como compatibilidad o datos de prueba.
    # - orden: posición de la imagen dentro de la galería.
    fields = ("imagen", "imagen_url", "orden")


@admin.register(Anuncio)
class AnuncioAdmin(admin.ModelAdmin):
    """
    Configuración administrativa del modelo Anuncio.

    Define cómo se visualizan y gestionan los anuncios en Django Admin:

    - columnas visibles en el listado;
    - filtros laterales;
    - campos de búsqueda;
    - edición rápida de estado;
    - ordenación;
    - imágenes relacionadas mediante inline;
    - agrupación de campos en el formulario de edición.
    """

    # Columnas que aparecen en el listado principal de anuncios.
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

    # Filtros laterales para localizar anuncios rápidamente.
    list_filter = (
        "tipo_vivienda",
        "publicado",
        "aprobado",
        "wifi",
        "terraza",
        "garaje",
    )

    # Campos sobre los que se puede buscar desde el buscador del admin.
    # También permite buscar por datos del propietario usando relaciones.
    search_fields = (
        "titulo",
        "descripcion",
        "localizacion",
        "propietario__username",
        "propietario__email",
    )

    # Campos editables directamente desde el listado, sin entrar al detalle.
    # Es útil para aprobar/publicar anuncios rápidamente.
    list_editable = ("publicado", "aprobado")

    # Orden por defecto: anuncios más recientes primero.
    ordering = ("-fecha_creacion",)

    # Permite gestionar imágenes del anuncio desde la misma pantalla.
    inlines = [ImagenAnuncioInline]

    # Agrupa los campos del formulario de edición en bloques más claros.
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
        """
        Personaliza el guardado de anuncios desde Django Admin.

        Funcionamiento:
        1. Si se está creando un anuncio nuevo y no tiene propietario asignado,
           se asigna como propietario el usuario que está usando el admin.
        2. Se sincronizan los campos antiguos de contacto del anuncio con los
           datos reales del propietario.
        3. Se llama al guardado normal de Django Admin.

        Esta sincronización mantiene compatibilidad con campos como
        telefono_contacto y email_contacto, aunque el contacto principal se
        obtenga desde el perfil del propietario.
        """

        # Si el anuncio es nuevo y no se seleccionó propietario,
        # se asigna automáticamente el usuario actual del admin.
        if not obj.pk and not obj.propietario_id:
            obj.propietario = request.user

        # Sincroniza datos de contacto desde el perfil del propietario.
        obj.telefono_contacto = obj.telefono_propietario
        obj.email_contacto = obj.email_propietario

        # Ejecuta el guardado estándar de Django.
        super().save_model(request, obj, form, change)


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    """
    Configuración administrativa de perfiles de usuario.

    Permite revisar y modificar el rol y el teléfono asociado a cada cuenta.
    Es especialmente importante para propietarios, ya que su teléfono se utiliza
    como contacto principal en los anuncios.
    """

    # Columnas visibles en el listado de perfiles.
    list_display = ("usuario", "rol", "telefono")

    # Filtro lateral por rol.
    list_filter = ("rol",)

    # Búsqueda por nombre de usuario, email o teléfono.
    search_fields = ("usuario__username", "usuario__email", "telefono")


@admin.register(ImagenAnuncio)
class ImagenAnuncioAdmin(admin.ModelAdmin):
    """
    Configuración administrativa de imágenes de anuncios.

    Permite revisar imágenes de forma independiente, sin entrar necesariamente
    en el anuncio. Es útil para comprobar qué imágenes están asociadas a cada
    alojamiento y en qué orden aparecen.
    """

    # Columnas visibles en el listado de imágenes.
    list_display = ("anuncio", "imagen", "imagen_url", "orden")

    # Filtro por anuncio asociado.
    list_filter = ("anuncio",)

    # Búsqueda por título del anuncio relacionado.
    search_fields = ("anuncio__titulo",)


@admin.register(Valoracion)
class ValoracionAdmin(admin.ModelAdmin):
    """
    Configuración administrativa de valoraciones.

    Permite moderar comentarios de estudiantes. El administrador puede cambiar
    el campo aprobado para decidir si una valoración aparece públicamente o no.
    """

    # Columnas visibles en el listado de valoraciones.
    list_display = ("anuncio", "usuario", "puntuacion", "aprobado", "fecha_creacion")

    # Filtros para localizar comentarios por puntuación o estado de moderación.
    list_filter = ("puntuacion", "aprobado")

    # Búsqueda por texto del comentario, usuario o anuncio.
    search_fields = ("comentario", "usuario__username", "anuncio__titulo")

    # Permite aprobar o desaprobar comentarios desde el listado.
    list_editable = ("aprobado",)


@admin.register(SolicitudContacto)
class SolicitudContactoAdmin(admin.ModelAdmin):
    """
    Configuración administrativa de solicitudes de contacto.

    Permite revisar el historial de contacto entre estudiantes y propietarios.
    Desde aquí se puede cambiar el estado de una solicitud, por ejemplo de
    pendiente a respondida o cerrada.
    """

    # Columnas visibles en el listado de solicitudes.
    list_display = (
        "anuncio",
        "estudiante",
        "estado",
        "telefono_propietario_snapshot",
        "fecha_creacion",
    )

    # Filtro lateral por estado de la solicitud.
    list_filter = ("estado",)

    # Búsqueda por anuncio, estudiante, mensaje o teléfono guardado.
    search_fields = (
        "anuncio__titulo",
        "estudiante__username",
        "mensaje",
        "telefono_propietario_snapshot",
    )

    # Permite actualizar el estado directamente desde el listado.
    list_editable = ("estado",)


# Personalización visual básica del panel de administración de Django.
admin.site.site_header = "ErasmusStay - Panel de Administración"
admin.site.site_title = "ErasmusStay Admin"
admin.site.index_title = "Gestión de Alojamientos"