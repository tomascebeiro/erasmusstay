<script setup>
import Navigation from './components/Navigation.vue'

/**
 * Componente raíz de la aplicación.
 *
 * Responsabilidades:
 * - Mostrar la barra de navegación global.
 * - Renderizar la vista correspondiente mediante Vue Router.
 * - Mostrar un pie de página común en toda la aplicación.
 */
</script>

<template>
  <div class="min-h-screen bg-slate-50 text-slate-900">
    <Navigation />

    <router-view />

    <footer class="border-t border-slate-200 bg-white">
      <div class="mx-auto grid max-w-7xl gap-8 px-4 py-10 md:grid-cols-4">
        <div class="md:col-span-2">
          <router-link to="/" class="text-xl font-black tracking-tight text-slate-900">
            Erasmus<span class="text-slate-600">Stay</span>
          </router-link>

          <p class="mt-3 max-w-md text-sm leading-6 text-slate-500">
            Plataforma web para facilitar la búsqueda de alojamiento temporal a estudiantes Erasmus en Malta.
          </p>
        </div>

        <div>
          <h2 class="text-sm font-black uppercase tracking-wide text-slate-900">
            Plataforma
          </h2>

          <ul class="mt-4 space-y-2 text-sm text-slate-500">
            <li>
              <router-link to="/" class="hover:text-blue-600">
                Inicio
              </router-link>
            </li>

            <li>
              <router-link to="/anuncios" class="hover:text-blue-600">
                Buscar alojamientos
              </router-link>
            </li>

            <li>
              <router-link to="/crear-anuncio" class="hover:text-blue-600">
                Publicar anuncio
              </router-link>
            </li>

            <li>
              <router-link to="/mis-anuncios" class="hover:text-blue-600">
                Mis anuncios
              </router-link>
            </li>
          </ul>
        </div>

        <div>
          <h2 class="text-sm font-black uppercase tracking-wide text-slate-900">
            Cuenta
          </h2>

          <ul class="mt-4 space-y-2 text-sm text-slate-500">
            <li>
              <router-link to="/login" class="hover:text-blue-600">
                Iniciar sesión
              </router-link>
            </li>

            <li>
              <router-link to="/register" class="hover:text-blue-600">
                Crear cuenta
              </router-link>
            </li>

            <li>
              <router-link to="/profile" class="hover:text-blue-600">
                Mi perfil
              </router-link>
            </li>

            <li>
              <router-link to="/contacto" class="hover:text-blue-600">
                Solicitudes de contacto
              </router-link>
            </li>
          </ul>
        </div>
      </div>

      <div class="border-t border-slate-100 py-4">
        <div class="mx-auto flex max-w-7xl flex-col gap-2 px-4 text-sm text-slate-400 md:flex-row md:items-center md:justify-between">
          <p>
            © 2026 ErasmusStay. Proyecto de fin de ciclo DAW.
          </p>

          <p>
            Desarrollado con Django, Django REST Framework y Vue.
          </p>
        </div>
      </div>
    </footer>
  </div>
</template>