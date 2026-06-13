"""
Vistas y endpoints principales de la API REST de ErasmusStay.

Este archivo contiene la lógica que conecta el frontend Vue con el backend
Django. Define las vistas que responden a las peticiones HTTP de la aplicación.

En Django REST Framework, un ViewSet permite agrupar varias operaciones sobre
un mismo recurso:

- listar registros;
- consultar un detalle;
- crear;
- actualizar;
- eliminar.

En este archivo se gestionan principalmente:

- anuncios de alojamiento;
- valoraciones y comentarios;
- solicitudes de contacto;
- administración de usuarios;
- registro;
- login;
- perfil del usuario autenticado.

También se aplican reglas de permisos según el rol del usuario:

- anónimo;
- estudiante;
- propietario;
- administrador.

El frontend Vue consume estos endpoints mediante fetch, enviando el token de
autenticación cuando necesita acceder a rutas privadas.
"""

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

    Esta función centraliza la lógica de roles para no repetir comprobaciones
    en todas las vistas.

    Se considera administrador si:
    - el usuario es superusuario de Django;
    - el nombre de usuario es "admin";
    - el perfil tiene rol "administrador".

    Si el usuario no está autenticado, devuelve "anonimo".
    Si el usuario no tiene perfil, devuelve "usuario" como valor de seguridad.
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

    Internamente utiliza obtener_rol para mantener una única fuente de verdad
    sobre los permisos administrativos.
    """
    return obtener_rol(usuario) == "administrador"


def convertir_booleano(valor):
    """
    Convierte valores recibidos por JSON o multipart en booleanos reales.

    Esta función es necesaria porque, cuando el frontend envía datos mediante
    FormData o multipart/form-data, algunos booleanos pueden llegar como texto.

    Soporta valores como:
    - true / false;
    - "true" / "false";
    - "1" / "0";
    - "yes" / "no";
    - "si" / "sí".

    Devuelve True o False de forma consistente para poder guardar correctamente
    los campos booleanos en la base de datos.
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

    Este ViewSet controla las operaciones CRUD de los alojamientos:

    - listar anuncios;
    - ver detalle de un anuncio;
    - crear anuncio;
    - editar anuncio;
    - eliminar anuncio.

    Permisos:
    - Usuarios anónimos: pueden listar y ver anuncios aprobados y publicados.
    - Estudiantes: pueden listar y ver anuncios aprobados y publicados.
    - Propietarios: pueden ver anuncios aprobados y también sus propios anuncios.
    - Administradores: pueden ver, editar, aprobar y eliminar cualquier anuncio.

    Filtro especial:
    - GET /api/anuncios/?mine=true

    Este filtro devuelve los anuncios del propietario autenticado. Si el usuario
    es administrador, devuelve todos los anuncios para facilitar la revisión.
    """

    # Serializer que convierte los anuncios en JSON y valida datos entrantes.
    serializer_class = AnuncioSerializer

    # Parsers aceptados por este endpoint.
    # MultiPartParser y FormParser permiten recibir imágenes desde el frontend.
    # JSONParser permite recibir peticiones JSON normales.
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_permissions(self):
        """
        Define los permisos según la acción ejecutada.

        Las acciones list y retrieve son públicas porque cualquier usuario debe
        poder consultar anuncios aprobados.

        El resto de acciones requieren autenticación:
        - create;
        - update;
        - partial_update;
        - destroy.
        """
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]

        return [IsAuthenticated()]

    def get_queryset(self):
        """
        Construye el queryset de anuncios según el rol del usuario y los filtros.

        Filtros soportados desde el frontend:
        - mine=true: muestra anuncios propios del propietario.
        - localizacion: filtra por texto de ubicación.
        - tipo_vivienda: filtra por habitación, piso completo o estudio.
        - precio_min: precio mínimo mensual.
        - precio_max: precio máximo mensual.
        - wifi=true: exige que tenga wifi.
        - terraza=true: exige que tenga terraza.
        - garaje=true: exige que tenga garaje.

        También optimiza consultas usando:
        - select_related para propietario y perfil;
        - prefetch_related para imágenes y valoraciones.
        """
        user = self.request.user
        params = self.request.query_params

        # Consulta base de anuncios con relaciones precargadas.
        # Esto reduce el número de consultas a base de datos cuando el serializer
        # necesita acceder a propietario, perfil, imágenes o valoraciones.
        qs = (
            Anuncio.objects
            .select_related("propietario", "propietario__perfil")
            .prefetch_related("imagenes", "valoraciones", "valoraciones__usuario")
            .all()
        )

        # Filtro especial usado en "Mis anuncios".
        mine = params.get("mine") == "true"

        if mine:
            if not user.is_authenticated:
                return Anuncio.objects.none()

            rol = obtener_rol(user)

            if rol == "administrador":
                # El administrador puede usar esta vista para revisar todo.
                pass
            elif rol == "propietario":
                # El propietario solo ve sus propios anuncios.
                qs = qs.filter(propietario=user)
            else:
                # Un estudiante no tiene anuncios propios.
                return Anuncio.objects.none()
        else:
            if not user.is_authenticated:
                # Usuario anónimo: solo anuncios públicos.
                qs = qs.filter(aprobado=True, publicado=True)
            else:
                rol = obtener_rol(user)

                if rol == "administrador":
                    # El administrador ve todos los anuncios.
                    pass
                elif rol == "propietario":
                    # El propietario ve anuncios públicos y también los suyos,
                    # aunque todavía no estén aprobados.
                    qs = qs.filter(
                        Q(aprobado=True, publicado=True) |
                        Q(propietario=user)
                    )
                else:
                    # Estudiantes y otros usuarios solo ven anuncios públicos.
                    qs = qs.filter(aprobado=True, publicado=True)

        # Filtro por localización parcial.
        localizacion = params.get("localizacion")
        if localizacion:
            qs = qs.filter(localizacion__icontains=localizacion)

        # Filtro por tipo de vivienda exacto.
        tipo_vivienda = params.get("tipo_vivienda")
        if tipo_vivienda:
            qs = qs.filter(tipo_vivienda=tipo_vivienda)

        # Filtro por precio mínimo.
        precio_min = params.get("precio_min")
        if precio_min:
            qs = qs.filter(precio_mes__gte=precio_min)

        # Filtro por precio máximo.
        precio_max = params.get("precio_max")
        if precio_max:
            qs = qs.filter(precio_mes__lte=precio_max)

        # Filtros por servicios.
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

        El propietario no se recibe desde el frontend. Se asigna siempre desde
        request.user para evitar que un usuario pueda crear anuncios en nombre
        de otra cuenta.
        """
        rol = obtener_rol(self.request.user)

        if rol not in ["propietario", "administrador"]:
            raise PermissionDenied(
                "Solo propietarios o administradores pueden publicar anuncios."
            )

        serializer.save(propietario=self.request.user)

    def perform_update(self, serializer):
        """
        Actualiza un anuncio aplicando reglas de permisos.

        Reglas:
        - El administrador puede modificar cualquier anuncio y aprobar/desaprobar.
        - El propietario solo puede modificar sus propios anuncios.
        - Si un propietario edita su anuncio, vuelve a quedar pendiente de
          aprobación para que el administrador revise los cambios.

        Esta lógica evita que un propietario cambie datos importantes después de
        que el anuncio haya sido aprobado sin pasar por moderación.
        """
        anuncio = self.get_object()
        rol = obtener_rol(self.request.user)

        if rol == "administrador":
            # El administrador puede cambiar explícitamente aprobado/publicado.
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

        Si otro usuario intenta eliminar el anuncio, se devuelve un error 403.
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

    Este flujo permite moderar las opiniones antes de que aparezcan
    públicamente en la ficha de un anuncio.
    """

    serializer_class = ValoracionSerializer

    def get_permissions(self):
        """
        Define permisos para las valoraciones.

        Listar y ver valoraciones es público.
        Crear, editar y eliminar requiere autenticación.
        """
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]

        return [IsAuthenticated()]

    def get_queryset(self):
        """
        Devuelve comentarios según rol.

        - Administrador: ve todos los comentarios, aprobados y pendientes.
        - Resto de usuarios: solo ve comentarios aprobados.

        Esto permite que el panel de administración pueda moderar valoraciones
        sin exponer comentarios pendientes al público.
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
        Crea una valoración nueva.

        Solo los estudiantes pueden valorar anuncios. La valoración se guarda
        con aprobado=False para que el administrador la modere antes de que sea
        visible públicamente.
        """
        rol = obtener_rol(self.request.user)

        if rol != "estudiante":
            raise PermissionDenied(
                "Solo las cuentas de estudiante pueden dejar valoraciones."
            )

        serializer.save(usuario=self.request.user, aprobado=False)

    def perform_update(self, serializer):
        """
        Actualiza una valoración.

        Solo el administrador puede moderar comentarios, por ejemplo cambiando
        el campo aprobado.
        """
        if not es_administrador(self.request.user):
            raise PermissionDenied("Solo el administrador puede moderar comentarios.")

        serializer.save()

    def destroy(self, request, *args, **kwargs):
        """
        Elimina una valoración.

        Solo el administrador puede eliminar comentarios.
        """
        if not es_administrador(request.user):
            raise PermissionDenied("Solo el administrador puede eliminar comentarios.")

        return super().destroy(request, *args, **kwargs)


class SolicitudContactoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para solicitudes de contacto.

    Gestiona el flujo en el que un estudiante solicita contactar con el
    propietario de un anuncio.

    Reglas:
    - Estudiante: ve sus solicitudes realizadas.
    - Propietario: ve solicitudes recibidas en sus anuncios.
    - Administrador: ve todas.
    """

    serializer_class = SolicitudContactoSerializer

    # Todas las operaciones de solicitudes requieren usuario autenticado.
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filtra las solicitudes según el rol del usuario.

        El objetivo es que cada tipo de usuario vea solo la información que le
        corresponde:

        - administrador: todas las solicitudes;
        - propietario: solicitudes de sus anuncios;
        - estudiante: solicitudes que realizó.
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

        Solo estudiantes pueden solicitar contacto. Además, un usuario no puede
        solicitar contacto sobre su propio anuncio.

        Al crear la solicitud se guarda una copia del teléfono y email del
        propietario en ese momento. Esto permite conservar el historial aunque el
        propietario cambie sus datos más adelante.
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
        Actualiza una solicitud de contacto.

        Puede actualizar:
        - el administrador;
        - el propietario del anuncio asociado.

        Normalmente se usa para cambiar el estado de la solicitud.
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

    Permite al administrador:
    - listar usuarios;
    - consultar su rol y teléfono;
    - activar o bloquear cuentas.

    No devuelve superusuarios para evitar que el panel gestione la cuenta
    principal de administración del sistema.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        """
        Lista todos los usuarios no superusuarios.

        Solo puede acceder el administrador. La respuesta devuelve una lista
        simplificada con los datos necesarios para el panel frontend.
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

        Recibe el campo `activo` desde el frontend. Si llega, se convierte a
        booleano y se guarda en user.is_active.
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

    El token permite que el frontend pueda autenticar llamadas posteriores a la
    API usando la cabecera Authorization.
    """

    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        """
        Registra al usuario y devuelve token + datos básicos.

        Se usa el serializer UserRegistrationSerializer para validar los datos,
        crear el usuario y crear el perfil asociado.
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

    Si las credenciales son válidas, devuelve:
    - token de autenticación;
    - datos básicos del usuario;
    - rol;
    - teléfono.
    """

    # Login es público, por eso no se exige autenticación previa.
    permission_classes = []

    def post(self, request):
        """
        Devuelve token y datos básicos del usuario autenticado.

        Si las credenciales son incorrectas o la cuenta está suspendida, devuelve
        error 400.
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

        Si el usuario no tiene perfil, se crea uno automáticamente para evitar
        errores en cuentas antiguas.
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

        Solo permite modificar datos propios. El username y el rol no se
        actualizan desde este endpoint para evitar cambios de identidad o
        escalado de permisos desde el frontend.
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