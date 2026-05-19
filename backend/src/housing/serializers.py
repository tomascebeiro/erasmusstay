from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Anuncio, Valoracion, ImagenAnuncio, PerfilUsuario

class ImagenAnuncioSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImagenAnuncio
        fields = ['id', 'imagen_url', 'orden']


class ValoracionSerializer(serializers.ModelSerializer):
    # Campo de solo lectura para extraer el nombre del autor automáticamente
    usuario_nombre = serializers.CharField(source='usuario.username', read_only=True)

    class Meta:
        model = Valoracion
        fields = ['id', 'anuncio', 'usuario', 'usuario_nombre', 'puntuacion', 'comentario', 'fecha_creacion']
        read_only_fields = ['usuario'] # El usuario lo inyecta el backend por seguridad


class UserRegistrationSerializer(serializers.ModelSerializer):
    # write_only=True evita que el rol se devuelva expuesto en la respuesta de creación del User
    rol = serializers.ChoiceField(choices=PerfilUsuario.Rol.choices, default=PerfilUsuario.Rol.ESTUDIANTE, write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'rol']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
        }

    def create(self, validated_data):
        """ Sobreescritura del método para crear atómicamente User + PerfilUsuario """
        role = validated_data.pop('rol', PerfilUsuario.Rol.ESTUDIANTE)
        password = validated_data.pop('password')
        
        user = User.objects.create_user(**validated_data, password=password)
        # Se genera automáticamente la vinculación 1 a 1 requerida
        PerfilUsuario.objects.create(usuario=user, rol=role)
        return user


class AnuncioSerializer(serializers.ModelSerializer):
    imagenes = ImagenAnuncioSerializer(many=True, read_only=True)
    valoraciones = ValoracionSerializer(many=True, read_only=True)
    propietario_nombre = serializers.CharField(source='propietario.username', read_only=True)

    class Meta:
        model = Anuncio
        fields = [
            'id',
            'propietario',
            'propietario_nombre',
            'titulo',
            'descripcion',
            'precio_mes',
            'localizacion',
            'tipo_vivienda',
            'duracion_min_meses',
            'duracion_max_meses',
            'wifi',
            'terraza',
            'garaje',
            'telefono_contacto',
            'email_contacto',
            'publicado',
            'aprobado',
            'fecha_creacion',
            'imagenes',
            'valoraciones',
        ]
        read_only_fields = ['propietario', 'aprobado'] # Solo el admin puede modificar 'aprobado'