from django.contrib import admin
from .models import PerfilUsuario, Anuncio, ImagenAnuncio, Valoracion

admin.site.register(PerfilUsuario)
admin.site.register(Anuncio)
admin.site.register(ImagenAnuncio)
admin.site.register(Valoracion)