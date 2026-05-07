from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import AnuncioViewSet, ValoracioViewSet, RegistroView, LoginView, MiPerfilView

router = DefaultRouter()
router.register(r'anuncios', AnuncioViewSet)
router.register(r'valoraciones', ValoracioViewSet)

urlpatterns = router.urls + [
    path('register/', RegistroView.as_view(), name='registro'),
    path('login/', LoginView.as_view(), name='login'),
    path('me/', MiPerfilView.as_view(), name='mi-perfil'),
]