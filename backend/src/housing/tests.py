from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from .models import Anuncio, PerfilUsuario

class ErasmusStayTests(APITestCase):

    def setUp(self):
        # Limpiamos anuncios previos antes de cada test para evitar que se acumulen
        Anuncio.objects.all().delete()
        
        self.admin = User.objects.create_superuser('admin', 'admin@test.com', 'pass')
        PerfilUsuario.objects.create(usuario=self.admin, rol='administrador')
        
        self.propietario = User.objects.create_user('propietario', 'p@test.com', 'pass')
        PerfilUsuario.objects.create(usuario=self.propietario, rol='propietario')
        
        self.estudiante = User.objects.create_user('estudiante', 'e@test.com', 'pass')
        PerfilUsuario.objects.create(usuario=self.estudiante, rol='estudiante')

        self.anuncios_url = reverse('anuncio-list')

    def test_crear_anuncio_como_propietario(self):
        self.client.force_authenticate(user=self.propietario)
        data = {
            'titulo': 'Test Piso',
            'descripcion': 'Descripción de prueba',
            'precio_mes': 500,
            'localizacion': 'Sliema',
            'tipo_vivienda': 'habitacion' # Aseguramos campo obligatorio
        }
        response = self.client.post(self.anuncios_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_crear_anuncio_como_estudiante_denegado(self):
        self.client.force_authenticate(user=self.estudiante)
        # Enviamos datos completos para que no falle por validación (400) sino por permisos (403)
        data = {
            'titulo': 'Piso ilegal', 
            'descripcion': 'x', 
            'precio_mes': 100, 
            'localizacion': 'x',
            'tipo_vivienda': 'habitacion'
        }
        response = self.client.post(self.anuncios_url, data, format='json')
        # Ahora debería devolver 403 Forbidden porque el estudiante no tiene rol
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_busqueda_filtros(self):
        """Prueba que el filtro de precio funciona correctamente."""
        # 1. Crear datos
        Anuncio.objects.create(
            propietario=self.propietario, titulo='Caro', descripcion='x',
            precio_mes=1000, localizacion='Sliema', aprobado=True, publicado=True, tipo_vivienda='habitacion'
        )
        Anuncio.objects.create(
            propietario=self.propietario, titulo='Barato', descripcion='x',
            precio_mes=200, localizacion='Sliema', aprobado=True, publicado=True, tipo_vivienda='habitacion'
        )
        
        # 2. Llamada a la API con filtro
        response = self.client.get(f"{self.anuncios_url}?precio_max=300")
        
        # 3. Acceder a los resultados dentro de la respuesta paginada
        # Si no hay paginación activa en el test, response.data es la lista.
        # Si hay paginación, es data['results']. Manejamos ambos casos:
        results = response.data['results'] if isinstance(response.data, dict) and 'results' in response.data else response.data
        
        self.assertEqual(len(results), 1, f"Se esperaban 1 resultado, pero se obtuvieron {len(results)}")
        self.assertEqual(results[0]['titulo'], 'Barato')