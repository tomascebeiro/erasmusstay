from django.contrib import admin

from .models import (
    Anuncio,
    ImagenAnuncio,
    PerfilUsuario,
    SolicitudContacto,
    Valoracion,
)


class ImagenAnuncioInline(admin.TabularInline):
    model = ImagenAnuncio
    extra = 2
    fields = ("imagen", "imagen_url", "orden")


@admin.register(Anuncio)
class AnuncioAdmin(admin.ModelAdmin):
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
    list_filter = (
        "tipo_vivienda",
        "publicado",
        "aprobado",
        "wifi",
        "terraza",
        "garaje",
    )
    search_fields = (
        "titulo",
        "descripcion",
        "localizacion",
        "propietario__username",
        "propietario__email",
    )
    list_editable = ("publicado", "aprobado")
    ordering = ("-fecha_creacion",)
    inlines = [ImagenAnuncioInline]

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
        if not obj.pk and not obj.propietario_id:
            obj.propietario = request.user

        obj.telefono_contacto = obj.telefono_propietario
        obj.email_contacto = obj.email_propietario

        super().save_model(request, obj, form, change)


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ("usuario", "rol", "telefono")
    list_filter = ("rol",)
    search_fields = ("usuario__username", "usuario__email", "telefono")


@admin.register(ImagenAnuncio)
class ImagenAnuncioAdmin(admin.ModelAdmin):
    list_display = ("anuncio", "imagen", "imagen_url", "orden")
    list_filter = ("anuncio",)
    search_fields = ("anuncio__titulo",)


@admin.register(Valoracion)
class ValoracionAdmin(admin.ModelAdmin):
    list_display = ("anuncio", "usuario", "puntuacion", "aprobado", "fecha_creacion")
    list_filter = ("puntuacion", "aprobado")
    search_fields = ("comentario", "usuario__username", "anuncio__titulo")
    list_editable = ("aprobado",)


@admin.register(SolicitudContacto)
class SolicitudContactoAdmin(admin.ModelAdmin):
    list_display = (
        "anuncio",
        "estudiante",
        "estado",
        "telefono_propietario_snapshot",
        "fecha_creacion",
    )
    list_filter = ("estado",)
    search_fields = (
        "anuncio__titulo",
        "estudiante__username",
        "mensaje",
        "telefono_propietario_snapshot",
    )
    list_editable = ("estado",)


admin.site.site_header = "ErasmusStay - Panel de Administración"
admin.site.site_title = "ErasmusStay Admin"
admin.site.index_title = "Gestión de Alojamientos"