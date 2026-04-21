from rest_framework import serializers
from .models import Anuncio, Valoracion, ImagenAnuncio, PerfilUsuario


class ImagenAnuncioSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImagenAnuncio
        fields = ['id', 'imagen_url', 'orden']


class ValoracionSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source='usuario.username', read_only=True)

    class Meta:
        model = Valoracion
        fields = ['id', 'anuncio', 'usuario', 'usuario_nombre', 'puntuacion', 'comentario', 'fecha_creacion']


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