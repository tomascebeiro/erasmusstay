from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import AnuncioViewSet, ValoracionViewSet, RegisterView

router = DefaultRouter()
router.register(r'anuncios', AnuncioViewSet)
router.register(r'valoraciones', ValoracionViewSet)

urlpatterns = router.urls + [
    path('register/', RegisterView.as_view(), name='register'),
]