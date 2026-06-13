<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'

/**
 * Barra de navegación principal de ErasmusStay.
 *
 * Responsabilidades:
 * - Mostrar enlaces públicos: inicio, anuncios y contacto.
 * - Mostrar enlaces privados según el rol del usuario.
 * - Permitir a propietarios acceder a "Mis anuncios" y publicar anuncios.
 * - Permitir a administradores acceder al panel de administración.
 * - Gestionar cierre de sesión y menú móvil.
 */

const router = useRouter()
const menuOpen = ref(false)

const { user, isAuthenticated, logout } = useAuth()

/**
 * Cierra el menú móvil.
 */
const closeMenu = () => {
  menuOpen.value = false
}

/**
 * Cierra la sesión del usuario y lo devuelve a la página de inicio.
 */
const handleLogout = () => {
  logout()
  closeMenu()
  router.push('/')
}

/**
 * Normaliza el rol del usuario para evitar errores por mayúsculas,
 * espacios o usuarios administradores creados como superuser.
 */
const normalizedRole = computed(() => {
  return (user.value?.rol || '').toLowerCase().trim()
})

const normalizedUsername = computed(() => {
  return (user.value?.username || '').toLowerCase().trim()
})

/**
 * Determina si el usuario actual es administrador.
 *
 * Se aceptan dos casos:
 * - rol explícito "administrador";
 * - usuario "admin", usado habitualmente en desarrollo.
 */
const isAdmin = computed(() => {
  if (!isAuthenticated.value) return false

  return normalizedRole.value === 'administrador' || normalizedUsername.value === 'admin'
})

/**
 * Determina si el usuario puede publicar y gestionar anuncios.
 *
 * Pueden hacerlo:
 * - propietarios;
 * - administradores;
 * - usuario admin de desarrollo.
 */
const isOwnerOrAdmin = computed(() => {
  if (!isAuthenticated.value) return false

  return ['propietario', 'administrador'].includes(normalizedRole.value) || normalizedUsername.value === 'admin'
})

/**
 * Texto visible del rol en castellano.
 */
const displayRole = computed(() => {
  if (!user.value?.rol) return 'Usuario'

  if (normalizedRole.value === 'administrador') return 'Administrador'
  if (normalizedRole.value === 'propietario') return 'Propietario'
  if (normalizedRole.value === 'estudiante') return 'Estudiante'

  return 'Usuario'
})
</script>

