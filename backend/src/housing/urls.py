from rest_framework.routers import DefaultRouter
from .views import AnuncioViewSet, ValoracionViewSet

router = DefaultRouter()
router.register(r'anuncios', AnuncioViewSet)
router.register(r'valoraciones', ValoracionViewSet)

urlpatterns = router.urls