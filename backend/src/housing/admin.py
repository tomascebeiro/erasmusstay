from django.contrib import admin
from .models import PerfilUsuario, Anuncio, ImagenAnuncio, Valoracion


class ImagenAnuncioInline(admin.TabularInline):
    model = ImagenAnuncio
    extra = 3
    fields = ('imagen_url', 'orden')


@admin.register(Anuncio)
class AnuncioAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'tipo_vivienda', 'localizacion', 'precio_mes', 'publicado', 'aprobado', 'fecha_creacion')
    list_filter = ('tipo_vivienda', 'publicado', 'aprobado', 'wifi', 'terraza', 'garaje')
    search_fields = ('titulo', 'descripcion', 'localizacion')
    list_editable = ('publicado', 'aprobado')
    ordering = ('-fecha_creacion',)
    inlines = [ImagenAnuncioInline]
    fieldsets = (
        ('Informacion principal', {
            'fields': ('propietario', 'titulo', 'descripcion', 'tipo_vivienda')
        }),
        ('Ubicacion y precio', {
            'fields': ('localizacion', 'precio_mes', 'duracion_min_meses', 'duracion_max_meses')
        }),
        ('Caracteristicas', {
            'fields': ('wifi', 'terraza', 'garaje')
        }),
        ('Contacto', {
            'fields': ('telefono_contacto', 'email_contacto')
        }),
        ('Estado', {
            'fields': ('publicado', 'aprobado')
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.propietario = request.user
        super().save_model(request, obj, form, change)


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'rol', 'telefono')
    list_filter = ('rol',)
    search_fields = ('usuario__username', 'usuario__email')


@admin.register(ImagenAnuncio)
class ImagenAnuncioAdmin(admin.ModelAdmin):
    list_display = ('anuncio', 'imagen_url', 'orden')


@admin.register(Valoracion)
class ValoracionAdmin(admin.ModelAdmin):
    list_display = ('anuncio', 'usuario', 'puntuacion')
    list_filter = ('puntuacion',)


admin.site.site_header = 'ErasmusStay - Panel de Administracion'
admin.site.site_title = 'ErasmusStay Admin'
admin.site.index_title = 'Gestion de Alojamientos'