<template>
  <header class="sticky top-0 z-50 border-b border-slate-200 bg-white">
    <nav class="mx-auto flex h-16 max-w-7xl items-center justify-between px-4">
      <!-- Marca -->
      <router-link
        to="/"
        class="flex items-center gap-2"
        @click="closeMenu"
      >
        <span class="text-xl font-bold tracking-tight text-slate-900">
          Erasmus<span class="text-slate-600">Stay</span>
        </span>
      </router-link>

      <!-- Navegación escritorio -->
      <div class="hidden items-center gap-6 md:flex">
        <router-link
          to="/"
          class="text-sm font-medium text-slate-600 hover:text-slate-900"
          active-class="text-slate-900 font-semibold"
        >
          Inicio
        </router-link>

        <router-link
          to="/anuncios"
          class="text-sm font-medium text-slate-600 hover:text-slate-900"
          active-class="text-slate-900 font-semibold"
        >
          Alojamientos
        </router-link>

        <router-link
          v-if="isOwnerOrAdmin"
          to="/mis-anuncios"
          class="text-sm font-medium text-slate-600 hover:text-slate-900"
          active-class="text-slate-900 font-semibold"
        >
          Mis anuncios
        </router-link>

        <router-link
          to="/contacto"
          class="text-sm font-medium text-slate-600 hover:text-slate-900"
          active-class="text-slate-900 font-semibold"
        >
          Solicitudes
        </router-link>

        <router-link
          v-if="isAdmin"
          to="/admin-panel"
          class="text-sm font-medium text-blue-600 hover:text-blue-700"
          active-class="text-blue-700 font-semibold"
        >
          Panel de administración
        </router-link>
      </div>

      <!-- Acciones escritorio -->
      <div class="hidden items-center gap-3 md:flex">
        <template v-if="isAuthenticated">
          <router-link
            to="/profile"
            class="mr-2 text-sm font-medium text-slate-600 hover:text-slate-900"
            active-class="text-slate-900 font-semibold"
          >
            Mi perfil
          </router-link>

          <router-link
            v-if="isOwnerOrAdmin"
            to="/crear-anuncio"
            class="rounded bg-slate-900 px-4 py-2 text-sm font-medium text-white transition hover:bg-slate-800"
          >
            Publicar anuncio
          </router-link>

          <div class="flex items-center gap-3 border-l border-slate-200 pl-4">
            <div class="text-right">
              <p class="text-sm font-bold leading-none text-slate-900">
                {{ user?.username }}
              </p>

              <p class="mt-1 text-xs text-slate-400">
                {{ displayRole }}
              </p>
            </div>

            <button
              type="button"
              class="text-sm font-medium text-slate-500 transition-colors hover:text-red-600"
              @click="handleLogout"
            >
              Cerrar sesión
            </button>
          </div>
        </template>

        <template v-else>
          <router-link
            to="/login"
            class="rounded bg-slate-100 px-5 py-2 text-sm font-medium text-slate-900 transition hover:bg-slate-200"
          >
            Iniciar sesión
          </router-link>

          <router-link
            to="/register"
            class="rounded bg-slate-900 px-5 py-2 text-sm font-medium text-white transition hover:bg-slate-800"
          >
            Crear cuenta
          </router-link>
        </template>
      </div>

      <!-- Botón menú móvil -->
      <button
        type="button"
        class="p-1 text-slate-900 md:hidden"
        aria-label="Abrir o cerrar menú"
        @click="menuOpen = !menuOpen"
      >
        <svg
          v-if="!menuOpen"
          class="h-6 w-6"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M4 6h16M4 12h16M4 18h16"
          />
        </svg>

        <svg
          v-else
          class="h-6 w-6"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M6 18L18 6M6 6l12 12"
          />
        </svg>
      </button>
    </nav>

    <!-- Navegación móvil -->
    <div
      v-if="menuOpen"
      class="space-y-3 border-t border-slate-200 bg-white p-4 shadow-sm md:hidden"
    >
      <router-link
        to="/"
        class="block font-medium text-slate-600"
        @click="closeMenu"
      >
        Inicio
      </router-link>

      <router-link
        to="/anuncios"
        class="block font-medium text-slate-600"
        @click="closeMenu"
      >
        Alojamientos
      </router-link>

      <router-link
        v-if="isOwnerOrAdmin"
        to="/mis-anuncios"
        class="block font-medium text-slate-600"
        @click="closeMenu"
      >
        Mis anuncios
      </router-link>

      <router-link
        to="/contacto"
        class="block font-medium text-slate-600"
        @click="closeMenu"
      >
        Solicitudes
      </router-link>

      <router-link
        v-if="isAdmin"
        to="/admin-panel"
        class="block font-medium text-blue-600"
        @click="closeMenu"
      >
        Panel de administración
      </router-link>

      <router-link
        v-if="isAuthenticated"
        to="/profile"
        class="block font-medium text-slate-600"
        @click="closeMenu"
      >
        Mi perfil
      </router-link>

      <div
        v-if="!isAuthenticated"
        class="flex flex-col gap-2 border-t border-slate-100 pt-4"
      >
        <router-link
          to="/login"
          class="rounded bg-slate-100 py-2 text-center font-medium text-slate-900"
          @click="closeMenu"
        >
          Iniciar sesión
        </router-link>

        <router-link
          to="/register"
          class="rounded bg-slate-900 py-2 text-center font-medium text-white"
          @click="closeMenu"
        >
          Crear cuenta
        </router-link>
      </div>

      <div
        v-else
        class="flex flex-col gap-2 border-t border-slate-100 pt-4"
      >
        <router-link
          v-if="isOwnerOrAdmin"
          to="/crear-anuncio"
          class="rounded bg-slate-900 py-2 text-center font-medium text-white"
          @click="closeMenu"
        >
          Publicar anuncio
        </router-link>

        <button
          type="button"
          class="rounded bg-red-50 py-2 text-center font-medium text-red-600"
          @click="handleLogout"
        >
          Cerrar sesión
        </button>
      </div>
    </div>
  </header>
</template>