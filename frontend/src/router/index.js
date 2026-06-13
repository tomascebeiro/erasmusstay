/**
 * Configuración principal del router de Vue para ErasmusStay.
 *
 * Este archivo define todas las rutas del frontend. Cada ruta conecta una URL
 * del navegador con un componente o vista de Vue.
 *
 * Además de declarar páginas, también se gestionan restricciones de acceso
 * mediante el campo `meta`:
 *
 * - requiresAuth:
 *   la ruta necesita que el usuario haya iniciado sesión.
 *
 * - requiresOwner:
 *   la ruta solo puede ser usada por propietarios o administradores.
 *
 * - requiresAdmin:
 *   la ruta solo puede ser usada por administradores.
 *
 * - guestOnly:
 *   la ruta solo tiene sentido para usuarios no autenticados, como login o
 *   registro. Si el usuario ya está autenticado, se redirige al inicio.
 *
 * La protección real se aplica en `router.beforeEach`, que se ejecuta antes de
 * entrar en cualquier ruta.
 */

import { createRouter, createWebHistory } from 'vue-router'
import { useAuth } from '../composables/useAuth'

// Componentes y vistas usadas por las rutas.
import ListadoAnuncios from '../components/ListadoAnuncios.vue'
import AnuncioDetalle from '../views/AnuncioDetalle.vue'
import Contacto from '../views/Contacto.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import CrearAnuncio from '../views/CrearAnuncio.vue'
import AdminPanel from '../views/AdminPanel.vue'
import Inicio from '../views/Inicio.vue'
import Profile from '../views/Profile.vue'
import MisAnuncios from '../views/MisAnuncios.vue'


/**
 * Lista de rutas de la aplicación.
 *
 * Cada objeto representa una URL del frontend:
 *
 * - path: URL que verá el usuario.
 * - name: nombre interno usado para redirecciones y router-link.
 * - component: componente Vue que se renderiza.
 * - meta: reglas adicionales de acceso.
 */
const routes = [
  {
    // Página principal o landing.
    path: '/',
    name: 'inicio',
    component: Inicio,
  },
  {
    // Listado público de anuncios con filtros.
    path: '/anuncios',
    name: 'anuncios',
    component: ListadoAnuncios,
  },
  {
    // Panel de anuncios propios del propietario.
    // Solo propietarios o administradores pueden acceder.
    path: '/mis-anuncios',
    name: 'mis-anuncios',
    component: MisAnuncios,
    meta: {
      requiresAuth: true,
      requiresOwner: true,
    },
  },
  {
    // Ficha pública de un anuncio concreto.
    // El parámetro :id indica qué anuncio se debe cargar desde la API.
    path: '/anuncio/:id',
    name: 'anuncio-detalle',
    component: AnuncioDetalle,
  },
  {
    // Formulario de creación de anuncio.
    // Requiere sesión y rol de propietario o administrador.
    path: '/crear-anuncio',
    name: 'crear-anuncio',
    component: CrearAnuncio,
    meta: {
      requiresAuth: true,
      requiresOwner: true,
    },
  },
  {
    // Formulario de edición de anuncio.
    // Reutiliza el mismo componente que la creación, pero con un id en la URL.
    path: '/editar-anuncio/:id',
    name: 'editar-anuncio',
    component: CrearAnuncio,
    meta: {
      requiresAuth: true,
      requiresOwner: true,
    },
  },
  {
    // Página de contacto e historial de solicitudes.
    // El parámetro :id es opcional y se usa cuando se solicita contacto desde
    // un anuncio concreto.
    path: '/contacto/:id?',
    name: 'contacto',
    component: Contacto,
    meta: {
      requiresAuth: true,
    },
  },
  {
    // Página de inicio de sesión.
    // Solo debe mostrarse a usuarios no autenticados.
    path: '/login',
    name: 'login',
    component: Login,
    meta: {
      guestOnly: true,
    },
  },
  {
    // Perfil del usuario autenticado.
    // Permite consultar o modificar email y teléfono.
    path: '/profile',
    name: 'profile',
    component: Profile,
    meta: {
      requiresAuth: true,
    },
  },
  {
    // Página de registro.
    // Solo debe mostrarse a usuarios no autenticados.
    path: '/register',
    name: 'register',
    component: Register,
    meta: {
      guestOnly: true,
    },
  },
  {
    // Panel de administración del frontend.
    // Solo administradores pueden acceder.
    path: '/admin-panel',
    name: 'admin-panel',
    component: AdminPanel,
    meta: {
      requiresAuth: true,
      requiresAdmin: true,
    },
  },
]


/**
 * Creación del router.
 *
 * createWebHistory usa URLs limpias sin hash (#), por ejemplo:
 *
 * /anuncios
 * /profile
 * /admin-panel
 *
 * Esto hace que la navegación sea más natural para el usuario.
 */
const router = createRouter({
  history: createWebHistory(),
  routes,
})


/**
 * Guardia global de navegación.
 *
 * Esta función se ejecuta antes de entrar en cualquier ruta.
 *
 * Sirve para:
 * 1. Restaurar la sesión si existe un token guardado.
 * 2. Redirigir al login si una ruta requiere autenticación.
 * 3. Bloquear rutas de administrador si el usuario no tiene permisos.
 * 4. Bloquear rutas de propietario si el usuario no es propietario/admin.
 * 5. Evitar que usuarios autenticados entren en login o registro.
 */
router.beforeEach(async (to) => {
  const { isAuthenticated, restoreSession, user } = useAuth()

  // Si Vue todavía no tiene sesión en memoria pero existe token guardado,
  // se intenta restaurar la sesión llamando al backend.
  if (!isAuthenticated.value && localStorage.getItem('token')) {
    await restoreSession()
  }

  // Si la ruta requiere autenticación y el usuario no está autenticado,
  // se envía al login. Se guarda la ruta original en query.redirect para poder
  // volver después del inicio de sesión.
  if (to.meta.requiresAuth && !isAuthenticated.value) {
    return {
      name: 'login',
      query: {
        redirect: to.fullPath,
      },
    }
  }

  // Normalizamos rol y username para evitar problemas con mayúsculas.
  const role = (user.value?.rol || '').toLowerCase()
  const username = (user.value?.username || '').toLowerCase()

  // Protección de rutas exclusivas para administradores.
  // Se permite acceso si el rol es administrador o si el username es admin.
  if (to.meta.requiresAdmin) {
    if (role !== 'administrador' && username !== 'admin') {
      return { name: 'inicio' }
    }
  }

  // Protección de rutas para propietarios o administradores.
  // Se usa en crear anuncio, editar anuncio y mis anuncios.
  if (to.meta.requiresOwner) {
    if (!['propietario', 'administrador'].includes(role) && username !== 'admin') {
      return { name: 'inicio' }
    }
  }

  // Si el usuario ya inició sesión, no tiene sentido que entre en login o
  // registro. Se redirige al inicio.
  if (to.meta.guestOnly && isAuthenticated.value) {
    return { name: 'inicio' }
  }

  // Si ninguna regla bloquea la navegación, se permite continuar.
  return true
})


export default router