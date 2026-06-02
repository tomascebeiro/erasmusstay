from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework import generics, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Anuncio, PerfilUsuario, SolicitudContacto, Valoracion
from .serializers import (
    AnuncioSerializer,
    SolicitudContactoSerializer,
    UserRegistrationSerializer,
    ValoracionSerializer,
)


def obtener_rol(usuario):
    """
    Devuelve el rol real del usuario de forma segura.

    Se considera administrador si:
    - el usuario es superusuario de Django;
    - el nombre de usuario es "admin";
    - el perfil tiene rol "administrador".
    """
    if not usuario or not usuario.is_authenticated:
        return "anonimo"

    if usuario.is_superuser or usuario.username == "admin":
        return "administrador"

    try:
        return usuario.perfil.rol
    except PerfilUsuario.DoesNotExist:
        return "usuario"


def es_administrador(usuario):
    """
    Indica si el usuario tiene permisos de administración.
    """
    return obtener_rol(usuario) == "administrador"


def convertir_booleano(valor):
    """
    Convierte valores recibidos por JSON o multipart en booleanos reales.

    Sirve para tratar correctamente valores como:
    - true / false;
    - "true" / "false";
    - "1" / "0";
    - "sí" / "no".
    """
    if isinstance(valor, bool):
        return valor

    if valor is None:
        return False

    if isinstance(valor, str):
        return valor.strip().lower() in ["true", "1", "yes", "si", "sí"]

    return bool(valor)


class AnuncioViewSet(viewsets.ModelViewSet):
    """
    ViewSet principal para gestionar anuncios.

    Permisos:
    - Usuarios anónimos: pueden listar y ver anuncios aprobados y publicados.
    - Estudiantes: pueden listar y ver anuncios aprobados y publicados.
    - Propietarios: pueden ver anuncios aprobados y también sus propios anuncios.
    - Administradores: pueden ver, editar, aprobar y eliminar cualquier anuncio.

    Filtro especial:
    - GET /api/anuncios/?mine=true
      Devuelve los anuncios del propietario autenticado.
      Si el usuario es administrador, devuelve todos.
    """

    serializer_class = AnuncioSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_permissions(self):
        """
        Los listados y detalles son públicos.
        Crear, editar y eliminar requiere autenticación.
        """
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]

        return [IsAuthenticated()]

    def get_queryset(self):
        """
        Construye el queryset según el rol del usuario y los filtros recibidos.

        Filtros soportados:
        - mine=true
        - localizacion
        - tipo_vivienda
        - precio_min
        - precio_max
        - wifi=true
        - terraza=true
        - garaje=true
        """
        user = self.request.user
        params = self.request.query_params

        qs = (
            Anuncio.objects
            .select_related("propietario", "propietario__perfil")
            .prefetch_related("imagenes", "valoraciones", "valoraciones__usuario")
            .all()
        )

        mine = params.get("mine") == "true"

        if mine:
            if not user.is_authenticated:
                return Anuncio.objects.none()

            rol = obtener_rol(user)

            if rol == "administrador":
                # El administrador puede usar esta vista para revisar todo.
                pass
            elif rol == "propietario":
                qs = qs.filter(propietario=user)
            else:
                return Anuncio.objects.none()
        else:
            if not user.is_authenticated:
                qs = qs.filter(aprobado=True, publicado=True)
            else:
                rol = obtener_rol(user)

                if rol == "administrador":
                    # El administrador ve todos los anuncios.
                    pass
                elif rol == "propietario":
                    # El propietario ve anuncios públicos y también los suyos.
                    qs = qs.filter(
                        Q(aprobado=True, publicado=True) |
                        Q(propietario=user)
                    )
                else:
                    # Estudiantes y otros usuarios solo ven anuncios públicos.
                    qs = qs.filter(aprobado=True, publicado=True)

        localizacion = params.get("localizacion")
        if localizacion:
            qs = qs.filter(localizacion__icontains=localizacion)

        tipo_vivienda = params.get("tipo_vivienda")
        if tipo_vivienda:
            qs = qs.filter(tipo_vivienda=tipo_vivienda)

        precio_min = params.get("precio_min")
        if precio_min:
            qs = qs.filter(precio_mes__gte=precio_min)

        precio_max = params.get("precio_max")
        if precio_max:
            qs = qs.filter(precio_mes__lte=precio_max)

        if params.get("wifi") == "true":
            qs = qs.filter(wifi=True)

        if params.get("terraza") == "true":
            qs = qs.filter(terraza=True)

        if params.get("garaje") == "true":
            qs = qs.filter(garaje=True)

        return qs

    def perform_create(self, serializer):
        """
        Crea un anuncio asignándolo al usuario autenticado.

        Solo pueden crear anuncios:
        - propietarios;
        - administradores.
        """
        rol = obtener_rol(self.request.user)

        if rol not in ["propietario", "administrador"]:
            raise PermissionDenied(
                "Solo propietarios o administradores pueden publicar anuncios."
            )

        serializer.save(propietario=self.request.user)

    def perform_update(self, serializer):
        """
        Actualiza un anuncio.

        Reglas:
        - El administrador puede modificar cualquier anuncio y aprobar/desaprobar.
        - El propietario solo puede modificar sus propios anuncios.
        - Al editar un propietario, el anuncio queda pendiente de aprobación de nuevo.
        """
        anuncio = self.get_object()
        rol = obtener_rol(self.request.user)

        if rol == "administrador":
            aprobado = self.request.data.get("aprobado", anuncio.aprobado)

            serializer.save(
                aprobado=convertir_booleano(aprobado),
                publicado=convertir_booleano(
                    self.request.data.get("publicado", anuncio.publicado)
                ),
            )
            return

        if rol == "propietario" and anuncio.propietario == self.request.user:
            # Si el propietario edita su anuncio, vuelve a revisión.
            serializer.save(aprobado=False)
            return

        raise PermissionDenied("No tienes permisos para modificar este anuncio.")

    def destroy(self, request, *args, **kwargs):
        """
        Elimina un anuncio.

        Puede eliminar:
        - el administrador;
        - el propietario si el anuncio es suyo.
        """
        anuncio = self.get_object()
        rol = obtener_rol(request.user)

        if rol == "administrador" or (
            rol == "propietario" and anuncio.propietario == request.user
        ):
            anuncio.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(
            {"error": "Operación denegada. Sin privilegios."},
            status=status.HTTP_403_FORBIDDEN,
        )


class ValoracioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para valoraciones y comentarios.

    Funcionamiento:
    - El público solo ve comentarios aprobados.
    - Los estudiantes pueden crear comentarios.
    - Los nuevos comentarios quedan pendientes.
    - El administrador puede aprobar, ocultar o eliminar comentarios.
    """

    serializer_class = ValoracionSerializer

    def get_permissions(self):
        """
        Listar y ver valoraciones es público.
        Crear, editar y eliminar requiere autenticación.
        """
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]

        return [IsAuthenticated()]

    def get_queryset(self):
        """
        Devuelve comentarios según rol.

        - Administrador: todos.
        - Resto: solo aprobados.
        """
        qs = Valoracion.objects.select_related("usuario", "anuncio").order_by(
            "-fecha_creacion"
        )

        user = self.request.user

        if user.is_authenticated and es_administrador(user):
            return qs

        return qs.filter(aprobado=True)

    def perform_create(self, serializer):
        """
        Crea una valoración.

        Solo los estudiantes pueden valorar.
        La valoración queda pendiente de moderación.
        """
        rol = obtener_rol(self.request.user)

        if rol != "estudiante":
            raise PermissionDenied(
                "Solo las cuentas de estudiante pueden dejar valoraciones."
            )

        serializer.save(usuario=self.request.user, aprobado=False)

    def perform_update(self, serializer):
        """
        Solo el administrador puede moderar comentarios.
        """
        if not es_administrador(self.request.user):
            raise PermissionDenied("Solo el administrador puede moderar comentarios.")

        serializer.save()

    def destroy(self, request, *args, **kwargs):
        """
        Solo el administrador puede eliminar comentarios.
        """
        if not es_administrador(request.user):
            raise PermissionDenied("Solo el administrador puede eliminar comentarios.")

        return super().destroy(request, *args, **kwargs)


class SolicitudContactoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para solicitudes de contacto.

    Reglas:
    - Estudiante: ve sus solicitudes realizadas.
    - Propietario: ve solicitudes recibidas en sus anuncios.
    - Administrador: ve todas.
    """

    serializer_class = SolicitudContactoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filtra las solicitudes según el rol del usuario.
        """
        user = self.request.user
        rol = obtener_rol(user)

        qs = (
            SolicitudContacto.objects
            .select_related(
                "estudiante",
                "anuncio",
                "anuncio__propietario",
                "anuncio__propietario__perfil",
            )
            .all()
        )

        if rol == "administrador":
            return qs

        if rol == "propietario":
            return qs.filter(anuncio__propietario=user)

        return qs.filter(estudiante=user)

    def perform_create(self, serializer):
        """
        Crea una solicitud de contacto.

        Solo estudiantes pueden solicitar contacto.
        Se guarda una copia del teléfono y email del propietario en ese momento.
        """
        rol = obtener_rol(self.request.user)

        if rol != "estudiante":
            raise PermissionDenied(
                "Solo los estudiantes pueden solicitar contacto con propietarios."
            )

        anuncio = serializer.validated_data["anuncio"]

        if anuncio.propietario == self.request.user:
            raise PermissionDenied(
                "No puedes solicitar contacto sobre tu propio anuncio."
            )

        serializer.save(
            estudiante=self.request.user,
            telefono_propietario_snapshot=anuncio.telefono_propietario,
            email_propietario_snapshot=anuncio.email_propietario,
        )

    def perform_update(self, serializer):
        """
        Actualiza una solicitud.

        Puede actualizar:
        - el administrador;
        - el propietario del anuncio asociado.
        """
        solicitud = self.get_object()
        rol = obtener_rol(self.request.user)

        if rol == "administrador" or solicitud.anuncio.propietario == self.request.user:
            serializer.save()
            return

        raise PermissionDenied("No tienes permisos para actualizar esta solicitud.")


class UsuarioAdminView(APIView):
    """
    Endpoint de administración para usuarios.

    Permite:
    - listar usuarios;
    - activar o bloquear cuentas.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        """
        Lista todos los usuarios no superusuarios.
        """
        if not es_administrador(request.user):
            raise PermissionDenied("Acceso denegado.")

        usuarios = (
            User.objects
            .exclude(is_superuser=True)
            .select_related("perfil")
            .order_by("-date_joined")
        )

        data = []

        for usuario in usuarios:
            perfil = getattr(usuario, "perfil", None)

            data.append({
                "id": usuario.id,
                "username": usuario.username,
                "email": usuario.email,
                "rol": obtener_rol(usuario),
                "telefono": perfil.telefono if perfil else "",
                "activo": usuario.is_active,
            })

        return Response(data)

    def patch(self, request, pk):
        """
        Activa o bloquea una cuenta de usuario.
        """
        if not es_administrador(request.user):
            raise PermissionDenied("Acceso denegado.")

        try:
            usuario = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response(
                {"error": "Usuario no encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )

        nuevo_estado = request.data.get("activo")

        if nuevo_estado is not None:
            usuario.is_active = convertir_booleano(nuevo_estado)
            usuario.save(update_fields=["is_active"])

        return Response({
            "id": usuario.id,
            "activo": usuario.is_active,
        })


class RegistroView(generics.CreateAPIView):
    """
    Registro público de usuarios.

    Crea:
    - usuario Django;
    - perfil asociado;
    - token de autenticación.
    """

    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        """
        Registra al usuario y devuelve token + datos básicos.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        usuario = serializer.save()
        token, _ = Token.objects.get_or_create(user=usuario)

        return Response(
            {
                "token": token.key,
                "user": {
                    "id": usuario.id,
                    "username": usuario.username,
                    "email": usuario.email,
                    "rol": obtener_rol(usuario),
                    "telefono": usuario.perfil.telefono,
                },
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """
    Inicio de sesión mediante usuario y contraseña.
    """

    permission_classes = []

    def post(self, request):
        """
        Devuelve token y datos básicos del usuario autenticado.
        """
        username = request.data.get("username")
        password = request.data.get("password")

        usuario = authenticate(username=username, password=password)

        if usuario is None:
            return Response(
                {"error": "Credenciales incorrectas o cuenta suspendida."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token, _ = Token.objects.get_or_create(user=usuario)
        perfil = getattr(usuario, "perfil", None)

        return Response({
            "token": token.key,
            "user": {
                "id": usuario.id,
                "username": usuario.username,
                "email": usuario.email,
                "rol": obtener_rol(usuario),
                "telefono": perfil.telefono if perfil else "",
            },
        })


class MiPerfilView(APIView):
    """
    Perfil del usuario autenticado.

    Permite:
    - consultar datos propios;
    - actualizar email;
    - actualizar teléfono.

    El teléfono del perfil es el que aparece en los anuncios del propietario.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Devuelve los datos del usuario autenticado.
        """
        perfil, _ = PerfilUsuario.objects.get_or_create(usuario=request.user)

        return Response({
            "id": request.user.id,
            "username": request.user.username,
            "email": request.user.email,
            "rol": obtener_rol(request.user),
            "telefono": perfil.telefono,
        })

    def patch(self, request):
        """
        Actualiza email y teléfono del usuario autenticado.
        """
        user = request.user
        perfil, _ = PerfilUsuario.objects.get_or_create(usuario=user)

        nuevo_email = request.data.get("email")
        nuevo_telefono = request.data.get("telefono")

        if nuevo_email is not None:
            user.email = nuevo_email
            user.save(update_fields=["email"])

        if nuevo_telefono is not None:
            perfil.telefono = nuevo_telefono
            perfil.save(update_fields=["telefono"])

        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "rol": obtener_rol(user),
            "telefono": perfil.telefono,
        })