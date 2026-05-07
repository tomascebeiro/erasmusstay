from django.shortcuts import render
from rest_framework import generics, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.decorators import action
from .models import Anuncio, Valoracion, PerfilUsuario
from .serializers import AnuncioSerializer, ValoracionSerializer, UserRegistrationSerializer
from django.contrib.auth import authenticate


def obtener_rol(usuario):
    try:
        perfil = usuario.perfilusuario
        return perfil.rol
    except PerfilUsuario.DoesNotExist:
        perfil = PerfilUsuario.objects.create(usuario=usuario, rol='estudiante')
        return perfil.rol


class AnuncioViewSet(viewsets.ModelViewSet):
    queryset = Anuncio.objects.all().order_by('-fecha_creacion')
    serializer_class = AnuncioSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        rol = obtener_rol(self.request.user)
        if rol not in ['propietario', 'administrador']:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Solo los propietarios pueden publicar pisos')
        serializer.save(propietario=self.request.user)

    def destroy(self, request, *args, **kwargs):
        anuncio = self.get_object()
        rol = obtener_rol(request.user)
        if rol == 'administrador':
            anuncio.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        if rol == 'propietario' and anuncio.propietario == request.user:
            anuncio.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'error': 'Sin permiso para eliminar este anuncio'}, status=status.HTTP_403_FORBIDDEN)


class ValoracioViewSet(viewsets.ModelViewSet):
    queryset = Valoracion.objects.all().order_by('-fecha_creacion')
    serializer_class = ValoracionSerializer


class RegistroView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        usuario = serializer.save()
        token, _ = Token.objects.get_or_create(user=usuario)
        datos_respuesta = serializer.data
        datos_respuesta['token'] = token.key
        return Response(datos_respuesta, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        nombre = request.data.get('username')
        contrasena = request.data.get('password')
        usuario = authenticate(username=nombre, password=contrasena)
        if not usuario:
            return Response({'error': 'Usuario o contrasena incorrectos'}, status=status.HTTP_400_BAD_REQUEST)
        token, _ = Token.objects.get_or_create(user=usuario)
        rol = obtener_rol(usuario)
        return Response({
            'token': token.key,
            'username': usuario.username,
            'id': usuario.id,
            'rol': rol
        })


class MiPerfilView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        rol = obtener_rol(request.user)
        return Response({
            'id': request.user.id,
            'username': request.user.username,
            'email': request.user.email,
            'rol': rol
        })