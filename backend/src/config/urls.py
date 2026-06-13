from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve as static_serve

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("housing.urls")),
]

# Servir archivos media en Railway.
# Esto se usa para que las imágenes subidas por usuarios sean accesibles desde /media/.
# Para un proyecto grande sería mejor usar S3 o un bucket, pero para Railway/TFC funciona.
urlpatterns += [
    re_path(
        r"^media/(?P<path>.*)$",
        static_serve,
        {"document_root": settings.MEDIA_ROOT},
    ),
]