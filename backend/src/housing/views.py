from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from .models import Anuncio, Valoracion
from .serializers import AnuncioSerializer, ValoracionSerializer


class AnuncioViewSet(viewsets.ModelViewSet):
    queryset = Anuncio.objects.all().order_by('-fecha_creacion')
    serializer_class = AnuncioSerializer


class ValoracionViewSet(viewsets.ModelViewSet):
    queryset = Valoracion.objects.all().order_by('-fecha_creacion')
    serializer_class = ValoracionSerializer