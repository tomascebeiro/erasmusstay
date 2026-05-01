from django.shortcuts import render

# Create your views here.
from rest_framework import generics, status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .models import Anuncio, Valoracion
from .serializers import AnuncioSerializer, ValoracionSerializer, UserRegistrationSerializer


class AnuncioViewSet(viewsets.ModelViewSet):
    queryset = Anuncio.objects.all().order_by('-fecha_creacion')
    serializer_class = AnuncioSerializer


class ValoracionViewSet(viewsets.ModelViewSet):
    queryset = Valoracion.objects.all().order_by('-fecha_creacion')
    serializer_class = ValoracionSerializer


class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        response_data = serializer.data
        response_data['token'] = token.key
        return Response(response_data, status=status.HTTP_201_CREATED)