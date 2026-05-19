from django.shortcuts import render
from rest_framework import generics, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from django.db.models import Q
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth.models import User

from .models import Anuncio, Valoracion, PerfilUsuario
from .serializers import AnuncioSerializer, ValoracionSerializer, UserRegistrationSerializer


def obtener_rol(usuario):
    """ Función auxiliar robusta para recuperar el rol del usuario """
    if usuario.is_superuser or usuario.username == 'admin':
        return 'administrador'
    try:
        return usuario.perfil.rol
    except Exception:
        return 'usuario'


class AnuncioViewSet(viewsets.ModelViewSet):
    serializer_class = AnuncioSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        """ 
        1. SEGURIDAD DE ROLES: Decide qué anuncios puede ver cada tipo de usuario.
        2. FILTROS DE BÚSQUEDA: Procesa los parámetros de la URL enviados desde Vue.
        """
        user = self.request.user
        qs = Anuncio.objects.all()
        
        # Filtro base por permisos
        if not user.is_authenticated:
            qs = qs.filter(aprobado=True, publicado=True)
        else:
            rol = obtener_rol(user)
            if rol == 'administrador':
                pass # El admin ve absolutamente toda la base de datos
            elif rol == 'propietario':
                qs = qs.filter(Q(aprobado=True, publicado=True) | Q(propietario=user))
            else:
                qs = qs.filter(aprobado=True, publicado=True)

        # --- APLICACIÓN DE FILTROS DEL BUSCADOR ---
        params = self.request.query_params

        loc = params.get('localizacion')
        if loc:
            qs = qs.filter(localizacion__icontains=loc) # Búsqueda flexible

        tipo = params.get('tipo_vivienda')
        if tipo:
            qs = qs.filter(tipo_vivienda=tipo)

        p_min = params.get('precio_min')
        if p_min:
            qs = qs.filter(precio_mes__gte=p_min) # gte = Mayor o igual que

        p_max = params.get('precio_max')
        if p_max:
            qs = qs.filter(precio_mes__lte=p_max) # lte = Menor o igual que

        if params.get('wifi') == 'true':
            qs = qs.filter(wifi=True)
        if params.get('terraza') == 'true':
            qs = qs.filter(terraza=True)
        if params.get('garaje') == 'true':
            qs = qs.filter(garaje=True)

        return qs

    def perform_create(self, serializer):
        rol = obtener_rol(self.request.user)
        if rol not in ['propietario', 'administrador']:
            raise PermissionDenied('Solo los propietarios o administradores pueden publicar anuncios.')
        serializer.save(propietario=self.request.user)

    def perform_update(self, serializer):
        anuncio = self.get_object()
        rol = obtener_rol(self.request.user)
        
        if rol == 'administrador':
            aprobado_status = self.request.data.get('aprobado', anuncio.aprobado)
            serializer.save(aprobado=aprobado_status)
        elif rol == 'propietario' and anuncio.propietario == self.request.user:
            serializer.save()
        else:
            raise PermissionDenied('No tienes permisos para modificar este anuncio.')

    def destroy(self, request, *args, **kwargs):
        anuncio = self.get_object()
        rol = obtener_rol(request.user)
        
        if rol == 'administrador' or (rol == 'propietario' and anuncio.propietario == request.user):
            anuncio.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        return Response({'error': 'Operación denegada. Sin privilegios.'}, status=status.HTTP_403_FORBIDDEN)


class ValoracioViewSet(viewsets.ModelViewSet):
    queryset = Valoracion.objects.all().order_by('-fecha_creacion')
    serializer_class = ValoracionSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        rol = obtener_rol(self.request.user)
        if rol != 'estudiante':
            raise PermissionDenied('Exclusivo estudiantes: Solo las cuentas de estudiante pueden dejar valoraciones.')
        serializer.save(usuario=self.request.user)


class UsuarioAdminView(APIView):
    """
    Nuevo endpoint exclusivo para que el administrador gestione bloqueos de usuarios.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if obtener_rol(request.user) != 'administrador':
            raise PermissionDenied('Acceso denegado.')

        # Listamos usuarios excluyendo a los superusuarios para no bloquear a otros admins accidentalmente
        usuarios = User.objects.exclude(is_superuser=True).select_related('perfil').order_by('-date_joined')
        data = []
        for u in usuarios:
            data.append({
                'id': u.id,
                'username': u.username,
                'email': u.email,
                'rol': obtener_rol(u),
                'activo': u.is_active,
            })
        return Response(data)

    def patch(self, request, pk):
        if obtener_rol(request.user) != 'administrador':
            raise PermissionDenied('Acceso denegado.')
        
        try:
            usuario = User.objects.get(pk=pk)
            nuevo_estado = request.data.get('activo')
            if nuevo_estado is not None:
                usuario.is_active = nuevo_estado
                usuario.save()
            return Response({'id': usuario.id, 'activo': usuario.is_active})
        except User.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)


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
    permission_classes = []

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        usuario = authenticate(username=username, password=password)

        if usuario is None:
            # Si el usuario existe pero is_active es False, authenticate devuelve None. 
            # El bloqueo funciona nativamente.
            return Response({'error': 'Credenciales incorrectas o cuenta suspendida.'}, status=status.HTTP_400_BAD_REQUEST)

        token, created = Token.objects.get_or_create(user=usuario)
        rol = obtener_rol(usuario)

        return Response({
            'token': token.key,
            'user': {
                'id': usuario.id,
                'username': usuario.username,
                'email': usuario.email,
                'rol': rol,
            }
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

    def patch(self, request):
        user = request.user
        nuevo_email = request.data.get('email')
        
        if nuevo_email:
            user.email = nuevo_email
            user.save()
            
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'rol': obtener_rol(user)
        })