<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuth } from '../composables/useAuth'

/**
 * Vista de inicio de sesión.
 *
 * Responsabilidades:
 * - Recoger usuario y contraseña.
 * - Enviar credenciales al backend.
 * - Guardar el token y los datos del usuario autenticado.
 * - Redirigir al usuario a la ruta original o al inicio.
 */

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const router = useRouter()
const route = useRoute()

const { login } = useAuth()

const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

/**
 * Envía las credenciales al backend y gestiona la respuesta.
 */
const handleSubmit = async () => {
  error.value = ''

  if (!username.value || !password.value) {
    error.value = 'Introduce tu usuario y contraseña.'
    return
  }

  loading.value = true

  try {
    const response = await fetch(`${API_URL}/api/login/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username: username.value,
        password: password.value,
      }),
    })

    let data = {}

    try {
      data = await response.json()
    } catch {
      data = {}
    }

    if (!response.ok) {
      throw new Error(
        data.detail ||
        data.error ||
        data.non_field_errors?.[0] ||
        'Las credenciales introducidas no son válidas.'
      )
    }

    const token = data.token

    if (!token) {
      throw new Error('No se pudo procesar el token de seguridad.')
    }

    /**
     * Guardamos sesión en el composable global de autenticación.
     * Si el backend no devuelve user completo, se mantiene una estructura mínima.
     */
    login(token, data.user || {
      id: data.user?.id,
      username: username.value,
      email: data.user?.email || '',
      rol: data.user?.rol || 'estudiante',
      telefono: data.user?.telefono || '',
    })

    /**
     * Si el usuario intentaba acceder a una ruta protegida,
     * vuelve a esa ruta. Si no, va al inicio.
     */
    router.push(route.query.redirect || '/')
  } catch (err) {
    error.value = err.message || 'Se produjo un error al iniciar sesión.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <main class="flex min-h-[calc(100vh-4rem)] items-center justify-center bg-slate-50 px-4 py-12">
    <div class="w-full max-w-md rounded-lg border border-slate-200 bg-white p-6 shadow-sm md:p-8">
      <div class="mb-6 text-center">
        <h1 class="text-2xl font-extrabold tracking-tight text-slate-900">
          Iniciar sesión
        </h1>

        <p class="mt-2 text-sm text-slate-500">
          Accede a ErasmusStay para gestionar tus alojamientos, solicitudes y valoraciones.
        </p>
      </div>

      <form class="space-y-4" @submit.prevent="handleSubmit">
        <div>
          <label class="mb-2 block text-xs font-semibold uppercase text-slate-500">
            Usuario
          </label>

          <input
            v-model="username"
            type="text"
            autocomplete="username"
            placeholder="Tu nombre de usuario"
            required
            class="w-full rounded border border-slate-300 px-3 py-2 text-sm text-slate-700 focus:border-slate-900 focus:outline-none disabled:opacity-50"
            :disabled="loading"
          >
        </div>

        <div>
          <label class="mb-2 block text-xs font-semibold uppercase text-slate-500">
            Contraseña
          </label>

          <input
            v-model="password"
            type="password"
            autocomplete="current-password"
            placeholder="••••••••"
            required
            class="w-full rounded border border-slate-300 px-3 py-2 text-sm text-slate-700 focus:border-slate-900 focus:outline-none disabled:opacity-50"
            :disabled="loading"
          >
        </div>

        <div
          v-if="error"
          class="rounded border border-red-200 bg-red-50 p-3 text-xs text-red-600"
        >
          {{ error }}
        </div>

        <button
          type="submit"
          class="mt-2 w-full rounded bg-slate-900 py-2.5 text-sm font-bold text-white transition-colors hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
          :disabled="loading"
        >
          {{ loading ? 'Comprobando credenciales...' : 'Entrar' }}
        </button>
      </form>

      <div class="mt-6 flex flex-col gap-2 border-t border-slate-200 pt-6 text-center">
        <p class="text-sm text-slate-500">
          ¿Todavía no tienes cuenta?

          <router-link
            to="/register"
            class="ml-1 font-bold text-blue-600 transition-colors hover:text-blue-700"
          >
            Regístrate aquí
          </router-link>
        </p>

        <router-link
          to="/"
          class="mt-4 block text-sm font-medium text-slate-400 transition-colors hover:text-slate-600"
        >
          ← Volver al inicio
        </router-link>
      </div>
    </div>
  </main>
</template>