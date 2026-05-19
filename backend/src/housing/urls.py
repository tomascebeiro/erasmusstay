from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import AnuncioViewSet, ValoracioViewSet, RegistroView, LoginView, MiPerfilView, UsuarioAdminView

router = DefaultRouter()
router.register(r'anuncios', AnuncioViewSet, basename='anuncio')
router.register(r'valoraciones', ValoracioViewSet, basename='valoracion')

urlpatterns = [
    path('register/', RegistroView.as_view(), name='registro'),
    path('login/', LoginView.as_view(), name='login'),
    path('me/', MiPerfilView.as_view(), name='mi-perfil'),
    
    # Nuevos endpoints de administración
    path('admin/usuarios/', UsuarioAdminView.as_view(), name='admin-usuarios-list'),
    path('admin/usuarios/<int:pk>/', UsuarioAdminView.as_view(), name='admin-usuarios-detail'),
]

urlpatterns += router.urls