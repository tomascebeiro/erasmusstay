from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    AnuncioViewSet,
    LoginView,
    MiPerfilView,
    RegistroView,
    SolicitudContactoViewSet,
    UsuarioAdminView,
    ValoracioViewSet,
)

router = DefaultRouter()
router.register(r"anuncios", AnuncioViewSet, basename="anuncio")
router.register(r"valoraciones", ValoracioViewSet, basename="valoracion")
router.register(r"solicitudes", SolicitudContactoViewSet, basename="solicitud")

urlpatterns = [
    path("register/", RegistroView.as_view(), name="registro"),
    path("login/", LoginView.as_view(), name="login"),
    path("me/", MiPerfilView.as_view(), name="mi-perfil"),

    path("admin/usuarios/", UsuarioAdminView.as_view(), name="admin-usuarios-list"),
    path("admin/usuarios/<int:pk>/", UsuarioAdminView.as_view(), name="admin-usuarios-detail"),
]

urlpatterns += router.urls