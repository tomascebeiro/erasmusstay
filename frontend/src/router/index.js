import { createRouter, createWebHistory } from 'vue-router'
import { useAuth } from '../composables/useAuth'

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

const routes = [
  {
    path: '/',
    name: 'inicio',
    component: Inicio,
  },
  {
    path: '/anuncios',
    name: 'anuncios',
    component: ListadoAnuncios,
  },
  {
    path: '/mis-anuncios',
    name: 'mis-anuncios',
    component: MisAnuncios,
    meta: {
      requiresAuth: true,
      requiresOwner: true,
    },
  },
  {
    path: '/anuncio/:id',
    name: 'anuncio-detalle',
    component: AnuncioDetalle,
  },
  {
    path: '/crear-anuncio',
    name: 'crear-anuncio',
    component: CrearAnuncio,
    meta: {
      requiresAuth: true,
      requiresOwner: true,
    },
  },
  {
    path: '/editar-anuncio/:id',
    name: 'editar-anuncio',
    component: CrearAnuncio,
    meta: {
      requiresAuth: true,
      requiresOwner: true,
    },
  },
  {
    path: '/contacto/:id?',
    name: 'contacto',
    component: Contacto,
    meta: {
      requiresAuth: true,
    },
  },
  {
    path: '/login',
    name: 'login',
    component: Login,
    meta: {
      guestOnly: true,
    },
  },
  {
    path: '/profile',
    name: 'profile',
    component: Profile,
    meta: {
      requiresAuth: true,
    },
  },
  {
    path: '/register',
    name: 'register',
    component: Register,
    meta: {
      guestOnly: true,
    },
  },
  {
    path: '/admin-panel',
    name: 'admin-panel',
    component: AdminPanel,
    meta: {
      requiresAuth: true,
      requiresAdmin: true,
    },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to) => {
  const { isAuthenticated, restoreSession, user } = useAuth()

  if (!isAuthenticated.value && localStorage.getItem('token')) {
    await restoreSession()
  }

  if (to.meta.requiresAuth && !isAuthenticated.value) {
    return {
      name: 'login',
      query: {
        redirect: to.fullPath,
      },
    }
  }

  const role = (user.value?.rol || '').toLowerCase()
  const username = (user.value?.username || '').toLowerCase()

  if (to.meta.requiresAdmin) {
    if (role !== 'administrador' && username !== 'admin') {
      return { name: 'inicio' }
    }
  }

  if (to.meta.requiresOwner) {
    if (!['propietario', 'administrador'].includes(role) && username !== 'admin') {
      return { name: 'inicio' }
    }
  }

  if (to.meta.guestOnly && isAuthenticated.value) {
    return { name: 'inicio' }
  }

  return true
})

export default router